import os
import json
import requests
import argparse
from typing import List, Dict, Any, Union, Optional

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

# LangChain imports - crewAI uses LangChain under the hood
from langchain_openai import ChatOpenAI

# Load environment variables
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
DEFAULT_CONTEXT = "What are the latest advancements in AI for drug discovery discussed on Reddit?"
DEFAULT_NUM_SEARCH_TERMS = 2
DEFAULT_TOP_RESULTS_PER_TERM = 3
DEFAULT_SITE_SEARCH = "reddit.com"

# --- Define Custom Tools ---

# No changes needed inside the class definitions themselves for this specific error
class GoogleCustomSearchTool(BaseTool):
    name: str = "Google Custom Search Tool"
    description: str = (
        "Searches Google and returns results as a list of dictionaries, each containing 'title', 'link', and 'snippet', "
        "or an error message as {'error': message}. "
        "Input must be a dictionary containing 'query' (string) and optionally 'num_results' (int, default 3) "
        "and 'site_search' (string, e.g., 'reddit.com')."
    )
    
    def _run(self, tool_input=None, **kwargs) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """
        Executes the Google Custom Search.
        tool_input or kwargs must contain 'query' (string).
        Optionally can include 'num_results' (int, default 3) and 'site_search' (string).
        """
        # Check if API keys are set
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        
        print(f"[GoogleCustomSearchTool] API keys configured: GOOGLE_API_KEY={bool(api_key)}, GOOGLE_CSE_ID={bool(cse_id)}")
        
        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable is not set")
            return {"error": "GOOGLE_API_KEY environment variable is not set"}
            
        if not cse_id:
            print("Error: GOOGLE_CSE_ID environment variable is not set")
            return {"error": "GOOGLE_CSE_ID environment variable is not set"}
        
        # Handle different ways the input might be passed
        import json
        
        print("GoogleCustomSearchTool received kwargs:", kwargs)
        print("GoogleCustomSearchTool received tool_input:", tool_input)
        
        # Initialize parameters
        query = None
        num_results = 3
        site_search = None
        
        # Process tool_input if it's a string (likely JSON)
        if isinstance(tool_input, str):
            try:
                # Try to parse it as JSON
                parsed_input = json.loads(tool_input)
                print("Successfully parsed JSON from tool_input:", parsed_input)
                query = parsed_input.get("query")
                num_results = parsed_input.get("num_results", 3)
                site_search = parsed_input.get("site_search")
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed for tool_input: {e}")
                # If not JSON, assume it's the query itself
                query = tool_input
        
        # Process tool_input if it's a dictionary
        elif isinstance(tool_input, dict):
            print("tool_input is a dictionary")
            query = tool_input.get("query")
            num_results = tool_input.get("num_results", 3)
            site_search = tool_input.get("site_search")
        
        # Process kwargs if no query was found yet
        if not query:
            # Check if we have a single parameter that might be JSON
            if len(kwargs) == 1:
                param_name = next(iter(kwargs.keys()))
                param_value = next(iter(kwargs.values()))
                print(f"Single parameter from kwargs - Name: {param_name}, Value: {param_value}")
                
                # If it's a string that looks like JSON
                if isinstance(param_value, str) and param_value.strip().startswith('{') and param_value.strip().endswith('}'):
                    try:
                        # Try to parse it as JSON
                        parsed_input = json.loads(param_value)
                        print("Successfully parsed JSON from kwargs:", parsed_input)
                        query = parsed_input.get("query")
                        num_results = parsed_input.get("num_results", 3)
                        site_search = parsed_input.get("site_search")
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing failed for kwargs: {e}")
            
            # If we still don't have a query, try to get it from kwargs directly
            if not query:
                query = kwargs.get("query")
                num_results = kwargs.get("num_results", 3)
                site_search = kwargs.get("site_search")
        
        print(f"Final search parameters - Query: {query}, Num Results: {num_results}, Site Search: {site_search}")
        
        # Check if we have the required query
        if not query:
            print("Error: Query is required but not found in input")
            return {"error": "Query is required for Google Search."}

        service = build("customsearch", "v1", developerKey=api_key)
        
        try:
            # Prepare search parameters
            search_params = {
                'q': query,
                'cx': cse_id,
                'num': min(num_results, 10)  # API limits to 10 results max per call
            }
            
            # Add site search if specified
            if site_search:
                search_params['q'] += f" site:{site_search}"
            
            print(f"Executing Google search with params: {search_params}")
            
            # Execute the search
            result = service.cse().list(**search_params).execute()
            items = result.get('items', [])
            
            if not items:
                print(f"No search results found for query: {query}")
                return {"error": f"No search results found for query: {query}"}
            
            formatted_results = []
            for item in items:
                formatted_results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            print(f"Search successful. Found {len(formatted_results)} results.")
            return formatted_results
            
        except HttpError as e:
            error_msg = f"Google API HTTP error: {e}"
            print(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error during Google search: {e}"
            print(error_msg)
            return {"error": error_msg}

class WebContentScraperTool(BaseTool):
    name: str = "Web Content Scraper Tool"
    description: str = (
        "Fetches content from a given URL, extracts the main article text, "
        "cleans it (converts to Markdown, removes boilerplate), and returns the cleaned text "
        "in a dictionary {'content': text} or an error {'error': message}. "
        "Input must be a dictionary containing 'url'."
    )

    def _run(self, tool_input=None, **kwargs) -> Dict[str, str]:
        """
        Fetches, cleans, and returns web content.
        tool_input or kwargs must contain 'url' (string).
        """
        # Handle different ways the input might be passed
        import json
        
        print("WebContentScraperTool received kwargs:", kwargs)
        print("WebContentScraperTool received tool_input:", tool_input)
        
        # Initialize parameters
        url = None
        
        # Process tool_input if it's a string (likely JSON)
        if isinstance(tool_input, str):
            try:
                # Try to parse it as JSON
                parsed_input = json.loads(tool_input)
                print("Successfully parsed JSON from tool_input:", parsed_input)
                url = parsed_input.get("url")
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed for tool_input: {e}")
                # If not JSON, assume it's the URL itself
                url = tool_input if tool_input.startswith("http") else None
        
        # Process tool_input if it's a dictionary
        elif isinstance(tool_input, dict):
            print("tool_input is a dictionary")
            url = tool_input.get("url")
        
        # Process kwargs if no URL was found yet
        if not url:
            # Check if we have a single parameter that might be JSON
            if len(kwargs) == 1:
                param_name = next(iter(kwargs.keys()))
                param_value = next(iter(kwargs.values()))
                print(f"Single parameter from kwargs - Name: {param_name}, Value: {param_value}")
                
                # If it's a string that looks like JSON
                if isinstance(param_value, str):
                    if param_value.strip().startswith('{') and param_value.strip().endswith('}'):
                        try:
                            # Try to parse it as JSON
                            parsed_input = json.loads(param_value)
                            print("Successfully parsed JSON from kwargs:", parsed_input)
                            url = parsed_input.get("url")
                        except json.JSONDecodeError as e:
                            print(f"JSON parsing failed for kwargs: {e}")
            
            # If we still don't have a URL, try to get it from kwargs directly
            if not url:
                url = kwargs.get("url")
        
        print(f"Final URL: {url}")
        
        # Check if we have the required URL
        if not url:
            print("Error: URL is required but not found in input")
            return {"error": "URL is required for scraping."}

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            article = Article(url)
            article.download(input_html=response.text)
            article.parse()

            if not article.text:
                 print(f"Warning: newspaper3k failed for {url}. Falling back to basic HTML body extraction.")
                 soup = BeautifulSoup(response.text, 'html.parser')
                 body = soup.find('body')
                 content_html = str(body) if body else response.text
                 cleaned_text = markdownify(content_html, heading_style="ATX")
            else:
                 cleaned_text = article.text

            cleaned_text = '\n'.join([line for line in cleaned_text.splitlines() if line.strip()])

            if not cleaned_text.strip():
                 print(f"No substantial content found at {url} after cleaning.")
                 return {"error": f"No substantial content found at {url} after cleaning."}

            print(f"Successfully scraped content from {url}: {len(cleaned_text)} characters")
            return {"content": cleaned_text}

        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed for {url}: {e}")
            return {"error": f"HTTP request failed for {url}: {e}"}
        except ArticleException as e:
             print(f"Newspaper article processing failed for {url}: {e}")
             return {"error": f"Newspaper article processing failed for {url}: {e}. It might be a non-article page or inaccessible."}
        except Exception as e:
            print(f"Unexpected error while scraping {url}: {e}")
            return {"error": f"An unexpected error occurred scraping {url}: {e}"}

# --- Instantiate Tools ---
search_tool = GoogleCustomSearchTool()
scrape_tool = WebContentScraperTool()

# --- Define Agents ---
# (No changes needed in Agent/Task definitions for this error)
search_planner = Agent(
    role='Search Query Planner',
    goal='Generate a list of {num_search_terms} diverse and effective Google search queries based on the provided research context: "{context}".',
    backstory=(
        "You are an expert researcher skilled at formulating targeted search strategies. "
        "You understand how to break down a complex topic into specific, searchable questions "
        "and keywords to maximize the chances of finding relevant information."
        "You need to provide *only* the list of search query strings."
    ),
    verbose=True,
    allow_delegation=False,
    llm=ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.5)
)

