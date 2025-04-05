# 🚀 Gemini Deep Research Platform

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/Google_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google API">
</div>

<div align="center">
  <p><i>An AI-powered research platform that generates comprehensive reports using Google's Gemini</i></p>
</div>

---

## 📖 Overview

Gemini Deep Research is a powerful, autonomous research system that leverages Google's Gemini LLM to generate comprehensive, detailed reports on any topic. The system performs extensive web research, producing thoroughly researched reports with proper citations, in-depth analysis, and academic rigor.

## 🔎 Project Files

| File | Purpose |
|------|---------|
| **`gemini_research.py`** | **Core implementation using Google's Gemini API for research** |
| `google_search_schema.py` | Defines the data structure for Google search parameters |
| `.env.example` | Template for creating your `.env` file with the required API keys |
| `requirements.txt` | List of Python dependencies |
| `CODE_DOCUMENTATION.md` | Detailed technical documentation for the codebase |
| `CONTRIBUTING.md` | Guidelines for contributing to the project |
| `research_report_*.md` | Sample generated reports demonstrating the platform's capabilities |

## ✨ Features

- 🧠 **Google Gemini Integration** - Uses Google's powerful Gemini 1.5 Pro LLM
- 📊 **Configurable Research Depth** - Choose from 3 depth levels (basic, detailed, comprehensive)
- 📈 **Customizable Search Scope** - Configure search queries and results per your needs
- 📚 **Publication-Quality Reports** - Generate reports with proper academic structure
- 🔗 **Proper Citations** - Enhanced in-text citations and formal bibliography
- 📝 **Multiple Perspectives** - Present diverse viewpoints on the research topic
- 💰 **Cost-Effective** - Uses Google Gemini models which may be more affordable than OpenAI alternatives
- 🔄 **Sectional Report Generation** - Generates comprehensive reports by breaking down complex topics into manageable sections
- 📅 **Up-to-Date Research** - Incorporates recency filters to ensure latest information is included
- 📑 **Standardized Report Structure** - Ensures logical flow with consistent section organization (challenges, future directions, references)
- 🎯 **Focused Content Sections** - Dedicated sections for challenges, limitations, and future directions
- 📊 **Consolidated References** - All citations organized in a single, properly formatted reference section

## 🚀 Research Depth Levels

| Level | Name | Description | Equivalent Length | Default Queries | Default Results per Query |
|-------|------|-------------|-------------------|-----------------|---------------------------|
| 1 | Basic | Brief overview (~3000-5000 words) | 5-7 pages | 3 | 2 |
| 2 | Detailed | Standard depth (~10,000-15,000 words) | 10-15 pages | 5 | 3 |
| 3 | Comprehensive | Comprehensive deep dive (~25,000-30,000 words) | 20-30 pages | 8 | 4 |

## 🛠️ Usage

```bash
# Basic research
python gemini_research.py "Future of renewable energy" --depth 1

# Detailed research
python gemini_research.py "Impact of artificial intelligence on education" --depth 2

# Comprehensive research
python gemini_research.py "Quantum computing applications in cryptography" --depth 3
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `topic` | The research topic (required) | N/A |
| `--depth` | Research depth level (1=basic, 2=detailed, 3=comprehensive) | 1 |
| `--queries` | Number of search queries to generate (optional) | Based on depth |
| `--results` | Number of results per query (optional) | Based on depth |
| `--site` | Limit searches to a specific site (e.g., 'nature.com') | None |
| `--verbose` | Verbosity level (0=minimal, 1=regular, 2=debug) | 1 |

## 🔍 How It Works

The script processes research in several key steps:

1. **Search Query Generation**: Uses Google Gemini AI to create tailored search queries that cover different aspects of your research topic
2. **Web Research**: Performs Google searches with the generated queries and collects results
3. **Content Scraping**: Extracts relevant content from web pages using newspaper3k and BeautifulSoup
4. **Date Extraction**: Analyzes content to identify and prioritize the most recent information
5. **Sectional Report Creation**: Organizes research into a standardized structure:
   - Executive Summary and Introduction
   - Main Content Sections (tailored to the topic)
   - Dedicated Challenges and Limitations section
   - Future Directions section
   - Conclusion
   - Consolidated References section
6. **Formatting Standardization**: Ensures consistent heading styles, section numbering, and citation format
7. **Output Generation**: Produces a comprehensive markdown report with proper academic structure

The sectional approach ensures reports maintain a logical flow and professional structure regardless of topic complexity or research depth.

## 📋 Example Output

The research tool generates a comprehensive, well-structured report on the specified topic. The report includes:

- Executive summary
- Introduction to the topic
- Multiple sections exploring different aspects of the topic
- Analysis of key findings
- Challenges and limitations
- Future directions and research opportunities  
- Conclusion
- Consolidated references

### Sample Report Included

This repository includes sample reports generated at different depth levels. These reports demonstrate the capabilities of the platform and follow the standardized structure. You can view these reports in the repository to see examples of the platform's output.

## 📧 Getting Started

### Prerequisites

- Python 3.9+
- Google API key (for Gemini LLM)
- Google Search API key
- Google Custom Search Engine ID

### Setting Up Google Custom Search Engine and API

1. **Create a Programmable Search Engine**:
   - Go to [Google Programmable Search Engine Control Panel](https://programmablesearchengine.google.com/controlpanel/all)
   - Click "Add" to create a new search engine
   - Enter the sites you want to search (or select "Search the entire web" for comprehensive research)
   - Name your search engine and click "Create"

2. **Get Your Search Engine ID**:
   - In the control panel, click on your newly created search engine
   - Click "Setup" in the left sidebar
   - Find your "Search engine ID" (This will be your `GOOGLE_CSE_ID`)

3. **Create a Google Cloud Project for API Access**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Navigate to "APIs & Services" > "Library"
   - Search for "Custom Search API" and enable it
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key (This will be your `GOOGLE_SEARCH_API_KEY`)

4. **Set Up Gemini API Key**:
   - Visit the [Google AI Studio](https://ai.google.dev/)
   - Create or sign in to your account
   - Go to "API keys" in the left sidebar
   - Create a new API key or use an existing one (This will be your `GOOGLE_API_KEY`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GaganRao01/Gemini-Deep-Research.git
   cd Gemini-Deep-Research
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables in `.env` file:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
   GOOGLE_CSE_ID=your_custom_search_engine_id_here
   ```

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgements

- [Google Gemini](https://ai.google.dev/gemini) - Google's advanced language models
- [Google Custom Search](https://developers.google.com/custom-search) - Google's search API
- [Newspaper3k](https://github.com/codelucas/newspaper) - Article scraping & curation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping library
