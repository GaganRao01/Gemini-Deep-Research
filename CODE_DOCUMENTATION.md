# Gemini Deep Research Platform – Code Documentation

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
</div>

<div align="center">
  <p><i>In-depth documentation of the Gemini Deep Research platform's code architecture and workflow</i></p>
</div>

---

## Table of Contents

- [Overview](#overview)
- [Application Architecture](#application-architecture)
- [Core Components](#core-components)
  - [1. Initialization & Setup](#1-initialization--setup)
  - [2. Search Query Generation](#2-search-query-generation)
  - [3. Web Search Engine](#3-web-search-engine)
  - [4. Content Scraping System](#4-content-scraping-system)
  - [5. Sectional Report Generation](#5-sectional-report-generation)
  - [6. Format Standardization](#6-format-standardization)
- [Data Flow & Process Sequence](#data-flow--process-sequence)
- [Advanced Features](#advanced-features)
  - [Recency Prioritization](#recency-prioritization)
  - [Content Chunking](#content-chunking)
  - [Error Handling](#error-handling)
- [Configuration Options](#configuration-options)

---

## Overview

The Gemini Deep Research platform is an automated research solution that leverages Google's Gemini Large Language Model (LLM) to generate comprehensive, well-structured research reports on any topic. The platform functions as an end-to-end research assistant, automating every step from search query formulation to final report synthesis.

At its core, the system orchestrates a complex workflow that begins with generating diverse, targeted search queries about a research topic. It then executes these queries through the Google Custom Search API, extracts and processes textual content from high-quality sources, and finally synthesizes the collected information into a professionally structured research report with proper citations and references.

## Application Architecture

The platform follows a sequential pipeline architecture where each component performs a specific function and passes its output to the next component in the chain:

1. **Initialization & Setup**: Validates and configures essential API connections and environment variables
2. **Search Query Generation**: Creates intelligently formulated search queries tailored to the research topic
3. **Web Search Engine**: Retrieves relevant search results using the Google Custom Search API
4. **Content Scraping System**: Extracts, cleans, and normalizes text content from web pages
5. **Sectional Report Generation**: Synthesizes collected data into structured report sections
6. **Format Standardization**: Applies consistent formatting, citation styles, and section organization

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Query          │────▶│  Web Search     │────▶│  Content        │
│  Generation     │     │  System         │     │  Scraping       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Report         │◀────│  Sectional      │◀────│  Research Data  │
│  Formatting     │     │  Report         │     │  Collection     │
│                 │     │  Generation     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐
│                 │
│  Markdown       │
│  Output         │
│                 │
└─────────────────┘
```

---

## Core Components

### 1. Initialization & Setup

The system begins by loading three critical API keys from environment variables using the `dotenv` library:

```python
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
```

The system requires:
- `GOOGLE_API_KEY`: For accessing Gemini API (used for query generation and report synthesis)
- `GOOGLE_SEARCH_API_KEY`: For executing Google Custom Search queries
- `GOOGLE_CSE_ID`: The unique identifier for your configured Custom Search Engine

The code performs validation checks to ensure all required keys are present, raising explicit errors if any are missing.

### 2. Search Query Generation

The `generate_search_queries()` function is a sophisticated component that uses Gemini to create diverse, targeted search queries optimized for thorough research:

```python
def generate_search_queries(research_topic: str, num_queries: int) -> List[str]:
    """
    Generate diverse search queries to explore the research topic using Gemini.
    
    Args:
        research_topic: The topic to research
        num_queries: Number of search queries to generate
        
    Returns:
        List of search query strings
    """
```

Under the hood, this function:

1. **Prepares a context-aware prompt**: Creates a detailed prompt instructing Gemini to generate diverse queries that cover different aspects of the topic with specific search operators
2. **Requests query generation**: Calls the Gemini API with specific generation parameters (temperature=0.7 for balanced creativity)
3. **Processes the response**: Extracts and validates the generated queries from the LLM's response
4. **Implements robust fallbacks**: If the LLM fails or returns incorrectly formatted queries, the system has multiple parsing strategies and ultimately falls back to a predefined set of generic query templates

Key aspects of the prompt design:
```python
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
```

Fallback query templates include:
```python
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
```

### 3. Web Search Engine

The `google_search()` function executes search queries through the Google Custom Search API and returns structured results:

```python
def google_search(query: str, num_results: int = 5, site_search: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Performs a Google search with the given query and returns a list of search results.
    """
```

The function's implementation includes:

1. **Query preparation**: Formats the search query with site restrictions if specified
2. **Advanced search parameters**: Sets up the search with appropriate parameters like date restrictions
3. **Intelligent date filtering**: Automatically restricts results to recent content when the query suggests recency is important
4. **Response processing**: Extracts and structures the search results with consistent formatting
5. **Error handling**: Handles API errors with specific recognition of quota limits and access issues

The date restriction logic is particularly sophisticated:
```python
if any(term in final_query.lower() for term in ['recent', 'latest', 'new', 'current', 'after:', '2023..', '2024..', 'last year']):
    search_params['dateRestrict'] = 'y1'  # Last year
    if 'last week' in final_query.lower() or 'past week' in final_query.lower():
        search_params['dateRestrict'] = 'w1'  # Last week
    elif 'last month' in final_query.lower() or 'past month' in final_query.lower():
        search_params['dateRestrict'] = 'm1'  # Last month
    # Additional date restrictions...
```

The returned results include structured data with:
- Page title
- URL link
- Text snippet
- Publication date (when available)

### 4. Content Scraping System

The `scrape_web_content()` function implements a sophisticated content extraction system:

```python
def scrape_web_content(url: str) -> Dict[str, str]:
    """
    Fetches content from a URL, extracts the main text, and returns cleaned content.
    """
```

The system employs a multi-layered approach to content extraction:

1. **URL validation**: Ensures the provided URL is properly formatted
2. **Configurable request headers**: Uses browser-like headers to minimize blocking by websites
3. **Primary extraction**: Uses the newspaper3k library to extract the main article text
4. **Intelligent fallback**: If newspaper3k fails, falls back to BeautifulSoup with targeted element selection
5. **Content cleaning**: Removes extraneous whitespace, normalizes formatting
6. **Content limiting**: Truncates overly long content to 15,000 characters to stay within model context limits

The fallback mechanism is particularly important for handling diverse web pages:
```python
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
```

The function returns either a dictionary with a 'content' key containing the extracted text or an 'error' key with a descriptive error message if extraction fails.

### 5. Sectional Report Generation

The `synthesize_report()` function is the most complex component, responsible for transforming the collected research data into a coherent, structured report:

```python
def synthesize_report(research_topic: str, research_data: List[Dict[str, Any]], depth: int) -> str:
    """
    Synthesize a comprehensive research report using Gemini by breaking it into manageable chunks.
    """
```

This function employs two distinct approaches based on the depth level:

**Approach 1: Sectional Generation (depth ≥ 2)**
For more comprehensive reports, the function breaks the task into multiple smaller generations:

1. **Outline Generation**: First creates a detailed outline for the entire report
   ```python
   outline_prompt = f"""Create a detailed outline for a {report_length} research report on '{research_topic}'..."""
   ```

2. **Section-by-Section Generation**: Generates each major section individually
   ```python
   for i, section_title in enumerate(content_sections):
       section_num = i + 3  # Starting from section 3 (after exec summary and intro)
       section_prompt = f"""Write section {section_num}: "{section_title}" for a depth level {depth} research report..."""
   ```

3. **Specialized Sections**: Separately generates standardized sections such as executive summary, introduction, challenges, future directions, and conclusion
   ```python
   challenges_prompt = f"""Write the "Challenges and Limitations" section for a depth level {depth} research report..."""
   ```

4. **Reference Consolidation**: Extracts and consolidates all references from individual sections
   ```python
   # Extract references from the section to consolidate later
   references_match = re.search(r'(?:References|Sources):\s*([\s\S]+?)(?=\n\n|$)', section_content, re.IGNORECASE)
   if references_match:
       section_refs = references_match.group(1).strip()
       all_references.extend([ref.strip() for ref in section_refs.split('\n') if ref.strip()])
   ```

**Approach 2: Single-Pass Generation (depth = 1 or fallback)**
For simpler reports or when sectional generation fails:

1. **Comprehensive Prompt**: Creates a detailed prompt with all research data
   ```python
   prompt = f"""Based on the research data provided, create a comprehensive, well-structured research report on '{research_topic}'..."""
   ```

2. **Single Generation**: Makes a single API call to generate the entire report

**Common Post-Processing**
Both approaches use sophisticated post-processing to:

1. **Format Standardization**: Normalizes headings and section numbering
   ```python
   # Standardize section numbering and formatting
   formatted_lines = []
   section_pattern = r'^#+\s*(.*?)$|^(\d+\..*?)$'  # Match markdown headings or numbered headings
   
   in_references = False
   for line in report.split('\n'):
       # Process line by line...
   ```

2. **Reference Formatting**: Ensures references are consistently formatted and placed at the end
3. **Section Organization**: Ensures proper hierarchy of sections and subsections
4. **Date Inclusion**: Adds current date as publication date if not already included

The function adapts its generation strategy based on the depth level:
```python
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
```

### 6. Format Standardization

The report formatting system ensures consistent structure through:

1. **Section Standardization**: Normalizes section headers to follow proper Markdown format
   ```python
   # Process section headings
   section_match = re.search(section_pattern, line)
   if section_match:
       heading = section_match.group(1) or section_match.group(2)
       # Remove numbering from the heading text
       clean_heading = re.sub(r'^\d+\.\d*\s*', '', heading)
       clean_heading = re.sub(r'^\d+\.\s*', '', clean_heading)
       
       # Check for subsection (contains a dot in the number or has ### format)
       if '.' in heading or line.startswith('###'):
           formatted_lines.append(f"### {clean_heading}")
       # Main section (just a number or ## format)
       elif re.match(r'^\d+\.?\s*', heading) or line.startswith('##'):
           formatted_lines.append(f"## {clean_heading}")
       else:
           formatted_lines.append(line)
   ```

2. **Reference Consolidation**: Collects and deduplicates references across all sections
3. **Date Format Consistency**: Ensures the publication date is consistently formatted
4. **Citation Style Standardization**: Regularizes in-text citations

---

## Data Flow & Process Sequence

The platform's workflow follows these steps in sequence:

1. **Command-Line Argument Processing**
   ```python
   parser = argparse.ArgumentParser(description="Deep Research Tool using Google Gemini")
   parser.add_argument("-c", "--context", required=True, help="The research context/question")
   parser.add_argument("--depth", type=int, choices=[1, 2, 3], default=1)
   # Additional arguments...
   ```

2. **Depth-Based Configuration**
   ```python
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
   ```

3. **Search Query Generation**
   ```python
   search_queries = generate_search_queries(args.context, num_queries)
   ```

4. **Research Execution**
   ```python
   research_data = execute_research(search_queries, results_per_query, args.site)
   ```
   The `execute_research()` function orchestrates:
   - Iterating through each search query
   - Executing the search using `google_search()`
   - Processing each result using `scrape_web_content()`
   - Collecting and structuring all research data

5. **Report Synthesis**
   ```python
   report = synthesize_report(args.context, research_data, args.depth)
   ```

6. **Report Saving**
   ```python
   filename = f"research_report_{args.context.replace(' ', '_')[:30]}.md"
   with open(filename, "w", encoding="utf-8") as f:
       f.write(report)
   ```

---

## Advanced Features

### Recency Prioritization

The system employs multiple mechanisms to prioritize recent information:

1. **Query-Level Recency Terms**
   ```python
   # In query generation prompt
   prompt = f"""
   ...
   - PRIORITIZE recent content by using date ranges for recent information
   - Use date filters extensively, especially "{last_year}..{current_year}" or "after:{last_year}"
   - Include "latest", "recent", "new", or "current" in several queries
   ...
   """
   ```

2. **Search Parameter Tuning**
   ```python
   # Dynamic date restriction in google_search()
   if any(term in final_query.lower() for term in ['recent', 'latest', 'new', 'current', 'after:', '2023..', '2024..', 'last year']):
       search_params['dateRestrict'] = 'y1'
       # More granular restrictions based on query terms...
   ```

3. **Date Extraction from Content**
   ```python
   # In execute_research()
   def extract_date_from_content(content: str) -> Optional[str]:
       import re
       
       # Looking for common date patterns in the content
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
   ```

### Content Chunking

To manage context limits in Gemini API calls, the system implements sophisticated content chunking:

1. **Section-by-Section Generation**
   ```python
   # In synthesize_report()
   content_sections = [section for section in main_sections if section not in 
                    ["Executive Summary", "Introduction", "Conclusion", "References", 
                     "Challenges and Limitations", "Future Directions and Research Opportunities"]]
   
   # First generate all content sections
   for i, section_title in enumerate(content_sections):
       # Generate each section individually
   ```

2. **Context Limiting in Prompts**
   ```python
   # Example of context limiting in section generation
   section_prompt = f"""Write section {section_num}: "{section_title}" for a depth level {depth} research report on '{research_topic}'.
   ...
   Research data related to this section:
   {context[:20000]}  # Limit context to avoid token limit
   """
   ```

3. **Content Truncation in Web Scraping**
   ```python
   # In scrape_web_content()
   max_chars = 15000
   if len(cleaned_text) > max_chars:
       print(f"[WebScraper] Warning: Content from {url} truncated to {max_chars} characters.")
       cleaned_text = cleaned_text[:max_chars] + "\n... [Content Truncated]"
   ```

### Error Handling

The system implements comprehensive error handling throughout:

1. **API Quota Management**
   ```python
   # In google_search()
   except HttpError as e:
       error_details = json.loads(e.content.decode())
       error_reason = error_details.get("error", {}).get("errors", [{}])[0].get("reason", "unknown")
       error_message = error_details.get("error", {}).get("message", str(e))
       
       print(f"[GoogleSearch] API Error: {error_reason} - {error_message}")
       if error_reason == "dailyLimitExceeded":
           print("[GoogleSearch] Daily quota exceeded for Google Custom Search API.")
   ```

2. **Multi-Layer Fallbacks in Web Scraping**
   ```python
   # Primary and fallback extraction in scrape_web_content()
   article = Article(url)
   article.download(input_html=response.text)
   article.parse()
   content_text = article.text
   
   if not content_text or len(content_text) < 100:
       print(f"[WebScraper] Warning: newspaper3k extracted minimal/no content from {url}. Attempting fallback with BeautifulSoup.")
       soup = BeautifulSoup(response.text, 'html.parser')
       main_content = soup.find('article') or soup.find('main') or soup.find('div', attrs={'role': 'main'}) or soup.find('body')
       # Fallback extraction logic...
   ```

3. **Graceful Fallbacks in Report Generation**
   ```python
   # In synthesize_report()
   try:
       # Sectional report generation approach
   except Exception as e:
       print(f"[Synthesizer] Error in sectional report generation: {str(e)}")
       print(f"[Synthesizer] Falling back to standard report generation")
       # Standard approach fallback
   ```

## Configuration Options

The platform supports flexible configuration through command-line arguments:

```python
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
```

The depth parameter is particularly important as it controls:
- Number of search queries (3 for depth=1, 5 for depth=2, 8 for depth=3)
- Results per query (2 for depth=1, 3 for depth=2, 4 for depth=3)
- Report length and detail level
- Sectional breakdown approach

## Conclusion

The Gemini Deep Research platform represents a sophisticated application of AI to automate the research process. Its modular, pipeline architecture allows for flexible processing of research topics, while its depth-level configuration provides adaptability for different use cases.

The most significant technical features include:
1. Multi-stage content extraction with fallbacks
2. Intelligent chunking to manage model context limits
3. Section-by-section report generation for longer documents
4. Comprehensive error handling with appropriate fallbacks
5. Customizable search patterns with recency prioritization

These capabilities enable the system to generate high-quality, structured research reports on virtually any topic with minimal user input beyond specifying the research question and desired depth level. 