researcher = Agent(
    role='Information Researcher and Analyzer',
    goal=(
        "For each provided search query, use the Google Search Tool to find the top {top_results} results (specifically on {site_search} if specified, otherwise web-wide). "
        "Handle potential errors from the search tool (e.g., if it returns an error dictionary). "
        "For each valid result link found: "
        "1. Use the Web Scraper Tool to fetch and clean the content. Handle potential errors gracefully (e.g., skip link if scraping returns an error dictionary). "
        "2. If content is retrieved successfully (tool returns {{'content': ...}}), summarize the key information from the cleaned content concisely. "
        "3. Critically evaluate if the summarized content is directly relevant and useful to the original research context: '{context}'. "
        "Compile a final list containing only the relevant findings. Each finding should be a dictionary including 'title', 'link', 'snippet' (from search result), and 'summary' (your summary)."
    ),
    backstory=(
        "You are a meticulous researcher and analyst. You systematically execute search plans, "
        "retrieve information from the web, and critically evaluate its relevance and value. "
        "You are adept at summarizing complex information accurately and filtering out noise. "
        "You pay close attention to the original research goal to ensure findings are on-topic."
        "You MUST use the provided tools for searching and scraping and handle their potential error outputs."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[search_tool, scrape_tool],
    llm=ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.5)
)

