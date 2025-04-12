# NewsSense - "Why Is My Nifty Down?"

![NewsSense](https://img.shields.io/badge/NewsSense-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

A financial market explanation system that connects real-world news and events to market movements. Get AI-powered explanations for why stocks, ETFs, and mutual funds are moving up or down.

## 📑 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Example Queries](#example-queries)
- [Data Sources](#data-sources)
- [Technologies Used](#technologies-used)
- [Screenshots](#screenshots)
- [License](#license)

## 🔍 Overview

NewsSense is an AI-powered financial analysis tool that helps investors understand market movements by connecting price changes to real-world news and events. Instead of just seeing that a stock is "down 2%", NewsSense provides comprehensive explanations of the factors affecting security prices.

This project was created as a solution to the "Why Is My Nifty Down?" hackathon challenge, which required building a smart explanation system for market movements.

## ✨ Features

- **Security Analysis**: Detailed analysis of stocks, ETFs, and mutual funds
- **News Integration**: Scrapes and analyzes news from multiple financial sources
- **Natural Language Interface**: Ask questions in plain English about market movements
- **Multi-source News Scraping**: Custom HTML scraping from major financial news sites
- **Sentiment Analysis**: Analyzes sentiment of news articles to understand impact
- **Technical Indicators**: Provides technical analysis context for price movements
- **Market Context**: Shows how broader market trends affect individual securities
- **Sector Analysis**: Compares security performance to its sector
- **Multiple Securities Tracking**: Compare performance across a portfolio
- **Historical Analysis**: View saved analyses to track changes over time

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection for downloading dependencies and fetching market data

### Option 1: Automatic Installation (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/newssense.git
   cd newssense
   ```

2. Run the installation script:
   ```bash
   python install.py
   ```

3. The installation script will:
   - Check your Python version
   - Create the necessary directory structure
   - Install all required dependencies
   - Set up NLTK data for text processing
   - Test the installation

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/newssense.git
   cd newssense
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Install NLTK data for TextBlob:
   ```bash
   python -c "import nltk; nltk.download('punkt')"
   ```

5. Create the required directories:
   ```bash
   mkdir -p data/scraped_news data/market_data data/analysis data/queries data/gemini_cache
   ```

### Environment Variables (Optional)

For enhanced natural language processing capabilities, set these environment variables:

- `GEMINI_API_KEY`: Google's Gemini API key for advanced NLP
- `ALPHA_VANTAGE_KEY`: Alpha Vantage API key for additional market data

You can set these in a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
```

## 📂 Project Structure

```
newssense/
│
├── data/                     # Data storage
│   ├── scraped_news/         # Scraped news articles
│   ├── market_data/          # Market and security data
│   ├── analysis/             # Saved analyses
│   ├── queries/              # Query history
│   └── gemini_cache/         # Cached Gemini API responses
│
├── src/                      # Source code
│   ├── analyzer/             # Market data analysis
│   │   └── market_analyzer.py
│   │
│   ├── news_scraper/         # News scraping modules
│   │   └── news_collector.py
│   │
│   ├── query_processor/      # Natural language query processing
│   │   ├── query_processor.py
│   │   └── create_structure.py
│   │
│   └── utils/                # Utility functions
│       ├── helpers.py
│       ├── path_helper.py
│       └── gemini_helper.py
│
├── main.py                   # Main application entry point
├── install.py                # Installation script
├── requirements.txt          # Required Python packages
└── README.md                 # Project documentation
```

## 🚀 Usage

### Starting the Application

After installation, start the application with:

```bash
python main.py
```

### Main Menu Options

The CLI interface provides the following options:

1. **Analyze Security**: Get detailed analysis of a specific ticker
2. **Ask a Question**: Ask natural language questions about market movements
3. **Track Multiple Securities**: Compare multiple securities side-by-side
4. **View Recent Analyses**: Access previously saved analyses
5. **Help**: Display usage information and examples
6. **Exit**: Quit the application

### Using the Analysis Features

#### Option 1: Analyze Security
Enter a ticker symbol (e.g., AAPL, MSFT, NIFTY50) to get a comprehensive analysis including:
- Price movement
- Volume analysis
- News sentiment
- Market context
- Key factors affecting price

#### Option 2: Ask a Question
Ask natural language questions about market movements, such as:
- "Why is Apple up today?"
- "What happened to Nifty this week?"
- "Any macro news impacting tech stocks?"

#### Option 3: Track Multiple Securities
Enter multiple tickers separated by commas to compare:
- Price movements
- News sentiment
- Sector performance
- Correlations between securities

#### Option 4: View Recent Analyses
Browse and view previously saved analyses to track changes over time.

## 💬 Example Queries

NewsSense supports a wide range of natural language queries:

- "Why is AAPL up today?"
- "What happened to Nifty this week?"
- "Why did Jyothy Labs go up today?"
- "How is QQQ performing compared to the market?"
- "Any macro news impacting tech-focused stocks?"
- "What's happening with SBI AMC?"
- "Why is RELIANCE.NS down?"
- "How is the technology sector performing?"
- "What's driving the drop in emerging market funds?"
- "Why is my ETF not following the market trend?"

## 📊 Data Sources

NewsSense collects data from multiple sources:

### Market Data
- **datasets**: Securities price data, company information, and technical indicators , mutual funds and holdings
- **Alpha Vantage** (optional): Additional market data with API key

### News Sources
NewsSense scrapes financial news from:
- Yahoo finance
- MarketWatch
- Reuters
- CNBC
- Seeking Alpha
- Investing.com
- Benzinga
- Finviz
- The Fly
- Zacks
- Barron's
- Bloomberg

## 🔧 Technologies Used

- **Python**: Core programming language
- **Alpha vantage and datasets**: mf , mf_holdings, market data
- **BeautifulSoup**: HTML parsing for news scraping
- **Requests**: HTTP requests for web scraping
- **TextBlob**: Natural language processing and sentiment analysis
- **pandas**: Data manipulation and analysis
- **Colorama**: Terminal color formatting
- **Tabulate**: Formatted table output
- **Google Gemini API** (optional): Enhanced natural language understanding

## 📸 Screenshots

(Insert screenshots of the application here)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📣 Disclaimer

NewsSense is for educational and informational purposes only. It does not provide investment advice, and you should not rely solely on its analysis for making investment decisions. The data and analysis provided may not be accurate or complete. Always consult with a qualified financial advisor before making investment decisions.