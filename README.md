# Research Crew - AI Research Tool

This project uses CrewAI to set up a research team of AI agents that can perform web research on topics of interest.

## Issues Identified and Fixed

1. **Import Error**: `BaseTool` was being imported from an incorrect path. 
   - Fixed by updating import from `crewai.tools` instead of `crewai_tools.tools.base_tool`.

2. **Parameter Format Issue**: The `Crew` class parameter `verbose` was set to `2` instead of `True`.
   - Fixed by changing the parameter to a boolean type.

3. **Tool Input Handling**: The Google Custom Search and Web Scraper tools had issues parsing input.
   - Fixed by enhancing input handling to accept different formats including JSON strings and dictionaries.
   - Added better error handling and debugging output.

4. **API Credentials**: The script was not properly checking for environment variables.
   - Added explicit checks for required API keys.
   - Improved error messages to guide the user on setting up these credentials.

5. **LangChain Integration**: Updated OpenAI import to use `langchain_openai` instead of the direct OpenAI package.

## Setup Instructions

1. Copy the `.env.example` file to `.env` and fill in your API keys:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your:
   - OpenAI API key
   - Google API key
   - Google Custom Search Engine ID

3. Install the required packages:
   ```
   pip install crewai google-api-python-client newspaper3k langchain-openai python-dotenv
   ```

4. Run the example research:
   ```
   python research_crew.py -c "Your research topic" -n 1 -r 3
   ```

## Command Line Arguments

- `-c, --context`: The research topic (required)
- `-n, --num_iterations`: Number of research iterations (default: 1)
- `-r, --num_results`: Maximum results per agent task (default: 3)
- `--verbosity`: Set verbosity level (0=minimal, 1=detailed, 2=debug)
- `--site`: Limit searches to a specific site (e.g., 'reddit.com')

## Troubleshooting

If you encounter issues with the Google Custom Search Tool or environment variables:

1. Run the diagnostic script to check your credentials:
   ```
   python check_creds.py
   ```

2. Ensure the `.env` file is properly formatted and contains valid API keys.

3. Check that all required packages are installed.

4. Look for detailed error messages in the console output.

## Tools Used

- **Google Custom Search Tool**: Searches Google and returns results.
- **Web Content Scraper Tool**: Fetches and cleans content from URLs.

## Agents

- **Search Query Planner**: Generates optimal search queries for research.
- **Information Researcher and Analyzer**: Finds, analyzes, and summarizes information. 