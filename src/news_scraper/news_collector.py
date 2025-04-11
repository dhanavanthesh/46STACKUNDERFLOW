import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from urllib.parse import urljoin, quote
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("news_scraper.log"), logging.StreamHandler()]
)
logger = logging.getLogger("NewsCollector")

class NewsCollector:
    def __init__(self):
        self.news_dir = "data/scraped_news"
        os.makedirs(self.news_dir, exist_ok=True)
        
        # Multiple user agents to rotate
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        ]
        
        # Add timestamps for rate limiting
        self.last_request_time = {}
        
        # List of news sources to scrape
        self.sources = {
            "yahoo_finance": self._scrape_yahoo_finance,
            "marketwatch": self._scrape_marketwatch,
            "reuters": self._scrape_reuters,
            "cnbc": self._scrape_cnbc,
            "seeking_alpha": self._scrape_seeking_alpha
        }
        
        # News cache to avoid duplicate scraping
        self.news_cache = {}
        self.cache_expiry = 3600  # 1 hour in seconds

    def get_random_headers(self):
        """Generate random headers for requests"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def scrape_all_sources(self, ticker):
        """Scrape news from multiple sources with parallel execution"""
        cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d_%H')}"
        
        # Check if we have cached results
        if cache_key in self.news_cache:
            cache_time, cached_news = self.news_cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.cache_expiry:
                logger.info(f"Using cached news for {ticker}")
                return cached_news
        
        logger.info(f"Scraping news for {ticker} from multiple sources...")
        all_news = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            future_to_source = {
                executor.submit(scrape_func, ticker): source_name
                for source_name, scrape_func in self.sources.items()
            }
            
            for future in future_to_source:
                source_name = future_to_source[future]
                try:
                    news_items = future.result()
                    if news_items:
                        logger.info(f"Found {len(news_items)} articles from {source_name}")
                        all_news.extend(news_items)
                except Exception as e:
                    logger.error(f"Error in {source_name} scraper: {str(e)}")
        
        # Add entity tags to news items
        self._add_entity_tags(all_news, ticker)
        
        # Save the scraped news
        if all_news:
            self._save_news(ticker, all_news)
            logger.info(f"Total articles found for {ticker}: {len(all_news)}")
            
            # Cache the results
            self.news_cache[cache_key] = (datetime.now(), all_news)
        else:
            logger.warning(f"No news articles found for {ticker}")
        
        return all_news

    def _rate_limit(self, source):
        """Implement rate limiting for requests"""
        current_time = time.time()
        if source in self.last_request_time:
            time_passed = current_time - self.last_request_time[source]
            min_delay = 2.0  # Minimum 2 seconds between requests to same source
            if time_passed < min_delay:
                delay = min_delay - time_passed + random.uniform(0.1, 0.5)  # Add jitter
                logger.debug(f"Rate limiting {source}. Sleeping for {delay:.2f} seconds")
                time.sleep(delay)
        self.last_request_time[source] = time.time()

    def _scrape_yahoo_finance(self, ticker):
        """Scrape news from Yahoo Finance"""
        try:
            self._rate_limit('yahoo')
            url = f"https://finance.yahoo.com/quote/{ticker}/news"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"Yahoo Finance returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"class": "Py(14px)"})
            
            for article in articles[:10]:  # Get top 10 news items
                try:
                    title_elem = article.find("h3")
                    summary_elem = article.find("p")
                    link_elem = article.find("a")
                    time_elem = article.find("span", {"class": "C($c-fuji-grey-j)"})
                    
                    if title_elem and link_elem:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": summary_elem.text.strip() if summary_elem else "",
                            "source": "Yahoo Finance",
                            "url": urljoin("https://finance.yahoo.com", link_elem["href"]),
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Yahoo Finance article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Yahoo Finance: {str(e)}")
            return []

    def _scrape_marketwatch(self, ticker):
        """Scrape news from MarketWatch"""
        try:
            self._rate_limit('marketwatch')
            url = f"https://www.marketwatch.com/investing/stock/{ticker.lower()}"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"MarketWatch returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"class": "article__content"})
            
            for article in articles[:8]:
                try:
                    title_elem = article.find("a", {"class": "link"})
                    time_elem = article.find("span", {"class": "article__timestamp"})
                    
                    if title_elem:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "MarketWatch",
                            "url": title_elem["href"] if title_elem.has_attr("href") else "",
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing MarketWatch article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping MarketWatch: {str(e)}")
            return []

    def _scrape_reuters(self, ticker):
        """Scrape news from Reuters"""
        try:
            self._rate_limit('reuters')
            url = f"https://www.reuters.com/companies/{ticker.upper()}.O"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"Reuters returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"data-testid": "media-story-card"})
            
            for article in articles[:8]:
                try:
                    title_elem = article.find("a", {"data-testid": "heading-link"})
                    time_elem = article.find("time")
                    
                    if title_elem:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Reuters",
                            "url": urljoin("https://www.reuters.com", title_elem["href"]),
                            "timestamp": time_elem["datetime"] if time_elem and time_elem.has_attr("datetime") 
                                      else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Reuters article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Reuters: {str(e)}")
            return []

    def _scrape_cnbc(self, ticker):
        """Scrape news from CNBC"""
        try:
            self._rate_limit('cnbc')
            url = f"https://www.cnbc.com/quotes/{ticker.lower()}"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"CNBC returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"class": "LatestNews-item"})
            
            for article in articles[:8]:
                try:
                    title_elem = article.find("a")
                    time_elem = article.find("time") or article.find("span", {"class": "LatestNews-timestamp"})
                    
                    if title_elem:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "CNBC",
                            "url": title_elem["href"] if title_elem.has_attr("href") else "",
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing CNBC article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping CNBC: {str(e)}")
            return []

    def _scrape_seeking_alpha(self, ticker):
        """Scrape news from Seeking Alpha"""
        try:
            self._rate_limit('seeking_alpha')
            url = f"https://seekingalpha.com/symbol/{ticker.upper()}/news"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"Seeking Alpha returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_items = []
            articles = soup.find_all("div", {"data-test-id": "post-list-item"})
            
            for article in articles[:8]:
                try:
                    title_elem = article.find("a", {"data-test-id": "post-list-item-title"})
                    time_elem = article.find("span", {"data-test-id": "post-list-item-date"})
                    
                    if title_elem:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Seeking Alpha",
                            "url": urljoin("https://seekingalpha.com", title_elem["href"]),
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Seeking Alpha article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Seeking Alpha: {str(e)}")
            return []

    def _add_entity_tags(self, news_items, ticker):
        """Add relevant entity tags to news items"""
        for item in news_items:
            # Initialize entity fields
            item["entities"] = {
                "tickers": [ticker],  # Add the main ticker
                "companies": [],
                "people": [],
                "topics": []
            }
            
            # Simple keyword-based tagging
            title = item.get("title", "").lower()
            summary = item.get("summary", "").lower()
            content = title + " " + summary
            
            # Extract additional tickers (simple regex-like detection)
            import re
            additional_tickers = re.findall(r'\b[A-Z]{1,5}\b', item.get("title", "") + " " + item.get("summary", ""))
            for t in additional_tickers:
                if t != ticker and t not in ["A", "I", "S", "IT", "FOR", "ON"]:  # Filter common words in all caps
                    if t not in item["entities"]["tickers"]:
                        item["entities"]["tickers"].append(t)
            
            # Topics detection based on keywords
            topics_keywords = {
                "earnings": ["earnings", "revenue", "profit", "loss", "quarter", "financial", "eps"],
                "merger": ["merger", "acquisition", "takeover", "deal", "buy"],
                "product": ["launch", "release", "new product", "update", "unveil"],
                "leadership": ["ceo", "executive", "appoint", "resign", "management"],
                "legal": ["lawsuit", "court", "legal", "sue", "settlement"],
                "market": ["market", "index", "dow", "nasdaq", "s&p"],
                "technology": ["tech", "technology", "innovation", "patent", "ai", "artificial intelligence"],
                "economy": ["fed", "inflation", "interest rate", "economy", "economic"],
                "regulation": ["regulation", "compliance", "regulatory", "rule", "law"]
            }
            
            for topic, keywords in topics_keywords.items():
                if any(keyword in content for keyword in keywords):
                    item["entities"]["topics"].append(topic)

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
            
            logger.info(f"News saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving news: {str(e)}")
            return None

    def _clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.split())