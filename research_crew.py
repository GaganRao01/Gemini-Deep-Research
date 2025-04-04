import os
import json
import requests
import argparse
from typing import List, Dict, Any, Union, Optional, ClassVar, Type

# Third-party imports
from bs4 import BeautifulSoup
from markdownify import markdownify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from newspaper import Article
from newspaper.article import ArticleException

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool

# LangChain imports (CrewAI uses LangChain)
from langchain_openai import ChatOpenAI

# Local imports
from google_search_schema import GoogleCustomSearchToolSchema

# Load environment variables
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
print(f"Dotenv loaded: OPENAI_API_KEY set: {bool(os.getenv('OPENAI_API_KEY'))}")

# --- Define Custom Tools ---

class GoogleCustomSearchTool(BaseTool):
    name: str = "Google Custom Search Tool"
    description: str = (
        "Performs a Google search using a Custom Search Engine (CSE) and returns results. "
        "Input MUST be a dictionary containing the key 'query' (a string for the search term). "
        "Optionally, it can include 'num_results' (int, default 3, max 10) and 'site_search' (string, e.g., 'wikipedia.org'). "
        "Returns a list of search result dictionaries (each with 'title', 'link', 'snippet') OR an error dictionary {'error': message}."
    )
    
    # Use the schema from our imported module with proper annotation
    schema_class: ClassVar[Type[GoogleCustomSearchToolSchema]] = GoogleCustomSearchToolSchema

    def _run(self, query: str, num_results: int = 3, site_search: Optional[str] = None) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")

        print(f"\n[GoogleCustomSearchTool] Attempting to run...")
        print(f"[GoogleCustomSearchTool] Received arguments -> query: '{query}', num_results: {num_results}, site_search: '{site_search if site_search is not None else 'None'}'")

        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable is not set")
            return {"error": "Configuration Error: GOOGLE_API_KEY environment variable is not set"}
        if not cse_id:
            print("Error: GOOGLE_CSE_ID environment variable is not set")
            return {"error": "Configuration Error: GOOGLE_CSE_ID environment variable is not set"}

        if not query or not isinstance(query, str):
            error_msg = f"Input Error: 'query' parameter is required and must be a non-empty string. Received: '{query}' (type: {type(query)})"
            print(f"Error: {error_msg}")
            return {"error": error_msg}

        if not isinstance(num_results, int) or not 1 <= num_results <= 10:
            print(f"Warning: Invalid num_results '{num_results}'. Defaulting to 3.")
            num = 3
        else:
            num = num_results

        # Normalize site_search parameter - treat empty string as None
        if site_search == "":
            site_search = None
        elif site_search == "null":
            site_search = None

        if site_search and not isinstance(site_search, str):
            print(f"Warning: Invalid site_search '{site_search}'. Ignoring.")
            site_search = None

        print(f"[GoogleCustomSearchTool] Validated parameters -> Query: '{query}', Num Results: {num}, Site Search: '{site_search if site_search is not None else 'None'}'")

        service = build("customsearch", "v1", developerKey=api_key)

        try:
            search_params = {'q': query, 'cx': cse_id, 'num': num}
            if site_search and isinstance(site_search, str) and f"site:{site_search}" not in query:
                 search_params['q'] = f"{search_params['q']} site:{site_search}"
                 print(f"[GoogleCustomSearchTool] Added site restriction: {site_search}")

            print(f"[GoogleCustomSearchTool] Executing Google search with final query: '{search_params['q']}', num: {num}")
            result = service.cse().list(**search_params).execute()
            items = result.get('items', [])

            if not items:
                print(f"Info: No search results found for query: '{search_params['q']}'")
                return []

            formatted_results = [{'title': item.get('title', ''), 'link': item.get('link', ''), 'snippet': item.get('snippet', '')} for item in items]
            print(f"[GoogleCustomSearchTool] Search successful. Found {len(formatted_results)} results.")
            return formatted_results

        except HttpError as e:
            try:
                error_content = json.loads(e.content.decode('utf-8'))
                error_details = error_content.get('error', {}).get('message', 'No details provided.')
            except Exception:
                error_details = f"Could not parse error content. Raw reason: {e.resp.reason}"
            error_msg = f"Google API HTTP Error: {e.resp.status} {e.resp.reason}. Details: {error_details}"
            print(f"Error: {error_msg}")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected Error during Google search for query '{query}': {e}"
            print(f"Error: {error_msg}")
            return {"error": error_msg}


