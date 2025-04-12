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
        
        self.last_request_time = {}
        
        self.sources = {
        "yahoo_finance": self._scrape_yahoo_finance,
        "marketwatch": self._scrape_marketwatch,
        "reuters": self._scrape_reuters,
        "cnbc": self._scrape_cnbc,
        "seeking_alpha": self._scrape_seeking_alpha,
        "investing_com": self._scrape_investing_com,
        "benzinga": self._scrape_benzinga,
        "finviz": self._scrape_finviz,
        "thefly": self._scrape_thefly,
        "zacks": self._scrape_zacks,
        "barrons": self._scrape_barrons,
        "bloomberg": self._scrape_bloomberg
    }
        
        self.news_cache = {}
        self.cache_expiry = 3600 

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




    def _scrape_investing_com(self, ticker):
        """Scrape news from Investing.com"""
        try:
            self._rate_limit('investing_com')
            url = f"https://www.investing.com/equities/{ticker.lower()}-news"
            logger.info(f"Requesting: {url}")
            
            headers = self.get_random_headers()
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                logger.warning(f"Investing.com returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            articles = soup.find_all("div", {"class": "articleItem"})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find("a", {"class": "title"})
                    time_elem = article.find("span", {"class": "date"})
                    
                    if title_elem:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Investing.com",
                            "url": urljoin("https://www.investing.com", title_elem["href"]),
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Investing.com article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Investing.com: {str(e)}")
            return []

    def _scrape_finviz(self, ticker):
        """Scrape news from Finviz"""
        try:
            self._rate_limit('finviz')
            url = f"https://finviz.com/quote.ashx?t={ticker.lower()}"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"Finviz returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            news_table = soup.find("table", {"class": "news-table"})
            
            if news_table:
                rows = news_table.find_all("tr")
                for row in rows[:10]:
                    try:
                        cols = row.find_all("td")
                        if len(cols) >= 2:
                            time_col = cols[0]
                            news_col = cols[1]
                            link = news_col.find("a")
                            
                            if link:
                                item = {
                                    "title": link.text.strip(),
                                    "summary": "",
                                    "source": "Finviz",
                                    "url": link["href"],
                                    "timestamp": time_col.text.strip()
                                }
                                news_items.append(item)
                    except Exception as e:
                        logger.error(f"Error parsing Finviz article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Finviz: {str(e)}")
            return []




    def _scrape_thefly(self, ticker):
        """Scrape news from TheFly"""
        try:
            self._rate_limit('thefly')
            url = f"https://thefly.com/news.php?symbol={ticker}"
            logger.info(f"Requesting: {url}")
            
            response = self._make_request(url, 'thefly')
            if not response or response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # Find news items - adjust selectors based on actual HTML structure
            articles = soup.find_all("div", {"class": "news_item"})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find("div", {"class": "headline"})
                    time_elem = article.find("div", {"class": "time"})
                    link = article.find("a")
                    
                    if title_elem and link:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "TheFly",
                            "url": urljoin("https://thefly.com", link["href"]),
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing TheFly article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping TheFly: {str(e)}")
            return []

    def _scrape_barrons(self, ticker):
        """Scrape news from Barron's"""
        try:
            self._rate_limit('barrons')
            url = f"https://www.barrons.com/quote/stock/{ticker}"
            logger.info(f"Requesting: {url}")
            
            response = self._make_request(url, 'barrons')
            if not response or response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # Find news items - adjust selectors based on actual HTML structure
            articles = soup.find_all("div", {"class": "article-wrap"})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find("h3", {"class": "article-title"})
                    time_elem = article.find("time")
                    link = article.find("a")
                    
                    if title_elem and link:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Barron's",
                            "url": urljoin("https://www.barrons.com", link["href"]),
                            "timestamp": time_elem["datetime"] if time_elem and time_elem.has_attr("datetime") 
                                    else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Barron's article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Barron's: {str(e)}")
            return []

    def _scrape_bloomberg(self, ticker):
        """Scrape news from Bloomberg"""
        try:
            self._rate_limit('bloomberg')
            url = f"https://www.bloomberg.com/quote/{ticker}:US"
            logger.info(f"Requesting: {url}")
            
            response = self._make_request(url, 'bloomberg')
            if not response or response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # Find news items - adjust selectors based on actual HTML structure
            articles = soup.find_all("div", {"class": "story-list-story"})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find("h3", {"class": "story-list-story__headline"})
                    time_elem = article.find("time", {"class": "story-list-story__time"})
                    link = article.find("a")
                    
                    if title_elem and link:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Bloomberg",
                            "url": urljoin("https://www.bloomberg.com", link["href"]),
                            "timestamp": time_elem["datetime"] if time_elem and time_elem.has_attr("datetime") 
                                    else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Bloomberg article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Bloomberg: {str(e)}")
            return []
    
    def _scrape_benzinga(self, ticker):
        """Scrape news from Benzinga"""
        try:
            self._rate_limit('benzinga')
            url = f"https://www.benzinga.com/stock/{ticker.lower()}"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"Benzinga returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            articles = soup.find_all("div", {"class": "news-article"})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find("h3")
                    time_elem = article.find("time")
                    link = article.find("a")
                    
                    if title_elem and link:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Benzinga",
                            "url": urljoin("https://www.benzinga.com", link["href"]),
                            "timestamp": time_elem["datetime"] if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Benzinga article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Benzinga: {str(e)}")
            return []

    def _scrape_zacks(self, ticker):
        """Scrape news from Zacks"""
        try:
            self._rate_limit('zacks')
            url = f"https://www.zacks.com/stock/quote/{ticker}/news"
            logger.info(f"Requesting: {url}")
            
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            if response.status_code != 200:
                logger.warning(f"Zacks returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            articles = soup.find_all("div", {"class": "news_item"})
            
            for article in articles[:10]:
                try:
                    title_elem = article.find("h4", {"class": "news_heading"})
                    time_elem = article.find("span", {"class": "news_date"})
                    link = title_elem.find("a") if title_elem else None
                    
                    if title_elem and link:
                        item = {
                            "title": title_elem.text.strip(),
                            "summary": "",
                            "source": "Zacks",
                            "url": urljoin("https://www.zacks.com", link["href"]),
                            "timestamp": time_elem.text.strip() if time_elem else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        news_items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing Zacks article: {str(e)}")
            
            return news_items
        except Exception as e:
            logger.error(f"Error scraping Zacks: {str(e)}")
            return []
    
    

    def _rate_limit(self, source):
        """Enhanced rate limiting with exponential backoff"""
        current_time = time.time()
        if source in self.last_request_time:
            time_passed = current_time - self.last_request_time[source]
            min_delay = random.uniform(2.0, 4.0)  # Random delay between 2-4 seconds
            
            if time_passed < min_delay:
                delay = min_delay - time_passed + random.uniform(0.5, 1.5)
                logger.debug(f"Rate limiting {source}. Sleeping for {delay:.2f} seconds")
                time.sleep(delay)
        
        # Add jitter to prevent pattern detection
        time.sleep(random.uniform(0.1, 0.3))
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


    def _make_request(self, url, source, max_retries=3):
        """Make HTTP request with retry mechanism"""
        for attempt in range(max_retries):
            try:
                self._rate_limit(source)
                headers = self.get_random_headers()
                
                # Add random proxy selection if needed
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too Many Requests
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    logger.warning(f"{source} rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"{source} returned status code {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {source}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                return None
        
        return None

    def _clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.split())