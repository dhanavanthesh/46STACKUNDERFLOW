import re
import logging
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("query_processor.log"), logging.StreamHandler()]
)
logger = logging.getLogger("QueryProcessor")

class QueryProcessor:
    def __init__(self, news_collector, market_analyzer, gemini_helper=None):
        self.news_collector = news_collector
        self.market_analyzer = market_analyzer
        self.gemini_helper = gemini_helper  # New: Add Gemini helper for better entity extraction
        
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
            'WEEK', 'MONTH', 'YEAR', 'TIME', 'BACK', 'GO', 'COME', 'GET', 'MAKE',
            'ETF', 'IPO', 'CEO', 'CFO', 'CTO', 'COO', 'FUND', 'STOCK', 'SHARE'
        }
        
        # Lists of supported security types
        self.security_types = ['stock', 'etf', 'fund', 'mutual fund', 'index']
        
        # Common stock tickers for validation
        self.common_tickers = {
            # US stocks
            'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'NVDA', 'JPM', 
            'JNJ', 'V', 'PG', 'UNH', 'HD', 'BAC', 'MA', 'XOM', 'DIS', 'VZ', 'NFLX',
            'ADBE', 'CSCO', 'INTC', 'CRM', 'AMD', 'CMCSA', 'PEP', 'COST', 'ABT', 'TMO',
            'AVGO', 'ACN', 'NKE', 'DHR', 'NEE', 'TXN', 'WMT', 'LLY', 'PM', 'MDT',
            
            # ETFs
            'QQQ', 'SPY', 'IWM', 'DIA', 'VOO', 'VTI', 'EEM', 'XLF', 'XLK', 'XLE',
            
            # Indian stocks (NSE)
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS', 'BAJFINANCE.NS',
            'JYOTHYLAB.NS'
        }
        
        # Company name to ticker mappings
        self.company_to_ticker = {
            # Indian companies
            'jyothy labs': 'JYOTHYLAB.NS',
            'reliance industries': 'RELIANCE.NS',
            'tcs': 'TCS.NS',
            'tata consultancy services': 'TCS.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'infosys': 'INFY.NS',
            'icici bank': 'ICICIBANK.NS',
            'state bank of india': 'SBIN.NS',
            'sbi': 'SBIN.NS',
            
            # US companies
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'facebook': 'META',
            'meta': 'META',
            'tesla': 'TSLA',
            'nvidia': 'NVDA',
            
            # Indices
            'nifty': '^NSEI',
            'sensex': '^BSESN',
            's&p 500': '^GSPC',
            'dow jones': '^DJI',
            'nasdaq': '^IXIC',
            
            # ETFs
            'qqq': 'QQQ',
            'invesco qqq': 'QQQ'
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
            
            # Extract query components using better methods
            if self.gemini_helper:
                # Try using Gemini helper first for better entity recognition
                gemini_components = self.gemini_helper.extract_query_components(query_text)
                if gemini_components and gemini_components.get('tickers'):
                    query_info = self._extract_query_components(query_text)
                    # Merge the components, prioritizing Gemini's ticker extraction
                    query_info['tickers'] = gemini_components.get('tickers', [])
                    if 'company_name' in gemini_components:
                        query_info['company_name'] = gemini_components.get('company_name')
                    logger.info(f"Using Gemini analysis for query: {query_info}")
                else:
                    # Fallback to traditional extraction
                    query_info = self._extract_query_components(query_text)
            else:
                # Use traditional extraction method
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
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": "Sorry, I couldn't process that query. Please try asking in a different way.",
                "error": str(e)
            }
    
    def _extract_query_components(self, query_text):
        """Extract important components from the query text with improved company name recognition"""
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
        
        # Extract tickers - first try with potential ticker symbols (direct ticker mention)
        potential_tickers = re.findall(self.ticker_pattern, original_query)
        valid_tickers = [t for t in potential_tickers if t not in self.common_words]
        if valid_tickers:
            components['tickers'] = valid_tickers
        
        # If no tickers found, try with company name mapping
        if not components['tickers']:
            for company_name, ticker in self.company_to_ticker.items():
                if company_name in query_text:
                    components['tickers'].append(ticker)
                    components['company_name'] = company_name
                    break
        
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
                logger.error(traceback.format_exc())
                response['security_data'][ticker] = {"error": str(e)}
        
        return response
    
    # The rest of the methods remain the same as in the original class
    # (keeping _generate_explanation, _generate_answer, etc.)
    
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
            
            # Display company name if available
            display_name = query_info.get('company_name', '').title() if 'company_name' in query_info else ticker
            
            # Construct answer
            answer = f"{display_name} ({ticker}) is {direction} {abs(price_change_pct):.2f}% today, trading at ${current_price:.2f}."
            
            # Add factors if available
            if top_factors:
                answer += f" Key factors include {' and '.join(top_factors)}."
            
            # Add market context
            answer += market_context
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating price movement answer: {str(e)}")
            return f"I couldn't analyze the price movement for {ticker}."
    
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
            logger.error(traceback.format_exc())