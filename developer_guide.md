# NewsSense Developer Guide

This developer guide provides detailed information about the architecture, components, and implementation details of the NewsSense system. It's intended for developers who want to understand, modify, or extend the codebase.

## Table of Contents
- [System Architecture](#system-architecture)
- [Component Overview](#component-overview)
- [Code Structure](#code-structure)
- [Adding New Features](#adding-new-features)
- [Common Developer Tasks](#common-developer-tasks)
- [API Integrations](#api-integrations)
- [Testing](#testing)
- [Deployment](#deployment)

## System Architecture

NewsSense follows a modular architecture with several key components:

```
[User Interface (CLI)] <-> [Query Processor]
        ^                         ^
        |                         |
        v                         v
[News Scraper] <-----> [Market Analyzer] <-----> [External APIs]
```

The system works as follows:

1. User inputs a query via the CLI interface
2. Query Processor extracts intent and entities from the query
3. Market Analyzer fetches market data for relevant securities
4. News Scraper collects recent news about the securities
5. Market Analyzer combines market data and news to generate explanations
6. Results are formatted and displayed to the user via the CLI

## Component Overview

### 1. Command Line Interface (CLI)

- **File**: `main.py`
- **Class**: `NewsSenseCLI`
- **Purpose**: Provides user interaction through a text-based interface
- **Features**:
  - Interactive menu system
  - Color-coded output using Colorama
  - Table formatting using Tabulate
  - Command history and session management

### 2. News Scraper

- **File**: `src/news_scraper/news_collector.py`
- **Class**: `NewsCollector`
- **Purpose**: Scrapes financial news from multiple sources
- **Features**:
  - Multi-source collection from financial websites
  - Rate limiting and retry mechanisms
  - HTML parsing with BeautifulSoup
  - Entity tagging and categorization

### 3. Market Analyzer

- **File**: `src/analyzer/market_analyzer.py`
- **Class**: `MarketAnalyzer`
- **Purpose**: Analyzes market data and correlates with news
- **Features**:
  - Security price and volume analysis
  - Technical indicator calculation
  - News sentiment analysis
  - Market and sector context
  - Explanation generation

### 4. Query Processor

- **File**: `src/query_processor/query_processor.py`
- **Class**: `QueryProcessor`
- **Purpose**: Processes natural language queries into structured components
- **Features**:
  - Intent detection
  - Entity extraction (tickers, timeframes)
  - Query categorization
  - Response generation
  - Integration with Gemini API (optional)

### 5. Gemini Helper

- **File**: `src/utils/gemini_helper.py`
- **Class**: `GeminiHelper`
- **Purpose**: Provides enhanced NLP capabilities using Google's Gemini API
- **Features**:
  - Query component extraction
  - Market context analysis
  - Sentiment enhancement
  - Entity resolution

## Code Structure

### Main Modules

1. **Main Application** (`main.py`)
   - Entry point and CLI interface
   - Initializes components
   - Handles user interaction

2. **Installation Script** (`install.py`)
   - Sets up the environment
   - Installs dependencies
   - Creates directory structure
   - Tests the installation

3. **Requirements** (`requirements.txt`)
   - Lists all Python package dependencies

### Source Directories

1. **Analyzer** (`src/analyzer/`)
   - Market data analysis modules
   - Technical indicator calculation
   - Explanation generation

2. **News Scraper** (`src/news_scraper/`)
   - Web scraping for financial news
   - News source management
   - Content extraction and parsing

3. **Query Processor** (`src/query_processor/`)
   - Natural language processing
   - Intent and entity extraction
   - Response generation

4. **Utilities** (`src/utils/`)
   - Helper functions
   - Path management
   - Formatting utilities
   - API integrations

### Data Directories

1. **Scraped News** (`data/scraped_news/`)
   - Downloaded and parsed news articles
   - Stored as JSON files with metadata

2. **Market Data** (`data/market_data/`)
   - Security price and volume data
   - Technical indicators
   - Market indices data

3. **Analysis** (`data/analysis/`)
   - Generated analysis reports
   - Saved explanations

4. **Queries** (`data/queries/`)
   - Historical query log
   - User interaction history

5. **Gemini Cache** (`data/gemini_cache/`)
   - Cached responses from Gemini API
   - Reduces API usage and improves performance

## Adding New Features

### Adding a New News Source

To add a new financial news source:

1. Create a new method in `NewsCollector` class:
   ```python
   def _scrape_new_source(self, ticker):
       """Scrape news from New Source"""
       try:
           self._rate_limit('new_source')
           url = f"https://www.newsource.com/stocks/{ticker.lower()}"
           
           response = self._make_request(url, 'new_source')
           if not response or response.status_code != 200:
               return []
               
           soup = BeautifulSoup(response.text, 'html.parser')
           news_items = []
           
           # Find news items - adjust selectors based on actual HTML structure
           articles = soup.find_all("div", {"class": "news-item"})
           
           for article in articles[:10]:
               try:
                   # Extract title, timestamp, link, etc.
                   # Add to news_items list
               except Exception as e:
                   logger.error(f"Error parsing New Source article: {str(e)}")
           
           return news_items
       except Exception as e:
           logger.error(f"Error scraping New Source: {str(e)}")
           return []
   ```

2. Add the new source to the `sources` dictionary in the `__init__` method:
   ```python
   self.sources["new_source"] = self._scrape_new_source
   ```

### Adding a New Analysis Feature

To add a new analysis capability:

1. Create a new method in the `MarketAnalyzer` class:
   ```python
   def _analyze_new_feature(self, security_data):
       """Analyze a new feature of the security"""
       try:
           # Implementation
           result = {
               'feature_metric_1': value1,
               'feature_metric_2': value2,
           }
           return result
       except Exception as e:
           logger.error(f"Error analyzing new feature: {str(e)}")
           return {}
   ```

2. Integrate it into the `analyze_security` method:
   ```python
   # Add to analyze_security method
   new_feature_analysis = self._analyze_new_feature(data)
   
   # Add to result
   result['new_feature_analysis'] = new_feature_analysis
   ```

3. Update the explanation generation to include the new feature:
   ```python
   # Add to _generate_explanation or create a new explanation method
   new_feature_explanation = self._generate_new_feature_explanation(security_data)
   explanation_parts.append(new_feature_explanation)
   ```

### Adding a New Query Type

To support a new type of query:

1. Add new intent keywords in `QueryProcessor.__init__`:
   ```python
   self.intent_keywords['new_intent'] = [
       'keyword1', 'keyword2', 'keyword3'
   ]
   ```

2. Create a new explanation generation method:
   ```python
   def _generate_new_intent_explanation(self, security_data, news_analysis, ticker):
       """Generate explanation for the new intent"""
       try:
           # Implementation
           return explanation_text
       except Exception as e:
           logger.error(f"Error generating new intent explanation: {str(e)}")
           return f"I couldn't analyze this aspect for {ticker}."
   ```

3. Update the `_generate_explanation` method to handle the new intent:
   ```python
   elif intent == 'new_intent':
       return self._generate_new_intent_explanation(security_data, news_analysis, ticker)
   ```

## Common Developer Tasks

### 1. Adding Support for a New Market Index

To add support for a new market index:

1. Add the index to the `market_indicators` dictionary in `MarketAnalyzer.__init__`:
   ```python
   self.market_indicators["^NEW"] = "New Index Name"
   ```

### 2. Enhancing News Sentiment Analysis

To improve sentiment analysis:

1. Modify the `analyze_news_impact` method in `MarketAnalyzer`
2. Adjust sentiment thresholds or categorization logic
3. Add more sophisticated sentiment analysis using additional libraries
4. Implement custom sentiment dictionaries for financial terminology

### 3. Adding Command Line Arguments

To support command line arguments:

1. Import the `argparse` module in `main.py`
2. Set up command line argument parsing before creating the CLI instance
3. Pass parsed arguments to the CLI initialization

Example:
```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='NewsSense - Market Explanation System')
    parser.add_argument('--ticker', type=str, help='Analyze a specific ticker')
    parser.add_argument('--query', type=str, help='Process a specific query')
    return parser.parse_args()

def main():
    args = parse_args()
    cli = NewsSenseCLI()
    
    if args.ticker:
        cli.analyze_security(args.ticker)
    elif args.query:
        cli.process_query(args.query)
    else:
        cli.run()
```

## API Integrations

### Yahoo Finance

The system uses `yfinance` to retrieve market data:

- **Purpose**: Fetch security price data, company information, historical data
- **Implementation**: `src/data_fetcher/yahoo_finance.py`
- **Usage**:
  ```python
  stock = yf.Ticker(ticker)
  hist = stock.history(period=period, interval=interval)
  info = stock.info
  ```

### Google Gemini API

For enhanced NLP capabilities:

- **Purpose**: Advanced natural language understanding and generation
- **Implementation**: `src/utils/gemini_helper.py`
- **API Key**: Required as environment variable or in `.env` file
- **Usage**:
  ```python
  components = self.gemini_helper.extract_query_components(query_text)
  analysis = self.gemini_helper.analyze_market_context(query, data)
  ```

### Alpha Vantage API

For additional financial data:

- **Purpose**: Alternative source for stock data and news
- **Implementation**: `src/utils/gemini_helper.py` (embedded functionality)
- **API Key**: Required as environment variable or in `.env` file
- **Usage**:
  ```python
  params = {
      "function": "NEWS_SENTIMENT",
      "tickers": ticker,
      "apikey": self.alpha_vantage_key
  }
  response = requests.get(self.alpha_vantage_url, params=params)
  ```

## Testing

Currently, NewsSense doesn't have a formal testing framework. To implement tests:

1. Create a `tests` directory with test modules for each component
2. Use Python's `unittest` or `pytest` framework
3. Implement unit tests for each class and method
4. Create mock objects for external APIs and services
5. Set up GitHub Actions for continuous integration

Example test structure:
```
tests/
├── test_market_analyzer.py
├── test_news_collector.py
├── test_query_processor.py
└── test_gemini_helper.py
```

Example test module:
```python
import unittest
from unittest.mock import patch, MagicMock
from src.analyzer.market_analyzer import MarketAnalyzer

class TestMarketAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = MarketAnalyzer()
        
    def test_analyze_security(self):
        with patch('yfinance.Ticker') as mock_ticker:
            mock_ticker.return_value.history.return_value = self.mock_history_data()
            mock_ticker.return_value.info = self.mock_info_data()
            
            result = self.analyzer.analyze_security("AAPL")
            self.assertTrue('data' in result)
            self.assertTrue('info' in result)
            # More assertions...
            
    # Helper methods for creating mock data
    def mock_history_data(self):
        # Create a pandas DataFrame with mock data
        pass
        
    def mock_info_data(self):
        # Create a dictionary with mock info
        pass
```

## Deployment

NewsSense is designed as a standalone Python application. For deployment options:

### Option 1: Package as a Python Package

1. Add a `setup.py` file:
   ```python
   from setuptools import setup, find_packages

   setup(
       name="newssense",
       version="1.0.0",
       packages=find_packages(),
       install_requires=[
           # List dependencies from requirements.txt
       ],
       entry_points={
           'console_scripts': [
               'newssense=main:main',
           ],
       },
       # Add more metadata
   )
   ```

2. Build and install the package:
   ```bash
   pip install -e .
   ```

3. Users can then install via pip:
   ```bash
   pip install newssense
   ```

### Option 2: Docker Container

1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "main.py"]
   ```

2. Build and run the container:
   ```bash
   docker build -t newssense .
   docker run -it newssense
   ```

### Option 3: Web Service

Convert NewsSense into a web service:

1. Add a web framework like Flask:
   ```python
   from flask import Flask, request, jsonify

   app = Flask(__name__)

   @app.route('/api/analyze', methods=['POST'])
   def analyze():
       data = request.json
       ticker = data.get('ticker')
       # Process the request using NewsSense components
       result = market_analyzer.analyze_security(ticker)
       return jsonify(result)

   if __name__ == '__main__':
       app.run(debug=True)
   ```

2. Deploy to a cloud service like Heroku, AWS, or Google Cloud