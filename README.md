# NewsSense - "Why Is My Nifty Down?"

NewsSense is an AI-powered financial news analysis system that explains market movements by connecting real-world news and events to investment performance. It helps investors understand why their stocks, ETFs, or mutual funds are moving up or down.

## Features

- **Real-time Market Data**: Fetches current and historical price data for stocks, ETFs, and mutual funds
- **Multi-source News Scraping**: Collects financial news from Yahoo Finance, MarketWatch, Reuters, CNBC, and Seeking Alpha
- **Smart Entity Recognition**: Maps financial instruments to news mentions
- **Sentiment Analysis**: Evaluates the emotional tone of news articles
- **Natural Language Querying**: Answer questions about market movements in plain English
- **Comprehensive Explanations**: Generates detailed explanations for price movements

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/newssense.git
   cd newssense
   ```

2. Install dependencies:
   ```
   python install.py
   ```
   
   Or manually install required packages:
   ```
   pip install -r requirements.txt
   ```

## Project Structure

```
market_analyzer/
├── data/
│   ├── scraped_news/   # Stores scraped news articles
│   ├── market_data/    # Stores financial market data
│   └── analysis/       # Stores analysis results
├── src/
│   ├── __init__.py
│   ├── analyzer/
│   │   ├── __init__.py
│   │   └── market_analyzer.py   # Analysis of market data and news
│   ├── news_scraper/
│   │   ├── __init__.py
│   │   └── news_collector.py    # Multi-source news collection
│   ├── query_processor/
│   │   ├── __init__.py
│   │   └── query_processor.py   # Natural language query processing
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # Helper functions and utilities
├── main.py                      # Main application entry point
└── requirements.txt             # Project dependencies
```

## Usage

### Command Line Interface

Run the application with:

```
python main.py
```

This will start an interactive CLI where you can:
1. Enter stock tickers or fund identifiers
2. Ask natural language questions about market movements
3. Get detailed explanations about recent performance

### Example Queries

- "Why is Apple up today?"
- "What happened to Nifty this week?"
- "Explain the recent drop in Tesla"
- "How is Amazon performing compared to the market?"
- "What's the news impact on Microsoft?"

## Data Sources

- **Market Data**: Yahoo Finance API
- **News Sources**:
  - Yahoo Finance
  - MarketWatch
  - Reuters
  - CNBC
  - Seeking Alpha

## Implementation Notes

### News Scraping

Instead of using plug-and-play news APIs, NewsSense implements custom HTML scraping using:
- Beautiful Soup for HTML parsing
- Strategic rate limiting to avoid blocking
- Multi-threaded scraping for improved performance
- User-agent rotation for better reliability

### Entity Resolution

The system connects news articles to financial instruments using:
- Direct ticker symbol matching
- Company name recognition
- Sector and industry mapping
- Entity extraction from headlines and content

### Natural Language Processing

News articles are processed using:
- TextBlob for sentiment analysis
- Keyword extraction for topic classification
- Entity recognition for relevant mentions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

NewsSense is for educational and informational purposes only. It does not provide investment advice, and you should not rely solely on its analysis for making investment decisions.

### CLI OUTPUT:

![WhatsApp Image 2025-04-12 at 09 20 43_8fcbe462](https://github.com/user-attachments/assets/7c58d6d0-5e29-4cce-8651-e28fcdf06151)

