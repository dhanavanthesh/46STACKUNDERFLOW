#!/usr/bin/env python3
"""
NewsSense API - Financial News Analysis System
This module provides API endpoints to serve the NewsSense functionality.
"""

import numpy as np
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            return super().default(obj)
        except Exception:
            return str(obj)

# Create Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.json_encoder = CustomJSONEncoder
CORS(app)

# Rest of your imports
import os
import sys
import logging
from datetime import datetime
import traceback
from dotenv import load_dotenv

# Rest of your code remains exactly the same...

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("newssense_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsSenseAPI")

class NewsSenseAPI:
    def __init__(self):
        """Initialize the API with required components"""
        try:
            self._fix_path_issues()
            
            from src.news_scraper.news_collector import NewsCollector
            from src.analyzer.market_analyzer import MarketAnalyzer
            from src.query_processor.query_processor import QueryProcessor
            from src.utils.gemini_helper import GeminiHelper
            
            self.gemini_helper = GeminiHelper(
                api_key=os.getenv("GEMINI_API_KEY"),
                alpha_vantage_key=os.getenv("ALPHA_VANTAGE_KEY")
            )
            
            self.news_collector = NewsCollector()
            self.market_analyzer = MarketAnalyzer()
            self.query_processor = QueryProcessor(
                self.news_collector, 
                self.market_analyzer,
                self.gemini_helper
            )
            
            # Ensure data directories exist
            os.makedirs(os.path.join("data", "analysis"), exist_ok=True)
            os.makedirs(os.path.join("data", "scraped_news"), exist_ok=True)
            os.makedirs(os.path.join("data", "market_data"), exist_ok=True)
            
            logger.info("NewsSense API initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _fix_path_issues(self):
        """Fix common path issues"""
        src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        current_dir = os.path.abspath(os.path.dirname(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
    
    def analyze_ticker(self, ticker):
        """Analyze a specific ticker symbol"""
        try:
            logger.info(f"Analyzing ticker: {ticker}")
            
            # Fetch market data
            security_data = self.market_analyzer.analyze_security(ticker)
            if not security_data:
                return {
                    "success": False,
                    "message": f"Failed to fetch market data for {ticker}"
                }
            
            # Collect news from multiple sources
            news_items = self.news_collector.scrape_all_sources(ticker)
            
            # Analyze news and market context
            news_analysis = self.market_analyzer.analyze_news_impact(news_items)
            
            # Generate explanation
            explanation = self.market_analyzer.generate_explanation(security_data, news_analysis, ticker)
            
            # Prepare correlation data for price vs news (if available)
            correlation_result = self.market_analyzer.compute_price_news_correlation(security_data, news_items)
            
            # Extract key metrics for frontend display
            price_info = self._extract_price_info(security_data)
            volume_info = self._extract_volume_info(security_data)
            market_context = self._extract_market_context(security_data)
            news_data = self._format_news_data(news_items, news_analysis)

            # Format the response
            response = {
                "success": True,
                "ticker": ticker,
                "companyInfo": self._extract_company_info(security_data, ticker),
                "priceInfo": price_info,
                "volumeInfo": volume_info,
                "marketContext": market_context,
                "explanation": explanation,
                "newsAnalysis": {
                    "sentimentSummary": {
                        "overall": news_analysis.get("sentiment_label", "Neutral"),
                        "score": news_analysis.get("average_sentiment", 0),
                        "distribution": news_analysis.get("sentiment_distribution", {})
                    },
                    "topTopics": self._extract_top_topics(news_analysis),
                    "newsItems": news_data
                },
                "correlation": correlation_result
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing ticker {ticker}: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"Error analyzing {ticker}: {str(e)}"
            }
    
    def process_query(self, query_text):
        """Process a natural language query"""
        try:
            logger.info(f"Processing query: {query_text}")
            
            # First try using Gemini helper to extract intent and tickers
            components = self.gemini_helper.extract_query_components(query_text)
            
            # If no tickers found in the query, provide a general market analysis
            if not components or not components.get('tickers'):
                logger.info("No specific tickers found in query, providing general market analysis")
                return self._generate_general_market_analysis(query_text)
            
            # Extract the main ticker from components
            ticker = components['tickers'][0]
            
            # Get detailed analysis for the ticker
            ticker_analysis = self.analyze_ticker(ticker)
            
            # Generate a specific explanation for the query
            context_analysis = self.gemini_helper.analyze_market_context(
                query_text,
                {
                    'ticker': ticker,
                    'market_data': ticker_analysis.get('marketContext', {}),
                    'news': ticker_analysis.get('newsAnalysis', {}).get('newsItems', [])
                }
            )
            
            # Add the specific query analysis to the response
            ticker_analysis['queryAnalysis'] = context_analysis
            ticker_analysis['queryComponents'] = components
            
            return ticker_analysis
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"Error processing query: {str(e)}"
            }
    
    def track_multiple_securities(self, tickers):
        """Track and compare multiple securities"""
        try:
            if not tickers:
                return {
                    "success": False,
                    "message": "No tickers provided"
                }
            
            # Limit to maximum 10 tickers
            if len(tickers) > 10:
                tickers = tickers[:10]
            
            logger.info(f"Tracking multiple securities: {', '.join(tickers)}")
            
            # Collect data for all securities
            securities_data = []
            
            for ticker in tickers:
                try:
                    # Get market data
                    security_data = self.market_analyzer.analyze_security(ticker)
                    
                    # Skip if there was an error getting the security
                    if security_data and 'error' in security_data:
                        logger.warning(f"Error with {ticker}: {security_data['error']}")
                        continue
                    
                    # Get news and sentiment
                    news_items = self.news_collector.scrape_all_sources(ticker)
                    news_analysis = self.market_analyzer.analyze_news_impact(news_items)
                    
                    # Extract key metrics
                    if security_data and 'data' in security_data and 'today' in security_data['data']:
                        today_data = security_data['data']['today']
                        if not today_data.empty:
                            current_price = today_data['Close'].iloc[-1]
                            open_price = today_data['Open'].iloc[0]
                            price_change = current_price - open_price
                            price_change_pct = (price_change / open_price) * 100
                            
                            securities_data.append({
                                'ticker': ticker,
                                'name': security_data.get('info', {}).get('longName', ticker),
                                'sector': security_data.get('info', {}).get('sector', 'Unknown'),
                                'industry': security_data.get('info', {}).get('industry', 'Unknown'),
                                'price': current_price,
                                'openPrice': open_price,
                                'change': price_change,
                                'changePercent': price_change_pct,
                                'news_sentiment': news_analysis.get('average_sentiment', 0),
                                'sentiment_label': news_analysis.get('sentiment_label', 'Neutral'),
                                'news_count': len(news_analysis.get('sentiments', [])),
                                'newsItems': self._format_news_data(news_items, news_analysis)[:5]  # Include top 5 news items
                            })
                except Exception as e:
                    logger.error(f"Error fetching data for {ticker}: {str(e)}")
                    logger.error(traceback.format_exc())
            
            # Find correlations and patterns
            observations = self._generate_securities_observations(securities_data)
            
            # Format the response
            response = {
                "success": True,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "query": f"Track: {', '.join(tickers)}",
                "securitiesData": securities_data,
                "observations": observations,
                "count": len(securities_data)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error tracking securities: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"Error tracking securities: {str(e)}"
            }
    
    def _generate_general_market_analysis(self, query_text):
        """Generate a general market analysis when no specific ticker is found"""
        try:
            # Market indices to analyze
            market_indices = ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"]
            
            # Collect data for key indices
            indices_data = []
            for index_symbol in market_indices:
                try:
                    security_data = self.market_analyzer.analyze_security(index_symbol)
                    if security_data and 'data' in security_data and 'today' in security_data['data']:
                        today_data = security_data['data']['today']
                        if not today_data.empty:
                            current_price = today_data['Close'].iloc[-1]
                            open_price = today_data['Open'].iloc[0]
                            price_change = current_price - open_price
                            price_change_pct = (price_change / open_price) * 100
                            
                            # Get full index name
                            index_name = security_data.get('info', {}).get('shortName', index_symbol)
                            if index_symbol == "^GSPC":
                                index_name = "S&P 500"
                            elif index_symbol == "^DJI":
                                index_name = "Dow Jones Industrial Average"
                            elif index_symbol == "^IXIC":
                                index_name = "NASDAQ Composite"
                            elif index_symbol == "^RUT":
                                index_name = "Russell 2000"
                            elif index_symbol == "^VIX":
                                index_name = "CBOE Volatility Index"
                            
                            indices_data.append({
                                'symbol': index_symbol,
                                'name': index_name,
                                'price': current_price,
                                'change': price_change,
                                'changePercent': price_change_pct,
                                'direction': 'up' if price_change >= 0 else 'down'
                            })
                except Exception as e:
                    logger.error(f"Error analyzing index {index_symbol}: {str(e)}")
            
            # Analyze key sector ETFs
            sector_etfs = {
                "XLK": "Technology",
                "XLF": "Financials",
                "XLE": "Energy",
                "XLV": "Healthcare",
                "XLI": "Industrials",
                "XLP": "Consumer Staples",
                "XLY": "Consumer Discretionary"
            }
            
            sectors_data = []
            for etf_symbol, sector_name in sector_etfs.items():
                try:
                    security_data = self.market_analyzer.analyze_security(etf_symbol)
                    if security_data and 'data' in security_data and 'today' in security_data['data']:
                        today_data = security_data['data']['today']
                        if not today_data.empty:
                            current_price = today_data['Close'].iloc[-1]
                            open_price = today_data['Open'].iloc[0]
                            price_change = current_price - open_price
                            price_change_pct = (price_change / open_price) * 100
                            
                            sectors_data.append({
                                'symbol': etf_symbol,
                                'sector': sector_name,
                                'price': current_price,
                                'change': price_change,
                                'changePercent': price_change_pct,
                                'direction': 'up' if price_change >= 0 else 'down'
                            })
                except Exception as e:
                    logger.error(f"Error analyzing sector ETF {etf_symbol}: {str(e)}")
            
            # Collect top market news
            market_news = []
            for index_symbol in ["SPY", "QQQ"]:  # Use ETFs for better news coverage
                news_items = self.news_collector.scrape_all_sources(index_symbol)
                market_news.extend(news_items)
            
            # Remove duplicate news
            seen_titles = set()
            unique_news = []
            for item in market_news:
                title = item.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(item)
            
            # Analyze sentiment of market news
            news_analysis = self.market_analyzer.analyze_news_impact(unique_news)
            
            # Use Gemini for market context analysis
            market_context = self.gemini_helper.analyze_market_context(
                query_text,
                {
                    'indices': indices_data,
                    'sectors': sectors_data,
                    'news': unique_news
                }
            )
            
            # Format the response
            response = {
                "success": True,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "query": query_text,
                "marketIndices": indices_data,
                "sectorPerformance": sectors_data,
                "marketNews": self._format_news_data(unique_news, news_analysis)[:10],  # Top 10 news
                "newsSentiment": {
                    "overall": news_analysis.get("sentiment_label", "Neutral"),
                    "score": news_analysis.get("average_sentiment", 0),
                    "distribution": news_analysis.get("sentiment_distribution", {})
                },
                "marketAnalysis": market_context,
                "topics": self._extract_top_topics(news_analysis)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating general market analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"Error analyzing market data: {str(e)}"
            }
    
    def _extract_company_info(self, security_data, ticker):
        """Extract company information from security data"""
        if not security_data or 'info' not in security_data:
            return {"name": ticker, "ticker": ticker}
        
        info = security_data.get('info', {})
        return {
            "name": info.get('longName', ticker),
            "ticker": ticker,
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "website": info.get('website', ''),
            "description": info.get('longBusinessSummary', ''),
            "country": info.get('country', ''),
            "exchange": info.get('exchange', ''),
            "marketCap": info.get('marketCap', None),
            "peRatio": info.get('trailingPE', None),
            "beta": info.get('beta', None)
        }
    
    def _extract_price_info(self, security_data):
        """Extract price information from security data"""
        price_info = {
            "current": None,
            "open": None,
            "high": None,
            "low": None,
            "change": None,
            "changePercent": None,
            "direction": None
        }
        
        if not security_data or 'data' not in security_data or 'today' not in security_data['data']:
            return price_info
        
        today_data = security_data['data']['today']
        if today_data.empty:
            return price_info
        
        # Extract price data
        current_price = today_data['Close'].iloc[-1]
        open_price = today_data['Open'].iloc[0]
        high_price = today_data['High'].max()
        low_price = today_data['Low'].min()
        price_change = current_price - open_price
        price_change_pct = (price_change / open_price) * 100
        
        price_info = {
            "current": current_price,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "change": price_change,
            "changePercent": price_change_pct,
            "direction": "up" if price_change >= 0 else "down"
        }
        
        return price_info
    
    def _extract_volume_info(self, security_data):
        """Extract volume information from security data"""
        volume_info = {
            "current": None,
            "average": None,
            "change": None,
            "changePercent": None
        }
        
        if not security_data or 'data' not in security_data or 'today' not in security_data['data']:
            return volume_info
        
        today_data = security_data['data']['today']
        if today_data.empty or 'Volume' not in today_data.columns:
            return volume_info
        
        # Extract volume data
        current_volume = today_data['Volume'].sum()
        avg_volume = today_data['Volume'].mean()
        volume_change = current_volume - avg_volume
        volume_change_pct = ((current_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
        
        volume_info = {
            "current": current_volume,
            "average": avg_volume,
            "change": volume_change,
            "changePercent": volume_change_pct
        }
        
        return volume_info
    
    def _extract_market_context(self, security_data):
        """Extract market context information"""
        if not security_data or 'market_context' not in security_data:
            return []
        
        market_context = security_data['market_context']
        result = []
        
        for index_name, index_data in market_context.items():
            if isinstance(index_data, dict) and 'change_pct' in index_data:
                result.append({
                    "name": index_name,
                    "change": index_data.get('change_pct', 0),
                    "direction": "up" if index_data.get('change_pct', 0) >= 0 else "down",
                    "price": index_data.get('price', 0)
                })
        
        return result
    
    def _format_news_data(self, news_items, news_analysis):
        """Format news data for API response"""
        if not news_items:
            return []
        
        # Get sentiment data from analysis
        sentiment_items = news_analysis.get('sentiments', [])
        sentiment_map = {item.get('title', ''): item.get('sentiment', 0) for item in sentiment_items}
        
        formatted_news = []
        for item in news_items:
            title = item.get('title', '')
            sentiment = sentiment_map.get(title, 0)
            
            # Determine sentiment label
            sentiment_label = "Neutral"
            if sentiment > 0.2:
                sentiment_label = "Positive"
            elif sentiment < -0.2:
                sentiment_label = "Negative"
            
            # Determine impact level
            impact = "Low"
            if abs(sentiment) > 0.5:
                impact = "High"
            elif abs(sentiment) > 0.2:
                impact = "Medium"
            
            formatted_news.append({
                "id": str(hash(title + item.get('url', ''))),
                "title": title,
                "summary": item.get('summary', ''),
                "content": item.get('summary', ''),
                "url": item.get('url', ''),
                "source": item.get('source', 'Unknown'),
                "date": item.get('timestamp', datetime.now().strftime('%Y-%m-%d')),
                "sentiment": sentiment_label,
                "sentimentScore": sentiment,
                "impact": impact,
                "entities": item.get('entities', {}).get('tickers', [])
            })
        
        # Sort by sentiment impact (absolute value of sentiment)
        formatted_news.sort(key=lambda x: abs(x['sentimentScore']), reverse=True)
        
        return formatted_news
    
    def _extract_top_topics(self, news_analysis):
        """Extract top topics from news analysis"""
        if not news_analysis or 'topics' not in news_analysis:
            return []
        
        topics = news_analysis['topics']
        return [{"name": topic.replace("_", " ").title(), "count": count} 
                for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True) 
                if count > 0][:5]  # Return top 5 topics
    
    def _generate_securities_observations(self, securities_data):
        """Generate observations and patterns from multiple securities data"""
        observations = []
        
        if len(securities_data) < 2:
            return observations
        
        # Sector patterns
        sectors = {}
        for data in securities_data:
            sector = data['sector']
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(data)
        
        for sector, stocks in sectors.items():
            if len(stocks) > 1:
                avg_change = sum(s['changePercent'] for s in stocks) / len(stocks)
                direction = "up" if avg_change > 0 else "down"
                observations.append({
                    "type": "sector",
                    "text": f"{sector} sector is trending {direction} ({avg_change:.2f}%)",
                    "sector": sector,
                    "direction": direction,
                    "change": avg_change,
                    "securities": [s['ticker'] for s in stocks]
                })
        
        # News sentiment correlation
        correlated_count = sum(1 for s in securities_data 
                            if (s['changePercent'] > 0 and s['news_sentiment'] > 0) or
                              (s['changePercent'] < 0 and s['news_sentiment'] < 0))
        correlation_pct = (correlated_count / len(securities_data)) * 100
        
        correlation_level = "strong" if correlation_pct > 70 else "moderate" if correlation_pct > 40 else "weak"
        observations.append({
            "type": "correlation",
            "text": f"{correlation_level.title()} correlation between news sentiment and price movement ({correlation_pct:.0f}%)",
            "level": correlation_level,
            "percentage": correlation_pct
        })
        
        # Performance outliers
        avg_performance = sum(s['changePercent'] for s in securities_data) / len(securities_data)
        outliers = []
        
        for security in securities_data:
            # If a security differs from average by more than 2x
            if abs(security['changePercent'] - avg_performance) > (2 * abs(avg_performance)):
                outliers.append({
                    "ticker": security['ticker'],
                    "name": security['name'],
                    "change": security['changePercent'],
                    "difference": security['changePercent'] - avg_performance
                })
        
        if outliers:
            observations.append({
                "type": "outliers",
                "text": f"Found {len(outliers)} securities with unusual performance",
                "count": len(outliers),
                "details": outliers
            })
        
        return observations

# Create a Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the NewsSense API
api = NewsSenseAPI()

@app.route('/api/analyze/<ticker>', methods=['GET'])
def analyze_ticker(ticker):
    """API endpoint to analyze a specific ticker"""
    ticker = ticker.upper()
    result = api.analyze_ticker(ticker)
    return app.response_class(
        response=json.dumps(result, cls=CustomJSONEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/query', methods=['POST'])
def process_query():
    """API endpoint to process a natural language query"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return app.response_class(
            response=json.dumps({
                "success": False,
                "message": "No query provided"
            }),
            status=400,
            mimetype='application/json'
        )
    
    result = api.process_query(query)
    return app.response_class(
        response=json.dumps(result, cls=CustomJSONEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/track', methods=['POST'])
def track_securities():
    """API endpoint to track multiple securities"""
    data = request.json
    tickers = data.get('tickers', [])
    
    if not tickers:
        return app.response_class(
            response=json.dumps({
                "success": False,
                "message": "No tickers provided"
            }),
            status=400,
            mimetype='application/json'
        )
    
    tickers = [ticker.upper() for ticker in tickers]
    result = api.track_multiple_securities(tickers)
    return app.response_class(
        response=json.dumps(result, cls=CustomJSONEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return app.response_class(
        response=json.dumps({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }),
        status=200,
        mimetype='application/json'
    )

# Add error handler for JSON encoder errors
@app.errorhandler(TypeError)
def handle_type_error(e):
    return app.response_class(
        response=json.dumps({
            "success": False,
            "message": "Data serialization error",
            "error": str(e)
        }),
        status=500,
        mimetype='application/json'
    )
    
# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response   
    
    

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting NewsSense API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)