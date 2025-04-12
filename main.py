#!/usr/bin/env python3
"""
NewsSense - "Why Is My Nifty Down?"
A financial news analysis system that explains market movements.
"""

import json
import sys
import os
import logging
from datetime import datetime
from colorama import init, Fore, Style
import requests
from tabulate import tabulate
import traceback
from dotenv import load_dotenv

load_dotenv()

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("newssense.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NewsSense")

class NewsSenseCLI:
    def __init__(self):
        """Initialize the CLI interface with required components"""
        try:
            self._fix_path_issues()
            
            
            from src.news_scraper.news_collector import NewsCollector
            from src.analyzer.market_analyzer import MarketAnalyzer
            from src.query_processor.query_processor import QueryProcessor
            from src.utils.gemini_helper import GeminiHelper  

            try:
                from src.utils.gemini_helper import GeminiHelper
                self.gemini_helper = GeminiHelper()
                logger.info("Gemini helper initialized successfully")
            except Exception as e:
                logger.warning(f"Gemini helper not available: {str(e)}")
                self.gemini_helper = None
            
            self.gemini_helper = GeminiHelper(
            api_key=os.getenv("GEMINI_API_KEY"),
            alpha_vantage_key=os.getenv("ALPHA_VANTAGE_KEY")
            )
            logger.info("Gemini helper initialized successfully")
            
            self.gemini_helper = GeminiHelper()
            self.news_collector = NewsCollector()
            self.market_analyzer = MarketAnalyzer()
            self.query_processor = QueryProcessor(
                self.news_collector, 
                self.market_analyzer,
                self.gemini_helper
            )
            
            self.user = os.getenv('USERNAME', 'User')
            
            self.setup_display_settings()
            
            os.makedirs(os.path.join("data", "analysis"), exist_ok=True)
            os.makedirs(os.path.join("data", "scraped_news"), exist_ok=True)
            os.makedirs(os.path.join("data", "market_data"), exist_ok=True)
            
            logger.info("NewsSense initialized successfully")
            
        except Exception as e:
            print(f"{Fore.RED}Error initializing the application: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Initialization error: {str(e)}")
            logger.error(traceback.format_exc())
            sys.exit(1)
    
    def _fix_path_issues(self):
        """Fix common path issues"""
        src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        current_dir = os.path.abspath(os.path.dirname(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

    def setup_display_settings(self):
        """Setup display settings and colors"""
        self.colors = {
            'header': Fore.CYAN + Style.BRIGHT,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'info': Fore.WHITE,
            'positive': Fore.GREEN,
            'negative': Fore.RED,
            'neutral': Fore.YELLOW,
            'prompt': Fore.MAGENTA + Style.BRIGHT
        }
        self.formats = {
            'timestamp': '%Y-%m-%d %H:%M:%S',
            'date': '%Y-%m-%d',
            'currency': '${:,.2f}'
        }

    def display_header(self):
        """Display application header with current time and user information"""
        try:
            current_time = datetime.now().strftime(self.formats['timestamp'])
            print(f"\n{self.colors['header']}=== NewsSense - 'Why Is My Nifty Down?' ==={Style.RESET_ALL}")
            print(f"{self.colors['info']}Current Date and Time: {current_time}")
            print(f"Welcome!")
            print("=" * 50)
        except Exception as e:
            print(f"{self.colors['error']}Error displaying header: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Header display error: {str(e)}")

    def display_menu(self):
        """Display main menu options"""
        print("\nOptions:")
        print("1. Analyze Security")
        print("2. Ask a Question")
        print("3. Track Multiple Securities")
        print("4. View Recent Analyses")
        print("5. Help")
        print("6. Exit")


    def extract_query_components(self, query_text):
        """First use of Gemini - Extract ticker and intent"""
        try:
            prompt = f"""
            Analyze this financial market query: "{query_text}"
            Return a JSON object with:
            {{
                "tickers": ["TICKER"],
                "intent": "price_movement/company_news/financial_metrics",
                "timeframe": "today/this_week/recent",
                "focus": "price/news/both"
            }}
            Example: "How is AAPL doing?" -> {{"tickers": ["AAPL"], "intent": "price_movement", "timeframe": "today", "focus": "both"}}
            """
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1024
                    }
                }
            )

            if response.status_code == 200:
                components = self._extract_json_from_response(
                    response.json()['candidates'][0]['content']['parts'][0]['text']
                )
                return components

        except Exception as e:
            logger.error(f"Error extracting components: {str(e)}")
            return None
    
    
    def analyze_market_context(self, query, data):
        """Generate market analysis using Gemini"""
        try:
            # Convert DataFrame to dict if present
            if 'market_data' in data and 'data' in data['market_data']:
                for sector in data['market_data']['data']:
                    for etf in data['market_data']['data'][sector]:
                        if hasattr(data['market_data']['data'][sector][etf], 'to_dict'):
                            data['market_data']['data'][sector][etf] = data['market_data']['data'][sector][etf].to_dict()

            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            user_login = os.getenv('USERNAME', 'User')

            prompt = f"""
            Current Date and Time (UTC): {current_time}
            Current User's Login: {user_login}
            
            Query: "{query}"
            
            Market Data and News Analysis:
            {json.dumps(data, indent=2, default=str)}
            
            Provide a comprehensive analysis including:
            1. Market trends and sector impacts
            2. News sentiment analysis
            3. Key factors affecting markets
            4. Actionable insights for investors

            Format the response in clear sections with bullet points.
            Include specific data points and percentage changes where relevant.
            Consider both technical indicators and news sentiment in the analysis.
            """

            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1024
                    }
                }
            )

            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']

        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return None


    def _collect_market_data(self):
        """Collect market data for relevant ETFs and sectors"""
        market_data = {
            'sectors': {
                'tech': ['QQQ', 'XLK', 'VGT'],
                'finance': ['XLF', 'VFH', 'IYF'],
                'healthcare': ['XLV', 'VHT', 'IYH']
            },
            'data': {}
        }
        
        try:
            for sector, etfs in market_data['sectors'].items():
                sector_data = {}
                for etf in etfs:
                    security_data = self.market_analyzer.analyze_security(etf)
                    if security_data and 'data' in security_data and 'today' in security_data['data']:
                        price_data = security_data['data']['today']
                        if not price_data.empty:
                            sector_data[etf] = {
                                'current_price': float(price_data['Close'].iloc[-1]),
                                'open_price': float(price_data['Open'].iloc[0]),
                                'change': float(price_data['Close'].iloc[-1] - price_data['Open'].iloc[0]),
                                'change_pct': float((price_data['Close'].iloc[-1] - price_data['Open'].iloc[0]) / price_data['Open'].iloc[0] * 100),
                                'volume': int(price_data['Volume'].sum()) if 'Volume' in price_data else 0
                            }
                market_data['data'][sector] = sector_data
            
            return market_data
        
        except Exception as e:
            logger.error(f"Error collecting market data: {str(e)}")
            return None

    def process_query(self, query):
        """Main query processing with dual Gemini usage"""
        try:
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            user_login = os.getenv('USERNAME', 'User')
            print(f"Processing query at {current_time} for {user_login}")

            components = self.gemini_helper.extract_query_components(query)

            if components and components.get('tickers'):
                ticker = components['tickers'][0]
                market_data = self.market_analyzer.analyze_security(ticker)
                news_items = self.news_collector.scrape_all_sources(ticker)
                
                analysis = self.gemini_helper.analyze_market_context(
                    query,
                    {
                        'ticker': ticker,
                        'market_data': market_data,
                        'news': news_items
                    }
                )
                
                self._display_specific_analysis(ticker, market_data, news_items, analysis)

            else:
                market_data = self._collect_market_data()
                news_data = self._collect_sector_news()
                
                analysis = self.gemini_helper.analyze_market_context(
                    query,
                    {
                        'market_data': market_data,
                        'news': news_data
                    }
                )
                
                self._display_market_analysis(market_data, news_data, analysis)

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return None
    
     
    def _collect_sector_news(self):
        """Collect news for relevant sectors and ETFs"""
        news_data = {
            'tech': [],
            'finance': [],
            'healthcare': []
        }
        
        try:
            sector_etfs = {
                'tech': ['QQQ', 'XLK', 'VGT'],
                'finance': ['XLF', 'VFH', 'IYF'],
                'healthcare': ['XLV', 'VHT', 'IYH']
            }
            
            for sector, etfs in sector_etfs.items():
                sector_news = []
                for etf in etfs:
                    news_items = self.news_collector.scrape_all_sources(etf)
                    if news_items:
                        for item in news_items:
                            item['sector'] = sector
                            item['etf'] = etf
                        sector_news.extend(news_items)
                
                sector_news.sort(key=lambda x: abs(x.get('sentiment', 0)), reverse=True)
                news_data[sector] = sector_news[:5] 
            
            return news_data
        
        except Exception as e:
            logger.error(f"Error collecting sector news: {str(e)}")
            return None
     
    
    def analyze_security(self, ticker):
        """Perform comprehensive security analysis"""
        try:
            print(f"\n{self.colors['info']}Analyzing {ticker}...{Style.RESET_ALL}")
            
            print(f"{self.colors['info']}Fetching market data...{Style.RESET_ALL}")
            security_data = self.market_analyzer.analyze_security(ticker)
            if not security_data:
                print(f"{self.colors['error']}Failed to fetch market data for {ticker}{Style.RESET_ALL}")
                return
            
            print(f"{self.colors['info']}Collecting news from multiple sources...{Style.RESET_ALL}")
            news_items = self.news_collector.scrape_all_sources(ticker)
            
            print(f"{self.colors['info']}Analyzing news and market context...{Style.RESET_ALL}")
            news_analysis = self.market_analyzer.analyze_news_impact(news_items)
            
            explanation = self.market_analyzer.generate_explanation(security_data, news_analysis, ticker)
            
            self.display_analysis_results(ticker, security_data, news_analysis, explanation)
            
        except Exception as e:
            print(f"{self.colors['error']}Error in security analysis: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Security analysis error: {str(e)}")
            logger.error(traceback.format_exc())

    def display_analysis_results(self, ticker, security_data, news_analysis, explanation):
        """Display comprehensive analysis results"""
        try:
            print(f"\n{self.colors['header']}=== Analysis Results for {ticker} ==={Style.RESET_ALL}")
            
            if security_data and 'error' in security_data:
                print(f"{self.colors['error']}Error: {security_data['error']}{Style.RESET_ALL}")
                return
            
            if security_data and 'info' in security_data and security_data['info']:
                info = security_data['info']
                print(f"\n{self.colors['header']}Company Information:{Style.RESET_ALL}")
                print(f"Name: {info.get('longName', ticker)}")
                print(f"Sector: {info.get('sector', 'N/A')}")
                print(f"Industry: {info.get('industry', 'N/A')}")
                print(f"Website: {info.get('website', 'N/A')}")

            if security_data and 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty:
                    print(f"\n{self.colors['header']}Price Information:{Style.RESET_ALL}")
                    
                    current_price = today_data['Close'].iloc[-1]
                    open_price = today_data['Open'].iloc[0]
                    price_change = current_price - open_price
                    price_change_pct = (price_change / open_price) * 100
                    
                    color = self.colors['positive'] if price_change >= 0 else self.colors['negative']
                    print(f"Current Price: {self.format_price(current_price)}")
                    print(f"Change: {color}{price_change:+.2f} ({price_change_pct:+.2f}%){Style.RESET_ALL}")
                    print(f"Day Range: ${today_data['Low'].min():.2f} - ${today_data['High'].max():.2f}")

            if security_data and 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty and 'Volume' in today_data.columns:
                    print(f"\n{self.colors['header']}Volume Information:{Style.RESET_ALL}")
                    current_volume = today_data['Volume'].sum()
                    avg_volume = today_data['Volume'].mean()
                    volume_change = ((current_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
                    print(f"Current Volume: {current_volume:,.0f}")
                    print(f"Average Volume: {avg_volume:,.0f}")
                    print(f"Volume Change: {volume_change:+.1f}% vs average")

            if news_analysis and 'topics' in news_analysis:
                print(f"\n{self.colors['header']}Key Factors Affecting Price:{Style.RESET_ALL}")
                has_factors = False
                for topic, count in sorted(news_analysis['topics'].items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        has_factors = True
                        print(f"- {topic.replace('_', ' ').title()}: {count} mentions")
                if not has_factors:
                    print("No significant factors identified")

            if security_data and 'market_context' in security_data:
                context = security_data.get('market_context', {})
                if context:
                    print(f"\n{self.colors['header']}Market Context:{Style.RESET_ALL}")
                    for index_name, index_data in context.items():
                        if isinstance(index_data, dict) and 'change_pct' in index_data:
                            change_pct = index_data['change_pct']
                            color = self.colors['positive'] if change_pct >= 0 else self.colors['negative']
                            print(f"{index_name}: {color}{change_pct:+.2f}%{Style.RESET_ALL}")

            # News Analysis with improved display
            if news_analysis and 'sentiments' in news_analysis:
                print(f"\n{self.colors['header']}Recent News:{Style.RESET_ALL}")
                sentiments = news_analysis.get('sentiments', [])
                
                if sentiments:
                    # Group news by source
                    news_by_source = {}
                    for item in sentiments:
                        source = item.get('source', 'Unknown')
                        if source not in news_by_source:
                            news_by_source[source] = []
                        news_by_source[source].append(item)

                    # Display news by source
                    for source, items in news_by_source.items():
                        print(f"\n{self.colors['header']}{source} News:{Style.RESET_ALL}")
                        news_table = []
                        for item in items:
                            sentiment = item.get('sentiment', 0)
                            sentiment_color = (self.colors['positive'] if sentiment > 0.2 
                                            else self.colors['negative'] if sentiment < -0.2 
                                            else self.colors['neutral'])
                            
                            title = item.get('title', '')
                            if len(title) > 50:
                                title = title[:47] + "..."
                            
                            news_table.append([
                                title,
                                f"{sentiment_color}{sentiment:.2f}{Style.RESET_ALL}",
                                item.get('timestamp', 'N/A')[:10]  # Just show the date part
                            ])
                        
                        if news_table:
                            print(tabulate(news_table, 
                                        headers=["Title", "Sentiment", "Date"],
                                        tablefmt="grid"))

                    print(f"\n{self.colors['info']}Total articles found: {len(sentiments)}{Style.RESET_ALL}")
                else:
                    print(f"{self.colors['warning']}No news articles found{Style.RESET_ALL}")

            # Analysis Explanation
            if explanation:
                print(f"\n{self.colors['header']}Analysis Explanation:{Style.RESET_ALL}")
                print(explanation)
            
        except Exception as e:
            print(f"{self.colors['error']}Error displaying results: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Results display error: {str(e)}")
            logger.error(traceback.format_exc())
            
    def format_price(self, price):
        """Format price with currency symbol"""
        try:
            return self.formats['currency'].format(price)
        except:
            return str(price)


    def _display_market_analysis(self, market_data, news_data, analysis):
        """Display market analysis results for broader queries"""
        try:
            print(f"\n{self.colors['header']}=== Market Analysis Results ==={Style.RESET_ALL}")
            
            # Display sector performance if available
            if market_data and 'data' in market_data:
                print(f"\n{self.colors['header']}Sector Performance:{Style.RESET_ALL}")
                
                for sector, data in market_data['data'].items():
                    print(f"\n{sector.title()} Sector:")
                    for etf, metrics in data.items():
                        color = self.colors['positive'] if metrics['change_pct'] >= 0 else self.colors['negative']
                        print(f"- {etf}: {color}{metrics['change_pct']:+.2f}%{Style.RESET_ALL}")
                        print(f"  Price: ${metrics['current_price']:.2f}")
                        if metrics.get('volume', 0) > 0:
                            print(f"  Volume: {metrics['volume']:,}")

            # Display news analysis if available
            if news_data:
                print(f"\n{self.colors['header']}Market Moving News:{Style.RESET_ALL}")
                
                for sector, news_items in news_data.items():
                    if news_items:
                        print(f"\n{sector.title()} Sector News:")
                        for item in news_items:
                            sentiment_color = (self.colors['positive'] if item.get('sentiment', 0) > 0.2
                                            else self.colors['negative'] if item.get('sentiment', 0) < -0.2
                                            else self.colors['neutral'])
                            
                            title = item.get('title', '')
                            if len(title) > 70:
                                title = title[:67] + "..."
                            
                            print(f"- {title}")
                            print(f"  {item.get('etf', '')} | {sentiment_color}Sentiment: {item.get('sentiment', 0):+.2f}{Style.RESET_ALL}")

            # Display Gemini's analysis if available
            if analysis:
                print(f"\n{self.colors['header']}Market Insights:{Style.RESET_ALL}")
                print(analysis)
                
            print(f"\n{self.colors['info']}Use options 1 or 3 to analyze specific securities in detail.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{self.colors['error']}Error displaying market analysis: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Display error: {str(e)}")
            logger.error(traceback.format_exc()) 
            
        
        
    def track_multiple_securities(self):
        """Track and compare multiple securities"""
        try:
            print(f"\n{self.colors['info']}Enter tickers separated by commas (e.g. AAPL,MSFT,AMZN):{Style.RESET_ALL}")
            ticker_input = input(f"{self.colors['prompt']}> {Style.RESET_ALL}").strip()
            
            if not ticker_input:
                print(f"{self.colors['warning']}No tickers entered.{Style.RESET_ALL}")
                return
            
            tickers = [t.strip().upper() for t in ticker_input.split(',')]
            
            if len(tickers) > 10:
                print(f"{self.colors['warning']}Too many tickers (maximum 10). Using the first 10.{Style.RESET_ALL}")
                tickers = tickers[:10]
            
            print(f"\n{self.colors['info']}Tracking: {', '.join(tickers)}{Style.RESET_ALL}")
            print(f"{self.colors['info']}Fetching data for multiple securities...{Style.RESET_ALL}")
            
            # Collect data for all securities
            securities_data = []
            
            for ticker in tickers:
                try:
                    security_data = self.market_analyzer.analyze_security(ticker)
                    
                    # Skip if there was an error getting the security
                    if security_data and 'error' in security_data:
                        print(f"{self.colors['error']}Error with {ticker}: {security_data['error']}{Style.RESET_ALL}")
                        continue
                        
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
                                'price': current_price,
                                'change_pct': price_change_pct,
                                'news_sentiment': news_analysis.get('average_sentiment', 0),
                                'news_count': len(news_analysis.get('sentiments', []))
                            })
                except Exception as e:
                    print(f"{self.colors['error']}Error fetching data for {ticker}: {str(e)}{Style.RESET_ALL}")
                    logger.error(f"Error fetching data for {ticker}: {str(e)}")
                    logger.error(traceback.format_exc())
            
            # Display comparison table
            if securities_data:
                print(f"\n{self.colors['header']}Securities Comparison:{Style.RESET_ALL}")
                
                table_data = []
                for data in sorted(securities_data, key=lambda x: abs(x['change_pct']), reverse=True):
                    change_color = self.colors['positive'] if data['change_pct'] >= 0 else self.colors['negative']
                    sentiment_color = (self.colors['positive'] if data['news_sentiment'] > 0.1 
                                    else self.colors['negative'] if data['news_sentiment'] < -0.1 
                                    else self.colors['neutral'])
                    
                    name = data['name']
                    if len(name) > 20:
                        name = name[:17] + '...'
                    
                    table_data.append([
                        data['ticker'],
                        name,
                        f"${data['price']:.2f}",
                        f"{change_color}{data['change_pct']:+.2f}%{Style.RESET_ALL}",
                        f"{sentiment_color}{data['news_sentiment']:.2f}{Style.RESET_ALL}",
                        data['news_count']
                    ])
                
                print(tabulate(table_data, 
                             headers=["Ticker", "Name", "Price", "Change", "Sentiment", "News"],
                             tablefmt="grid"))
                
                # Find correlations
                print(f"\n{self.colors['header']}Observations:{Style.RESET_ALL}")
                
                # 1. Sector patterns
                sectors = {}
                for data in securities_data:
                    sector = data['sector']
                    if sector not in sectors:
                        sectors[sector] = []
                    sectors[sector].append(data)
                
                for sector, stocks in sectors.items():
                    if len(stocks) > 1:
                        avg_change = sum(s['change_pct'] for s in stocks) / len(stocks)
                        direction = "up" if avg_change > 0 else "down"
                        print(f"- {sector} sector is trending {direction} ({avg_change:.2f}%)")
                
                # 2. News sentiment correlation
                if len(securities_data) > 1:
                    correlated_count = sum(1 for s in securities_data 
                                        if (s['change_pct'] > 0 and s['news_sentiment'] > 0) or
                                           (s['change_pct'] < 0 and s['news_sentiment'] < 0))
                    correlation_pct = (correlated_count / len(securities_data)) * 100
                    
                    if correlation_pct > 70:
                        print(f"- Strong correlation between news sentiment and price movement ({correlation_pct:.0f}%)")
                    elif correlation_pct > 40:
                        print(f"- Moderate correlation between news sentiment and price movement ({correlation_pct:.0f}%)")
                    else:
                        print(f"- Weak correlation between news sentiment and price movement ({correlation_pct:.0f}%)")
            else:
                print(f"{self.colors['warning']}No data available for comparison.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{self.colors['error']}Error tracking securities: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Securities tracking error: {str(e)}")
            logger.error(traceback.format_exc())



    # def visualize_price_news_correlation(self, ticker, security_data, news_items):
    #     """Create a matplotlib visualization window for price-news correlation"""
    #     try:
    #         # Check if matplotlib is available
    #         import matplotlib
    #         import matplotlib.pyplot as plt
    #         import matplotlib.dates as mdates
    #         import numpy as np
    #         from datetime import datetime
            
    #         print(f"{self.colors['info']}Creating visualization for price-news correlation...{Style.RESET_ALL}")
            
    #         # Calculate correlation using market analyzer
    #         correlation_result = self.market_analyzer.compute_price_news_correlation(security_data, news_items)
            
    #         if 'error' in correlation_result and correlation_result['error']:
    #             print(f"{self.colors['error']}Error: {correlation_result['error']}{Style.RESET_ALL}")
    #             return
            
    #         correlation_data = correlation_result.get('data', [])
    #         correlation_coef = correlation_result.get('correlation_coefficient')
    #         days_analyzed = correlation_result.get('days_analyzed', 0)
            
    #         if not correlation_data or len(correlation_data) < 2:
    #             print(f"{self.colors['warning']}Insufficient data to visualize price-news correlation.{Style.RESET_ALL}")
    #             return
                
    #         # Prepare data for plotting
    #         dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in correlation_data]
    #         prices = [item['price'] for item in correlation_data]
    #         neg_news = [item['negative_news'] for item in correlation_data]
            
    #         # Create figure with two y-axes
    #         plt.style.use('ggplot')  # Use a nice style
    #         fig, ax1 = plt.subplots(figsize=(12, 8))
    #         fig.patch.set_facecolor('#f5f5f5')
            
    #         # Format title with correlation info
    #         if correlation_coef is not None:
    #             abs_corr = abs(correlation_coef)
    #             if abs_corr > 0.7:
    #                 strength = "Strong"
    #             elif abs_corr > 0.4:
    #                 strength = "Moderate"
    #             elif abs_corr > 0.2:
    #                 strength = "Weak"
    #             else:
    #                 strength = "No clear"
                
    #             corr_type = "negative" if correlation_coef < 0 else "positive"
    #             title = f"Price vs. Negative News Correlation for {ticker}\n"
    #             title += f"Correlation: {correlation_coef:.2f} ({strength} {corr_type})"
    #             plt.suptitle(title, fontsize=16, fontweight='bold')
    #         else:
    #             plt.suptitle(f"Price vs. Negative News for {ticker}", fontsize=16, fontweight='bold')
            
    #         # Plot price line
    #         ax1.set_xlabel('Date', fontsize=12)
    #         ax1.set_ylabel('Price ($)', color='#3366cc', fontsize=12)
    #         line1 = ax1.plot(dates, prices, 'o-', color='#3366cc', linewidth=2.5, label='Price', markersize=8)
    #         ax1.tick_params(axis='y', labelcolor='#3366cc')
            
    #         # Format date axis
    #         ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #         plt.xticks(rotation=45)
            
    #         # Create second y-axis for negative news
    #         ax2 = ax1.twinx()
    #         ax2.set_ylabel('Negative News Count', color='#cc3333', fontsize=12)
    #         bar_width = 0.4
    #         bars = ax2.bar(dates, neg_news, alpha=0.7, color='#cc3333', width=bar_width, label='Negative News')
    #         ax2.tick_params(axis='y', labelcolor='#cc3333')
            
    #         # Add grid
    #         ax1.grid(True, linestyle='--', alpha=0.6)
            
    #         # Add legend with both datasets
    #         lines1, labels1 = ax1.get_legend_handles_labels()
    #         lines2, labels2 = ax2.get_legend_handles_labels()
    #         ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, framealpha=0.9)
            
    #         # Add correlation visualization - highlight relationships with arrows
    #         if correlation_coef:
    #             for i, (date, price, news) in enumerate(zip(dates, prices, neg_news)):
    #                 if news > np.mean(neg_news):  # Only annotate days with above-average negative news
    #                     # Place arrows showing relationship between news and price
    #                     arrow_symbol = '↓' if correlation_coef < 0 else '↑'
    #                     arrow_color = '#cc3333' if correlation_coef < 0 else '#33cc33'
    #                     ax1.annotate(f'{arrow_symbol}', 
    #                                 xy=(date, price),
    #                                 xytext=(0, 10 if correlation_coef > 0 else -15),
    #                                 textcoords='offset points',
    #                                 fontsize=15,
    #                                 color=arrow_color,
    #                                 ha='center',
    #                                 weight='bold')
            
    #         # Add insight text based on correlation
    #         if correlation_coef is not None:
    #             insight_text = ""
    #             if correlation_coef < -0.2:
    #                 insight_text = "Insight: Increased negative news tends to correspond with price declines."
    #                 insight_color = '#cc3333'
    #             elif correlation_coef > 0.2:
    #                 insight_text = "Insight: Prices have moved in the same direction as negative news, which is unusual."
    #                 insight_color = '#e68a00'  # Orange
    #             else:
    #                 insight_text = "Insight: No clear relationship between price and negative news in this period."
    #                 insight_color = '#808080'  # Gray
                    
    #             plt.figtext(0.5, 0.01, insight_text, ha='center', fontsize=13, 
    #                     bbox=dict(facecolor='#f9f9f9', edgecolor=insight_color, alpha=0.8, 
    #                             boxstyle='round,pad=0.5', linewidth=2))
            
    #         # Add statistical significance note if correlation is strong
    #         if correlation_coef and abs(correlation_coef) > 0.4:
    #             if correlation_coef < 0:
    #                 sig_text = "This security is particularly sensitive to negative news sentiment."
    #                 sig_color = '#cc3333'  # Red for negative correlation
    #             else:
    #                 sig_text = "This security is showing unusual resilience to negative news."
    #                 sig_color = '#e68a00'  # Orange for positive correlation
                    
    #             plt.figtext(0.5, 0.04, sig_text, ha='center', fontsize=12, style='italic',
    #                     bbox=dict(facecolor='#f9f9f9', edgecolor=sig_color, alpha=0.6, 
    #                             boxstyle='round,pad=0.3', linewidth=1))
            
    #         # Add a footer with the data source
    #         plt.figtext(0.01, 0.01, "Data source: NewsSense Analysis", fontsize=8, color='#666666')
            
    #         # Adjust layout and display
    #         plt.tight_layout()
    #         plt.subplots_adjust(top=0.9, bottom=0.15)
            
    #         # Show plot in a non-blocking way so CLI can continue
    #         plt.show(block=False)
            
    #         print(f"{self.colors['success']}Visualization window opened for {ticker} price-news correlation.{Style.RESET_ALL}")
    #         print(f"{self.colors['info']}Close the window to continue with CLI.{Style.RESET_ALL}")
            
    #         return True
            
    #     except ImportError as e:
    #         print(f"{self.colors['error']}Error: Matplotlib is required for visualization.{Style.RESET_ALL}")
    #         print(f"{self.colors['info']}Install matplotlib with: pip install matplotlib{Style.RESET_ALL}")
    #         return False
    #     except Exception as e:
    #         print(f"{self.colors['error']}Error creating visualization: {str(e)}{Style.RESET_ALL}")
    #         return False
        
 
        def visualize_price_news_correlation(self, ticker, security_data, news_items):
            """Create a matplotlib visualization window for price-news correlation"""
            try:
                # Make sure we have the required packages
                try:
                    import matplotlib
                    import matplotlib.pyplot as plt
                    import matplotlib.dates as mdates
                    import numpy as np
                    from datetime import datetime
                except ImportError as e:
                    print(f"{self.colors['error']}Error importing visualization libraries: {str(e)}{Style.RESET_ALL}")
                    print(f"{self.colors['info']}Install matplotlib with: pip install matplotlib numpy{Style.RESET_ALL}")
                    return False
                
                print(f"{self.colors['info']}Creating visualization for price-news correlation...{Style.RESET_ALL}")
                
                # Calculate correlation using market analyzer
                correlation_result = self.market_analyzer.compute_price_news_correlation(security_data, news_items)
                
                if 'error' in correlation_result and correlation_result['error']:
                    print(f"{self.colors['error']}Error: {correlation_result['error']}{Style.RESET_ALL}")
                    return False
                
                correlation_data = correlation_result.get('data', [])
                correlation_coef = correlation_result.get('correlation_coefficient')
                days_analyzed = correlation_result.get('days_analyzed', 0)
                
                if not correlation_data or len(correlation_data) < 2:
                    print(f"{self.colors['warning']}Insufficient data to visualize price-news correlation.{Style.RESET_ALL}")
                    return False
                    
                # Prepare data for plotting
                try:
                    dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in correlation_data]
                    prices = [float(item['price']) for item in correlation_data]
                    neg_news = [int(item['negative_news']) for item in correlation_data]
                except Exception as e:
                    print(f"{self.colors['error']}Error processing data for visualization: {str(e)}{Style.RESET_ALL}")
                    return False
                
                # Configure matplotlib to use a GUI backend that works without blocking
                # This helps ensure the visualization works in various environments
                try:
                    matplotlib.use('TkAgg', force=True)  # Use TkAgg as it's widely available
                except:
                    # If TkAgg fails, try other backends
                    for backend in ['Qt5Agg', 'MacOSX', 'GTK3Agg', 'Agg']:
                        try:
                            matplotlib.use(backend, force=True)
                            break
                        except:
                            continue
                
                # Create figure with two y-axes
                plt.style.use('ggplot')  # Use a nice style
                fig, ax1 = plt.subplots(figsize=(12, 8))
                fig.patch.set_facecolor('#f5f5f5')
                
                # Format title with correlation info
                if correlation_coef is not None:
                    abs_corr = abs(correlation_coef)
                    if abs_corr > 0.7:
                        strength = "Strong"
                    elif abs_corr > 0.4:
                        strength = "Moderate"
                    elif abs_corr > 0.2:
                        strength = "Weak"
                    else:
                        strength = "No clear"
                    
                    corr_type = "negative" if correlation_coef < 0 else "positive"
                    title = f"Price vs. Negative News Correlation for {ticker}\n"
                    title += f"Correlation: {correlation_coef:.2f} ({strength} {corr_type})"
                    plt.suptitle(title, fontsize=16, fontweight='bold')
                else:
                    plt.suptitle(f"Price vs. Negative News for {ticker}", fontsize=16, fontweight='bold')
                
                # Plot price line
                ax1.set_xlabel('Date', fontsize=12)
                ax1.set_ylabel('Price ($)', color='#3366cc', fontsize=12)
                line1 = ax1.plot(dates, prices, 'o-', color='#3366cc', linewidth=2.5, label='Price', markersize=8)
                ax1.tick_params(axis='y', labelcolor='#3366cc')
                
                # Format date axis
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plt.xticks(rotation=45)
                
                # Create second y-axis for negative news
                ax2 = ax1.twinx()
                ax2.set_ylabel('Negative News Count', color='#cc3333', fontsize=12)
                bar_width = 0.4
                bars = ax2.bar(dates, neg_news, alpha=0.7, color='#cc3333', width=bar_width, label='Negative News')
                ax2.tick_params(axis='y', labelcolor='#cc3333')
                
                # Add grid
                ax1.grid(True, linestyle='--', alpha=0.6)
                
                # Add legend with both datasets
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, framealpha=0.9)
                
                # Add correlation visualization - highlight relationships with arrows
                if correlation_coef:
                    for i, (date, price, news) in enumerate(zip(dates, prices, neg_news)):
                        if i > 0 and news > np.mean(neg_news):  # Only annotate days with above-average negative news
                            # Place arrows showing relationship between news and price
                            arrow_symbol = '↓' if correlation_coef < 0 else '↑'
                            arrow_color = '#cc3333' if correlation_coef < 0 else '#33cc33'
                            ax1.annotate(f'{arrow_symbol}', 
                                        xy=(date, price),
                                        xytext=(0, 10 if correlation_coef > 0 else -15),
                                        textcoords='offset points',
                                        fontsize=15,
                                        color=arrow_color,
                                        ha='center',
                                        weight='bold')
                
                # Add insight text based on correlation
                if correlation_coef is not None:
                    insight_text = ""
                    if correlation_coef < -0.2:
                        insight_text = "Insight: Increased negative news tends to correspond with price declines."
                        insight_color = '#cc3333'
                    elif correlation_coef > 0.2:
                        insight_text = "Insight: Prices have moved in the same direction as negative news, which is unusual."
                        insight_color = '#e68a00'  # Orange
                    else:
                        insight_text = "Insight: No clear relationship between price and negative news in this period."
                        insight_color = '#808080'  # Gray
                        
                    plt.figtext(0.5, 0.01, insight_text, ha='center', fontsize=13, 
                            bbox=dict(facecolor='#f9f9f9', edgecolor=insight_color, alpha=0.8, 
                                    boxstyle='round,pad=0.5', linewidth=2))
                
                # Add statistical significance note if correlation is strong
                if correlation_coef and abs(correlation_coef) > 0.4:
                    if correlation_coef < 0:
                        sig_text = "This security is particularly sensitive to negative news sentiment."
                        sig_color = '#cc3333'  # Red for negative correlation
                    else:
                        sig_text = "This security is showing unusual resilience to negative news."
                        sig_color = '#e68a00'  # Orange for positive correlation
                        
                    plt.figtext(0.5, 0.04, sig_text, ha='center', fontsize=12, style='italic',
                            bbox=dict(facecolor='#f9f9f9', edgecolor=sig_color, alpha=0.6, 
                                    boxstyle='round,pad=0.3', linewidth=1))
                
                # Add a footer with the data source
                plt.figtext(0.01, 0.01, "Data source: NewsSense Analysis", fontsize=8, color='#666666')
                
                # Adjust layout and display
                plt.tight_layout()
                plt.subplots_adjust(top=0.9, bottom=0.15)
                
                # Show plot in a non-blocking way so CLI can continue
                try:
                    plt.show(block=False)
                    print(f"{self.colors['success']}Visualization window opened for {ticker} price-news correlation.{Style.RESET_ALL}")
                    print(f"{self.colors['info']}Close the window when finished to continue with CLI.{Style.RESET_ALL}")
                    return True
                except Exception as e:
                    print(f"{self.colors['error']}Error displaying plot: {str(e)}{Style.RESET_ALL}")
                    # Try alternative display method
                    print(f"{self.colors['info']}Trying alternative display method...{Style.RESET_ALL}")
                    try:
                        plt.savefig(f"news_correlation_{ticker}.png")
                        print(f"{self.colors['success']}Visualization saved to 'news_correlation_{ticker}.png'{Style.RESET_ALL}")
                        return True
                    except Exception as e:
                        print(f"{self.colors['error']}Could not save visualization: {str(e)}{Style.RESET_ALL}")
                        return False
                
            except ImportError as e:
                print(f"{self.colors['error']}Error: Matplotlib is required for visualization.{Style.RESET_ALL}")
                print(f"{self.colors['info']}Install matplotlib with: pip install matplotlib numpy{Style.RESET_ALL}")
                return False
            except Exception as e:
                print(f"{self.colors['error']}Error creating visualization: {str(e)}{Style.RESET_ALL}")
                return False
    
    
    def _display_price_news_correlation(self, ticker, security_data, news_items):
        """Display correlation between price movement and negative news volume"""
        print(f"\n{self.colors['header']}Price vs. Negative News Correlation:{Style.RESET_ALL}")
        print("This analysis shows the relationship between price movements and negative news volume.")
        
        # Calculate correlation using market analyzer
        correlation_result = self.market_analyzer.compute_price_news_correlation(security_data, news_items)
        
        if 'error' in correlation_result and correlation_result['error']:
            print(f"{self.colors['error']}Error: {correlation_result['error']}{Style.RESET_ALL}")
            return
        
        correlation_data = correlation_result.get('data', [])
        correlation_coef = correlation_result.get('correlation_coefficient')
        days_analyzed = correlation_result.get('days_analyzed', 0)
        
        if not correlation_data:
            print(f"{self.colors['warning']}Insufficient data to analyze price-news correlation.{Style.RESET_ALL}")
            return
        
        # Print correlation coefficient with interpretation
        if correlation_coef is not None:
            # Determine correlation strength and color
            abs_corr = abs(correlation_coef)
            if abs_corr > 0.7:
                strength = "Strong"
                color = self.colors['negative'] if correlation_coef < 0 else self.colors['positive']
            elif abs_corr > 0.4:
                strength = "Moderate"
                color = self.colors['negative'] if correlation_coef < 0 else self.colors['positive']
            elif abs_corr > 0.2:
                strength = "Weak"
                color = self.colors['negative'] if correlation_coef < 0 else self.colors['positive']
            else:
                strength = "No clear"
                color = self.colors['neutral']
            
            corr_type = "negative" if correlation_coef < 0 else "positive"
            
            print(f"\nCorrelation Coefficient: {color}{correlation_coef:.2f}{Style.RESET_ALL}")
            print(f"Interpretation: {color}{strength} {corr_type} correlation{Style.RESET_ALL} between price and negative news")
            print(f"Time period analyzed: {days_analyzed} trading days")
            
            # Print insight based on correlation
            print("\nInsight:", end=" ")
            if correlation_coef < -0.2:
                print(f"{self.colors['negative']}Increased negative news tends to correspond with price declines.{Style.RESET_ALL}")
            elif correlation_coef > 0.2:
                print(f"{self.colors['warning']}For this period, prices have moved in the same direction as negative news, which is unusual.{Style.RESET_ALL}")
            else:
                print(f"{self.colors['neutral']}No clear relationship between price and negative news in this period.{Style.RESET_ALL}")
        
        # Create a visual representation of the data
        print("\nPrice to Negative News Relationship (timeline):")
        print(f"\n{self.colors['header']}Date       | Price ($) | Neg News | Visualization{Style.RESET_ALL}")
        print("─" * 80)
        
        # Find max values for scaling the visualization
        max_price = max(item['price'] for item in correlation_data) if correlation_data else 0
        max_neg_news = max(item['negative_news'] for item in correlation_data) if correlation_data else 0
        
        # Calculate scaling factors
        price_scale = 20 / max_price if max_price > 0 else 0
        news_scale = 10 / max_neg_news if max_neg_news > 0 else 0
        
        # Display each data point with visual bars
        for item in correlation_data:
            date = item['date']
            price = item['price']
            neg_news = item['negative_news']
            
            # Create ASCII bar charts with proper scaling
            price_bar_length = int(price * price_scale)
            news_bar_length = int(neg_news * news_scale)
            
            price_bar = "█" * price_bar_length
            news_bar = "▓" * news_bar_length
            
            print(f"{date} | ${price:8.2f} | {neg_news:8d} | ", end="")
            print(f"{self.colors['info']}{price_bar}{Style.RESET_ALL} ", end="")
            
            # Add directional arrow to show relationship
            if neg_news > 0:
                if correlation_coef and correlation_coef < 0:
                    print("↘ ", end="")  # Negative correlation: price down when news negative
                elif correlation_coef and correlation_coef > 0:
                    print("↗ ", end="")  # Positive correlation: price up when news negative
                else:
                    print("→ ", end="")  # No clear correlation
                    
                print(f"{self.colors['negative']}{news_bar}{Style.RESET_ALL}")
            else:
                print()
        
        # Add legend
        print("\nLegend:")
        print(f"{self.colors['info']}█{Style.RESET_ALL} Price")
        print(f"{self.colors['negative']}▓{Style.RESET_ALL} Negative News")
        print("↘ Negative correlation (price tends to fall with negative news)")
        print("↗ Positive correlation (price tends to rise despite negative news)")
        
        # Add statistical significance note if correlation is strong
        if correlation_coef and abs(correlation_coef) > 0.4:
            sig_color = self.colors['positive'] if correlation_coef < 0 else self.colors['warning']
            print(f"\n{sig_color}Note: This correlation appears statistically significant.{Style.RESET_ALL}")
            
            if correlation_coef < 0:
                print("This security is particularly sensitive to negative news sentiment.")
            else:
                print("This security is showing unusual resilience to negative news.")
        
        # Offer graphical visualization
        print(f"\n{self.colors['prompt']}Would you like to see a graphical visualization? (y/n){Style.RESET_ALL}")
        choice = input("> ").strip().lower()
        
        if choice == 'y':
            try:
                # Try to use matplotlib for visualization
                self.visualize_price_news_correlation(ticker, security_data, news_items)
            except Exception as e:
                print(f"{self.colors['error']}Error displaying graphical visualization: {str(e)}{Style.RESET_ALL}")
                print(f"{self.colors['info']}Using text-based visualization only.{Style.RESET_ALL}")
        
        return True

    # def _display_price_news_correlation(self, ticker, security_data, news_items):
    #     """Display correlation between price movement and negative news volume"""
    #     print(f"\n{self.colors['header']}Price vs. Negative News Correlation:{Style.RESET_ALL}")
    #     print("This analysis shows the relationship between price movements and negative news volume.")
        
    #     # Calculate correlation using market analyzer
    #     correlation_result = self.market_analyzer.compute_price_news_correlation(security_data, news_items)
        
    #     if 'error' in correlation_result:
    #         print(f"{self.colors['error']}Error: {correlation_result['error']}{Style.RESET_ALL}")
    #         return
        
    #     correlation_data = correlation_result.get('data', [])
    #     correlation_coef = correlation_result.get('correlation_coefficient')
    #     days_analyzed = correlation_result.get('days_analyzed', 0)
        
    #     if not correlation_data:
    #         print(f"{self.colors['warning']}Insufficient data to analyze price-news correlation.{Style.RESET_ALL}")
    #         return
        
    #     # Print correlation coefficient with interpretation
    #     if correlation_coef is not None:
    #         # Determine correlation strength and color
    #         abs_corr = abs(correlation_coef)
    #         if abs_corr > 0.7:
    #             strength = "Strong"
    #             color = self.colors['negative'] if correlation_coef < 0 else self.colors['positive']
    #         elif abs_corr > 0.4:
    #             strength = "Moderate"
    #             color = self.colors['negative'] if correlation_coef < 0 else self.colors['positive']
    #         elif abs_corr > 0.2:
    #             strength = "Weak"
    #             color = self.colors['negative'] if correlation_coef < 0 else self.colors['positive']
    #         else:
    #             strength = "No clear"
    #             color = self.colors['neutral']
            
    #         corr_type = "negative" if correlation_coef < 0 else "positive"
            
    #         print(f"\nCorrelation Coefficient: {color}{correlation_coef:.2f}{Style.RESET_ALL}")
    #         print(f"Interpretation: {color}{strength} {corr_type} correlation{Style.RESET_ALL} between price and negative news")
    #         print(f"Time period analyzed: {days_analyzed} trading days")
            
    #         # Print insight based on correlation
    #         print("\nInsight:", end=" ")
    #         if correlation_coef < -0.2:
    #             print(f"{self.colors['negative']}Increased negative news tends to correspond with price declines.{Style.RESET_ALL}")
    #         elif correlation_coef > 0.2:
    #             print(f"{self.colors['warning']}For this period, prices have moved in the same direction as negative news, which is unusual.{Style.RESET_ALL}")
    #         else:
    #             print(f"{self.colors['neutral']}No clear relationship between price and negative news in this period.{Style.RESET_ALL}")
        
    #     # Create a visual representation of the data
    #     print("\nPrice to Negative News Relationship (timeline):")
    #     print(f"\n{self.colors['header']}Date       | Price ($) | Neg News | Visualization{Style.RESET_ALL}")
    #     print("─" * 80)
        
    #     # Find max values for scaling the visualization
    #     max_price = max(item['price'] for item in correlation_data) if correlation_data else 0
    #     max_neg_news = max(item['negative_news'] for item in correlation_data) if correlation_data else 0
        
    #     # Calculate scaling factors
    #     price_scale = 20 / max_price if max_price > 0 else 0
    #     news_scale = 10 / max_neg_news if max_neg_news > 0 else 0
        
    #     # Display each data point with visual bars
    #     for item in correlation_data:
    #         date = item['date']
    #         price = item['price']
    #         neg_news = item['negative_news']
            
    #         # Create ASCII bar charts with proper scaling
    #         price_bar_length = int(price * price_scale)
    #         news_bar_length = int(neg_news * news_scale)
            
    #         price_bar = "█" * price_bar_length
    #         news_bar = "▓" * news_bar_length
            
    #         print(f"{date} | ${price:8.2f} | {neg_news:8d} | ", end="")
    #         print(f"{self.colors['info']}{price_bar}{Style.RESET_ALL} ", end="")
            
    #         # Add directional arrow to show relationship
    #         if neg_news > 0:
    #             if correlation_coef and correlation_coef < 0:
    #                 print("↘ ", end="")  # Negative correlation: price down when news negative
    #             elif correlation_coef and correlation_coef > 0:
    #                 print("↗ ", end="")  # Positive correlation: price up when news negative
    #             else:
    #                 print("→ ", end="")  # No clear correlation
                    
    #             print(f"{self.colors['negative']}{news_bar}{Style.RESET_ALL}")
    #         else:
    #             print()
        
    #     # Add legend
    #     print("\nLegend:")
    #     print(f"{self.colors['info']}█{Style.RESET_ALL} Price")
    #     print(f"{self.colors['negative']}▓{Style.RESET_ALL} Negative News")
    #     print("↘ Negative correlation (price tends to fall with negative news)")
    #     print("↗ Positive correlation (price tends to rise despite negative news)")
        
    #     # Add statistical significance note if correlation is strong
    #     if correlation_coef and abs(correlation_coef) > 0.4:
    #         sig_color = self.colors['positive'] if correlation_coef < 0 else self.colors['warning']
    #         print(f"\n{sig_color}Note: This correlation appears statistically significant.{Style.RESET_ALL}")
            
    #         if correlation_coef < 0:
    #             print("This security is particularly sensitive to negative news sentiment.")
    #         else:
    #             print("This security is showing unusual resilience to negative news.")
                

    # def _display_specific_analysis(self, ticker, market_data, news_items, analysis):
    #     """Display analysis for specific ticker"""
    #     try:
    #         current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    #         print(f"\n{self.colors['header']}=== Analysis Results for {ticker} ==={Style.RESET_ALL}")
    #         print(f"Current Date and Time (UTC): {current_time}")
    #         print(f"Current User's Login: {os.getenv('USERNAME', 'User')}")
            
    #         # Check for errors
    #         if market_data and 'error' in market_data:
    #             print(f"{self.colors['error']}Error: {market_data['error']}{Style.RESET_ALL}")
    #             return
            
    #         # Company Information
    #         if market_data and 'info' in market_data and market_data['info']:
    #             info = market_data['info']
    #             print(f"\n{self.colors['header']}Company Information:{Style.RESET_ALL}")
    #             print(f"Name: {info.get('longName', ticker)}")
    #             # print(f"Sector: {info.get('sector', 'N/A')}")
    #             # print(f"Industry: {info.get('industry', 'N/A')}")
    #             # print(f"Website: {info.get('website', 'N/A')}")

    #         if market_data and 'data' in market_data and 'today' in market_data['data']:
    #             today_data = market_data['data']['today']
    #             if not today_data.empty:
    #                 print(f"\n{self.colors['header']}Price Information:{Style.RESET_ALL}")
                    
    #                 current_price = today_data['Close'].iloc[-1]
    #                 open_price = today_data['Open'].iloc[0]
    #                 price_change = current_price - open_price
    #                 price_change_pct = (price_change / open_price) * 100
                    
    #                 color = self.colors['positive'] if price_change >= 0 else self.colors['negative']
    #                 print(f"Current Price: {self.format_price(current_price)}")
    #                 print(f"Change: {color}{price_change:+.2f} ({price_change_pct:+.2f}%){Style.RESET_ALL}")
    #                 print(f"Day Range: ${today_data['Low'].min():.2f} - ${today_data['High'].max():.2f}")

    #         if market_data and 'data' in market_data and 'today' in market_data['data']:
    #             today_data = market_data['data']['today']
    #             if not today_data.empty and 'Volume' in today_data.columns:
    #                 print(f"\n{self.colors['header']}Volume Information:{Style.RESET_ALL}")
    #                 current_volume = today_data['Volume'].sum()
    #                 avg_volume = today_data['Volume'].mean()
    #                 volume_change = ((current_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
    #                 print(f"Current Volume: {current_volume:,.0f}")
    #                 print(f"Average Volume: {avg_volume:,.0f}")
    #                 print(f"Volume Change: {volume_change:+.1f}% vs average")

    #         if news_items:
    #             print(f"\n{self.colors['header']}Key Factors Affecting Price:{Style.RESET_ALL}")
    #             topics = {}
    #             for item in news_items:
    #                 for topic in item.get('topics', []):
    #                     topics[topic] = topics.get(topic, 0) + 1
                
    #             if topics:
    #                 for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
    #                     print(f"- {topic.replace('_', ' ').title()}: {count} mentions")
    #             else:
    #                 print("No significant factors identified")

    #         if market_data and 'market_context' in market_data:
    #             context = market_data.get('market_context', {})
    #             if context:
    #                 print(f"\n{self.colors['header']}Market Context:{Style.RESET_ALL}")
    #                 for index_name, index_data in context.items():
    #                     if isinstance(index_data, dict) and 'change_pct' in index_data:
    #                         change_pct = index_data['change_pct']
    #                         color = self.colors['positive'] if change_pct >= 0 else self.colors['negative']
    #                         print(f"{index_name}: {color}{change_pct:+.2f}%{Style.RESET_ALL}")

    #         if news_items:
    #             print(f"\n{self.colors['header']}Recent News:{Style.RESET_ALL}")
                
    #             news_by_source = {}
    #             for item in news_items:
    #                 source = item.get('source', 'Unknown')
    #                 if source not in news_by_source:
    #                     news_by_source[source] = []
    #                 news_by_source[source].append(item)

    #             for source, items in news_by_source.items():
    #                 print(f"\n{self.colors['header']}{source} News:{Style.RESET_ALL}")
    #                 news_table = []
    #                 for item in items:
    #                     sentiment = item.get('sentiment', 0)
    #                     sentiment_color = (self.colors['positive'] if sentiment > 0.2 
    #                                     else self.colors['negative'] if sentiment < -0.2 
    #                                     else self.colors['neutral'])
                        
    #                     title = item.get('title', '')
    #                     if len(title) > 50:
    #                         title = title[:47] + "..."
                        
    #                     news_table.append([
    #                         title,
    #                         f"{sentiment_color}{sentiment:.2f}{Style.RESET_ALL}",
    #                         item.get('timestamp', 'N/A')[:10]  # Just show the date part
    #                     ])
                    
    #                 if news_table:
    #                     print(tabulate(news_table, 
    #                                 headers=["Title", "Sentiment", "Date"],
    #                                 tablefmt="grid"))

    #             print(f"\n{self.colors['info']}Total articles found: {len(news_items)}{Style.RESET_ALL}")

    #         # Analysis Explanation (Gemini's analysis)
    #         if analysis:
    #             print(f"\n{self.colors['header']}Analysis Explanation:{Style.RESET_ALL}")
    #             print(analysis)
                
    #             # Add observations section
    #             print(f"\n{self.colors['header']}Key Observations:{Style.RESET_ALL}")
    #             if market_data and 'data' in market_data and 'today' in market_data['data']:
    #                 today_data = market_data['data']['today']
    #                 if not today_data.empty:
    #                     price_change = today_data['Close'].iloc[-1] - today_data['Open'].iloc[0]
    #                     if price_change > 0:
    #                         print("- Stock is showing positive momentum today")
    #                     else:
    #                         print("- Stock is showing negative pressure today")
                        
    #                     if 'Volume' in today_data.columns:
    #                         avg_volume = today_data['Volume'].mean()
    #                         current_volume = today_data['Volume'].sum()
    #                         if current_volume > avg_volume:
    #                             print("- Trading volume is above average, indicating strong interest")
    #                         else:
    #                             print("- Trading volume is below average, suggesting lower activity")

    #         print(f"\n{self.colors['info']}Use 'Track Multiple Securities' for comparison with other tickers.{Style.RESET_ALL}")
            
    #     except Exception as e:
    #         print(f"{self.colors['error']}Error displaying specific analysis: {str(e)}{Style.RESET_ALL}")
    #         logger.error(f"Specific analysis display error: {str(e)}")
    #         logger.error(traceback.format_exc())
          
    def _display_specific_analysis(self, ticker, market_data, news_items, analysis):
        """Display analysis for specific ticker"""
        try:
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{self.colors['header']}=== Analysis Results for {ticker} ==={Style.RESET_ALL}")
            print(f"Current Date and Time (UTC): {current_time}")
            print(f"Current User's Login: {os.getenv('USERNAME', 'User')}")
            
            # Check for errors
            if market_data and 'error' in market_data:
                print(f"{self.colors['error']}Error: {market_data['error']}{Style.RESET_ALL}")
                return
            
            # Company Information
            if market_data and 'info' in market_data and market_data['info']:
                info = market_data['info']
                print(f"\n{self.colors['header']}Company Information:{Style.RESET_ALL}")
                print(f"Name: {info.get('longName', ticker)}")
                # print(f"Sector: {info.get('sector', 'N/A')}")
                # print(f"Industry: {info.get('industry', 'N/A')}")
                # print(f"Website: {info.get('website', 'N/A')}")

            # Price Information
            if market_data and 'data' in market_data and 'today' in market_data['data']:
                today_data = market_data['data']['today']
                if not today_data.empty:
                    print(f"\n{self.colors['header']}Price Information:{Style.RESET_ALL}")
                    
                    current_price = today_data['Close'].iloc[-1]
                    open_price = today_data['Open'].iloc[0]
                    price_change = current_price - open_price
                    price_change_pct = (price_change / open_price) * 100
                    
                    color = self.colors['positive'] if price_change >= 0 else self.colors['negative']
                    print(f"Current Price: {self.format_price(current_price)}")
                    print(f"Change: {color}{price_change:+.2f} ({price_change_pct:+.2f}%){Style.RESET_ALL}")
                    print(f"Day Range: ${today_data['Low'].min():.2f} - ${today_data['High'].max():.2f}")

            # Volume Information
            if market_data and 'data' in market_data and 'today' in market_data['data']:
                today_data = market_data['data']['today']
                if not today_data.empty and 'Volume' in today_data.columns:
                    print(f"\n{self.colors['header']}Volume Information:{Style.RESET_ALL}")
                    current_volume = today_data['Volume'].sum()
                    avg_volume = today_data['Volume'].mean()
                    volume_change = ((current_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
                    print(f"Current Volume: {current_volume:,.0f}")
                    print(f"Average Volume: {avg_volume:,.0f}")
                    print(f"Volume Change: {volume_change:+.1f}% vs average")

            # Key Factors
            if news_items:
                print(f"\n{self.colors['header']}Key Factors Affecting Price:{Style.RESET_ALL}")
                topics = {}
                for item in news_items:
                    for topic in item.get('topics', []):
                        topics[topic] = topics.get(topic, 0) + 1
                
                if topics:
                    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
                        print(f"- {topic.replace('_', ' ').title()}: {count} mentions")
                else:
                    print("No significant factors identified")

            # Market Context
            if market_data and 'market_context' in market_data:
                context = market_data.get('market_context', {})
                if context:
                    print(f"\n{self.colors['header']}Market Context:{Style.RESET_ALL}")
                    for index_name, index_data in context.items():
                        if isinstance(index_data, dict) and 'change_pct' in index_data:
                            change_pct = index_data['change_pct']
                            color = self.colors['positive'] if change_pct >= 0 else self.colors['negative']
                            print(f"{index_name}: {color}{change_pct:+.2f}%{Style.RESET_ALL}")

            # News Analysis
            if news_items:
                print(f"\n{self.colors['header']}Recent News:{Style.RESET_ALL}")
                
                # Group news by source
                news_by_source = {}
                for item in news_items:
                    source = item.get('source', 'Unknown')
                    if source not in news_by_source:
                        news_by_source[source] = []
                    news_by_source[source].append(item)

                # Display news by source
                for source, items in news_by_source.items():
                    print(f"\n{self.colors['header']}{source} News:{Style.RESET_ALL}")
                    news_table = []
                    for item in items:
                        sentiment = item.get('sentiment', 0)
                        sentiment_color = (self.colors['positive'] if sentiment > 0.2 
                                        else self.colors['negative'] if sentiment < -0.2 
                                        else self.colors['neutral'])
                        
                        title = item.get('title', '')
                        if len(title) > 50:
                            title = title[:47] + "..."
                        
                        news_table.append([
                            title,
                            f"{sentiment_color}{sentiment:.2f}{Style.RESET_ALL}",
                            item.get('timestamp', 'N/A')[:10]  # Just show the date part
                        ])
                    
                    if news_table:
                        print(tabulate(news_table, 
                                    headers=["Title", "Sentiment", "Date"],
                                    tablefmt="grid"))

                print(f"\n{self.colors['info']}Total articles found: {len(news_items)}{Style.RESET_ALL}")
                
                # Display Price-News Correlation
                self._display_price_news_correlation(ticker, market_data, news_items)
                
            # Analysis Explanation (Gemini's analysis)
            if analysis:
                print(f"\n{self.colors['header']}Analysis Explanation:{Style.RESET_ALL}")
                print(analysis)
                
                # Add observations section
                print(f"\n{self.colors['header']}Key Observations:{Style.RESET_ALL}")
                if market_data and 'data' in market_data and 'today' in market_data['data']:
                    today_data = market_data['data']['today']
                    if not today_data.empty:
                        price_change = today_data['Close'].iloc[-1] - today_data['Open'].iloc[0]
                        if price_change > 0:
                            print("- Stock is showing positive momentum today")
                        else:
                            print("- Stock is showing negative pressure today")
                        
                        if 'Volume' in today_data.columns:
                            avg_volume = today_data['Volume'].mean()
                            current_volume = today_data['Volume'].sum()
                            if current_volume > avg_volume:
                                print("- Trading volume is above average, indicating strong interest")
                            else:
                                print("- Trading volume is below average, suggesting lower activity")

            print(f"\n{self.colors['info']}Use 'Track Multiple Securities' for comparison with other tickers.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{self.colors['error']}Error displaying specific analysis: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Specific analysis display error: {str(e)}")
            logger.error(traceback.format_exc())          
          
          
    # def _display_specific_analysis(self, ticker, market_data, news_items, analysis):
    #     """Display analysis for specific ticker"""
    #     try:
    #         current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    #         print(f"\n{self.colors['header']}=== Analysis Results for {ticker} ==={Style.RESET_ALL}")
    #         print(f"Current Date and Time (UTC): {current_time}")
    #         print(f"Current User's Login: {os.getenv('USERNAME', 'User')}")
            
    #         # Check for errors
    #         if market_data and 'error' in market_data:
    #             print(f"{self.colors['error']}Error: {market_data['error']}{Style.RESET_ALL}")
    #             return
            
    #         # Company Information
    #         if market_data and 'info' in market_data and market_data['info']:
    #             info = market_data['info']
    #             print(f"\n{self.colors['header']}Company Information:{Style.RESET_ALL}")
    #             print(f"Name: {info.get('longName', ticker)}")
    #             # print(f"Sector: {info.get('sector', 'N/A')}")
    #             # print(f"Industry: {info.get('industry', 'N/A')}")
    #             # print(f"Website: {info.get('website', 'N/A')}")

    #         # Price Information
    #         if market_data and 'data' in market_data and 'today' in market_data['data']:
    #             today_data = market_data['data']['today']
    #             if not today_data.empty:
    #                 print(f"\n{self.colors['header']}Price Information:{Style.RESET_ALL}")
                    
    #                 current_price = today_data['Close'].iloc[-1]
    #                 open_price = today_data['Open'].iloc[0]
    #                 price_change = current_price - open_price
    #                 price_change_pct = (price_change / open_price) * 100
                    
    #                 color = self.colors['positive'] if price_change >= 0 else self.colors['negative']
    #                 print(f"Current Price: {self.format_price(current_price)}")
    #                 print(f"Change: {color}{price_change:+.2f} ({price_change_pct:+.2f}%){Style.RESET_ALL}")
    #                 print(f"Day Range: ${today_data['Low'].min():.2f} - ${today_data['High'].max():.2f}")

    #         # Volume Information
    #         if market_data and 'data' in market_data and 'today' in market_data['data']:
    #             today_data = market_data['data']['today']
    #             if not today_data.empty and 'Volume' in today_data.columns:
    #                 print(f"\n{self.colors['header']}Volume Information:{Style.RESET_ALL}")
    #                 current_volume = today_data['Volume'].sum()
    #                 avg_volume = today_data['Volume'].mean()
    #                 volume_change = ((current_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
    #                 print(f"Current Volume: {current_volume:,.0f}")
    #                 print(f"Average Volume: {avg_volume:,.0f}")
    #                 print(f"Volume Change: {volume_change:+.1f}% vs average")

    #         # Key Factors
    #         if news_items:
    #             print(f"\n{self.colors['header']}Key Factors Affecting Price:{Style.RESET_ALL}")
    #             topics = {}
    #             for item in news_items:
    #                 for topic in item.get('topics', []):
    #                     topics[topic] = topics.get(topic, 0) + 1
                
    #             if topics:
    #                 for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
    #                     print(f"- {topic.replace('_', ' ').title()}: {count} mentions")
    #             else:
    #                 print("No significant factors identified")

    #         # Market Context
    #         if market_data and 'market_context' in market_data:
    #             context = market_data.get('market_context', {})
    #             if context:
    #                 print(f"\n{self.colors['header']}Market Context:{Style.RESET_ALL}")
    #                 for index_name, index_data in context.items():
    #                     if isinstance(index_data, dict) and 'change_pct' in index_data:
    #                         change_pct = index_data['change_pct']
    #                         color = self.colors['positive'] if change_pct >= 0 else self.colors['negative']
    #                         print(f"{index_name}: {color}{change_pct:+.2f}%{Style.RESET_ALL}")

    #         # News Analysis
    #         if news_items:
    #             print(f"\n{self.colors['header']}Recent News:{Style.RESET_ALL}")
                
    #             # Group news by source
    #             news_by_source = {}
    #             for item in news_items:
    #                 source = item.get('source', 'Unknown')
    #                 if source not in news_by_source:
    #                     news_by_source[source] = []
    #                 news_by_source[source].append(item)

    #             # Display news by source
    #             for source, items in news_by_source.items():
    #                 print(f"\n{self.colors['header']}{source} News:{Style.RESET_ALL}")
    #                 news_table = []
    #                 for item in items:
    #                     sentiment = item.get('sentiment', 0)
    #                     sentiment_color = (self.colors['positive'] if sentiment > 0.2 
    #                                     else self.colors['negative'] if sentiment < -0.2 
    #                                     else self.colors['neutral'])
                        
    #                     title = item.get('title', '')
    #                     if len(title) > 50:
    #                         title = title[:47] + "..."
                        
    #                     news_table.append([
    #                         title,
    #                         f"{sentiment_color}{sentiment:.2f}{Style.RESET_ALL}",
    #                         item.get('timestamp', 'N/A')[:10]  # Just show the date part
    #                     ])
                    
    #                 if news_table:
    #                     print(tabulate(news_table, 
    #                                 headers=["Title", "Sentiment", "Date"],
    #                                 tablefmt="grid"))

    #             print(f"\n{self.colors['info']}Total articles found: {len(news_items)}{Style.RESET_ALL}")
                
    #             # News-Price Correlation
    #             print(f"\n{self.colors['header']}Fund Price vs. Negative News Correlation:{Style.RESET_ALL}")
    #             print("This visualization shows the relationship between price movements and negative news volume.")
                
    #             # Calculate negative news counts per day
    #             news_date_map = {}
    #             for item in news_items:
    #                 date_str = item.get('timestamp', '')[:10]  # Extract date part
    #                 if not date_str:
    #                     continue
                    
    #                 if date_str not in news_date_map:
    #                     news_date_map[date_str] = {'total': 0, 'negative': 0}
                    
    #                 news_date_map[date_str]['total'] += 1
    #                 if item.get('sentiment', 0) < -0.1:
    #                     news_date_map[date_str]['negative'] += 1
                
    #             # Get price data for the week
    #             week_price_data = {}
    #             if market_data and 'data' in market_data and 'week' in market_data['data']:
    #                 week_data = market_data['data']['week']
    #                 if not week_data.empty:
    #                     for i in range(len(week_data)):
    #                         date = week_data.index[i].strftime('%Y-%m-%d')
    #                         week_price_data[date] = week_data['Close'].iloc[i]
                
    #             # Create ASCII chart representation
    #             if week_price_data and news_date_map:
    #                 print("\nPrice to Negative News Relationship (last week):")
                    
    #                 # Get common dates
    #                 common_dates = sorted(set(week_price_data.keys()) & set(news_date_map.keys()))
                    
    #                 if common_dates:
    #                     # Simplified ASCII chart (in production, use a proper chart visualization)
    #                     for date in common_dates:
    #                         price = week_price_data.get(date, 0)
    #                         neg_news = news_date_map.get(date, {}).get('negative', 0)
                            
    #                         # Create ASCII bar chart
    #                         price_bar = "█" * int(min(price / 10, 20))  # Scale price
    #                         news_bar = "█" * (neg_news * 2)  # Scale negative news
                            
    #                         print(f"{date}: Price ${price:.2f}")
    #                         print(f"       Price trend: {self.colors['info']}{price_bar}{Style.RESET_ALL}")
    #                         print(f"       Negative news ({neg_news}): {self.colors['negative']}{news_bar}{Style.RESET_ALL}")
    #                 else:
    #                     print("Insufficient data to show correlation")
                        
    #                 # Add correlation analysis
    #                 print("\nInsight: Days with higher negative news volume often correlate with price declines.")
    #                 print("For a better visualization, run this analysis in a graphical environment.")
    #             else:
    #                 print("Insufficient data to analyze price-news correlation.")

    #         # Analysis Explanation (Gemini's analysis)
    #         if analysis:
    #             print(f"\n{self.colors['header']}Analysis Explanation:{Style.RESET_ALL}")
    #             print(analysis)
                
    #             # Add observations section
    #             print(f"\n{self.colors['header']}Key Observations:{Style.RESET_ALL}")
    #             if market_data and 'data' in market_data and 'today' in market_data['data']:
    #                 today_data = market_data['data']['today']
    #                 if not today_data.empty:
    #                     price_change = today_data['Close'].iloc[-1] - today_data['Open'].iloc[0]
    #                     if price_change > 0:
    #                         print("- Stock is showing positive momentum today")
    #                     else:
    #                         print("- Stock is showing negative pressure today")
                        
    #                     if 'Volume' in today_data.columns:
    #                         avg_volume = today_data['Volume'].mean()
    #                         current_volume = today_data['Volume'].sum()
    #                         if current_volume > avg_volume:
    #                             print("- Trading volume is above average, indicating strong interest")
    #                         else:
    #                             print("- Trading volume is below average, suggesting lower activity")

    #         print(f"\n{self.colors['info']}Use 'Track Multiple Securities' for comparison with other tickers.{Style.RESET_ALL}")
            
    #     except Exception as e:
    #         print(f"{self.colors['error']}Error displaying specific analysis: {str(e)}{Style.RESET_ALL}")
    #         logger.error(f"Specific analysis display error: {str(e)}")
    #         logger.error(traceback.format_exc())          
          
            
    def view_recent_analyses(self):
        """View recently saved analyses"""
        try:
            analysis_dir = os.path.join("data", "analysis")
            if not os.path.exists(analysis_dir):
                print(f"{self.colors['warning']}No analyses found.{Style.RESET_ALL}")
                return
            
            analysis_files = [f for f in os.listdir(analysis_dir) if f.startswith("analysis_") and f.endswith(".txt")]
            
            if not analysis_files:
                print(f"{self.colors['warning']}No analyses found.{Style.RESET_ALL}")
                return
            
            # Sort by modification time (most recent first)
            analysis_files.sort(key=lambda f: os.path.getmtime(os.path.join(analysis_dir, f)), reverse=True)
            
            # Display 10 most recent analyses
            recent_files = analysis_files[:10]
            
            print(f"\n{self.colors['header']}Recent Analyses:{Style.RESET_ALL}")
            
            for i, filename in enumerate(recent_files, 1):
                # Extract ticker and timestamp from filename
                parts = filename.replace("analysis_", "").replace(".txt", "").split("_")
                if len(parts) >= 2:
                    ticker = parts[0]
                    timestamp = "_".join(parts[1:])
                    
                    # Try to parse timestamp
                    try:
                        date_str = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = timestamp
                    
                    print(f"{i}. {ticker} - {date_str}")
            
            print(f"\n{self.colors['info']}Enter the number of the analysis to view (or 0 to cancel):{Style.RESET_ALL}")
            choice = input(f"{self.colors['prompt']}> {Style.RESET_ALL}").strip()
            
            try:
                choice_num = int(choice)
                if choice_num > 0 and choice_num <= len(recent_files):
                    selected_file = recent_files[choice_num - 1]
                    self.display_saved_analysis(os.path.join(analysis_dir, selected_file))
                elif choice_num != 0:
                    print(f"{self.colors['warning']}Invalid selection.{Style.RESET_ALL}")
            except ValueError:
                print(f"{self.colors['warning']}Invalid input. Please enter a number.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{self.colors['error']}Error viewing analyses: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Viewing analyses error: {str(e)}")
            logger.error(traceback.format_exc())

    def display_saved_analysis(self, filepath):
        """Display contents of a saved analysis file"""
        try:
            if not os.path.exists(filepath):
                print(f"{self.colors['warning']}Analysis file not found.{Style.RESET_ALL}")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n{self.colors['header']}Saved Analysis:{Style.RESET_ALL}")
            print(content)
            
        except Exception as e:
            print(f"{self.colors['error']}Error displaying analysis: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Display analysis error: {str(e)}")
            logger.error(traceback.format_exc())

    def show_help(self):
        """Display help information"""
        print(f"\n{self.colors['header']}=== NewsSense Help ==={Style.RESET_ALL}")
        print("""
=== NewsSense Help ===

NewsSense helps you understand why stocks, ETFs, and mutual funds are moving up or down.

Key Features:
1. Analyze Security - Get detailed analysis of a specific ticker
2. Ask a Question - Ask natural language questions about market movements
3. Track Multiple Securities - Compare multiple securities side-by-side
4. View Recent Analyses - Access previously saved analyses
5. News Crawler and Parsing -Using beautifulsoup

Example Questions:
- "Why is Apple up today?"
- "What happened to Nifty this week?"
- "Why did Jyothy Labs go up today?"
- "How is QQQ performing compared to the market?"
- "Any macro news impacting tech-focused stocks?"
- "What's happening with SBI AMC?"

Supported Indian Securities:
- "NIFTY50" or "^NSEI" - Nifty 50 Index
- "SENSEX" or "^BSESN" - BSE Sensex Index
- "JYOTHYLAB.NS" - Jyothy Labs
- "RELIANCE.NS" - Reliance Industries
- "TCS.NS" - Tata Consultancy Services
- "HDFCBANK.NS" - HDFC Bank""")

    def display_disclaimer(self):
        """Display legal disclaimer"""
#         print(f"\n{self.colors['warning']}DISCLAIMER:{Style.RESET_ALL}")
#         print("""
# NewsSense is for educational and informational purposes only. It does not provide 
# investment advice, and you should not rely solely on its analysis for making investment 
# decisions. The data and analysis provided may not be accurate or complete. 
# Always consult with a qualified financial advisor before making investment decisions.
# """)

    def run(self):
        """Main application loop"""
        try:
            # Display welcome banner at startup
            self.display_welcome_banner()
            
            while True:
                self.display_header()
                self.display_menu()
                
                choice = input(f"\n{self.colors['prompt']}Enter your choice (1-6): {Style.RESET_ALL}").strip()
                
                if choice == "1":
                    ticker = input(f"\n{self.colors['prompt']}Enter security ticker (e.g., AAPL, MSFT, NIFTY50): {Style.RESET_ALL}").upper().strip()
                    if ticker:
                        self.analyze_security(ticker)
                        input(f"\n{self.colors['warning']}Press Enter to continue...{Style.RESET_ALL}")
                    else:
                        print(f"{self.colors['error']}Invalid ticker symbol.{Style.RESET_ALL}")
                
                elif choice == "2":
                    query = input(f"\n{self.colors['prompt']}Ask a question (e.g., 'Why is AAPL up today?'): {Style.RESET_ALL}").strip()
                    if query:
                        self.process_query(query)
                        input(f"\n{self.colors['warning']}Press Enter to continue...{Style.RESET_ALL}")
                    else:
                        print(f"{self.colors['error']}Invalid query.{Style.RESET_ALL}")
                
                elif choice == "3":
                    self.track_multiple_securities()
                    input(f"\n{self.colors['warning']}Press Enter to continue...{Style.RESET_ALL}")
                
                elif choice == "4":
                    self.view_recent_analyses()
                    input(f"\n{self.colors['warning']}Press Enter to continue...{Style.RESET_ALL}")
                
                elif choice == "5":
                    self.show_help()
                    self.display_disclaimer()
                    input(f"\n{self.colors['warning']}Press Enter to continue...{Style.RESET_ALL}")
                
                elif choice == "6":
                    print(f"\n{self.colors['success']}Thank you for using NewsSense!{Style.RESET_ALL}")
                    break
                
                else:
                    print(f"{self.colors['error']}Invalid choice. Please try again.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{self.colors['warning']}Exiting...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{self.colors['error']}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            sys.exit(0)
    
    def display_welcome_banner(self):
        """Display welcome banner with ASCII art"""
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("=" * 80)
        print(r"""
  _   _                 _____                      
 | \ | |               / ____|                     
 |  \| | _____      __| (___   ___ _ __  ___  ___ 
 | . ` |/ _ \ \ /\ / /\___ \ / _ \ '_ \/ __|/ _ \
 | |\  |  __/\ V  V / ____) |  __/ | | \__ \  __/
 |_| \_|\___| \_/\_/ |_____/ \___|_| |_|___/\___|
                                                  
 Why Is My Nifty Down?                                                 
        """)
        print("=" * 80)
        print(f"{Style.RESET_ALL}")
        
        # Print short intro
        print(f"""
{Fore.GREEN}Welcome to NewsSense - Financial News Analyzer{Style.RESET_ALL}
        
NewsSense helps investors understand market movements by connecting real-world 
news and events to financial performance. Ask natural language questions about 
your stocks, ETFs, and mutual funds to get AI-powered explanations.
        """)
        
        # Show startup delay only during first run (can be removed later)
        print(f"{Fore.YELLOW}Initializing...{Style.RESET_ALL}")
        from time import sleep
        sleep(1)  # Short delay to allow user to read banner

def main():
    """Application entry point"""
    try:
        # Start the CLI
        cli = NewsSenseCLI()
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()