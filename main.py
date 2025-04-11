from datetime import datetime, UTC
import sys
import os
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama for cross-platform color support
init(autoreset=True)

class MarketAnalysisCLI:
    def __init__(self):
        """Initialize the CLI interface with required components"""
        try:
            from src.news_scraper.news_collector import NewsCollector
            from src.analyzer.market_analyzer import MarketAnalyzer
            
            self.news_collector = NewsCollector()
            self.market_analyzer = MarketAnalyzer()
            self.user = os.getenv('USERNAME', 'User')
            self.setup_display_settings()
            
            # Create necessary directories
            os.makedirs(os.path.join("data", "analysis"), exist_ok=True)
            
        except Exception as e:
            print(f"{Fore.RED}Error initializing the application: {str(e)}{Style.RESET_ALL}")
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
            'neutral': Fore.YELLOW
        }
        self.formats = {
            'timestamp': '%Y-%m-%d %H:%M:%S',
            'date': '%Y-%m-%d',
            'currency': '${:,.2f}'
        }

    def display_header(self):
        """Display application header with current time and user information"""
        try:
            current_time = datetime.now(UTC).strftime(self.formats['timestamp'])
            print(f"\n{self.colors['header']}=== Market Analysis Tool ==={Style.RESET_ALL}")
            print(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {current_time}")
            print(f"Current User's Login: {self.user}")
            print("=" * 50)
        except Exception as e:
            print(f"{self.colors['error']}Error displaying header: {str(e)}{Style.RESET_ALL}")

    def save_analysis_to_file(self, ticker, analysis_data):
        """Save analysis results to a text file"""
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_{ticker}_{timestamp}.txt"
            filepath = os.path.join("data", "analysis", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== Market Analysis for {ticker} ===\n")
                f.write(f"Analysis Date: {datetime.now(UTC).strftime(self.formats['timestamp'])}\n\n")
                
                # Write company information
                if 'info' in analysis_data:
                    f.write("Company Information:\n")
                    f.write(f"Name: {analysis_data['info'].get('longName', ticker)}\n")
                    f.write(f"Sector: {analysis_data['info'].get('sector', 'N/A')}\n")
                    f.write(f"Industry: {analysis_data['info'].get('industry', 'N/A')}\n")
                    f.write(f"Website: {analysis_data['info'].get('website', 'N/A')}\n\n")
                
                # Write price information
                if 'price' in analysis_data:
                    f.write("Price Information:\n")
                    f.write(f"Current Price: ${analysis_data['price'].get('current', 'N/A')}\n")
                    f.write(f"Change: {analysis_data['price'].get('change', 'N/A')}\n")
                    f.write(f"Change %: {analysis_data['price'].get('change_percent', 'N/A')}%\n")
                    f.write(f"Day Range: {analysis_data['price'].get('day_range', 'N/A')}\n\n")
                
                # Write volume information
                if 'volume' in analysis_data:
                    f.write("Volume Information:\n")
                    f.write(f"Current Volume: {analysis_data['volume'].get('current', 'N/A'):,}\n")
                    f.write(f"Average Volume: {analysis_data['volume'].get('average', 'N/A'):,}\n")
                    f.write(f"Volume Change: {analysis_data['volume'].get('change', 'N/A')}%\n\n")
                
                # Write key factors
                if 'factors' in analysis_data:
                    f.write("Key Factors Affecting Price:\n")
                    for factor, count in analysis_data['factors'].items():
                        if count > 0:
                            f.write(f"- {factor.replace('_', ' ').title()}: {count} mentions\n")
                    f.write("\n")
                
                # Write market context
                if 'market_context' in analysis_data:
                    f.write("Market Context:\n")
                    for index, data in analysis_data['market_context'].items():
                        if isinstance(data, dict) and 'change_pct' in data:
                            f.write(f"- {index}: {data['change_pct']:+.2f}%\n")
                    f.write("\n")
                
                # Write news items
                if 'news' in analysis_data and analysis_data['news']:
                    f.write("Recent News:\n")
                    for news_item in analysis_data['news']:
                        f.write(f"Title: {news_item.get('title', 'N/A')}\n")
                        f.write(f"Source: {news_item.get('source', 'N/A')}\n")
                        f.write(f"Sentiment: {news_item.get('sentiment', 0):.2f}\n")
                        f.write(f"URL: {news_item.get('url', 'N/A')}\n")
                        f.write("-" * 50 + "\n")
                
            print(f"\n{self.colors['success']}Analysis saved to {filepath}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{self.colors['error']}Error saving analysis: {str(e)}{Style.RESET_ALL}")

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
            
            # Prepare analysis data for saving
            if security_data and 'data' in security_data and 'today' in security_data['data']:
                today_data = security_data['data']['today']
                if not today_data.empty:
                    current_price = today_data['Close'].iloc[-1]
                    open_price = today_data['Open'].iloc[0]
                    
                    analysis_data = {
                        'info': security_data.get('info', {}),
                        'price': {
                            'current': current_price,
                            'change': current_price - open_price,
                            'change_percent': ((current_price - open_price) / open_price) * 100,
                            'day_range': f"${today_data['Low'].min():.2f} - ${today_data['High'].max():.2f}"
                        },
                        'volume': {
                            'current': today_data['Volume'].iloc[-1],
                            'average': today_data['Volume'].mean(),
                            'change': ((today_data['Volume'].iloc[-1] - today_data['Volume'].mean())
                                      / today_data['Volume'].mean() * 100)
                        },
                        'factors': news_analysis.get('topics', {}),
                        'market_context': security_data.get('market_context', {}),
                        'news': news_analysis.get('sentiments', [])
                    }
                    
                    # Display results
                    self.display_results(ticker, security_data, news_analysis, explanation)
                    
                    # Save analysis
                    self.save_analysis_to_file(ticker, analysis_data)
            
        except Exception as e:
            print(f"{self.colors['error']}Error in security analysis: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()

    def display_results(self, ticker, security_data, news_analysis, explanation):
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
                for topic, count in news_analysis['topics'].items():
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
            if news_analysis and isinstance(news_analysis, dict):
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
                            sentiment_color = (self.colors['positive'] if sentiment > 0 
                                            else self.colors['negative'] if sentiment < 0 
                                            else self.colors['neutral'])
                            
                            title = item.get('title', '')
                            if len(title) > 50:
                                title = title[:47] + "..."
                            
                            news_table.append([
                                title,
                                f"{sentiment_color}{sentiment:.2f}{Style.RESET_ALL}",
                                item.get('timestamp', 'N/A')
                            ])
                        
                        if news_table:
                            print(tabulate(news_table, 
                                        headers=["Title", "Sentiment", "Time"],
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
            import traceback
            traceback.print_exc()
            
    def format_price(self, price):
        """Format price with currency symbol"""
        try:
            return self.formats['currency'].format(price)
        except:
            return str(price)

    def run(self):
        """Main application loop"""
        try:
            while True:
                self.display_header()
                print("\nOptions:")
                print("1. Analyze Security")
                print("2. Exit")
                
                choice = input("\nEnter your choice (1-2): ").strip()
                
                if choice == "1":
                    ticker = input("\nEnter security ticker (e.g., QQQ, AAPL, MSFT): ").upper().strip()
                    if ticker:
                        self.analyze_security(ticker)
                        input(f"\n{self.colors['warning']}Press Enter to continue...{Style.RESET_ALL}")
                    else:
                        print(f"{self.colors['error']}Invalid ticker symbol.{Style.RESET_ALL}")
                        
                elif choice == "2":
                    print(f"\n{self.colors['success']}Thank you for using Market Analysis Tool!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{self.colors['error']}Invalid choice. Please try again.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{self.colors['warning']}Exiting...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{self.colors['error']}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
        finally:
            sys.exit(0)

def main():
    """Application entry point"""
    try:
        cli = MarketAnalysisCLI()
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()