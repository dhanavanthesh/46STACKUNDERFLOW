# NewsSense - CLI Based Scraped News,Market Insight.

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
###  📑Workflow
[news-sense-workflow.pdf](https://github.com/user-attachments/files/19717668/news-sense-workflow.pdf)


## Installation

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


### CLI OUTPUT (Command Line Interface)
1.
![WhatsApp Image 2025-04-12 at 09 20 43_8fcbe462](https://github.com/user-attachments/assets/7c58d6d0-5e29-4cce-8651-e28fcdf06151)
2.
![WhatsApp Image 2025-04-12 at 09 21 06_9ef66f44](https://github.com/user-attachments/assets/0fcecdbe-1f28-4412-8171-295b9ae2f788)
3.
![WhatsApp Image 2025-04-12 at 09 22 08_6838f219](https://github.com/user-attachments/assets/0c43d883-6c77-4ee9-914d-1eeb02ee4da0)
4.
![WhatsApp Image 2025-04-12 at 09 22 23_c4af60cc](https://github.com/user-attachments/assets/2df8b8ef-d083-47b1-8d8f-775f0eb97afc)

### Corelation

## Demo 1
![WhatsApp Image 2025-04-12 at 11 07 59_ff4fc558](https://github.com/user-attachments/assets/2cd31deb-052e-431b-8642-1ed4e2d4281e)

## Demo 2
![WhatsApp Image 2025-04-12 at 10 57 08_28d2077a](https://github.com/user-attachments/assets/4140bc80-a5ce-4863-ae85-e958241a138a)

The price increase on April 11 (from $442 to $455) represents a significant jump of about 3% in a single day, which is notable for an index fund like QQQ. Without corresponding negative news data, this suggests the price movement was likely driven by other market factors rather than news sentiment during this period.