# --- Define Tasks ---
plan_search_task = Task(
    description=(
        "Analyze the research context: '{context}'. "
        "Generate exactly {num_search_terms} distinct Google search query strings that are likely to yield relevant results. "
        "Focus on different facets or keywords within the context. "
        "Return *only* a Python list of these query strings."
        "Example Output: ['query 1', 'query 2']"
    ),
    expected_output=(
        "A Python list containing exactly {num_search_terms} search query strings."
    ),
    agent=search_planner,
)

execute_research_task = Task(
    description=(
        "Execute the research plan based on the search queries provided by the Search Query Planner. "
        "The original research context is: '{context}'. "
        "For each query: "
        "1. Use the Google Custom Search Tool (input like {{'query': '...', 'num_results': {top_results}, 'site_search': '{site_search}'}}) to find search results. Check if the tool returned a list of results or an error dictionary. Log errors and continue if possible. "
        "2. For each valid search result link: Use the Web Content Scraper Tool (input like {{'url': '...'}}). Check if the tool returned a dictionary with 'content' or one with 'error'. Log scraping errors and skip the link if needed. "
        "3. If content was successfully retrieved, summarize the key information relevant to the context. "
        "4. Determine if the summary is directly relevant and useful for answering the research context. "
        "Compile a final list of dictionaries. Each dictionary should represent a *relevant* finding and contain the keys: 'title', 'link', 'snippet', 'summary'. "
        "If no relevant results are found for a query or overall, return an empty list or a message indicating so."
    ),
    expected_output=(
        "A Python list of dictionaries, where each dictionary represents a relevant research finding "
        "and contains the keys: 'title' (string), 'link' (string), 'snippet' (string), 'summary' (string)."
        "Example: [{'title': 'AI Drug Discovery on Reddit', 'link': '...', 'snippet': '...', 'summary': '...'}, ...]"
    ),
    agent=researcher,
    context=[plan_search_task],
)

# --- Create and Run the Crew ---
def run_crew(context, num_terms, top_results, site_search):
    # Update agent goals and task descriptions with dynamic values
    search_planner.goal = search_planner.goal.format(num_search_terms=num_terms, context=context)
    researcher.goal = researcher.goal.format(
        top_results=top_results,
        site_search=site_search if site_search else "the web",
        context=context
    )

    plan_search_task.description = plan_search_task.description.format(context=context, num_search_terms=num_terms)
    plan_search_task.expected_output = plan_search_task.expected_output.format(num_search_terms=num_terms)

    site_search_str = site_search if site_search else ""

    execute_research_task.description = execute_research_task.description.format(
        context=context,
        top_results=top_results,
        site_search=site_search_str
    )

    # Define the crew
    research_crew = Crew(
        agents=[search_planner, researcher],
        tasks=[plan_search_task, execute_research_task],
        process=Process.sequential,
        verbose=True
    )

    # Kick off the crew
    print("--- Starting Research Crew ---")
    print(f"Context: {context}")
    print(f"Search Terms to Generate: {num_terms}")
    print(f"Results per Term: {top_results}")
    print(f"Site Search: {site_search if site_search else 'Web-wide'}")
    print("-----------------------------")

    result = research_crew.kickoff()

    print("\n--- Research Crew Finished ---")
    print("Final Result:")
    print(result)
    print("-----------------------------")
    return result

