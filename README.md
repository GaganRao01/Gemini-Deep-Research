# 🚀 Research Crew AI

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Google_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google API">
  <img src="https://img.shields.io/badge/CrewAI-FF4545?style=for-the-badge&logo=robot&logoColor=white" alt="CrewAI">
</div>

<div align="center">
  <p><i>An AI-powered research assistant that autonomously performs in-depth web research on any topic</i></p>
</div>

---

## 📖 Overview

Research Crew AI is a powerful, autonomous research system built with CrewAI that leverages multiple specialized AI agents to perform comprehensive web research on any topic of interest. The system orchestrates a team of AI agents, each with specific roles and responsibilities, to gather, process, and synthesize information from across the web into coherent, well-structured research reports.

<div align="center">
  <img src="https://via.placeholder.com/800x400.png?text=Research+Crew+AI+Flow" alt="Research Crew Flow" width="80%">
</div>

## 📁 Project Files

This project consists of several files, each with a specific purpose:

| File | Purpose |
|------|---------|
| `research_crew.py` | The **main script** that performs AI-powered research. Run this to create comprehensive reports on any topic. |
| `google_search_schema.py` | Defines the data structure for Google search parameters. Used internally by the main script to validate search inputs. |
| `check_creds.py` | A comprehensive diagnostic tool that tests if your API credentials actually work by performing a test Google search. |
| `check_api_keys.py` | A simple utility that checks if your API keys are present in the environment without testing them. |
| `.env.example` | Template for creating your `.env` file with the required API keys. |

## ✨ Features

- 🧠 **Multi-Agent Collaboration** - Specialized AI agents work together as a research team
- 🔍 **Intelligent Search Strategy** - Generates diverse and effective search queries to maximize information discovery
- 📊 **Comprehensive Results** - Produces well-structured reports with citations and source links
- 🌐 **Web Content Analysis** - Scrapes and analyzes content from various websites
- 🔄 **Resilient Processing** - Gracefully handles errors and continues research despite occasional failures
- 🎯 **Site-Specific Research** - Option to limit searches to specific websites
- 📈 **Customizable Parameters** - Adjust search depth, result count, and verbosity

## 🤖 The AI Research Crew

The system employs two specialized agents that work together sequentially:

### 1. Search Strategy Planner

This agent specializes in dissecting complex topics into effective search queries. It analyzes the research objective and generates a set of diverse queries that cover different aspects of the topic:

- Core concepts and definitions
- Applications and use cases
- Recent advancements and breakthroughs
- Challenges and limitations
- Future trends and predictions

### 2. Information Synthesizer and Research Analyst

This agent executes the search strategy, processes search results, and creates the final research report:

- Executes Google searches using the queries provided by the Search Strategy Planner
- Scrapes and analyzes content from search results
- Extracts relevant information from each source
- Combines findings into a comprehensive, well-organized report
- Properly cites sources throughout the document

## 🛠️ Tools

The system employs two custom tools to interact with the web:

### Google Custom Search Tool

- Interfaces with Google's Custom Search Engine API
- Retrieves search results for specified queries
- Handles site-specific searches
- Returns structured results with titles, links, and snippets

### Web Content Scraper Tool

- Fetches content from URLs identified in search results
- Extracts main article text using newspaper3k
- Cleans and formats content for analysis
- Handles various error cases gracefully (network issues, timeouts, etc.)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Google API key
- Google Custom Search Engine ID

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GaganRao01/Research-Crew-AI-project.git
   cd Research-Crew-AI-project
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install crewai google-api-python-client newspaper3k langchain-openai python-dotenv beautifulsoup4 markdownify
   ```

4. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Running the Research Tool

#### Setup Verification (Recommended First Steps)

1. Verify that your API keys are set in the environment:
   ```bash
   python check_api_keys.py
   ```

2. Test that your credentials work properly:
   ```bash
   python check_creds.py
   ```

#### Running Research

Basic usage:
```bash
python research_crew.py -c "Your research topic" -q 3 -r 3
```

Example with additional options:
```bash
python research_crew.py -c "AI applications in healthcare" -q 5 -r 5 --site "pubmed.gov" --model "gpt-4o" --verbose 2
```

## 📋 Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-c, --context` | The research topic (required) | N/A |
| `-q, --num_queries` | Number of diverse search queries to generate | 3 |
| `-r, --results_per_query` | Number of search results to fetch per query (1-10) | 3 |
| `--site` | Limit searches to a specific site (e.g., 'reddit.com') | None |
| `--model` | Specify the OpenAI model to use | gpt-4o-mini |
| `--verbose` | Verbosity level (0=minimal, 1=agent activity, 2=detailed logs) | 1 |

## 🔎 Typical Research Workflow

1. **Setup**: Configure your API keys in the `.env` file
2. **Verification**: Run `check_api_keys.py` and `check_creds.py` to ensure everything is configured properly
3. **Research**: Run `research_crew.py` with your desired topic and parameters
4. **Review**: Examine the comprehensive research report generated by the AI agents

## 🔧 Troubleshooting

If you encounter issues:

1. Verify your API credentials:
   ```bash
   python check_creds.py
   ```

2. Ensure you have the correct environment variables set in your `.env` file:
   ```bash
   python check_api_keys.py
   ```

3. Check that all required packages are installed with the correct versions:
   ```bash
   pip install -r requirements.txt
   ```

4. Look for detailed error messages in the console output.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgements

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Framework for orchestrating role-playing autonomous AI agents
- [LangChain](https://github.com/langchain-ai/langchain) - Building applications with LLMs through composability
- [Newspaper3k](https://github.com/codelucas/newspaper) - Article scraping & curation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping library