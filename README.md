<h1 align="center">🚀 Gemini Deep Research Platform</h1>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/Google_API-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google API">
</div>

<div align="center">
  <p><i>An AI-powered research platform that generates comprehensive reports using Google's Gemini</i></p>
</div>

---

> ⚠️ **Disclaimer**  
> This is a personal project where I attempted to replicate Google's Gemini Deep Research workflow. While not a perfect reproduction and still a work in progress, it was a great hands-on learning experience exploring Gemini APIs, web scraping, and structured AI report generation. Contributions, suggestions, and improvements are always welcome!

---

## 📖 Overview

**Gemini Deep Research** is a powerful, autonomous research system that leverages Google's Gemini LLM to generate comprehensive, detailed reports on any topic. It performs deep web research and produces well-cited, structured, and academically rigorous reports.

---

## 🔎 Project Files

| File | Purpose |
|------|---------|
| **`gemini_research.py`** | Core implementation using Google's Gemini API for research |
| `google_search_schema.py` | Defines the data structure for Google search parameters |
| `.env.example` | Template for creating your `.env` file with API keys |
| `requirements.txt` | List of Python dependencies |
| `CODE_DOCUMENTATION.md` | Technical documentation for the codebase |
| `CONTRIBUTING.md` | Contribution guidelines |
| `research_report_Quantum_computing_applications.md` | Sample generated report |

---

## ✨ Features

- 🧠 **Google Gemini Integration** – Uses Gemini 1.5 Pro for high-quality reasoning and text generation  
- 📊 **Configurable Research Depth** – Choose from 3 levels: basic, detailed, or comprehensive  
- 📈 **Customizable Search Scope** – Tailor search queries and scope to your needs  
- 📚 **Publication-Quality Reports** – Structured, academic-style reports  
- 🔗 **Proper Citations** – Includes in-text citations and a formal reference list  
- 📝 **Multiple Perspectives** – Offers diverse viewpoints within the research  
- 💰 **Cost-Effective** – Uses Gemini, a budget-friendly alternative to OpenAI  
- 🔄 **Sectional Generation** – Breaks topics into logical, manageable parts  
- 📅 **Up-to-Date Research** – Uses recency filters to prioritize recent findings  
- 📑 **Standard Structure** – Reports follow a consistent flow and formatting  
- 🎯 **Focused Sections** – Highlights challenges, limitations, and future directions  
- 📊 **Consolidated References** – All sources listed in a final reference section  

---

## ⚙️ Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `topic` | The research topic (required) | N/A |
| `--depth` | Research depth level (1=basic, 2=detailed, 3=comprehensive) | 1 |
| `--queries` | Number of search queries (optional) | Based on depth |
| `--results` | Results per query (optional) | Based on depth |
| `--site` | Restrict search to a specific site (e.g. `nature.com`) | None |
| `--verbose` | Verbosity (0=minimal, 1=normal, 2=debug) | 1 |

---

## 🚀 Research Depth Levels

| Level | Name | Description | Estimated Length | Default Queries | Default Results/Query |
|-------|------|-------------|------------------|-----------------|------------------------|
| 1 | Basic | Brief overview | 5–7 pages (~3–5k words) | 3 | 2 |
| 2 | Detailed | In-depth exploration | 10–15 pages (~10–15k words) | 5 | 3 |
| 3 | Comprehensive | Deep technical dive | 20–30 pages (~25–30k words) | 8 | 4 |

---

## 🛠️ Usage

```bash
# Basic Research
python gemini_research.py -c "Future of renewable energy" --depth 1

# Detailed Research
python gemini_research.py -c "Impact of artificial intelligence on education" --depth 2

# Comprehensive Research
python gemini_research.py -c "Quantum computing applications in cryptography" --depth 3
```

---

## 🔍 How It Works

1. **Search Query Generation** – Gemini creates custom search prompts  
2. **Web Research** – Performs Google searches for each query  
3. **Content Scraping** – Extracts relevant content using `newspaper3k` and `BeautifulSoup`  
4. **Date Prioritization** – Selects content based on recency  
5. **Sectional Writing** – Builds a structured report with standard sections:
   - Executive Summary & Introduction  
   - Thematic Content Sections  
   - Challenges & Limitations  
   - Future Directions  
   - Conclusion  
   - References  
6. **Formatting** – Applies clean markdown, citations, and section numbering  
7. **Output** – Generates a full academic-style markdown report  

---

## 📋 Example Output

Each generated report includes:

- Executive Summary  
- Introduction  
- Thematic Sections  
- Key Findings Analysis  
- Challenges & Limitations  
- Future Research Opportunities  
- Conclusion  
- Consolidated References

### 📄 Sample Reports Included

Check the sample markdown report in the repo for a real example of what the platform produces.

---

## 📧 Getting Started

### Prerequisites

- Python 3.9+
- Google Gemini API Key
- Google Search API Key
- Google CSE ID

🔗 [Get Google CSE & API Keys](https://programmablesearchengine.google.com/controlpanel/all)

### Installation

1. **Clone the repo**

```bash
git clone https://github.com/GaganRao01/Gemini-Deep-Research.git
cd Gemini-Deep-Research
```

2. **Set up virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file using `.env.example` as a template:

```
GOOGLE_API_KEY=your_google_gemini_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- [Google Gemini](https://ai.google.dev/gemini)  
- [Google Custom Search](https://developers.google.com/custom-search)  
- [Newspaper3k](https://github.com/codelucas/newspaper)  
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