def main():
    """Parse command-line arguments and run the research crew."""
    parser = argparse.ArgumentParser(description="Research Agent using CrewAI")
    parser.add_argument(
        "-c", "--context", required=True, help="Context for the research topic."
    )
    parser.add_argument(
        "-n", "--num_iterations", type=int, default=1, help="Number of research iterations."
    )
    parser.add_argument(
        "-r", "--num_results", type=int, default=3, help="Maximum number of results per agent task."
    )
    parser.add_argument(
        "--verbosity", type=int, default=0, choices=[0, 1, 2], help="Verbosity level (0=minimal, 1=detailed, 2=debug)."
    )
    parser.add_argument(
        "--site", type=str, default="", help="Limit searches to a specific site (e.g., 'reddit.com')."
    )
    args = parser.parse_args()

    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID")
    
    print("\n----- Environment Configuration -----")
    print(f"OPENAI_API_KEY configured: {bool(openai_key)}")
    print(f"GOOGLE_API_KEY configured: {bool(google_key)}")
    print(f"GOOGLE_CSE_ID configured: {bool(google_cse)}")
    print("------------------------------------\n")
    
    if not openai_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return
        
    if not google_key:
        print("Error: GOOGLE_API_KEY environment variable is not set")
        return
        
    if not google_cse:
        print("Error: GOOGLE_CSE_ID environment variable is not set")
        return

    # Configure tools
    google_search_tool = GoogleCustomSearchTool()
    web_scraper_tool = WebContentScraperTool()

    # Create agents
    search_query_planner = Agent(
        role="Search Query Planner",
        goal=f"Create optimal search queries for researching: {args.context}",
        backstory="""You are an expert at crafting search queries that yield high-quality results.
        You understand how to formulate queries that are specific, use advanced search operators,
        and target the most relevant and authoritative sources.""",
        verbose=args.verbosity > 0,
        allow_delegation=False,
        # Using gpt-4-turbo for better search query formulation
        llm=ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.5)
    )

    researcher = Agent(
        role="Information Researcher and Analyzer",
        goal=f"Find, analyze, and summarize information about: {args.context}",
        backstory="""You are a skilled researcher with expertise in finding and analyzing information.
        You know how to evaluate sources for credibility, extract key insights, and synthesize
        information into coherent summaries. You're skeptical, thorough, and have a knack for
        identifying valuable information hidden in large documents.""",
        verbose=args.verbosity > 0,
        allow_delegation=True,
        tools=[google_search_tool, web_scraper_tool],
        # Using gpt-4-turbo for deeper analysis capabilities
        llm=ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.5)
    )

    # Create research tasks
    tasks = [
        Task(
            description=f"""Generate a list of {args.num_results} highly effective Google search queries 
            for researching: "{args.context}". 
            Format your response as a Python list of strings.
            Each query should be designed to find specific, high-quality information.""",
            expected_output=f"A list of {args.num_results} optimized search queries for researching {args.context}.",
            agent=search_query_planner
        ),
        Task(
            description=f"""Research the topic: "{args.context}" using the provided search queries.
            For each query:
            1. Use the Google Custom Search Tool to find relevant results
            {f'from {args.site}' if args.site else ''}
            2. Use the Web Content Scraper Tool to extract content from the most promising links
            3. Analyze the information and identify key insights
            
            Provide a comprehensive summary of your findings, including:
            - Key trends or developments
            - Major challenges or opportunities
            - Expert opinions or consensus
            - Areas of disagreement or controversy
            - Gaps in current knowledge or research
            
            Your final answer should be in-depth, well-structured, and insightful.""",
            expected_output=f"A comprehensive analysis of {args.context} based on the research.",
            agent=researcher
        )
    ]

    # Create and run crew
    print(f"\nStarting research crew with context: {args.context}, iterations: {args.num_iterations}, results per task: {args.num_results}\n")
    crew = Crew(
        agents=[search_query_planner, researcher],
        tasks=tasks,
        verbose=True,  # Always set to True for basic output
        process=Process.sequential
    )

    result = crew.kickoff()
    
    print("\n----- Final Research Result -----")
    print(result)
    print("--------------------------------\n")
    
    return result

if __name__ == "__main__":
    # Create a simple test script to check environment variables
    test_api_keys = """
import os
print("API Key Check:")
print(f"GOOGLE_API_KEY found: {'Yes' if os.getenv('GOOGLE_API_KEY') else 'No'}")
print(f"GOOGLE_CSE_ID found: {'Yes' if os.getenv('GOOGLE_CSE_ID') else 'No'}")
print(f"OPENAI_API_KEY found: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
"""
    # Write the script to disk
    with open("check_api_keys.py", "w") as f:
        f.write(test_api_keys)
    
    # Print message about the test script
    print("Created check_api_keys.py - you can run this to verify your API keys.")
    print("Usage: python check_api_keys.py")
    
    # Continue with main execution
    main()