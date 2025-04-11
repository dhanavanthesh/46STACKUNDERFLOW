import yfinance as yf
from textblob import TextBlob
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import json
import os
import logging
import re
from collections import Counter, defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("market_analyzer.log"), logging.StreamHandler()]
)
logger = logging.getLogger("MarketAnalyzer")

class MarketAnalyzer:
    def __init__(self):
        self.market_indicators = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^RUT": "Russell 2000",
            "^VIX": "VIX"
        }
        
        self.sector_etfs = {
            "XLK": "Technology",
            "XLF": "Financials",
            "XLE": "Energy",
            "XLV": "Healthcare",
            "XLI": "Industrials",
            "XLP": "Consumer Staples",
            "XLY": "Consumer Discretionary",
            "XLB": "Materials",
            "XLU": "Utilities",
            "XLRE": "Real Estate"
        }
        
        # Cache for financial data to minimize API calls
        self.data_cache = {}
        self.cache_expiry = 3600  # 1 hour in seconds
        
        # Create data directories
        self.data_dir = "data/analysis"
        os.makedirs(self.data_dir, exist_ok=True)

    def analyze_security(self, ticker):
        """Comprehensive security analysis with detailed data"""
        try:
            cache_key = f"{ticker}_security_{datetime.now().strftime('%Y%m%d_%H')}"
            
            # Check if we have cached results
            if cache_key in self.data_cache:
                cache_time, cached_data = self.data_cache[cache_key]
                if (datetime.now() - cache_time).total_seconds() < self.cache_expiry:
                    logger.info(f"Using cached security data for {ticker}")
                    return cached_data
            
            logger.info(f"Analyzing security data for {ticker}")
            
            # Get ticker object
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
            
            # Get company-specific metrics
            company_metrics = self._extract_company_metrics(info, ticker)
            
            # Get sector and industry context
            sector_context = self._get_sector_context(info.get('sector'))
            
            # Get market context
            market_context = self._get_market_context()
            
            # Get price patterns and technical indicators
            technical_analysis = self._get_technical_analysis(data)
            
            # Prepare result
            result = {
                'data': data,
                'info': info,
                'stats': stats,
                'company_metrics': company_metrics,
                'sector_context': sector_context,
                'market_context': market_context,
                'technical_analysis': technical_analysis
            }
            
            # Cache the results
            self.data_cache[cache_key] = (datetime.now(), result)
            
            return result

        except Exception as e:
            logger.error(f"Error in security analysis for {ticker}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def analyze_news_impact(self, news_items):
        """Analyze news impact and sentiment with better categorization"""
        try:
            if not news_items:
                logger.warning("No news items to analyze")
                return self._get_empty_news_analysis()
            
            logger.info(f"Analyzing impact of {len(news_items)} news items")
            
            analysis = {
                'sentiments': [],
                'topics': defaultdict(int),
                'entities': defaultdict(set),
                'keywords': [],
                'average_sentiment': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'sources': defaultdict(int)
            }

            # Keywords for topic classification
            topic_keywords = {
                'earnings': ['earnings', 'revenue', 'profit', 'loss', 'quarter', 'financial', 'eps', 'income', 'guidance'],
                'merger_acquisition': ['merger', 'acquisition', 'takeover', 'deal', 'buyout', 'purchase', 'acquire'],
                'product_launch': ['launch', 'release', 'new product', 'update', 'unveil', 'introduce', 'announcement'],
                'leadership': ['ceo', 'executive', 'appoint', 'resign', 'management', 'leader', 'director', 'board'],
                'legal_regulatory': ['lawsuit', 'court', 'legal', 'sue', 'settlement', 'regulation', 'compliance', 'fine'],
                'market_trend': ['market', 'index', 'dow', 'nasdaq', 's&p', 'bull', 'bear', 'trend', 'correction'],
                'technology_innovation': ['tech', 'technology', 'innovation', 'patent', 'ai', 'artificial intelligence', 'research'],
                'economic_indicators': ['fed', 'inflation', 'interest rate', 'economy', 'growth', 'recession', 'gdp'],
                'analyst_rating': ['analyst', 'upgrade', 'downgrade', 'rating', 'target', 'buy', 'sell', 'hold', 'overweight'],
                'competition': ['competitor', 'rivalry', 'market share', 'outperform', 'versus', 'competition'],
                'international': ['global', 'international', 'foreign', 'overseas', 'export', 'import', 'tariff', 'trade']
            }
            
            # Extract sentiment and topics
            total_sentiment = 0
            keyword_counter = Counter()
            
            for item in news_items:
                # Sentiment analysis
                if 'title' in item:
                    title = item['title']
                    summary = item.get('summary', '')
                    content = f"{title} {summary}"
                    
                    # Use TextBlob for sentiment analysis
                    blob = TextBlob(content)
                    sentiment_score = blob.sentiment.polarity
                    
                    # Categorize sentiment
                    sentiment_category = 'neutral'
                    if sentiment_score > 0.2:
                        sentiment_category = 'positive'
                        analysis['sentiment_distribution']['positive'] += 1
                    elif sentiment_score < -0.2:
                        sentiment_category = 'negative'
                        analysis['sentiment_distribution']['negative'] += 1
                    else:
                        analysis['sentiment_distribution']['neutral'] += 1
                    
                    # Extract keywords (basic implementation)
                    words = re.findall(r'\b[A-Za-z][A-Za-z\-]{2,}\b', content.lower())
                    filtered_words = [w for w in words if len(w) > 3 and w not in [
                        'this', 'that', 'these', 'those', 'there', 'their', 'they',
                        'what', 'when', 'where', 'which', 'while', 'with', 'would',
                        'about', 'above', 'after', 'again', 'against', 'could', 'should',
                        'from', 'have', 'having', 'here', 'more', 'once', 'only', 'same', 'some',
                        'such', 'than', 'then', 'through'
                    ]]
                    keyword_counter.update(filtered_words)
                    
                    # Topic classification
                    content_lower = content.lower()
                    detected_topics = []
                    for topic, keywords in topic_keywords.items():
                        if any(keyword in content_lower for keyword in keywords):
                            analysis['topics'][topic] += 1
                            detected_topics.append(topic)
                    
                    # Add sentiment data
                    sentiment_item = {
                        'title': title,
                        'sentiment': sentiment_score,
                        'sentiment_category': sentiment_category,
                        'source': item.get('source', 'Unknown'),
                        'url': item.get('url', ''),
                        'timestamp': item.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        'topics': detected_topics
                    }
                    
                    # Add entity data if available
                    if 'entities' in item:
                        sentiment_item['entities'] = item['entities']
                        # Collect unique entities
                        for ticker in item['entities'].get('tickers', []):
                            analysis['entities']['tickers'].add(ticker)
                        for company in item['entities'].get('companies', []):
                            analysis['entities']['companies'].add(company)
                        for person in item['entities'].get('people', []):
                            analysis['entities']['people'].add(person)
                        for topic in item['entities'].get('topics', []):
                            analysis['entities']['topics'].add(topic)
                    
                    # Count sources
                    analysis['sources'][item.get('source', 'Unknown')] += 1
                    
                    analysis['sentiments'].append(sentiment_item)
                    total_sentiment += sentiment_score

            # Calculate average sentiment
            analysis['average_sentiment'] = total_sentiment / len(news_items) if news_items else 0
            
            # Get top keywords
            analysis['keywords'] = [item for item, count in keyword_counter.most_common(20)]
            
            # Convert sets to lists for JSON serialization
            for entity_type in analysis['entities']:
                analysis['entities'][entity_type] = list(analysis['entities'][entity_type])
            
            return analysis

        except Exception as e:
            logger.error(f"Error in news analysis: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_empty_news_analysis()

    def _get_empty_news_analysis(self):
        """Return empty news analysis structure"""
        return {
            'sentiments': [],
            'topics': defaultdict(int),
            'entities': {'tickers': [], 'companies': [], 'people': [], 'topics': []},
            'keywords': [],
            'average_sentiment': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'sources': {}
        }

    def generate_explanation(self, security_data, news_analysis, ticker):
        """Generate detailed market analysis explanation"""
        try:
            if not security_data:
                return f"Unable to generate analysis for {ticker} due to missing market data."
                
            logger.info(f"Generating explanation for {ticker}")
            
            explanation_parts = []
            
            # 1. Price movement summary
            price_summary = self._generate_price_summary(security_data, ticker)
            if price_summary:
                explanation_parts.append(price_summary)
            
            # 2. News impact summary
            news_summary = self._generate_news_summary(news_analysis, ticker)
            if news_summary:
                explanation_parts.append(news_summary)
            
            # 3. Market context
            market_context = self._generate_market_context(security_data)
            if market_context:
                explanation_parts.append(market_context)
            
            # 4. Sector performance
            sector_context = self._generate_sector_summary(security_data)
            if sector_context:
                explanation_parts.append(sector_context)
            
            # 5. Technical indicators
            technical_summary = self._generate_technical_summary(security_data)
            if technical_summary:
                explanation_parts.append(technical_summary)
            
            # 6. Key takeaway
            key_takeaway = self._generate_key_takeaway(security_data, news_analysis, ticker)
            if key_takeaway:
                explanation_parts.append(key_takeaway)
            
            return "\n\n".join(explanation_parts)

        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Analysis for {ticker} is currently unavailable. Please try again later."

    def _generate_price_summary(self, security_data, ticker):
        """Generate price movement summary"""
        try:
            if not security_data or 'data' not in security_data or 'today' not in security_data['data']:
                return None
                
            today_data = security_data['data']['today']
            if today_data.empty:
                return None
                
            current_price = today_data['Close'].iloc[-1]
            open_price = today_data['Open'].iloc[0]
            price_change = current_price - open_price
            price_change_pct = (price_change / open_price) * 100
            
            day_high = today_data['High'].max()
            day_low = today_data['Low'].min()
            
            direction = "up" if price_change > 0 else "down"
            magnitude = "slightly" if abs(price_change_pct) < 1 else "significantly" if abs(price_change_pct) > 3 else "moderately"
            
            summary = f"{ticker} is {direction} {magnitude} by {abs(price_change_pct):.2f}% today, currently trading at ${current_price:.2f}."
            summary += f" The stock opened at ${open_price:.2f} and has ranged from ${day_low:.2f} to ${day_high:.2f} during the session."
            
            # Add volume information if available
            if 'Volume' in today_data.columns:
                current_volume = today_data['Volume'].sum()
                if 'stats' in security_data and 'Average Volume' in security_data['stats']:
                    avg_volume = security_data['stats']['Average Volume']
                    if avg_volume and avg_volume > 0:
                        volume_ratio = current_volume / avg_volume
                        volume_desc = "higher than" if volume_ratio > 1.2 else "lower than" if volume_ratio < 0.8 else "in line with"
                        summary += f" Trading volume is {volume_desc} average."
            
            return summary
        except Exception as e:
            logger.error(f"Error generating price summary: {str(e)}")
            return None

    def _generate_news_summary(self, news_analysis, ticker):
        """Generate news impact summary"""
        try:
            if not news_analysis or 'sentiments' not in news_analysis or not news_analysis['sentiments']:
                return f"No significant news for {ticker} was found."
                
            sentiments = news_analysis['sentiments']
            avg_sentiment = news_analysis['average_sentiment']
            sentiment_desc = "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"
            
            # Count news by source
            sources_count = len(news_analysis['sources'])
            
            # Get dominant topics
            topics = news_analysis['topics']
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:3]
            
            summary = f"Recent news sentiment for {ticker} is overall {sentiment_desc} with {len(sentiments)} articles from {sources_count} sources."
            
            if top_topics:
                topics_text = ", ".join([f"{topic.replace('_', ' ')}" for topic, count in top_topics if count > 0])
                if topics_text:
                    summary += f" Key topics include {topics_text}."
            
            # Get most significant news items (highest sentiment magnitude)
            significant_news = sorted(sentiments, key=lambda x: abs(x['sentiment']), reverse=True)[:2]
            if significant_news:
                summary += " Notable headlines:"
                for item in significant_news:
                    sentiment_word = "positive" if item['sentiment'] > 0.2 else "negative" if item['sentiment'] < -0.2 else "neutral"
                    summary += f"\n- \"{item['title']}\" ({item['source']}, {sentiment_word})"
            
            return summary
        except Exception as e:
            logger.error(f"Error generating news summary: {str(e)}")
            return None

    def _generate_market_context(self, security_data):
        """Generate market context summary"""
        try:
            if 'market_context' not in security_data or not security_data['market_context']:
                return None
                
            context = security_data['market_context']
            
            # Get major indices performance
            indices_perf = []
            for index_name, data in context.items():
                if isinstance(data, dict) and 'change_pct' in data:
                    direction = "up" if data['change_pct'] > 0 else "down"
                    indices_perf.append(f"{index_name} is {direction} {abs(data['change_pct']):.2f}%")
            
            if indices_perf:
                summary = "Market Context: " + ", ".join(indices_perf) + "."
                
                # Determine market sentiment
                up_count = sum(1 for name, data in context.items() 
                             if isinstance(data, dict) and 'change_pct' in data and data['change_pct'] > 0)
                down_count = sum(1 for name, data in context.items() 
                               if isinstance(data, dict) and 'change_pct' in data and data['change_pct'] < 0)
                
                if up_count > down_count:
                    summary += " The broader market is showing positive momentum today."
                elif down_count > up_count:
                    summary += " The broader market is trending lower today."
                else:
                    summary += " Market sentiment is mixed today."
                
                return summary
            return None
        except Exception as e:
            logger.error(f"Error generating market context: {str(e)}")
            return None

    def _generate_sector_summary(self, security_data):
        """Generate sector performance summary"""
        try:
            if 'sector_context' not in security_data or not security_data['sector_context']:
                return None
                
            sector_context = security_data['sector_context']
            sector = security_data.get('info', {}).get('sector', None)
            
            if sector and sector in sector_context:
                sector_perf = sector_context[sector]
                direction = "up" if sector_perf > 0 else "down"
                
                summary = f"Sector Performance: The {sector} sector is {direction} {abs(sector_perf):.2f}% today."
                
                # Compare with stock performance
                if 'data' in security_data and 'today' in security_data['data']:
                    today_data = security_data['data']['today']
                    if not today_data.empty:
                        current_price = today_data['Close'].iloc[-1]
                        open_price = today_data['Open'].iloc[0]
                        price_change_pct = ((current_price - open_price) / open_price) * 100
                        
                        if (price_change_pct > 0 and sector_perf > 0) or (price_change_pct < 0 and sector_perf < 0):
                            relative = "outperforming" if abs(price_change_pct) > abs(sector_perf) else "underperforming"
                            summary += f" The stock is {relative} its sector."
                        else:
                            summary += " The stock is moving contrary to its sector today."
                
                return summary
            return None
        except Exception as e:
            logger.error(f"Error generating sector summary: {str(e)}")
            return None

    def _generate_technical_summary(self, security_data):
        """Generate technical indicators summary"""
        try:
            if 'technical_analysis' not in security_data or not security_data['technical_analysis']:
                return None
                
            tech_analysis = security_data['technical_analysis']
            
            if tech_analysis.get('signals'):
                signals = tech_analysis['signals']
                buy_signals = sum(1 for signal, value in signals.items() if value == 'buy')
                sell_signals = sum(1 for signal, value in signals.items() if value == 'sell')
                neutral_signals = sum(1 for signal, value in signals.items() if value == 'neutral')
                
                if buy_signals > sell_signals and buy_signals > neutral_signals:
                    signal_summary = "bullish"
                elif sell_signals > buy_signals and sell_signals > neutral_signals:
                    signal_summary = "bearish"
                else:
                    signal_summary = "neutral"
                
                summary = f"Technical Analysis: Technical indicators are showing {signal_summary} signals."
                
                # Add key indicators
                key_indicators = []
                if 'rsi' in tech_analysis:
                    rsi = tech_analysis['rsi']
                    rsi_desc = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"
                    key_indicators.append(f"RSI is {rsi:.1f} ({rsi_desc})")
                
                if 'macd' in tech_analysis:
                    macd = tech_analysis['macd']
                    macd_desc = "bullish" if macd > 0 else "bearish"
                    key_indicators.append(f"MACD is {macd_desc}")
                
                if key_indicators:
                    summary += " " + ", ".join(key_indicators) + "."
                
                return summary
            return None
        except Exception as e:
            logger.error(f"Error generating technical summary: {str(e)}")
            return None

    def _generate_key_takeaway(self, security_data, news_analysis, ticker):
        """Generate key takeaway conclusion"""
        try:
            # Extract price movement
            price_change_pct = None
            if 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty:
                    current_price = today_data['Close'].iloc[-1]
                    open_price = today_data['Open'].iloc[0]
                    price_change_pct = ((current_price - open_price) / open_price) * 100
            
            # Extract news sentiment
            avg_sentiment = news_analysis.get('average_sentiment', 0)
            
            # Extract market trend
            market_trend = 0
            if 'market_context' in security_data:
                market_context = security_data['market_context']
                market_changes = [data.get('change_pct', 0) for data in market_context.values() 
                                if isinstance(data, dict) and 'change_pct' in data]
                if market_changes:
                    market_trend = sum(market_changes) / len(market_changes)
            
            # Extract sector trend
            sector_trend = 0
            if 'sector_context' in security_data:
                sector_context = security_data['sector_context']
                sector = security_data.get('info', {}).get('sector', None)
                if sector and sector in sector_context:
                    sector_trend = sector_context[sector]
            
            # Determine key factor
            key_factor = None
            factor_description = None
            
            # News is the key factor
            if abs(avg_sentiment) > 0.3 and ((price_change_pct > 0 and avg_sentiment > 0) or 
                                          (price_change_pct < 0 and avg_sentiment < 0)):
                key_factor = "news"
                sentiment_desc = "positive" if avg_sentiment > 0 else "negative"
                factor_description = f"recent {sentiment_desc} news"
                
                # Add specific news topics if available
                topics = news_analysis.get('topics', {})
                top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:1]
                if top_topics and top_topics[0][1] > 0:
                    factor_description += f" related to {top_topics[0][0].replace('_', ' ')}"
            
            # Market is the key factor
            elif abs(market_trend) > 1.0 and ((price_change_pct > 0 and market_trend > 0) or 
                                          (price_change_pct < 0 and market_trend < 0)):
                key_factor = "market"
                trend_desc = "positive" if market_trend > 0 else "negative"
                factor_description = f"overall {trend_desc} market movement"
            
            # Sector is the key factor
            elif abs(sector_trend) > 1.5 and ((price_change_pct > 0 and sector_trend > 0) or 
                                          (price_change_pct < 0 and sector_trend < 0)):
                key_factor = "sector"
                trend_desc = "strength" if sector_trend > 0 else "weakness"
                sector = security_data.get('info', {}).get('sector', "its sector")
                factor_description = f"{sector} sector {trend_desc}"
            
            # Company-specific is the key factor (default if no other factors identified)
            else:
                key_factor = "company"
                factor_description = "company-specific factors"
                
                # Check for earnings-related news
                if 'topics' in news_analysis and news_analysis['topics'].get('earnings', 0) > 0:
                    factor_description = "recent earnings or financial news"
            
            # Generate the takeaway
            if price_change_pct is not None and factor_description:
                direction = "gain" if price_change_pct > 0 else "decline"
                takeaway = f"Key Takeaway: The primary driver behind {ticker}'s {direction} today appears to be {factor_description}."
                
                # Add recommendation context
                if key_factor == "news" and abs(avg_sentiment) > 0.3:
                    takeaway += " Investors should monitor for additional news developments."
                elif key_factor == "market":
                    takeaway += " The stock is currently moving with the broader market trend."
                elif key_factor == "sector":
                    takeaway += f" Watch other stocks in the {security_data.get('info', {}).get('sector', 'same')} sector for similar patterns."
                
                return takeaway
            
            return None
        except Exception as e:
            logger.error(f"Error generating key takeaway: {str(e)}")
            return None

    def _get_market_context(self):
        """Get broader market context with detailed metrics"""
        context = {}
        
        for symbol, name in self.market_indicators.items():
            try:
                # Use cache if available
                cache_key = f"{symbol}_market_{datetime.now().strftime('%Y%m%d_%H')}"
                if cache_key in self.data_cache:
                    cache_time, cached_data = self.data_cache[cache_key]
                    if (datetime.now() - cache_time).total_seconds() < self.cache_expiry:
                        context[name] = cached_data
                        continue
                
                index = yf.Ticker(symbol)
                data = index.history(period='1d')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    open_price = data['Open'].iloc[0]
                    change_pct = ((current_price - open_price) / open_price) * 100
                    result = {
                        'change_pct': change_pct,
                        'price': current_price,
                        'volume': data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
                    }
                    context[name] = result
                    
                    # Cache the result
                    self.data_cache[cache_key] = (datetime.now(), result)
            except Exception as e:
                logger.error(f"Error getting market data for {name}: {str(e)}")
                continue
                
        return context

    def _get_sector_context(self, sector):
        """Get sector performance context"""
        if not sector:
            return {}
            
        sector_performance = {}
        
        # Try to map sector to ETF
        sector_mapping = {
            'Technology': 'XLK',
            'Financial': 'XLF',
            'Financials': 'XLF',
            'Energy': 'XLE',
            'Healthcare': 'XLV',
            'Health Care': 'XLV',
            'Industrial': 'XLI',
            'Industrials': 'XLI',
            'Consumer Staples': 'XLP',
            'Consumer Discretionary': 'XLY',
            'Materials': 'XLB',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Communication Services': 'XLC'
        }
        
        # Try to get the sector ETF performance
        try:
            if sector in sector_mapping:
                etf_ticker = sector_mapping[sector]
                
                # Use cache if available
                cache_key = f"{etf_ticker}_sector_{datetime.now().strftime('%Y%m%d_%H')}"
                if cache_key in self.data_cache:
                    cache_time, cached_data = self.data_cache[cache_key]
                    if (datetime.now() - cache_time).total_seconds() < self.cache_expiry:
                        sector_performance[sector] = cached_data
                        return sector_performance
                
                etf = yf.Ticker(etf_ticker)
                data = etf.history(period='1d')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    open_price = data['Open'].iloc[0]
                    change_pct = ((current_price - open_price) / open_price) * 100
                    sector_performance[sector] = change_pct
                    
                    # Cache the result
                    self.data_cache[cache_key] = (datetime.now(), change_pct)
        except Exception as e:
            logger.error(f"Error getting sector data for {sector}: {str(e)}")
        
        # Get all sector ETFs for context
        for etf_symbol, etf_sector in self.sector_etfs.items():
            if etf_sector != sector:  # Skip the main sector, we already have it
                try:
                    # Use cache if available
                    cache_key = f"{etf_symbol}_sector_{datetime.now().strftime('%Y%m%d_%H')}"
                    if cache_key in self.data_cache:
                        cache_time, cached_data = self.data_cache[cache_key]
                        if (datetime.now() - cache_time).total_seconds() < self.cache_expiry:
                            sector_performance[etf_sector] = cached_data
                            continue
                    
                    etf = yf.Ticker(etf_symbol)
                    data = etf.history(period='1d')
                    if not data.empty:
                        current_price = data['Close'].iloc[-1]
                        open_price = data['Open'].iloc[0]
                        change_pct = ((current_price - open_price) / open_price) * 100
                        sector_performance[etf_sector] = change_pct
                        
                        # Cache the result
                        self.data_cache[cache_key] = (datetime.now(), change_pct)
                except Exception as e:
                    logger.error(f"Error getting sector data for {etf_sector}: {str(e)}")
                    continue
        
        return sector_performance

    def _extract_company_metrics(self, info, ticker):
        """Extract company-specific metrics from ticker info"""
        metrics = {
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'country': info.get('country', 'Unknown'),
            'employees': info.get('fullTimeEmployees', None)
        }
        
        # Financial metrics
        metrics['financial'] = {
            'market_cap': info.get('marketCap', None),
            'revenue': info.get('totalRevenue', None),
            'profit_margin': info.get('profitMargins', None),
            'operating_margin': info.get('operatingMargins', None),
            'return_on_equity': info.get('returnOnEquity', None),
            'return_on_assets': info.get('returnOnAssets', None),
            'debt_to_equity': info.get('debtToEquity', None)
        }
        
        # Valuation metrics
        metrics['valuation'] = {
            'pe_ratio': info.get('trailingPE', None),
            'forward_pe': info.get('forwardPE', None),
            'price_to_sales': info.get('priceToSalesTrailing12Months', None),
            'price_to_book': info.get('priceToBook', None),
            'enterprise_to_revenue': info.get('enterpriseToRevenue', None),
            'enterprise_to_ebitda': info.get('enterpriseToEbitda', None)
        }
        
        return metrics

    def _get_technical_analysis(self, price_data):
        """Calculate basic technical indicators"""
        if not price_data or 'week' not in price_data or price_data['week'].empty:
            return {}
            
        # Use weekly data for technical analysis
        df = price_data['week'].copy()
        
        # Ensure we have enough data points
        if len(df) < 10:
            return {}
            
        analysis = {}
        
        # Calculate SMA (Simple Moving Average)
        try:
            df['SMA_5'] = df['Close'].rolling(window=5).mean()
            df['SMA_10'] = df['Close'].rolling(window=10).mean()
            
            last_close = df['Close'].iloc[-1]
            last_sma5 = df['SMA_5'].iloc[-1]
            last_sma10 = df['SMA_10'].iloc[-1]
            
            analysis['sma'] = {
                'sma5': last_sma5,
                'sma10': last_sma10,
                'sma5_signal': 'buy' if last_close > last_sma5 else 'sell',
                'sma10_signal': 'buy' if last_close > last_sma10 else 'sell',
                'crossover': 'bullish' if last_sma5 > last_sma10 else 'bearish'
            }
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
        
        # Calculate RSI (Relative Strength Index)
        try:
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            last_rsi = df['RSI'].iloc[-1]
            
            analysis['rsi'] = last_rsi
            analysis['rsi_signal'] = 'sell' if last_rsi > 70 else 'buy' if last_rsi < 30 else 'neutral'
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
        
        # Calculate MACD (Moving Average Convergence Divergence)
        try:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
            
            last_macd = df['MACD'].iloc[-1]
            last_signal = df['Signal_Line'].iloc[-1]
            last_hist = df['MACD_Histogram'].iloc[-1]
            
            analysis['macd'] = last_macd
            analysis['macd_signal'] = 'buy' if last_macd > last_signal else 'sell'
            analysis['macd_histogram'] = last_hist
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
        
        # Bollinger Bands
        try:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['Std_Dev'] = df['Close'].rolling(window=20).std()
            
            df['Upper_Band'] = df['SMA_20'] + (df['Std_Dev'] * 2)
            df['Lower_Band'] = df['SMA_20'] - (df['Std_Dev'] * 2)
            
            last_close = df['Close'].iloc[-1]
            last_upper = df['Upper_Band'].iloc[-1]
            last_lower = df['Lower_Band'].iloc[-1]
            
            analysis['bollinger'] = {
                'upper': last_upper,
                'middle': df['SMA_20'].iloc[-1],
                'lower': last_lower,
                'signal': 'sell' if last_close > last_upper else 'buy' if last_close < last_lower else 'neutral'
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
        
        # Aggregate signals
        analysis['signals'] = {
            'sma': analysis.get('sma', {}).get('sma5_signal', 'neutral'),
            'rsi': analysis.get('rsi_signal', 'neutral'),
            'macd': analysis.get('macd_signal', 'neutral'),
            'bollinger': analysis.get('bollinger', {}).get('signal', 'neutral')
        }
        
        return analysis