import re
import logging
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("query_processor.log"), logging.StreamHandler()]
)
logger = logging.getLogger("QueryProcessor")

class QueryProcessor:
    def __init__(self, news_collector, market_analyzer):
        self.news_collector = news_collector
        self.market_analyzer = market_analyzer
        
        # Create data directory
        self.data_dir = "data/queries"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Keywords for identifying query intent
        self.intent_keywords = {
            'price_movement': [
                'why is', 'why did', 'why has', 'reason for', 'explain', 
                'what caused', 'what is causing', 'what made', 'movement', 
                'up today', 'down today', 'climbing', 'falling', 'dropped',
                'surged', 'plunged', 'rallied', 'declined', 'gained'
            ],
            'performance': [
                'how is', 'how did', 'performance', 'performing', 'trend',
                'doing', 'track record', 'history', 'historical', 'compare'
            ],
            'news_impact': [
                'news', 'headlines', 'articles', 'reported', 'announced',
                'press release', 'media', 'coverage', 'report', 'statement'
            ],
            'outlook': [
                'outlook', 'forecast', 'projection', 'future', 'expectation',
                'guidance', 'target', 'potential', 'prospect', 'predict'
            ],
            'recommendation': [
                'should i', 'is it good', 'is it bad', 'worth', 'recommend',
                'buy', 'sell', 'hold', 'invest', 'investment'
            ],
            'macro': [
                'macro', 'economy', 'economic', 'interest rate', 'inflation',
                'fed', 'federal reserve', 'global', 'market-wide', 'sector'
            ]
        }
        
        # Entity extraction patterns
        self.ticker_pattern = r'\b[A-Z]{1,5}\b'
        self.timeframe_patterns = {
            'today': [r'today', r'now', r'current'],
            'yesterday': [r'yesterday'],
            'this_week': [r'this week', r'past week', r'recent days'],
            'this_month': [r'this month', r'past month', r'recent weeks'],
            'this_quarter': [r'this quarter', r'past quarter', r'recent months'],
            'this_year': [r'this year', r'past year', r'ytd', r'year to date']
        }
        
        # Common words that should not be treated as tickers
        self.common_words = {
            'A', 'I', 'AM', 'PM', 'IS', 'ARE', 'BE', 'TO', 'IN', 'FOR', 'ON', 
            'AT', 'BY', 'THE', 'OF', 'AND', 'OR', 'WHY', 'WHAT', 'WHEN', 'WHERE',
            'WHO', 'HOW', 'WHICH', 'UP', 'DOWN', 'OVER', 'UNDER', 'ABOVE', 'BELOW',
            'MY', 'YOUR', 'OUR', 'THEIR', 'HIS', 'HER', 'ITS', 'THAT', 'THIS',
            'THESE', 'THOSE', 'FROM', 'WITH', 'WITHOUT', 'ABOUT', 'BETWEEN',
            'AMONG', 'THROUGH', 'DURING', 'BEFORE', 'AFTER', 'SINCE', 'UNTIL',
            'WHILE', 'SO', 'SUCH', 'RATHER', 'THAN', 'AS', 'JUST', 'VERY', 'TOO',
            'QUITE', 'MOST', 'LEAST', 'ALL', 'ANY', 'SOME', 'NO', 'NOT', 'ONLY',
            'BOTH', 'EITHER', 'NEITHER', 'EACH', 'EVERY', 'OTHER', 'ANOTHER',
            'MANY', 'MUCH', 'MORE', 'LESS', 'FEW', 'LITTLE', 'OWN', 'SAME',
            'SUCH', 'LIKE', 'ALSO', 'WELL', 'NOW', 'TODAY', 'YESTERDAY', 'TOMORROW',
            'WEEK', 'MONTH', 'YEAR', 'TIME', 'BACK', 'GO', 'COME', 'GET', 'MAKE'
        }
        
        # Lists of supported security types
        self.security_types = ['stock', 'etf', 'fund', 'mutual fund', 'index']
        
        # Common stock tickers for validation
        self.common_tickers = {
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'NVDA', 'JPM', 
            'JNJ', 'V', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'XOM', 'DIS', 'VZ', 'NFLX',
            'ADBE', 'CSCO', 'INTC', 'CRM', 'AMD', 'CMCSA', 'PEP', 'COST', 'ABT', 'TMO',
            'AVGO', 'ACN', 'NKE', 'DHR', 'NEE', 'TXN', 'WMT', 'LLY', 'PM', 'MDT',
            'UNP', 'QCOM', 'T', 'CVX', 'MRK', 'PYPL', 'BMY', 'SBUX', 'RTX', 'AMGN',
            'HON', 'UPS', 'IBM', 'LIN', 'BA', 'CAT', 'DE', 'MMM', 'GS', 'MCD',
            'QQQ', 'SPY', 'IWM', 'DIA', 'VOO', 'VTI', 'EEM', 'XLF', 'XLK', 'XLE'
        }
        
        # Cache for recent queries
        self.query_cache = {}
        self.cache_expiry = 300  # 5 minutes
    
    def process_query(self, query_text):
        """Process natural language query about market data"""
        try:
            # Check cache first
            cache_key = query_text.lower().strip()
            if cache_key in self.query_cache:
                cache_time, cached_response = self.query_cache[cache_key]
                if (datetime.now() - cache_time).total_seconds() < self.cache_expiry:
                    logger.info(f"Using cached response for query: {query_text}")
                    return cached_response
            
            logger.info(f"Processing query: {query_text}")
            
            # Extract query components
            query_info = self._extract_query_components(query_text)
            
            # Determine appropriate response based on intent
            response = self._generate_response(query_info)
            
            # Cache the response
            self.query_cache[cache_key] = (datetime.now(), response)
            
            # Save query for analysis
            self._save_query(query_text, query_info, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": "Sorry, I couldn't process that query. Please try asking in a different way.",
                "error": str(e)
            }
    
    def _extract_query_components(self, query_text):
        """Extract important components from the query text"""
        original_query = query_text
        query_text = query_text.lower()
        
        # Initialize components dictionary
        components = {
            'original_query': original_query,
            'intent': None,
            'tickers': [],
            'timeframe': 'today',  # Default timeframe
            'security_type': None,
            'direction': None,
            'specific_factors': []
        }
        
        # Determine query intent
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in query_text for keyword in keywords):
                components['intent'] = intent
                break
        
        # If no intent found, default to price movement
        if not components['intent']:
            components['intent'] = 'price_movement'
        
        # Extract tickers using common patterns in financial queries
        candidate_tickers = []
        
        # Pattern 1: "why is {TICKER} up/down today"
        pattern1 = re.search(r'(?:why|what|how) (?:is|are|did|does) ([A-Za-z]{1,5}) (?:up|down|going|moving|doing|performing)', query_text, re.IGNORECASE)
        if pattern1:
            ticker = pattern1.group(1).upper()
            if ticker not in self.common_words:
                candidate_tickers.append(ticker)
        
        # Pattern 2: "explain {TICKER} movement"
        pattern2 = re.search(r'(?:explain|about|analyze|check) ([A-Za-z]{1,5})(?:\s|$)', query_text, re.IGNORECASE)
        if pattern2:
            ticker = pattern2.group(1).upper()
            if ticker not in self.common_words:
                candidate_tickers.append(ticker)
        
        # Pattern 3: "what happened to {TICKER}"
        pattern3 = re.search(r'(?:what|explain) (?:happened|occurring|going on|news) (?:to|with|for|about) ([A-Za-z]{1,5})', query_text, re.IGNORECASE)
        if pattern3:
            ticker = pattern3.group(1).upper()
            if ticker not in self.common_words:
                candidate_tickers.append(ticker)
        
        # Extract all potential ticker symbols (1-5 uppercase letters)
        all_tickers = re.findall(self.ticker_pattern, original_query)
        
        # Filter out common words and add valid tickers
        for ticker in all_tickers:
            if ticker not in self.common_words and ticker not in candidate_tickers:
                candidate_tickers.append(ticker)
        
        # Prioritize well-known tickers if found
        prioritized_tickers = []
        for ticker in candidate_tickers:
            if ticker in self.common_tickers:
                prioritized_tickers.append(ticker)
        
        # If we found common tickers, use those
        if prioritized_tickers:
            components['tickers'] = prioritized_tickers
        # Otherwise use the candidates if we have any
        elif candidate_tickers:
            components['tickers'] = candidate_tickers
        
        # Extract timeframe
        for timeframe, patterns in self.timeframe_patterns.items():
            if any(re.search(pattern, query_text) for pattern in patterns):
                components['timeframe'] = timeframe
                break
        
        # Extract security type
        for security_type in self.security_types:
            if security_type in query_text:
                components['security_type'] = security_type
                break
        
        # Determine direction (up or down)
        if any(term in query_text for term in ['up', 'rise', 'rising', 'gain', 'grew', 'higher', 'increased', 'positive']):
            components['direction'] = 'up'
        elif any(term in query_text for term in ['down', 'fall', 'falling', 'drop', 'decline', 'lower', 'decreased', 'negative']):
            components['direction'] = 'down'
        
        # Extract specific factors of interest
        factor_keywords = {
            'earnings': ['earnings', 'revenue', 'profit', 'financial results'],
            'analyst': ['analyst', 'rating', 'upgrade', 'downgrade', 'target price'],
            'merger': ['merger', 'acquisition', 'takeover', 'buyout'],
            'product': ['product', 'launch', 'release', 'announcement'],
            'legal': ['lawsuit', 'legal', 'litigation', 'settlement'],
            'management': ['ceo', 'executive', 'management', 'leadership']
        }
        
        for factor, keywords in factor_keywords.items():
            if any(keyword in query_text for keyword in keywords):
                components['specific_factors'].append(factor)
        
        # Log the extracted components
        logger.info(f"Extracted query components: {components}")
        
        return components
    
    def _generate_response(self, query_info):
        """Generate an appropriate response based on query components"""
        # Initialize response
        response = {
            'success': True,
            'query_info': query_info,
            'answer': None,
            'security_data': {},
            'news_data': {},
            'explanation': None
        }
        
        # Handle case where no ticker is specified
        if not query_info['tickers']:
            response['success'] = False
            response['message'] = "I couldn't identify a specific stock, ETF, or fund in your query. Please specify a ticker symbol."
            return response
        
        # Process each ticker
        for ticker in query_info['tickers']:
            try:
                # Fetch security data
                security_data = self.market_analyzer.analyze_security(ticker)
                
                # Fetch news data
                news_items = self.news_collector.scrape_all_sources(ticker)
                news_analysis = self.market_analyzer.analyze_news_impact(news_items)
                
                # Generate explanation based on intent
                explanation = self._generate_explanation(query_info, security_data, news_analysis, ticker)
                
                # Store data in response
                response['security_data'][ticker] = security_data
                response['news_data'][ticker] = news_analysis
                
                # If this is the first/main ticker, set it as the primary explanation
                if not response['explanation']:
                    response['explanation'] = explanation
                    response['answer'] = self._generate_answer(query_info, security_data, news_analysis, ticker)
                
            except Exception as e:
                logger.error(f"Error generating response for {ticker}: {str(e)}")
                response['security_data'][ticker] = {"error": str(e)}
        
        return response
    
    def _generate_explanation(self, query_info, security_data, news_analysis, ticker):
        """Generate an explanation based on query intent"""
        intent = query_info['intent']
        
        if intent == 'price_movement':
            return self.market_analyzer.generate_explanation(security_data, news_analysis, ticker)
            
        elif intent == 'performance':
            return self._generate_performance_explanation(security_data, ticker, query_info['timeframe'])
            
        elif intent == 'news_impact':
            return self._generate_news_impact_explanation(news_analysis, ticker)
            
        elif intent == 'outlook':
            return self._generate_outlook_explanation(security_data, news_analysis, ticker)
            
        elif intent == 'recommendation':
            return "I don't provide investment recommendations. Please consult with a financial advisor for personalized advice."
            
        elif intent == 'macro':
            return self._generate_macro_explanation(security_data, news_analysis, ticker)
            
        else:
            return f"I couldn't generate a specific explanation for your query about {ticker}."
    
    def _generate_answer(self, query_info, security_data, news_analysis, ticker):
        """Generate a concise answer to the query"""
        intent = query_info['intent']
        
        # For price movement queries
        if intent == 'price_movement':
            return self._generate_price_movement_answer(security_data, news_analysis, ticker, query_info)
            
        # For performance queries
        elif intent == 'performance':
            return self._generate_performance_answer(security_data, ticker, query_info['timeframe'])
            
        # For news impact queries
        elif intent == 'news_impact':
            return self._generate_news_impact_answer(news_analysis, ticker)
            
        # For other queries, use the explanation
        else:
            explanation = self._generate_explanation(query_info, security_data, news_analysis, ticker)
            return explanation.split("\n\n")[0] if explanation else f"I couldn't find specific information for {ticker}."
    
    def _generate_price_movement_answer(self, security_data, news_analysis, ticker, query_info):
        """Generate a concise answer about price movement"""
        try:
            if not security_data or 'data' not in security_data or 'today' not in security_data['data']:
                return f"I couldn't retrieve current price data for {ticker}."
                
            # Get price movement
            today_data = security_data['data']['today']
            if today_data.empty:
                return f"I couldn't retrieve current price data for {ticker}."
                
            current_price = today_data['Close'].iloc[-1]
            open_price = today_data['Open'].iloc[0]
            price_change = current_price - open_price
            price_change_pct = (price_change / open_price) * 100
            
            direction = "up" if price_change > 0 else "down"
            
            # If user asked about specific direction, check if it matches
            if query_info['direction'] and query_info['direction'] != direction:
                return f"{ticker} is actually {direction} {abs(price_change_pct):.2f}% today, not {query_info['direction']}."
            
            # Get top factors from news
            top_factors = []
            if news_analysis and 'topics' in news_analysis:
                top_factors = sorted(news_analysis['topics'].items(), key=lambda x: x[1], reverse=True)[:2]
                top_factors = [factor.replace('_', ' ') for factor, count in top_factors if count > 0]
            
            # Get market context
            market_context = ""
            if 'market_context' in security_data:
                context = security_data['market_context']
                market_trends = []
                for name, data in context.items():
                    if isinstance(data, dict) and 'change_pct' in data:
                        direction_word = "up" if data['change_pct'] > 0 else "down"
                        market_trends.append(f"{name} is {direction_word} {abs(data['change_pct']):.2f}%")
                
                if market_trends:
                    market_context = f" The broader market trends show: {'; '.join(market_trends[:2])}."
            
            # Construct answer
            answer = f"{ticker} is {direction} {abs(price_change_pct):.2f}% today, trading at ${current_price:.2f}."
            
            # Add factors if available
            if top_factors:
                answer += f" Key factors include {' and '.join(top_factors)}."
            
            # Add market context
            answer += market_context
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating price movement answer: {str(e)}")
            return f"I couldn't analyze the price movement for {ticker}."
    
    def _generate_performance_explanation(self, security_data, ticker, timeframe):
        """Generate explanation about performance over a timeframe"""
        try:
            if not security_data or 'data' not in security_data:
                return f"I couldn't retrieve performance data for {ticker}."
            
            # Map timeframe to data key
            timeframe_to_data = {
                'today': 'today',
                'yesterday': 'today',  # We'll handle this specially
                'this_week': 'week',
                'this_month': 'month',
                'this_quarter': 'month',  # Use monthly data
                'this_year': 'year'
            }
            
            data_key = timeframe_to_data.get(timeframe, 'today')
            
            if data_key not in security_data['data'] or security_data['data'][data_key].empty:
                return f"I couldn't retrieve {timeframe} performance data for {ticker}."
            
            data = security_data['data'][data_key]
            
            # Get performance metrics
            if data_key == 'today':
                start_price = data['Open'].iloc[0]
                end_price = data['Close'].iloc[-1]
            else:
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Calculate volume metrics
            if 'Volume' in data.columns:
                avg_volume = data['Volume'].mean()
                max_volume = data['Volume'].max()
                volume_change = ((data['Volume'].iloc[-1] - avg_volume) / avg_volume) * 100
            else:
                avg_volume = None
                max_volume = None
                volume_change = None
            
            # Format the timeframe for display
            display_timeframe = {
                'today': 'today',
                'yesterday': 'yesterday',
                'this_week': 'this week',
                'this_month': 'this month',
                'this_quarter': 'this quarter',
                'this_year': 'this year'
            }.get(timeframe, timeframe)
            
            # Get volatility (using standard deviation of daily returns)
            if len(data) > 1:
                returns = data['Close'].pct_change().dropna()
                volatility = returns.std() * 100  # Convert to percentage
            else:
                volatility = None
            
            # Build explanation
            direction = "increased" if price_change > 0 else "decreased"
            result = f"{ticker} has {direction} by {abs(price_change_pct):.2f}% {display_timeframe}, "
            result += f"moving from ${start_price:.2f} to ${end_price:.2f}.\n\n"
            
            # Add volatility if available
            if volatility is not None:
                volatility_level = "high" if volatility > 2 else "moderate" if volatility > 1 else "low"
                result += f"Volatility has been {volatility_level} at {volatility:.2f}%.\n\n"
            
            # Add volume if available
            if avg_volume is not None:
                result += f"Average trading volume has been {avg_volume:,.0f} shares"
                if volume_change is not None:
                    volume_direction = "up" if volume_change > 0 else "down"
                    result += f", with recent volume {volume_direction} {abs(volume_change):.1f}% compared to average."
                result += "\n\n"
            
            # Add comparison to market
            if 'market_context' in security_data:
                context = security_data['market_context']
                market_text = []
                for index_name, index_data in context.items():
                    if isinstance(index_data, dict) and 'change_pct' in index_data:
                        change_pct = index_data['change_pct']
                        direction = "up" if change_pct > 0 else "down"
                        market_text.append(f"{index_name} is {direction} {abs(change_pct):.2f}%")
                
                if market_text:
                    result += f"For market context: {'; '.join(market_text)}.\n\n"
            
            # Add sector comparison
            if 'sector_context' in security_data:
                sector_context = security_data['sector_context']
                sector = security_data.get('info', {}).get('sector', None)
                if sector and sector in sector_context:
                    sector_perf = sector_context[sector]
                    direction = "up" if sector_perf > 0 else "down"
                    result += f"The {sector} sector is {direction} {abs(sector_perf):.2f}% {display_timeframe}."
                    
                    # Compare with stock performance
                    if (price_change_pct > 0 and sector_perf > 0) or (price_change_pct < 0 and sector_perf < 0):
                        relative = "outperforming" if abs(price_change_pct) > abs(sector_perf) else "underperforming"
                        result += f" {ticker} is {relative} its sector."
                    else:
                        result += f" {ticker} is moving contrary to its sector."
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating performance explanation: {str(e)}")
            return f"I couldn't analyze the performance for {ticker}."
    
    def _generate_performance_answer(self, security_data, ticker, timeframe):
        """Generate a concise answer about performance"""
        try:
            # Map timeframe to data key
            timeframe_to_data = {
                'today': 'today',
                'yesterday': 'today',  # We'll handle this specially
                'this_week': 'week',
                'this_month': 'month',
                'this_quarter': 'month',
                'this_year': 'year'
            }
            
            data_key = timeframe_to_data.get(timeframe, 'today')
            
            if not security_data or 'data' not in security_data or data_key not in security_data['data']:
                return f"I couldn't retrieve performance data for {ticker}."
                
            data = security_data['data'][data_key]
            if data.empty:
                return f"I couldn't retrieve performance data for {ticker}."
            
            # Get performance metrics
            if data_key == 'today':
                start_price = data['Open'].iloc[0]
                end_price = data['Close'].iloc[-1]
            else:
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                
            price_change = end_price - start_price
            price_change_pct = (price_change / start_price) * 100
            
            # Format the timeframe for display
            display_timeframe = {
                'today': 'today',
                'yesterday': 'yesterday',
                'this_week': 'this week',
                'this_month': 'this month',
                'this_quarter': 'this quarter',
                'this_year': 'this year'
            }.get(timeframe, timeframe)
            
            # Get sector performance
            sector_comparison = ""
            if 'sector_context' in security_data:
                sector_context = security_data['sector_context']
                sector = security_data.get('info', {}).get('sector', None)
                if sector and sector in sector_context:
                    sector_perf = sector_context[sector]
                    relative = "outperforming" if price_change_pct > sector_perf else "underperforming"
                    sector_comparison = f" It is {relative} the {sector} sector which is {sector_perf:+.2f}%."
            
            # Build answer
            direction = "up" if price_change > 0 else "down"
            answer = f"{ticker} is {direction} {abs(price_change_pct):.2f}% {display_timeframe}, currently at ${end_price:.2f}."
            
            if sector_comparison:
                answer += sector_comparison
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating performance answer: {str(e)}")
            return f"I couldn't analyze the performance for {ticker}."
    
    def _generate_news_impact_explanation(self, news_analysis, ticker):
        """Generate explanation about news impact"""
        try:
            if not news_analysis or 'sentiments' not in news_analysis or not news_analysis['sentiments']:
                return f"I couldn't find any recent news articles about {ticker}."
            
            sentiments = news_analysis['sentiments']
            avg_sentiment = news_analysis['average_sentiment']
            sentiment_desc = "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"
            
            # Build explanation
            result = f"I found {len(sentiments)} recent news articles about {ticker}. "
            result += f"The overall sentiment is {sentiment_desc} (score: {avg_sentiment:.2f}).\n\n"
            
            # Add source distribution
            if 'sources' in news_analysis:
                sources = news_analysis['sources']
                source_text = []
                for source, count in sources.items():
                    source_text.append(f"{source}: {count} articles")
                
                if source_text:
                    result += f"Sources: {', '.join(source_text)}.\n\n"
            
            # Add topic distribution
            if 'topics' in news_analysis:
                topics = news_analysis['topics']
                topic_text = []
                for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        topic_text.append(f"{topic.replace('_', ' ').title()}: {count} mentions")
                
                if topic_text:
                    result += f"Key topics in the news: {', '.join(topic_text[:5])}.\n\n"
            
            # Add most significant news (highest absolute sentiment)
            result += "Most significant recent news:\n"
            
            # Sort by absolute sentiment value (significance)
            significant_news = sorted(sentiments, key=lambda x: abs(x['sentiment']), reverse=True)[:5]
            
            for i, item in enumerate(significant_news, 1):
                sentiment_word = "positive" if item['sentiment'] > 0.2 else "negative" if item['sentiment'] < -0.2 else "neutral"
                result += f"{i}. \"{item['title']}\" ({item['source']}, {sentiment_word} {item['sentiment']:.2f})\n"
                
                # Add the URL
                if 'url' in item and item['url']:
                    result += f"   Source: {item['url']}\n"
                
                # Add the timestamp if available
                if 'timestamp' in item and item['timestamp']:
                    result += f"   Published: {item['timestamp']}\n"
                
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating news impact explanation: {str(e)}")
            return f"I couldn't analyze the news impact for {ticker}."
    
    def _generate_news_impact_answer(self, news_analysis, ticker):
        """Generate a concise answer about news impact"""
        try:
            if not news_analysis or 'sentiments' not in news_analysis or not news_analysis['sentiments']:
                return f"I couldn't find any recent news articles about {ticker}."
            
            sentiments = news_analysis['sentiments']
            avg_sentiment = news_analysis['average_sentiment']
            sentiment_desc = "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"
            
            # Get top topics
            top_topics = []
            if 'topics' in news_analysis:
                topics = news_analysis['topics']
                top_topics = [topic.replace('_', ' ') for topic, count in 
                            sorted(topics.items(), key=lambda x: x[1], reverse=True)[:2] 
                            if count > 0]
            
            # Get most significant news
            top_headline = ""
            if sentiments:
                significant_news = sorted(sentiments, key=lambda x: abs(x['sentiment']), reverse=True)[0]
                top_headline = significant_news['title']
            
            # Build answer
            answer = f"Recent news sentiment for {ticker} is {sentiment_desc} based on {len(sentiments)} articles."
            
            if top_topics:
                answer += f" Key topics include {' and '.join(top_topics)}."
            
            if top_headline:
                answer += f" Most significant headline: \"{top_headline}\""
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating news impact answer: {str(e)}")
            return f"I couldn't analyze the news impact for {ticker}."
    
    def _generate_outlook_explanation(self, security_data, news_analysis, ticker):
        """Generate explanation about future outlook"""
        try:
            company_info = security_data.get('info', {})
            
            # Extract analyst recommendations
            target_price = company_info.get('targetMeanPrice')
            recommendation = company_info.get('recommendationMean')
            
            # Map recommendation to text
            recommendation_text = "Unknown"
            if recommendation is not None:
                if recommendation < 1.5:
                    recommendation_text = "Strong Buy"
                elif recommendation < 2.5:
                    recommendation_text = "Buy"
                elif recommendation < 3.5:
                    recommendation_text = "Hold"
                elif recommendation < 4.5:
                    recommendation_text = "Sell"
                else:
                    recommendation_text = "Strong Sell"
            
            # Get current price
            current_price = None
            if 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty:
                    current_price = today_data['Close'].iloc[-1]
            
            # Calculate potential upside/downside
            potential = None
            if target_price is not None and current_price is not None:
                potential = ((target_price - current_price) / current_price) * 100
            
            # Extract outlook-related news
            outlook_news = []
            if news_analysis and 'sentiments' in news_analysis:
                for item in news_analysis['sentiments']:
                    # Simple keyword matching for outlook-related news
                    title = item['title'].lower()
                    if any(word in title for word in ['outlook', 'forecast', 'guidance', 'future', 'expect']):
                        outlook_news.append(item)
            
            # Build explanation
            result = f"Future Outlook for {ticker}:\n\n"
            
            if target_price is not None:
                result += f"Analyst Target Price: ${target_price:.2f}\n"
                
                if potential is not None:
                    direction = "upside" if potential > 0 else "downside"
                    result += f"Potential {direction}: {abs(potential):.2f}%\n"
            
            if recommendation is not None:
                result += f"Analyst Consensus: {recommendation_text} ({recommendation:.2f})\n\n"
            
            # Add news related to outlook
            if outlook_news:
                result += "Recent news related to future outlook:\n"
                for i, item in enumerate(outlook_news[:3], 1):
                    sentiment_word = "positive" if item['sentiment'] > 0.2 else "negative" if item['sentiment'] < -0.2 else "neutral"
                    result += f"{i}. \"{item['title']}\" ({item['source']}, {sentiment_word})\n"
                result += "\n"
            
            # Add general disclaimer
            result += "Note: This information is based on current market data and recent news. Future performance may vary significantly."
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating outlook explanation: {str(e)}")
            return f"I couldn't analyze the future outlook for {ticker}."
    
    def _generate_macro_explanation(self, security_data, news_analysis, ticker):
        """Generate explanation about macro factors"""
        try:
            # Get sector and industry information
            sector = security_data.get('info', {}).get('sector', 'Unknown')
            industry = security_data.get('info', {}).get('industry', 'Unknown')
            
            # Get market context
            market_context = security_data.get('market_context', {})
            
            # Get macro-related news
            macro_news = []
            if news_analysis and 'sentiments' in news_analysis:
                for item in news_analysis['sentiments']:
                    # Check if topics contain macro-related topics
                    if 'topics' in item and any(topic in ['economic_indicators', 'market_trend', 'international'] 
                                                 for topic in item.get('topics', [])):
                        macro_news.append(item)
                    
                    # Also check title keywords
                    title = item['title'].lower()
                    if any(word in title for word in ['fed', 'interest', 'inflation', 'gdp', 'economy', 'economic',
                                                   'market', 'global', 'trade', 'tariff', 'policy']):
                        if item not in macro_news:  # Avoid duplicates
                            macro_news.append(item)
            
            # Build explanation
            result = f"Macro Factors Affecting {ticker} ({sector}, {industry}):\n\n"
            
            # Add market performance
            if market_context:
                result += "Market Performance:\n"
                for index_name, index_data in market_context.items():
                    if isinstance(index_data, dict) and 'change_pct' in index_data:
                        direction = "up" if index_data['change_pct'] > 0 else "down"
                        result += f"- {index_name}: {direction} {abs(index_data['change_pct']):.2f}%\n"
                result += "\n"
            
            # Add sector performance
            if 'sector_context' in security_data:
                sector_context = security_data['sector_context']
                result += "Sector Performance:\n"
                for sector_name, performance in sector_context.items():
                    if isinstance(performance, (int, float)):
                        direction = "up" if performance > 0 else "down"
                        result += f"- {sector_name}: {direction} {abs(performance):.2f}%\n"
                result += "\n"
            
            # Add macro news
            if macro_news:
                result += "Recent Macro News:\n"
                for i, item in enumerate(macro_news[:5], 1):
                    sentiment_word = "positive" if item['sentiment'] > 0.2 else "negative" if item['sentiment'] < -0.2 else "neutral"
                    result += f"{i}. \"{item['title']}\" ({item['source']}, {sentiment_word})\n"
                result += "\n"
            
            # Add interpretation
            result += "Interpretation:\n"
            
            # Check market correlation
            if 'data' in security_data and 'today' in security_data['data'] and market_context:
                today_data = security_data['data']['today']
                if not today_data.empty:
                    current_price = today_data['Close'].iloc[-1]
                    open_price = today_data['Open'].iloc[0]
                    price_change_pct = ((current_price - open_price) / open_price) * 100
                    
                    # Calculate market average
                    market_changes = [data.get('change_pct', 0) for data in market_context.values() 
                                    if isinstance(data, dict) and 'change_pct' in data]
                    if market_changes:
                        market_avg = sum(market_changes) / len(market_changes)
                        
                        # Determine correlation
                        if (price_change_pct > 0 and market_avg > 0) or (price_change_pct < 0 and market_avg < 0):
                            correlation = "positively correlated with"
                        else:
                            correlation = "moving contrary to"
                        
                        result += f"- {ticker} is currently {correlation} the broader market.\n"
            
            # Check sector correlation
            if 'sector_context' in security_data:
                sector_context = security_data['sector_context']
                sector = security_data.get('info', {}).get('sector', None)
                if sector and sector in sector_context and 'data' in security_data and 'today' in security_data['data']:
                    today_data = security_data['data']['today']
                    if not today_data.empty:
                        current_price = today_data['Close'].iloc[-1]
                        open_price = today_data['Open'].iloc[0]
                        price_change_pct = ((current_price - open_price) / open_price) * 100
                        
                        sector_perf = sector_context[sector]
                        if (price_change_pct > 0 and sector_perf > 0) or (price_change_pct < 0 and sector_perf < 0):
                            correlation = "following the trend of"
                        else:
                            correlation = "moving independently from"
                        
                        result += f"- The stock is {correlation} its sector ({sector}).\n"
            
            # Add company specifics
            beta = security_data.get('info', {}).get('beta')
            if beta is not None:
                sensitivity = "highly sensitive" if beta > 1.5 else "moderately sensitive" if beta > 1 else "less sensitive"
                result += f"- With a beta of {beta:.2f}, {ticker} is {sensitivity} to market movements.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating macro explanation: {str(e)}")
            return f"I couldn't analyze the macro factors for {ticker}."
    
    def _save_query(self, query_text, query_info, response):
        """Save query and response for analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Prepare data to save
            data = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'query': query_text,
                'query_info': query_info,
                'response': {
                    'success': response.get('success', False),
                    'message': response.get('message', ''),
                    'answer': response.get('answer', '')
                }
            }
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Query saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving query: {str(e)}")