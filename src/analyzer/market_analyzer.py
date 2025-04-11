import yfinance as yf
from textblob import TextBlob
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class MarketAnalyzer:
    def __init__(self):
        self.market_indicators = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ"
        }

    def analyze_security(self, ticker):
        """Comprehensive security analysis with detailed data"""
        try:
            security = yf.Ticker(ticker)
            
            # Get detailed info
            info = security.info
            
            # Get various timeframe data
            data = {
                'today': security.history(period='1d', interval='5m'),
                'week': security.history(period='5d'),
                'month': security.history(period='1mo'),
                'year': security.history(period='1y')
            }
            
            # Get key statistics
            stats = {
                'Market Cap': info.get('marketCap'),
                'PE Ratio': info.get('trailingPE'),
                'EPS': info.get('trailingEps'),
                'Dividend Yield': info.get('dividendYield'),
                '52 Week High': info.get('fiftyTwoWeekHigh'),
                '52 Week Low': info.get('fiftyTwoWeekLow'),
                'Average Volume': info.get('averageVolume'),
                'Beta': info.get('beta')
            }

            return {
                'data': data,
                'info': info,
                'stats': stats,
                'market_context': self._get_market_context()
            }

        except Exception as e:
            print(f"Error in security analysis: {str(e)}")
            return None

    def analyze_news_impact(self, news_items):
        """Analyze news impact and sentiment"""
        try:
            if not news_items:
                return {
                    'sentiments': [],
                    'topics': {
                        'earnings': 0,
                        'market': 0,
                        'company': 0,
                        'technology': 0,
                        'regulatory': 0
                    },
                    'average_sentiment': 0
                }

            analysis = {
                'sentiments': [],
                'topics': {
                    'earnings': 0,
                    'market': 0,
                    'company': 0,
                    'technology': 0,
                    'regulatory': 0
                }
            }

            # Keywords for topic classification
            topic_keywords = {
                'earnings': ['earnings', 'revenue', 'profit', 'loss', 'quarter', 'financial'],
                'market': ['market', 'trading', 'stock', 'shares', 'investors'],
                'company': ['announces', 'launch', 'releases', 'introduces', 'company'],
                'technology': ['tech', 'technology', 'innovation', 'product', 'development'],
                'regulatory': ['sec', 'regulation', 'lawsuit', 'legal', 'compliance']
            }

            total_sentiment = 0
            for item in news_items:
                # Sentiment analysis
                if 'title' in item:
                    blob = TextBlob(item['title'])
                    sentiment = blob.sentiment.polarity
                    
                    # Topic classification
                    title_lower = item['title'].lower()
                    for topic, keywords in topic_keywords.items():
                        if any(keyword in title_lower for keyword in keywords):
                            analysis['topics'][topic] += 1

                    # Add sentiment data
                    analysis['sentiments'].append({
                        'title': item['title'],
                        'sentiment': sentiment,
                        'source': item.get('source', 'Unknown'),
                        'url': item.get('url', ''),
                        'timestamp': item.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    })
                    total_sentiment += sentiment

            # Calculate average sentiment
            analysis['average_sentiment'] = total_sentiment / len(news_items) if news_items else 0

            return analysis

        except Exception as e:
            print(f"Error in news analysis: {str(e)}")
            return {
                'sentiments': [],
                'topics': {
                    'earnings': 0,
                    'market': 0,
                    'company': 0,
                    'technology': 0,
                    'regulatory': 0
                },
                'average_sentiment': 0
            }

    def generate_explanation(self, security_data, news_analysis, ticker):
        """Generate detailed market analysis explanation"""
        try:
            explanation = []
            
            # Price movement analysis
            if security_data and 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty:
                    current_price = today_data['Close'].iloc[-1]
                    open_price = today_data['Open'].iloc[0]
                    price_change = current_price - open_price
                    price_change_pct = (price_change / open_price) * 100
                    
                    direction = "up" if price_change > 0 else "down"
                    explanation.append(f"{ticker} is {direction} {abs(price_change_pct):.2f}% today.")

            # Market context
            if 'market_context' in security_data:
                context = security_data['market_context']
                if context:
                    explanation.append("\nMarket Context:")
                    for index, data in context.items():
                        if isinstance(data, dict) and 'change_pct' in data:
                            direction = "up" if data['change_pct'] > 0 else "down"
                            explanation.append(f"- {index} is {direction} {abs(data['change_pct']):.2f}%")

            return "\n".join(explanation)

        except Exception as e:
            print(f"Error generating explanation: {str(e)}")
            return "Unable to generate analysis explanation."

    def _get_market_context(self):
        """Get broader market context with detailed metrics"""
        context = {}
        
        for symbol, name in self.market_indicators.items():
            try:
                index = yf.Ticker(symbol)
                data = index.history(period='1d')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    open_price = data['Open'].iloc[0]
                    change_pct = ((current_price - open_price) / open_price) * 100
                    context[name] = {
                        'change_pct': change_pct,
                        'price': current_price,
                        'volume': data['Volume'].iloc[-1]
                    }
            except Exception as e:
                print(f"Error getting market data for {name}: {str(e)}")
                continue
                
        return context