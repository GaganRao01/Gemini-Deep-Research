import os
import json
import time
import argparse
import requests
from typing import List, Dict, Any, Union, Optional
from bs4 import BeautifulSoup
from markdownify import markdownify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from newspaper import Article
from newspaper.article import ArticleException
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print(f"Dotenv loaded: GOOGLE_API_KEY set: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"Dotenv loaded: GOOGLE_SEARCH_API_KEY set: {bool(os.getenv('GOOGLE_SEARCH_API_KEY'))}")
print(f"Dotenv loaded: GOOGLE_CSE_ID set: {bool(os.getenv('GOOGLE_CSE_ID'))}")

# Initialize Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")
genai.configure(api_key=api_key)

# Initialize Google Custom Search API
search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")
if not search_api_key:
    raise ValueError("GOOGLE_SEARCH_API_KEY environment variable must be set")
if not google_cse_id:
    raise ValueError("GOOGLE_CSE_ID environment variable must be set")

# --- Google Search Tool ---
def google_search(query: str, num_results: int = 5, site_search: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Performs a Google search with the given query and returns a list of search results.
    
    Args:
        query: The search query string
        num_results: Number of search results to return (max 10)
        site_search: Optional site to restrict search to (e.g., "example.com")
        
    Returns:
        List of dictionaries containing search results with 'title', 'link', and 'snippet'
    """
    try:
        # Normalize site_search parameter
        if site_search is None or site_search == "" or site_search.lower() == "null" or site_search.lower() == "none":
            site_search = None
        
        # Add site restriction to query if provided
        final_query = query
        if site_search:
            if "site:" not in query:
                final_query = f"{query} site:{site_search}"
        
        print(f"\n[GoogleSearch] Executing search: '{final_query}' (max {num_results} results)")
        
        # Build Google Custom Search service
        service = build("customsearch", "v1", developerKey=search_api_key)
        
        # Set up search parameters with date sorting when appropriate
        search_params = {
            'q': final_query,
            'cx': google_cse_id,
            'num': min(num_results, 10)  # API limitation
        }
        
        # If query contains date-related terms, request date sorting
        # Note: 'sort' is not directly supported by Google CSE API, but we can add additional parameters
        if any(term in final_query.lower() for term in ['recent', 'latest', 'new', 'current', 'after:', '2023..', '2024..', 'last year']):
            # We'll use dateRestrict parameter to focus on recent content
            # Values can be: d[number] (past n days), w[number] (past n weeks), m[number] (past n months), y[number] (past n years)
            search_params['dateRestrict'] = 'y1'  # Default to past 1 year
            
            # Check for more specific timeframes in query
            if 'last week' in final_query.lower() or 'past week' in final_query.lower():
                search_params['dateRestrict'] = 'w1'
            elif 'last month' in final_query.lower() or 'past month' in final_query.lower():
                search_params['dateRestrict'] = 'm1'
            elif 'last 3 months' in final_query.lower() or 'past 3 months' in final_query.lower():
                search_params['dateRestrict'] = 'm3'
            elif 'last 6 months' in final_query.lower() or 'past 6 months' in final_query.lower():
                search_params['dateRestrict'] = 'm6'
                
            print(f"[GoogleSearch] Restricting results to {search_params['dateRestrict']} for recency-focused query")
        
        # Execute search
        result = service.cse().list(**search_params).execute()
        
        # Extract and return search results
        search_results = []
        if "items" in result:
            for item in result["items"]:
                # Extract date when available
                metatags = item.get("pagemap", {}).get("metatags", [{}])
                date = None
                for metatag in metatags:
                    # Try different meta tag formats for dates
                    for date_tag in ['article:published_time', 'datePublished', 'og:published_time', 'date']:
                        if date_tag in metatag:
                            date = metatag[date_tag]
                            break
                    if date:
                        break
                
                search_results.append({
                    "title": item.get("title", "No title"),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "No description available"),
                    "date": date if date else "Date not available"
                })
            
            print(f"[GoogleSearch] Found {len(search_results)} results")
            return search_results
        else:
            print(f"[GoogleSearch] No results found for query: '{final_query}'")
            return []
            
    except HttpError as e:
        error_details = json.loads(e.content.decode())
        error_reason = error_details.get("error", {}).get("errors", [{}])[0].get("reason", "unknown")
        error_message = error_details.get("error", {}).get("message", str(e))
        
        print(f"[GoogleSearch] API Error: {error_reason} - {error_message}")
        if error_reason == "dailyLimitExceeded":
            print("[GoogleSearch] Daily quota exceeded for Google Custom Search API.")
        elif error_reason == "accessNotConfigured":
            print("[GoogleSearch] API access not properly configured. Check your API key and search engine ID.")
        
        return []
    except Exception as e:
        print(f"[GoogleSearch] Error: {str(e)}")
        return []

# --- Web Content Scraper Tool ---
def scrape_web_content(url: str) -> Dict[str, str]:
    """
    Fetches content from a URL, extracts the main text, and returns cleaned content.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with 'content' or 'error' key
    """
    print(f"\n[WebScraper] Attempting to scrape: {url}")
    
    if not url or not isinstance(url, str) or not url.startswith("http"):
        error_msg = f"Input Error: A valid URL starting with 'http' is required. Received: '{url}'"
        print(f"[WebScraper] Error: {error_msg}")
        return {"error": error_msg}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"[WebScraper] Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=25, allow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        if 'html' not in content_type:
            error_msg = f"Skipping URL: Content-Type is '{content_type}', not HTML."
            print(f"[WebScraper] Info: {error_msg} URL: {url}")
            return {"error": error_msg}
        
        article = Article(url)
        article.download(input_html=response.text)
        article.parse()
        content_text = article.text
        
        if not content_text or len(content_text) < 100:
            print(f"[WebScraper] Warning: newspaper3k extracted minimal/no content from {url}. Attempting fallback with BeautifulSoup.")
            soup = BeautifulSoup(response.text, 'html.parser')
            main_content = soup.find('article') or soup.find('main') or soup.find('div', attrs={'role': 'main'}) or soup.find('body')
            if main_content:
                # Remove unwanted elements
                for tag_name in ['script', 'style', 'nav', 'footer', 'aside', 'header', 'form', 'button', 'input']:
                    for tag in main_content.select(tag_name):
                        tag.decompose()
                content_text = markdownify(str(main_content), heading_style="ATX")
            else:
                content_text = ""
            
            if not content_text or len(content_text) < 100:
                error_msg = f"Content Extraction Failed: newspaper3k and fallback method could not extract meaningful text content from {url}"
                print(f"[WebScraper] Error: {error_msg}")
                return {"error": error_msg}
        
        lines = [line.strip() for line in content_text.splitlines()]
        cleaned_text = '\n'.join(line for line in lines if line)
        
        if not cleaned_text.strip():
            error_msg = f"Content Extraction Failed: No text content found after cleaning for {url}."
            print(f"[WebScraper] Error: {error_msg}")
            return {"error": error_msg}
        
        print(f"[WebScraper] Successfully scraped and cleaned content from {url}. Length: {len(cleaned_text)} characters.")
        max_chars = 15000
        if len(cleaned_text) > max_chars:
            print(f"[WebScraper] Warning: Content from {url} truncated to {max_chars} characters.")
            cleaned_text = cleaned_text[:max_chars] + "\n... [Content Truncated]"
        
        return {"content": cleaned_text}
    
    except requests.exceptions.Timeout:
        error_msg = f"Scraping Error: Request timed out (>25s) for {url}."
        print(f"[WebScraper] Error: {error_msg}")
        return {"error": error_msg}
    except requests.exceptions.TooManyRedirects:
        error_msg = f"Scraping Error: Too many redirects for URL: {url}."
        print(f"[WebScraper] Error: {error_msg}")
        return {"error": error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"Scraping Error: Network issue fetching URL {url}. Reason: {e}"
        print(f"[WebScraper] Error: {error_msg}")
        return {"error": error_msg}
    except ArticleException as e:
        error_msg = f"Scraping Error: newspaper3k failed processing {url}. Reason: {e}. Likely not a standard article format."
        print(f"[WebScraper] Warning: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected Error while scraping {url}: {type(e).__name__} - {e}"
        import traceback
        print(f"[WebScraper] Error: {error_msg}\n{traceback.format_exc()}")
        return {"error": error_msg}

# --- Generate Search Queries with Gemini ---
def generate_search_queries(research_topic: str, num_queries: int) -> List[str]:
    """
    Generate diverse search queries to explore the research topic using Gemini.
    
    Args:
        research_topic: The topic to research
        num_queries: Number of search queries to generate
        
    Returns:
        List of search query strings
    """
    print(f"\n[SearchPlanner] Generating {num_queries} search queries for: '{research_topic}'")
    
    # Get the current year and month for date filtering
    from datetime import datetime
    current_year = datetime.now().year
    last_year = current_year - 1
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 2048
        }
    )
    
    prompt = f"""Generate exactly {num_queries} diverse and specific search queries to thoroughly research the topic: '{research_topic}'.

These queries should:
- Cover different aspects of the topic (concepts, applications, developments, challenges, etc.)
- Be specific and targeted rather than broad/generic
- PRIORITIZE recent content by using date ranges for recent information
- Use date filters extensively, especially "{last_year}..{current_year}" or "after:{last_year}"
- Include "latest", "recent", "new", or "current" in several queries
- Use advanced search operators where helpful (intitle:, intext:, etc.)
- For academic topics, include queries targeting recent papers, conferences, or research publications

Format your response as a Python list of strings. ONLY return the list, no other text:
["query 1", "query 2", ...]"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract list from response
        try:
            # Try to extract a proper Python list
            if response_text.startswith("[") and response_text.endswith("]"):
                queries = eval(response_text)
                if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
                    print(f"[SearchPlanner] Successfully generated {len(queries)} search queries")
                    return queries[:num_queries]  # Ensure we don't exceed the requested number
            
            # If eval fails or doesn't return a list, try parsing manually
            queries = []
            for line in response_text.split("\n"):
                line = line.strip()
                if line.startswith('"') or line.startswith("'"):
                    # Extract the query between quotes
                    query = line.strip('"\'').strip('",\'').strip()
                    if query:
                        queries.append(query)
                elif line.startswith("-") or line.startswith("*"):
                    # Extract queries from bullet points
                    query = line[1:].strip()
                    if query:
                        queries.append(query)
            
            if queries:
                print(f"[SearchPlanner] Extracted {len(queries)} queries through manual parsing")
                return queries[:num_queries]
                
            # If all else fails, split by commas
            if "," in response_text:
                queries = [q.strip() for q in response_text.split(",")]
                print(f"[SearchPlanner] Extracted {len(queries)} queries by splitting on commas")
                return queries[:num_queries]
        except:
            print(f"[SearchPlanner] Error parsing the generated queries. Using fallback method.")
        
        # Fallback: Generate generic queries with current date ranges
        fallback_queries = [
            f"{research_topic} definition AND latest developments {current_year}",
            f"{research_topic} recent research {last_year}..{current_year}",
            f"{research_topic} new applications case studies after:{last_year}",
            f"{research_topic} current challenges and limitations {current_year}",
            f"latest trends {research_topic} {current_year} expert analysis",
            f"recent breakthroughs in {research_topic} {last_year}..{current_year}",
            f"newest {research_topic} research papers {current_year}",
            f"{research_topic} future implications {current_year}"
        ]
        print(f"[SearchPlanner] Using {num_queries} fallback queries")
        return fallback_queries[:num_queries]
        
    except Exception as e:
        print(f"[SearchPlanner] Error generating search queries: {str(e)}")
        # Fallback queries
        from datetime import datetime
        current_year = datetime.now().year
        last_year = current_year - 1
        
        fallback_queries = [
            f"{research_topic} definition AND latest developments {current_year}",
            f"{research_topic} recent research {last_year}..{current_year}",
            f"{research_topic} new applications case studies after:{last_year}",
            f"{research_topic} current challenges and limitations {current_year}",
            f"latest trends {research_topic} {current_year} expert analysis",
            f"recent breakthroughs in {research_topic} {last_year}..{current_year}",
            f"newest {research_topic} research papers {current_year}",
            f"{research_topic} future implications {current_year}"
        ]
        print(f"[SearchPlanner] Using {num_queries} fallback queries due to error")
        return fallback_queries[:num_queries]

# --- Research Execution Function ---
def execute_research(queries: List[str], results_per_query: int, site_restriction: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Execute the research by running searches and scraping content.
    
    Args:
        queries: List of search queries to run
        results_per_query: Number of results to fetch per query
        site_restriction: Optional site to restrict searches to
        
    Returns:
        List of dictionaries with research data
    """
    research_data = []
    
    for query_idx, query in enumerate(queries):
        print(f"\n[Researcher] Processing query {query_idx+1}/{len(queries)}: '{query}'")
        
        # Search for results
        search_results = google_search(query, num_results=results_per_query, site_search=site_restriction)
        
        if not search_results:
            print(f"[Researcher] No search results found for query: '{query}'")
            research_data.append({
                "query": query,
                "search_results": [],
                "scraped_content": []
            })
            continue
        
        # Try to detect date pattern in the content
        def extract_date_from_content(content: str) -> Optional[str]:
            import re
            
            # Look for common date patterns in the content
            # YYYY-MM-DD format
            date_pattern1 = re.compile(r'\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12][0-9]|3[01])\b')
            # Month DD, YYYY format
            date_pattern2 = re.compile(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})\b')
            # DD Month YYYY format
            date_pattern3 = re.compile(r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b')
            
            date_match = date_pattern1.search(content) or date_pattern2.search(content) or date_pattern3.search(content)
            if date_match:
                return date_match.group(0)
            return None
        
        # Scrape content from each result
        scraped_content = []
        for result_idx, result in enumerate(search_results):
            url = result.get("link")
            if not url:
                continue
                
            print(f"[Researcher] Processing search result {result_idx+1}/{len(search_results)}: {url}")
            
            # Use the date from the search result if available
            date_from_search = result.get("date", "")
            
            # Attempt to scrape content
            scraped_result = scrape_web_content(url)
            content = scraped_result.get("content", "")
            error = scraped_result.get("error", "")
            
            # Try to extract date from content if not already available
            content_date = None
            if content and (not date_from_search or date_from_search == "Date not available"):
                content_date = extract_date_from_content(content)
            
            # Determine the most reliable date
            publication_date = date_from_search
            if (not publication_date or publication_date == "Date not available") and content_date:
                publication_date = content_date
            
            # Add to collected data
            scraped_content.append({
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("snippet", ""),
                "content": content,
                "error": error,
                "date": publication_date
            })
            
            # Add a short delay to avoid overwhelming servers
            time.sleep(1)
        
        # Add data for this query
        research_data.append({
            "query": query,
            "search_results": search_results,
            "scraped_content": scraped_content
        })
    
    return research_data

# --- Synthesize Research Report with Gemini ---
def synthesize_report(research_topic: str, research_data: List[Dict[str, Any]], depth: int) -> str:
    """
    Synthesize a comprehensive research report using Gemini by breaking it into manageable chunks.
    
    Args:
        research_topic: The research topic
        research_data: Collected research data
        depth: Research depth level (1-3)
        
    Returns:
        Formatted research report
    """
    print(f"\n[Synthesizer] Creating research report on '{research_topic}' at depth level {depth}")
    
    # Add current date to report
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Create context for the model
    context = f"# Research Topic: {research_topic}\n\n"
    
    # Add collected data
    source_count = 0
    for query_data in research_data:
        query = query_data.get("query", "")
        context += f"## Search Query: {query}\n\n"
        
        for content_item in query_data.get("scraped_content", []):
            title = content_item.get("title", "No title")
            url = content_item.get("url", "")
            content = content_item.get("content", "")
            date = content_item.get("date", "Date not available")  # Include date when available
            error = content_item.get("error", "")
            
            if content:  # Only add if content was successfully scraped
                source_count += 1
                context += f"### Source {source_count}: {title}\n"
                context += f"URL: {url}\n"
                context += f"Date: {date}\n\n"
                # Limit content length to avoid exceeding model context
                max_content_chars = 10000
                if len(content) > max_content_chars:
                    context += content[:max_content_chars] + "...\n\n"
                else:
                    context += content + "\n\n"
    
    # Determine report expectations based on depth
    if depth == 1:
        report_length = "5-7 pages"
        report_detail = "key findings, insights, and a clear overview"
        min_words = 2500  # Approximately 5 pages
        sections = 5  # Basic sections for depth 1
    elif depth == 2:
        report_length = "10-15 pages"
        report_detail = "thorough analysis, detailed exploration of subtopics, and synthesis of diverse perspectives"
        min_words = 5000  # Approximately 10 pages
        sections = 8  # More sections for depth 2
    else:  # depth == 3
        report_length = "20-30 pages"
        report_detail = "comprehensive coverage, in-depth analysis, historical context, theoretical frameworks, case studies, and future implications"
        min_words = 10000  # Approximately 20 pages
        sections = 12  # Many sections for depth 3
    
    # Initialize Gemini model with appropriate settings
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": 0.2,  # Lower temperature for more factual output
            "top_p": 0.95,
            "max_output_tokens": 100000  # Set to maximum for comprehensive reports
        }
    )
    
    # For larger reports (depth 2-3), break it down into sections
    if depth >= 2:
        print(f"[Synthesizer] Breaking down depth {depth} report into {sections} sections")
        
        # First, generate an outline
        outline_prompt = f"""Create a detailed outline for a {report_length} research report on '{research_topic}'.
        
Today's date is {current_date}.

The research report should include exactly {sections} main sections (plus executive summary, introduction, and conclusion).
Provide a detailed title for each section and 3-5 subsections under each main section.
The outline should be comprehensive and reflect the latest developments in this field.

FORMAT YOUR RESPONSE AS:
1. Title of section 1
   1.1 Subsection title
   1.2 Subsection title
   1.3 Subsection title
2. Title of section 2
   ...and so on

DO NOT include explanatory text, just the outline structure.
"""
        
        try:
            outline_response = model.generate_content(outline_prompt)
            outline = outline_response.text.strip()
            print(f"[Synthesizer] Successfully generated report outline with {sections} main sections")
            
            # Extract main sections from the outline
            import re
            main_sections = re.findall(r'^\d+\.\s+(.*?)$', outline, re.MULTILINE)
            
            if len(main_sections) < 3:  # Fallback if section extraction fails
                main_sections = [
                    "Background and Theoretical Foundations",
                    "Current Technologies and Implementations",
                    "Challenges and Limitations",
                    "Future Directions and Implications",
                    "Practical Applications and Case Studies"
                ]
                if depth == 3:
                    main_sections.extend([
                        "Comparative Analysis and Benchmarks",
                        "Regulatory and Compliance Considerations",
                        "Ethical Implications"
                    ])
            
            # Create executive summary and introduction
            intro_prompt = f"""Based on the research data provided, write the following parts of a research report on '{research_topic}':
1. A compelling executive summary (300-500 words)
2. An introduction that sets the context (500-800 words)

Today's date is {current_date}. Include this date in the publication date.

Research data:
{context[:15000]}  # Limit context to avoid token limit

FORMAT: Professional, academic style with appropriate headings.
"""
            
            intro_response = model.generate_content(intro_prompt)
            report_parts = [intro_response.text.strip()]
            
            # Generate each section separately
            for i, section_title in enumerate(main_sections[:sections]):
                section_num = i + 1
                section_prompt = f"""Write section {section_num}: "{section_title}" for a depth level {depth} research report on '{research_topic}'.

This section should be approximately {2000 if depth == 2 else 3000} words and dive deep into this aspect of the topic.
Include relevant subsections, use proper citations to sources, and provide detailed analysis.
Ensure you incorporate the most recent developments (current date: {current_date}).

Research data related to this section:
{context[:20000]}  # Limit context to avoid token limit

FORMAT: Professional academic style with clear subsection headings (e.g., "{section_num}.1", "{section_num}.2").
"""
                
                print(f"[Synthesizer] Generating section {section_num}: {section_title}")
                section_response = model.generate_content(section_prompt)
                report_parts.append(section_response.text.strip())
            
            # Generate conclusion
            conclusion_prompt = f"""Write the conclusion section for a depth level {depth} research report on '{research_topic}'.

The conclusion should:
1. Summarize the key findings from all sections
2. Synthesize insights into a coherent whole
3. Discuss implications for the field
4. Suggest directions for future research
5. End with strong closing thoughts

Length: Approximately 1000-1500 words

Research data:
{context[:10000]}  # Limit context to avoid token limit

FORMAT: Professional academic style.
"""
            
            conclusion_response = model.generate_content(conclusion_prompt)
            report_parts.append(conclusion_response.text.strip())
            
            # Combine all parts
            full_report = "\n\n".join(report_parts)
            
            # Ensure the report includes the current date
            if current_date not in full_report[:1000]:  # Check first 1000 chars
                full_report = f"## {research_topic}\n\n**Research Report**\n\n**Date: {current_date}**\n\n" + full_report
            
            word_count = len(full_report.split())
            print(f"[Synthesizer] Successfully generated comprehensive report ({len(full_report)} characters, ~{word_count} words)")
            
            return full_report
            
        except Exception as e:
            print(f"[Synthesizer] Error in sectional report generation: {str(e)}")
            print(f"[Synthesizer] Falling back to standard report generation")
            # Continue with standard approach below
    
    # Standard approach for depth 1 or if sectional approach fails
    prompt = f"""Based on the research data provided, create a comprehensive, well-structured research report on '{research_topic}'.

IMPORTANT: Today's date is {current_date}. Use this as the publication date of the report.

For depth level {depth}, your report should be {report_length} with {report_detail}.
YOU MUST generate a report of at least {min_words} words in length to meet the requirements for a depth level {depth} report.

Your report must include:
- Executive summary
- Introduction to the topic area
- Thorough exploration of all major dimensions of the topic
- {"Basic analysis of key findings" if depth == 1 else "Detailed analysis with supporting evidence" if depth == 2 else "Comprehensive analysis with nuanced insights, theoretical underpinnings, and practical applications"}
- Conclusion with key takeaways
- {"" if depth == 1 else "Recommendations based on findings" if depth == 2 else "Extensive recommendations, future research directions, and implications"}
- References/sources with URLs for all information presented

REQUIREMENTS:
1. Use ONLY the most recent sources when discussing current developments
2. Clearly indicate publication date at the top of your report ({current_date})
3. Present multiple perspectives on controversial aspects of the topic
4. Use proper academic citations throughout the text
5. Organize the report with clear section headers and subheaders
6. Include specific examples, case studies, and data points to support your analysis
7. For a depth-{depth} report, you MUST write at least {min_words} words to be sufficiently comprehensive

FORMAT: Present your research as a professional, academic-style report with appropriate headings, subheadings, and formatting.
Include URLs in proper citation format to credit your sources throughout the document.

Here is the research data to synthesize:

{context}"""

    try:
        print(f"[Synthesizer] Generating report with Gemini...")
        response = model.generate_content(prompt)
        report = response.text
        
        # Ensure the report includes the current date
        if current_date not in report[:1000]:  # Check first 1000 chars
            report = f"## {research_topic}\n\n**Research Report**\n\n**Date: {current_date}**\n\n" + report
        
        word_count = len(report.split())
        print(f"[Synthesizer] Successfully generated research report ({len(report)} characters, ~{word_count} words)")
        
        # Check if report is long enough
        if word_count < min_words * 0.8:  # Allow some flexibility
            print(f"[Synthesizer] Warning: Report may be shorter than expected for depth level {depth}")
            
        return report
    except Exception as e:
        print(f"[Synthesizer] Error generating research report: {str(e)}")
        return f"Error generating research report: {str(e)}\n\nPlease try again with a smaller research scope or lower depth level."

# --- Main Execution Logic ---
def main():
    parser = argparse.ArgumentParser(description="Deep Research Tool using Google Gemini")
    
    # Required arguments
    parser.add_argument("-c", "--context", required=True, help="The research context/question")
    
    # Optional arguments
    parser.add_argument("--depth", type=int, choices=[1, 2, 3], default=1, 
                        help="Research depth: 1 (Basic), 2 (Detailed), 3 (Comprehensive)")
    parser.add_argument("-q", "--queries", type=int, default=None, 
                        help="Number of search queries to generate (default: based on depth)")
    parser.add_argument("-r", "--results", type=int, default=None, 
                        help="Number of results per query (default: based on depth)")
    parser.add_argument("-s", "--site", default=None, 
                        help="Restrict search to a specific site (e.g., 'nytimes.com')")
    parser.add_argument("--verbose", type=int, default=1, choices=[0, 1, 2], 
                        help="Verbosity level: 0 (minimal), 1 (regular), 2 (debug)")
    
    args = parser.parse_args()
    
    # Set depth-based defaults if not specified
    if args.depth == 1:  # Basic
        num_queries = args.queries if args.queries is not None else 3
        results_per_query = args.results if args.results is not None else 2
    elif args.depth == 2:  # Detailed
        num_queries = args.queries if args.queries is not None else 5
        results_per_query = args.results if args.results is not None else 3
    else:  # Comprehensive (depth = 3)
        num_queries = args.queries if args.queries is not None else 8
        results_per_query = args.results if args.results is not None else 4
    
    # Print configuration
    print("\n" + "=" * 50)
    print(f"🔍 STARTING DEEP RESEARCH ON: '{args.context}'")
    print("=" * 50)
    print(f"📊 Configuration:")
    print(f"   - Research depth: {args.depth} ({'Basic' if args.depth == 1 else 'Detailed' if args.depth == 2 else 'Comprehensive'})")
    print(f"   - Number of search queries: {num_queries}")
    print(f"   - Results per query: {results_per_query}")
    print(f"   - Site restriction: {args.site if args.site else 'None'}")
    print(f"   - Verbosity level: {args.verbose}")
    print("=" * 50 + "\n")
    
    try:
        # Step 1: Generate search queries
        search_queries = generate_search_queries(args.context, num_queries)
        
        # Step 2: Execute research process
        research_data = execute_research(search_queries, results_per_query, args.site)
        
        # Step 3: Synthesize research into a report
        report = synthesize_report(args.context, research_data, args.depth)
        
        # Print report
        print("\n" + "=" * 50)
        print("🔍 RESEARCH COMPLETED")
        print("=" * 50 + "\n")
        print(report)
        
        # Optionally save report to file
        filename = f"research_report_{args.context.replace(' ', '_')[:30]}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
        
        return report
    
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred during research: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 