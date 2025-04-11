#!/usr/bin/env python3
"""
NewsSense - "Why Is My Nifty Down?"
A financial news analysis system that explains market movements.
"""

import sys
import os
import logging
from datetime import datetime
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Setup logging
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
            # Import components
            from src.news_scraper.news_collector import NewsCollector
            from src.analyzer.market_analyzer import MarketAnalyzer
            from src.query_processor.query_processor import QueryProcessor
            
            # Initialize components
            self.news_collector = NewsCollector()
            self.market_analyzer = MarketAnalyzer()
            self.query_processor = QueryProcessor(self.news_collector, self.market_analyzer)
            
            # Get username
            self.user = os.getenv('USERNAME', 'User')
            
            # Setup display settings
            self.setup_display_settings()
            
            # Create necessary directories
            os.makedirs(os.path.join("data", "analysis"), exist_ok=True)
            os.makedirs(os.path.join("data", "scraped_news"), exist_ok=True)
            os.makedirs(os.path.join("data", "market_data"), exist_ok=True)
            
            logger.info("NewsSense initialized successfully")
            
        except Exception as e:
            print(f"{Fore.RED}Error initializing the application: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Initialization error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            sys.exit(1)

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
            print(f"Welcome, {self.user}!")
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

    def process_query(self, query):
        """Process natural language query about market data"""
        try:
            print(f"\n{self.colors['info']}Processing your query: \"{query}\"{Style.RESET_ALL}")
            print(f"{self.colors['info']}This may take a moment as I gather market data and news...{Style.RESET_ALL}")
            
            # Process the query
            response = self.query_processor.process_query(query)
            
            if not response.get('success', False):
                print(f"\n{self.colors['error']}{response.get('message', 'Failed to process query.')}{Style.RESET_ALL}")
                return
            
            # Display the answer
            if response.get('answer'):
                print(f"\n{self.colors['success']}Answer:{Style.RESET_ALL}")
                print(response['answer'])
            
            # Display detailed explanation
            if response.get('explanation'):
                print(f"\n{self.colors['header']}Detailed Explanation:{Style.RESET_ALL}")
                print(response['explanation'])
            
            # Summarize the data processed
            ticker_count = len(response.get('security_data', {}))
            news_count = sum(len(data.get('sentiments', [])) 
                           for data in response.get('news_data', {}).values())
            
            print(f"\n{self.colors['info']}Analysis based on {ticker_count} securities and {news_count} news articles.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{self.colors['error']}Error processing query: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Query processing error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def analyze_security(self, ticker):
        """Perform comprehensive security analysis"""
        try:
            print(f"\n{self.colors['info']}Analyzing {ticker}...{Style.RESET_ALL}")
            
            # Get security data
            print(f"{self.colors['info']}Fetching market data...{Style.RESET_ALL}")
            security_data = self.market_analyzer.analyze_security(ticker)
            if not security_data:
                print(f"{self.colors['error']}Failed to fetch market data for {ticker}{Style.RESET_ALL}")
                return
            
            # Get news
            print(f"{self.colors['info']}Collecting news from multiple sources...{Style.RESET_ALL}")
            news_items = self.news_collector.scrape_all_sources(ticker)
            
            # Analyze news
            print(f"{self.colors['info']}Analyzing news and market context...{Style.RESET_ALL}")
            news_analysis = self.market_analyzer.analyze_news_impact(news_items)
            
            # Generate explanation
            explanation = self.market_analyzer.generate_explanation(security_data, news_analysis, ticker)
            
            # Display results
            self.display_analysis_results(ticker, security_data, news_analysis, explanation)
            
        except Exception as e:
            print(f"{self.colors['error']}Error in security analysis: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Security analysis error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

    def display_analysis_results(self, ticker, security_data, news_analysis, explanation):
        """Display comprehensive analysis results"""
        try:
            print(f"\n{self.colors['header']}=== Analysis Results for {ticker} ==={Style.RESET_ALL}")
            
            # Company Information
            if security_data and 'info' in security_data and security_data['info']:
                info = security_data['info']
                print(f"\n{self.colors['header']}Company Information:{Style.RESET_ALL}")
                print(f"Name: {info.get('longName', ticker)}")
                print(f"Sector: {info.get('sector', 'N/A')}")
                print(f"Industry: {info.get('industry', 'N/A')}")
                print(f"Website: {info.get('website', 'N/A')}")

            # Price Information
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

            # Volume Information
            if security_data and 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty and 'Volume' in today_data.columns:
                    print(f"\n{self.colors['header']}Volume Information:{Style.RESET_ALL}")
                    current_volume = today_data['Volume'].iloc[-1]
                    avg_volume = today_data['Volume'].mean()
                    volume_change = ((current_volume - avg_volume) / avg_volume) * 100
                    print(f"Current Volume: {current_volume:,.0f}")
                    print(f"Average Volume: {avg_volume:,.0f}")
                    print(f"Volume Change: {volume_change:+.1f}% vs average")

            # Key Factors
            if news_analysis and 'topics' in news_analysis:
                print(f"\n{self.colors['header']}Key Factors Affecting Price:{Style.RESET_ALL}")
                has_factors = False
                for topic, count in sorted(news_analysis['topics'].items(), key=lambda x: x[1], reverse=True):
                    if count > 0:
                        has_factors = True
                        print(f"- {topic.replace('_', ' ').title()}: {count} mentions")
                if not has_factors:
                    print("No significant factors identified")

            # Market Context
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
            import traceback
            logger.error(traceback.format_exc())
            
    def format_price(self, price):
        """Format price with currency symbol"""
        try:
            return self.formats['currency'].format(price)
        except:
            return str(price)

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
            
            # Display comparison table
            if securities_data:
                print(f"\n{self.colors['header']}Securities Comparison:{Style.RESET_ALL}")
                
                table_data = []
                for data in sorted(securities_data, key=lambda x: abs(x['change_pct']), reverse=True):
                    change_color = self.colors['positive'] if data['change_pct'] >= 0 else self.colors['negative']
                    sentiment_color = (self.colors['positive'] if data['news_sentiment'] > 0.1 
                                    else self.colors['negative'] if data['news_sentiment'] < -0.1 
                                    else self.colors['neutral'])
                    
                    table_data.append([
                        data['ticker'],
                        data['name'][:20] + ('...' if len(data['name']) > 20 else ''),
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
            import traceback
            logger.error(traceback.format_exc())

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
            import traceback
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

    def show_help(self):
        """Display help information"""
        print(f"\n{self.colors['header']}=== NewsSense Help ==={Style.RESET_ALL}")
        print("""
NewsSense helps you understand why stocks, ETFs, and mutual funds are moving up or down.

Key Features:
1. Analyze Security - Get detailed analysis of a specific ticker
2. Ask a Question - Ask natural language questions about market movements
3. Track Multiple Securities - Compare multiple securities side-by-side
4. View Recent Analyses - Access previously saved analyses

Example Questions:
- "Why is Apple up today?"
- "What happened to Tesla this week?"
- "Explain the recent drop in Amazon"
- "How is Microsoft performing compared to the market?"
- "Any macro news impacting tech-focused stocks?"
        """)

    def run(self):
        """Main application loop"""
        try:
            while True:
                self.display_header()
                self.display_menu()
                
                choice = input(f"\n{self.colors['prompt']}Enter your choice (1-6): {Style.RESET_ALL}").strip()
                
                if choice == "1":
                    ticker = input(f"\n{self.colors['prompt']}Enter security ticker (e.g., AAPL, MSFT): {Style.RESET_ALL}").upper().strip()
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
            import traceback
            logger.error(traceback.format_exc())
        finally:
            sys.exit(0)

def main():
    """Application entry point"""
    try:
        # Display startup banner
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
        
        # Start the CLI
        cli = NewsSenseCLI()
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Fatal error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()