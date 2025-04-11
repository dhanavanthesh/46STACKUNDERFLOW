import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from urllib.parse import urljoin
import time

class NewsCollector:
    def __init__(self):
        self.news_dir = "data/scraped_news"
        os.makedirs(self.news_dir, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        # Add timestamps for rate limiting
        self.last_request_time = {}

    def scrape_all_sources(self, ticker):
        """Scrape news from multiple sources"""
        print(f"\nScraping news for {ticker}...")
        all_news = []

        # Yahoo Finance
        print("Scraping Yahoo Finance...")
        yahoo_news = self._scrape_yahoo_finance(ticker)
        if yahoo_news:
            print(f"Found {len(yahoo_news)} articles from Yahoo Finance")
            all_news.extend(yahoo_news)

        # MarketWatch
        print("Scraping MarketWatch...")
        marketwatch_news = self._scrape_marketwatch(ticker)
        if marketwatch_news:
            print(f"Found {len(marketwatch_news)} articles from MarketWatch")
            all_news.extend(marketwatch_news)

        # Reuters
        print("Scraping Reuters...")
        reuters_news = self._scrape_reuters(ticker)
        if reuters_news:
            print(f"Found {len(reuters_news)} articles from Reuters")
            all_news.extend(reuters_news)

        # Save the scraped news
        if all_news:
            self._save_news(ticker, all_news)
            print(f"Total articles found: {len(all_news)}")
        else:
            print("No news articles found")

        return all_news

    def _rate_limit(self, source):
        """Implement rate limiting for requests"""
        current_time = time.time()
        if source in self.last_request_time:
            time_passed = current_time - self.last_request_time[source]
            if time_passed < 1:  # Minimum 1 second between requests
                time.sleep(1 - time_passed)
        self.last_request_time[source] = time.time()

    def _scrape_yahoo_finance(self, ticker):
        """Scrape news from Yahoo Finance"""
        try:
            self._rate_limit('yahoo')
            url = f"https://finance.yahoo.com/quote/{ticker}/news"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"class": "Py(14px)"})
            
            for article in articles[:10]:  # Get top 10 news items
                title_elem = article.find("h3")
                summary_elem = article.find("p")
                link_elem = article.find("a")
                time_elem = article.find("span", {"class": "C($c-fuji-grey-j)"})
                
                if title_elem and link_elem:
                    news_items.append({
                        "title": title_elem.text.strip(),
                        "summary": summary_elem.text.strip() if summary_elem else "",
                        "source": "Yahoo Finance",
                        "url": urljoin("https://finance.yahoo.com", link_elem["href"]),
                        "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            return news_items
        except Exception as e:
            print(f"Error scraping Yahoo Finance: {str(e)}")
            return []

    def _scrape_marketwatch(self, ticker):
        """Scrape news from MarketWatch"""
        try:
            self._rate_limit('marketwatch')
            url = f"https://www.marketwatch.com/investing/stock/{ticker}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"class": "article__content"})
            
            for article in articles[:5]:
                title_elem = article.find("a", {"class": "link"})
                time_elem = article.find("span", {"class": "article__timestamp"})
                
                if title_elem:
                    news_items.append({
                        "title": title_elem.text.strip(),
                        "summary": "",
                        "source": "MarketWatch",
                        "url": title_elem["href"] if title_elem.has_attr("href") else "",
                        "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            return news_items
        except Exception as e:
            print(f"Error scraping MarketWatch: {str(e)}")
            return []

    def _scrape_reuters(self, ticker):
        """Scrape news from Reuters"""
        try:
            self._rate_limit('reuters')
            url = f"https://www.reuters.com/companies/{ticker}.O"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"data-testid": "media-story-card"})
            
            for article in articles[:5]:
                title_elem = article.find("a", {"data-testid": "heading-link"})
                time_elem = article.find("time")
                
                if title_elem:
                    news_items.append({
                        "title": title_elem.text.strip(),
                        "summary": "",
                        "source": "Reuters",
                        "url": urljoin("https://www.reuters.com", title_elem["href"]),
                        "timestamp": time_elem["datetime"] if time_elem and time_elem.has_attr("datetime") 
                                   else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            return news_items
        except Exception as e:
            print(f"Error scraping Reuters: {str(e)}")
            return []

    def _save_news(self, ticker, news_items):
        """Save scraped news to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ticker}_news_{timestamp}.json"
            filepath = os.path.join(self.news_dir, filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save the news items
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, indent=4, ensure_ascii=False)
            
            print(f"News saved to {filepath}")
        except Exception as e:
            print(f"Error saving news: {str(e)}")

    def _clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.split())