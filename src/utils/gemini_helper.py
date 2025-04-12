import os
import requests
import json
import logging
from datetime import datetime
from difflib import get_close_matches

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("gemini_helper.log"), logging.StreamHandler()]
)
logger = logging.getLogger("GeminiHelper")

class GeminiHelper:
    def __init__(self, api_key: str = None, alpha_vantage_key: str = None):
        """Initialize the Gemini helper"""
        # Gemini API key
        self.api_key = (
            api_key or 
            os.getenv("GEMINI_API_KEY") or 
            "AIzaSyDBhdcypT-HFiKaxXbuGylRS25n3vtPESo"
        )
        
        # Alpha Vantage API key
        self.alpha_vantage_key = (
            alpha_vantage_key or 
            os.getenv("ALPHA_VANTAGE_KEY") or 
            "BG3460J22Y3PF2OK"
        )
        
        # URLs
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.alpha_vantage_url = "https://www.alphavantage.co/query"
        
        # Ensure cache directory exists
        os.makedirs("data/gemini_cache", exist_ok=True)
        
        # Initialize caches
        self.query_cache = {}
        self.ticker_cache = {}
        self.cache_expiry = 3600
        
        # Load ETF and stock mappings
        self.mappings = self._load_mappings()
        logger.info("Gemini helper initialized successfully")

    def _load_mappings(self):
        """Load all mappings including ETFs and investment companies"""
        return {
            # Investment Companies and their main ETFs
            "vanguard": "VTI",
            "fidelity": "FXAIX",
            "blackrock": "IVV",
            
            # ETFs
            "vti": "VTI",
            "vanguard total market": "VTI",
            "total stock market": "VTI",
            "spy": "SPY",
            "s&p etf": "SPY",
            "qqq": "QQQ",
            "nasdaq etf": "QQQ",
            "voo": "VOO",
            "vanguard 500": "VOO",
            "bnd": "BND",
            "vea": "VEA",
            "vwo": "VWO",
            
            # Stocks
            "apple": "AAPL",
            "appl": "AAPL",
            "appple": "AAPL",
            "microsoft": "MSFT",
            "meta": "META",
            "facebook": "META",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
        }

    def extract_query_components(self, query_text):
        """Extract components with enhanced company and ETF detection"""
        try:
            # Check for investment companies first
            companies = {
                "vanguard": ["VTI", "VOO", "BND"],
                "fidelity": ["FXAIX", "FNILX", "FZROX"],
                "blackrock": ["IVV", "IEFA", "AGG"]
            }
            
            query_lower = query_text.lower()
            components = {
                "tickers": [],
                "company_name": [],
                "timeframe": "recent",
                "direction": None,
                "intent": "company_news",
                "news": []
            }

            # Check for company mentions
            for company, default_tickers in companies.items():
                if company in query_lower:
                    components["company_name"].append(company.title())
                    components["tickers"].extend(default_tickers)
                    
                    # Get news for the main ticker
                    news = self._get_company_news(default_tickers[0])
                    if news:
                        components["news"].extend(news)

            if components["company_name"]:
                components["company_name"] = ", ".join(components["company_name"])
                logger.info(f"Found companies: {components['company_name']} with tickers: {components['tickers']}")
                return components

            # If no companies found, try Gemini API
            url = f"{self.base_url}?key={self.api_key}"
            
            prompt = f"""
            Analyze this financial market query: "{query_text}"
            Identify any investment companies (Vanguard, Fidelity, BlackRock) or their products.
            
            Return a JSON object with:
            {{
                "companies": ["company names"],
                "tickers": ["ETF or stock tickers"],
                "timeframe": "recent/today/this_week",
                "intent": "company_news/price_movement"
            }}
            """

            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1024
                }
            }

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result:
                    gemini_analysis = self._extract_json_from_response(
                        result['candidates'][0]['content']['parts'][0]['text']
                    )
                    
                    if gemini_analysis and gemini_analysis.get("companies"):
                        components["company_name"] = ", ".join(gemini_analysis["companies"])
                        components["tickers"] = gemini_analysis.get("tickers", [])
                        components["timeframe"] = gemini_analysis.get("timeframe", "recent")
                        components["intent"] = gemini_analysis.get("intent", "company_news")
                        
                        # Get news for the first ticker
                        if components["tickers"]:
                            news = self._get_company_news(components["tickers"][0])
                            if news:
                                components["news"] = news
                        
                        return components

            # If still no results, try Alpha Vantage search
            if not components["tickers"]:
                words = query_lower.split()
                for word in words:
                    if word in self.mappings:
                        ticker = self.mappings[word]
                        if self._verify_ticker(ticker):
                            components["tickers"].append(ticker)
                            components["company_name"] = word.title()
                            
                            # Get news
                            news = self._get_company_news(ticker)
                            if news:
                                components["news"] = news
                            break

            return components

        except Exception as e:
            logger.error(f"Error in extract_query_components: {str(e)}")
            return {
                "tickers": [],
                "company_name": None,
                "timeframe": "recent",
                "direction": None,
                "intent": "error",
                "news": []
            }

    def _search_company_tickers(self, company_name):
        """Search for tickers related to a company using Alpha Vantage"""
        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": company_name,
                "apikey": self.alpha_vantage_key
            }

            response = requests.get(self.alpha_vantage_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "bestMatches" in data:
                    tickers = []
                    for match in data["bestMatches"]:
                        ticker = match["1. symbol"]
                        if self._verify_ticker(ticker):
                            tickers.append(ticker)
                    return tickers
            return []

        except Exception as e:
            logger.error(f"Error searching company tickers: {str(e)}")
            return []

    def _get_company_news(self, ticker):
        """Get news for a company using Alpha Vantage"""
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": ticker,
                "apikey": self.alpha_vantage_key
            }

            response = requests.get(self.alpha_vantage_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "feed" in data:
                    return data["feed"][:5]
            return []

        except Exception as e:
            logger.error(f"Error getting company news: {str(e)}")
            return []

    def _verify_ticker(self, ticker):
        """Verify ticker using Alpha Vantage"""
        try:
            # Check cache
            if ticker in self.ticker_cache:
                return self.ticker_cache[ticker]

            # Common ETFs don't need verification
            if ticker in ["VTI", "SPY", "QQQ", "VOO", "BND", "VEA", "VWO", "FXAIX", "IVV"]:
                self.ticker_cache[ticker] = True
                return True

            # Verify with Alpha Vantage
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": self.alpha_vantage_key
            }

            response = requests.get(self.alpha_vantage_url, params=params)
            if response.status_code == 200:
                data = response.json()
                is_valid = "Global Quote" in data and data["Global Quote"]
                self.ticker_cache[ticker] = is_valid
                logger.info(f"Alpha Vantage verification for {ticker}: {is_valid}")
                return is_valid

            logger.warning(f"Alpha Vantage API error: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Error verifying ticker {ticker}: {str(e)}")
            return False

    def _extract_json_from_response(self, text):
        """Extract JSON from response"""
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return None