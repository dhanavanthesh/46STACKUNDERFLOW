 
from colorama import init, Fore, Style
from tabulate import tabulate
import os

init()  # Initialize colorama

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}{Style.BRIGHT}Error: {text}{Style.RESET_ALL}")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def format_price_movement(price_analysis):
    """Format price movement data"""
    if not price_analysis:
        return "No price data available"
    
    direction = price_analysis['direction']
    color = Fore.GREEN if direction == 'up' else Fore.RED
    
    return (
        f"{color}Current Price: ${price_analysis['current_price']:.2f}\n"
        f"Change: ${price_analysis['change']:.2f} ({price_analysis['change_percent']:.2f}%){Style.RESET_ALL}"
    )

def format_news_analysis(news_analysis):
    """Format news analysis data"""
    if not news_analysis:
        return "No news analysis available"
    
    # Format sentiment color based on label
    sentiment_label = news_analysis['sentiment_label']
    if 'Positive' in sentiment_label:
        sentiment_color = Fore.GREEN
    elif 'Negative' in sentiment_label:
        sentiment_color = Fore.RED
    else:
        sentiment_color = Fore.YELLOW
    
    # Create news table
    news_table = []
    for item in news_analysis['news_items']:
        news_table.append([
            item['title'],
            f"{item['sentiment']:.2f}",
            item['url']
        ])
    
    return (
        f"\nOverall Sentiment: {sentiment_color}{sentiment_label}{Style.RESET_ALL}\n"
        f"Average Sentiment Score: {news_analysis['average_sentiment']:.2f}\n\n"
        f"Recent News:\n"
        f"{tabulate(news_table, headers=['Title', 'Sentiment', 'URL'], tablefmt='grid')}"
    )