class WebContentScraperTool(BaseTool):
    name: str = "Web Content Scraper Tool"
    description: str = (
        "Fetches content from a given URL, extracts the main article text using newspaper3k, "
        "cleans it (converts to Markdown, removes excessive whitespace), and returns the cleaned text. "
        "Input MUST be a dictionary containing the key 'url' (a string representing the full URL). "
        "Returns a dictionary {'content': text} OR an error dictionary {'error': message}."
    )

    def _run(self, url: str) -> Dict[str, str]:
        print(f"\n[WebContentScraperTool] Attempting to run...")
        print(f"[WebContentScraperTool] Received argument -> url: {url}")

        if not url or not isinstance(url, str) or not url.startswith("http"):
            error_msg = f"Input Error: A valid 'url' parameter starting with 'http' is required. Received: '{url}'"
            print(f"Error: {error_msg}")
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
            print(f"[WebContentScraperTool] Fetching URL: {url}")
            response = requests.get(url, headers=headers, timeout=25, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()
            if 'html' not in content_type:
                error_msg = f"Skipping URL: Content-Type is '{content_type}', not HTML."
                print(f"Info: {error_msg} URL: {url}")
                return {"error": error_msg}

            article = Article(url)
            article.download(input_html=response.text)
            article.parse()
            content_text = article.text

            if not content_text or len(content_text) < 100:
                 print(f"Warning: newspaper3k extracted minimal/no content from {url}. Attempting fallback with BeautifulSoup.")
                 soup = BeautifulSoup(response.text, 'html.parser')
                 main_content = soup.find('article') or soup.find('main') or soup.find('div', role='main') or soup.find('body')
                 if main_content:
                     for tag in main_content(['script', 'style', 'nav', 'footer', 'aside', 'header', 'form', 'button', 'input']): tag.decompose()
                     content_text = markdownify(str(main_content), heading_style="ATX")
                 else: content_text = ""

                 if not content_text or len(content_text) < 100:
                    error_msg = f"Content Extraction Failed: newspaper3k and fallback method could not extract meaningful text content from {url}"
                    print(f"Error: {error_msg}")
                    return {"error": error_msg}

            lines = [line.strip() for line in content_text.splitlines()]
            cleaned_text = '\n'.join(line for line in lines if line)

            if not cleaned_text.strip():
                 error_msg = f"Content Extraction Failed: No text content found after cleaning for {url}."
                 print(f"Error: {error_msg}")
                 return {"error": error_msg}

            print(f"[WebContentScraperTool] Successfully scraped and cleaned content from {url}. Length: {len(cleaned_text)} characters.")
            max_chars = 15000
            if len(cleaned_text) > max_chars:
                print(f"Warning: Content from {url} truncated to {max_chars} characters.")
                cleaned_text = cleaned_text[:max_chars] + "\n... [Content Truncated]"

            return {"content": cleaned_text}

        except requests.exceptions.Timeout:
            error_msg = f"Scraping Error: Request timed out (>25s) for {url}."
            print(f"Error: {error_msg}")
            return {"error": error_msg}
        except requests.exceptions.TooManyRedirects:
             error_msg = f"Scraping Error: Too many redirects for URL: {url}."
             print(f"Error: {error_msg}")
             return {"error": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Scraping Error: Network issue fetching URL {url}. Reason: {e}"
            print(f"Error: {error_msg}")
            return {"error": error_msg}
        except ArticleException as e:
             error_msg = f"Scraping Error: newspaper3k failed processing {url}. Reason: {e}. Likely not a standard article format."
             print(f"Warning: {error_msg}")
             return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected Error while scraping {url}: {type(e).__name__} - {e}"
            import traceback
            print(f"Error: {error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg}

# --- Main Execution Logic ---
def main():
    parser = argparse.ArgumentParser(description="CrewAI Deep Research Agent")
    # Keep argparse definition for verbose as int for user input flexibility
    parser.add_argument(
        "-c", "--context", required=True, help="The research topic/context (e.g., 'AI applications in healthcare')."
    )
    parser.add_argument(
        "-q", "--num_queries", type=int, default=3, help="Number of diverse search queries to generate."
    )
    parser.add_argument(
        "-r", "--results_per_query", type=int, default=3, help="Number of search results to fetch per query (1-10)."
    )
    parser.add_argument(
        "--site", type=str, default="", help="Optional: Limit searches to a specific site (e.g., 'reddit.com', 'arxiv.org')."
    )
    parser.add_argument(
        "--model", type=str, default="gpt-4o-mini", help="Specify the OpenAI model name (e.g., gpt-4-turbo, gpt-4o, gpt-4o-mini)."
    )
    parser.add_argument(
        "--verbose", type=int, default=1, choices=[0, 1, 2], help="Verbosity level (0=minimal, 1=agent activity, 2=detailed tool/agent logs)."
    ) # User still inputs 0, 1, or 2
    args = parser.parse_args()

    if not 1 <= args.results_per_query <= 10:
        print(f"Warning: results_per_query ({args.results_per_query}) outside valid range [1, 10]. Clamping to 3.")
        args.results_per_query = 3

    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID")

    print("\n----- Configuration -----")
    print(f"Research Context: {args.context}")
    print(f"Search Queries to Generate: {args.num_queries}")
    print(f"Results per Query: {args.results_per_query}")
    print(f"Site Restriction: {args.site if args.site else 'None (Web-wide)'}")
    print(f"LLM Model: {args.model}")
    print(f"Verbosity Level (Input): {args.verbose}") # Show user input
    print(f"OPENAI_API_KEY configured: {bool(openai_key)}")
    print(f"GOOGLE_API_KEY configured: {bool(google_key)}")
    print(f"GOOGLE_CSE_ID configured: {bool(google_cse)}")
    print("--------------------------\n")

    if not all([openai_key, google_key, google_cse]):
        missing = [k for k, v in {"OpenAI Key": openai_key, "Google API Key": google_key, "Google CSE ID": google_cse}.items() if not v]
        print(f"CRITICAL ERROR: Missing required environment variables: {', '.join(missing)}. Please set them in your .env file or environment.")
        return

    try:
        llm = ChatOpenAI(model=args.model, temperature=0.5)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize LLM. Check OpenAI API key and model name ('{args.model}'). Error: {e}")
        return

    # Create tools inside the main function (fix indentation issue)
    search_tool = GoogleCustomSearchTool()
    scrape_tool = WebContentScraperTool()

    # --- Define Agents ---
    # Agent verbosity is often handled differently or less strictly,
    # keeping args.verbose > 0 should be fine here.
    search_planner = Agent(
        role='Search Strategy Planner',
        goal=f"""Generate a list of {args.num_queries} diverse and effective Google search queries
             to research the topic: '{args.context}'.
             Queries should cover different aspects like definition, applications, challenges, advancements, future trends.
             If a site restriction is provided ('{args.site}'), queries should ideally incorporate it using 'site:{args.site}' if relevant,
             but create general queries if the site restriction doesn't fit all aspects.
             Prioritize queries likely to find authoritative sources (news, research, .gov, .edu).""",
        backstory=(
            "You are a master research strategist. You excel at dissecting complex topics into focused, "
            "high-yield search queries. You understand search operators and how to target specific types of information. "
            "Your final output MUST be *only* a Python list of query strings, nothing else."
        ),
        llm=llm,
        verbose=(args.verbose > 0),  # Convert int level to boolean for agent
        allow_delegation=False,
    )

    researcher = Agent(
        role='Information Synthesizer and Research Analyst',
        goal=f"""Execute a detailed research plan using provided search queries to gather, analyze,
             and synthesize information on: '{args.context}'. Produce a comprehensive report.""",
        backstory=(
            "You are a highly skilled research analyst. You methodically execute search plans, critically evaluate sources, "
            "scrape web content, extract relevant insights, and synthesize findings into a coherent, well-structured report. "
            "You handle errors gracefully (e.g., skipping failed searches/scrapes) and focus relentlessly on the core research topic. "
            "You MUST use the 'Google Custom Search Tool' for searching and 'Web Content Scraper Tool' for getting content."
        ),
        llm=llm,
        tools=[search_tool, scrape_tool],
        verbose=(args.verbose > 0),  # Convert int level to boolean for agent
        allow_delegation=False,
    )

    # --- Define Tasks ---
    plan_search_task = Task(
        description=f"""Analyze the research context: '{args.context}'.
                    Generate exactly {args.num_queries} distinct Google search query strings.
                    These queries should aim to uncover key information about the topic, including:
                    - Core concepts/definitions
                    - Key applications/use cases
                    - Recent advancements/breakthroughs (e.g., within the last 1-2 years if applicable)
                    - Challenges/limitations/criticisms
                    - Future outlook/predictions
                    If a specific site '{args.site}' was requested, incorporate 'site:{args.site}' into the queries where it makes sense
                    (e.g., for academic research on .edu/.org sites, or discussions on reddit.com).
                    Return *only* a Python list of these {args.num_queries} query strings, ready for use.
                    Example: ["define {args.context}", "recent advancements {args.context}", "{args.context} challenges", "{args.context} future trends"]""",
        expected_output=f"A Python list exactly containing {args.num_queries} search query strings.",
        agent=search_planner,
    )

    execute_research_task = Task(
        description=f"""Execute the research plan based on the list of search queries provided by the Planner.
                    The overall research objective is to create a report on: '{args.context}'.
                    The site restriction requested (if any) is: '{args.site}'.

                    **Process:**
                    Initialize an empty list to store relevant findings.
                    For EACH `search_query` string in the list provided by the Planner:
                        1. Log the query being executed.
                        2. Prepare the input dictionary for the 'Google Custom Search Tool'. It MUST include the 'query' key with the current `search_query`, 'num_results' set to {args.results_per_query}, and 'site_search': '{args.site if args.site else ""}'. You MUST ALWAYS include the site_search parameter even if it's an empty string.
                        3. Call the 'Google Custom Search Tool' with the prepared dictionary.
                        4. **Handle Search Output:**
                           - If the tool returns an error dictionary `{{'error': ...}}`, log the query and the error, then **continue** to the next `search_query`.
                           - If the tool returns an empty list `[]`, log that no results were found for this query and **continue** to the next `search_query`.
                           - If the tool returns a list of result dictionaries: Proceed to scrape each result link.
                        5. For EACH `search_result` dictionary (with 'title', 'link', 'snippet') in the list from the search tool:
                           a. Log the link being scraped.
                           b. Prepare the input dictionary for the 'Web Content Scraper Tool'. It MUST include the 'url' key with the `search_result['link']`.
                           c. Call the 'Web Content Scraper Tool'.
                           d. **Handle Scraper Output:**
                              - If the tool returns an error dictionary `{{'error': ...}}`, log the URL and the error, then **continue** to the next `search_result`.
                              - If the tool returns `{{'content': text_content}}`:
                                  i. Analyze `text_content` to identify information *directly relevant* to '{args.context}'.
                                 ii. If relevant information is found, create a summary of it (a few key bullet points or sentences).
                                iii. Store this finding, including the summary, the source link (`search_result['link']`), and the title (`search_result['title']`). Add it to your list of relevant findings.

                    **Final Step: Synthesize Report**
                    After attempting all search queries and scraping:
                    - Review all the stored relevant findings.
                    - Synthesize them into a comprehensive, well-structured report. Organize the report logically (e.g., Introduction, Key Findings/Applications, Challenges, Future Outlook, Conclusion).
                    - Clearly cite the source link for each piece of information in the report.
                    - If NO relevant findings were collected across all searches, the final output must explicitly state that insufficient information was found.
                    """,
        expected_output=f"""A comprehensive, well-structured research report about '{args.context}'.
                        The report must synthesize findings from the scraped web pages, be organized logically
                        (e.g., Intro, Applications, Challenges, Future, Conclusion), and cite source links.
                        If no relevant information was found, the output must clearly state this fact.""",
        agent=researcher,
        context=[plan_search_task],
    )

    # --- Create and Run the Crew ---
    research_crew = Crew(
        agents=[search_planner, researcher],
        tasks=[plan_search_task, execute_research_task],
        process=Process.sequential,
        verbose=(args.verbose > 0),
    )

    print("\n--- Starting Research Crew ---")
    result = None
    try:
        result = research_crew.kickoff()
        
        print("\n--- Research Crew Finished ---")
        print("Final Result:")
        print("=============================")
        if isinstance(result, str): 
            print(result)
        else:
            # Fix for JSON serialization error
            try:
                # Try to access the content directly
                if hasattr(result, 'raw'):
                    print(result.raw)
                elif hasattr(result, 'last_task_output'):
                    print(result.last_task_output)
                else:
                    print(str(result))
            except Exception as e:
                print(f"Could not serialize result: {str(e)}")
                print("Result type:", type(result).__name__)
                print("Result representation:", repr(result))
        print("=============================")

    except Exception as e:
        print(f"\n--- An CRITICAL Error Occurred During Crew Execution ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        import traceback
        traceback.print_exc()
        print("-------------------------------------------------------")

    return result

if __name__ == "__main__":
    main() 