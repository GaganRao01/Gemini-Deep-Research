# 🚀 Gemini Deep Research Platform

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/Google_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google API">
</div>

<div align="center">
  <p><i>An AI-powered research platform that performs comprehensive in-depth research with publication-quality reports using Google's Gemini</i></p>
</div>

---

## 📖 Overview

Gemini Deep Research is a powerful, autonomous research system that leverages Google's Gemini LLM to generate comprehensive, detailed reports on any topic. The system performs extensive web research, producing thoroughly researched reports with proper citations, in-depth analysis, and academic rigor.

## 🔎 Project Files

| File | Purpose |
|------|---------|
| **`gemini_research.py`** | **Core implementation using Google's Gemini API for research** |
| `check_gemini_key.py` | Tests if your Google Gemini API key is valid |
| `check_api_keys.py` | Checks if your API keys are present in the environment |
| `check_creds.py` | Tests if your API credentials work by performing a test Google search |
| `google_search_schema.py` | Defines the data structure for Google search parameters |
| `.env.example` | Template for creating your `.env` file with the required API keys |
| `research_report_Quantum_computing_applications.md` | Sample generated report demonstrating the platform's capabilities |

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
| 1 | Basic | Concise but informative overview | 5-7 pages | 3 | 2 |
| 2 | Detailed | Thorough analysis with significant depth | 10-15 pages | 5 | 3 |
| 3 | Comprehensive | Exhaustive, publication-quality report | 20-30 pages | 8 | 4 |

## 🛠️ Usage

### Recommended: Using the Simplified Gemini Implementation

```bash
# Basic research
python gemini_research.py -c "Future of renewable energy" --depth 1

# Detailed research
python gemini_research.py -c "Impact of artificial intelligence on education" --depth 2

# Comprehensive research
python gemini_research.py -c "Quantum computing applications in cryptography" --depth 3
```

### Command Line Arguments for gemini_research.py

| Argument | Description | Default |
|----------|-------------|---------|
| `-c, --context` | The research topic (required) | N/A |
| `--depth` | Research depth level (1=basic, 2=detailed, 3=comprehensive) | 1 |
| `-q, --queries` | Number of search queries to generate (optional) | Based on depth |
| `-r, --results` | Number of results per query (optional) | Based on depth |
| `-s, --site` | Limit searches to a specific site (e.g., 'nature.com') | None |
| `--verbose` | Verbosity level (0=minimal, 1=regular, 2=debug) | 1 |

## 🔍 How It Works

1. **Query Generation**: The system generates diverse search queries covering different aspects of your research topic
2. **Web Search**: For each query, it searches the web using Google Custom Search API
3. **Content Extraction**: For each search result, it scrapes the content and extracts relevant information
4. **Report Synthesis**: All collected information is synthesized into a comprehensive report
5. **Final Output**: The report is displayed and saved as a markdown file

### How gemini_research.py Works

The `gemini_research.py` script processes research in several key steps:

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

> **Note**: Due to the current chunking and splitting approach used in report generation, some topics may be repeated across sections. We're aware of this limitation and plan to improve it in future updates.

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

This repository includes a sample report on "Quantum Computing Applications in Cryptography" generated at depth level 3. This approximately 20,000-word report demonstrates the capabilities of the platform and follows the standardized structure:

- Executive Summary and Introduction
- Comprehensive sections on quantum computing fundamentals
- Detailed analysis of quantum threats to classical cryptography
- In-depth coverage of post-quantum cryptography standardization
- Exploration of quantum key distribution technologies
- Dedicated sections on implementation challenges and limitations
- Future research directions
- Conclusion synthesizing the research
- Properly formatted references

You can view this report in the repository: [Sample Report: Quantum Computing Applications in Cryptography](research_report_Quantum_computing_applications.md)

## 📧 Getting Started

### Prerequisites

- Python 3.8+
- Google API key (for Gemini LLM)
- Google Search API key
- Google Custom Search Engine ID

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

5. Verify your setup:
   ```bash
   python check_api_keys.py
   python check_creds.py
   ```

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgements

- [Google Gemini](https://ai.google.dev/gemini) - Google's advanced language models
- [Google Custom Search](https://developers.google.com/custom-search) - Google's search API
- [Newspaper3k](https://github.com/codelucas/newspaper) - Article scraping & curation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping library
