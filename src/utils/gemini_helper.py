"""
Gemini API helper for enhanced natural language processing.
This module helps interpret user queries about financial markets.
"""

import os
import json
import logging
import requests
import time
import re
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("gemini_helper.log"), logging.StreamHandler()]
)
logger = logging.getLogger("GeminiHelper")

class GeminiHelper:
    """Helper class for Gemini API integration"""
    
    def __init__(self, api_key: str = None):
        """Initialize the Gemini helper"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or "AIzaSyDBhdcypT-HFiKaxXbuGylRS25n3vtPESo"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        # Create cache directory
        self.cache_dir = "data/gemini_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load known ticker mappings
        self.ticker_mappings = self._load_ticker_mappings()
        
        # Set rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _load_ticker_mappings(self) -> Dict[str, str]:
        """Load known company name to ticker mappings"""
        # Default mappings for common companies and indices
        default_mappings = {
            # Indian companies and indices
            "jyothy labs": "JYOTHYLAB.NS",
            "nifty": "^NSEI",
            "sensex": "^BSESN",
            "nifty 50": "^NSEI",
            "nifty50": "^NSEI",
            "swiggy": "SWIGGY.NS",  # Placeholder as Swiggy is not publicly traded
            "sbi": "SBIN.NS",
            "sbi amc": "SBIAMC.NS",  # Placeholder for SBI Asset Management Company
            "hdfc bank": "HDFCBANK.NS",
            "reliance": "RELIANCE.NS",
            "tcs": "TCS.NS",
            "infosys": "INFY.NS",
            "wipro": "WIPRO.NS",
            "icici bank": "ICICIBANK.NS",
            "larsen and toubro": "LT.NS",
            "l&t": "LT.NS",
            "itc": "ITC.NS",
            
            # US companies
            "apple": "AAPL",
            "microsoft": "MSFT",
            "amazon": "AMZN",
            "google": "GOOGL",
            "facebook": "META",
            "meta": "META",
            "tesla": "TSLA",
            "walmart": "WMT",
            "nvidia": "NVDA",
            
            # ETFs
            "invesco qqq": "QQQ",
            "qqq etf": "QQQ",
            "invesco qqq etf": "QQQ",
            "spy": "SPY",
            "spdr s&p 500": "SPY",
            "vanguard": "VOO",  # Default Vanguard ETF
            "fidelity": "FNCL",  # Default Fidelity ETF
            
            # Sectors
            "tech": "XLK",
            "technology": "XLK",
            "tech etf": "XLK",
            "technology etf": "XLK",
            "financial": "XLF",
            "financials": "XLF",
            "financial etf": "XLF",
            "healthcare": "XLV",
            "health care": "XLV",
            "healthcare etf": "XLV",
            "energy": "XLE",
            "energy etf": "XLE",
            
            # Market types
            "emerging markets": "EEM",
            "emerging market funds": "EEM",
            "em funds": "EEM",
            "developed markets": "VEA",
            "us market": "SPY",
            "s&p 500": "SPY",
            "dow jones": "DIA",
            "dow": "DIA",
            "nasdaq": "QQQ",
            "russell 2000": "IWM",
            "small cap": "IWM"
        }
        
        # Try to load custom mappings file if it exists
        mappings_file = os.path.join(self.cache_dir, "ticker_mappings.json")
        custom_mappings = {}
        
        try:
            if os.path.exists(mappings_file):
                with open(mappings_file, 'r') as f:
                    custom_mappings = json.load(f)
                logger.info(f"Loaded {len(custom_mappings)} custom ticker mappings")
        except Exception as e:
            logger.error(f"Error loading custom ticker mappings: {str(e)}")
        
        # Combine default and custom mappings (custom takes precedence)
        return {**default_mappings, **custom_mappings}
    
    def _save_ticker_mapping(self, company_name: str, ticker: str) -> None:
        """Save a new company name to ticker mapping"""
        mappings_file = os.path.join(self.cache_dir, "ticker_mappings.json")
        
        try:
            # Load existing mappings
            custom_mappings = {}
            if os.path.exists(mappings_file):
                with open(mappings_file, 'r') as f:
                    custom_mappings = json.load(f)
            
            # Add new mapping
            custom_mappings[company_name.lower()] = ticker.upper()
            
            # Save updated mappings
            with open(mappings_file, 'w') as f:
                json.dump(custom_mappings, f, indent=2)
            
            # Update in-memory mappings
            self.ticker_mappings[company_name.lower()] = ticker.upper()
            
            logger.info(f"Saved new ticker mapping: {company_name} -> {ticker}")
        except Exception as e:
            logger.error(f"Error saving ticker mapping: {str(e)}")
    
    def extract_query_components(self, query_text: str) -> Dict[str, Any]:
        """
        Extract components from a financial query using Gemini API
        
        Args:
            query_text: The user's query about financial markets
            
        Returns:
            Dictionary containing extracted components (tickers, timeframe, etc.)
        """
        # First, check if we can extract tickers from our local mappings
        components = self._extract_from_local_mappings(query_text)
        
        if components.get('tickers'):
            logger.info(f"Found tickers from local mappings: {components['tickers']}")
            return components
        
        # If no tickers found, use Gemini API (with retries for robustness)
        try:
            return self._extract_using_gemini(query_text)
        except Exception as e:
            logger.error(f"Error using Gemini API: {str(e)}")
            # If Gemini fails, fall back to our basic extraction method
            return self._extract_from_local_mappings(query_text)
    
    def _extract_from_local_mappings(self, query_text: str) -> Dict[str, Any]:
        """Extract query components using local mappings"""
        query_lower = query_text.lower()
        components = {
            'tickers': [],
            'timeframe': self._extract_timeframe(query_lower),
            'direction': self._extract_direction(query_lower),
            'intent': self._extract_intent(query_lower)
        }
        
        # Check for exact ticker symbols (2-5 uppercase letters)
        ticker_matches = re.findall(r'\b[A-Z]{1,5}\b', query_text)
        if ticker_matches:
            # Filter out common words that might be mistaken for tickers
            common_words = {'ETF', 'IPO', 'CEO', 'CFO', 'CTO', 'COO', 'WHY', 'UP', 'DOWN', 'THE'}
            components['tickers'] = [ticker for ticker in ticker_matches 
                                   if ticker not in common_words]
        
        # If no exact tickers found, look for company names in our mappings
        if not components['tickers']:
            for company, ticker in self.ticker_mappings.items():
                if company in query_lower:
                    components['tickers'].append(ticker)
                    components['company_name'] = company
                    break  # Just take the first match for now
        
        return components
    
    def _extract_timeframe(self, query_lower: str) -> str:
        """Extract timeframe from the query"""
        if 'today' in query_lower or 'now' in query_lower:
            return 'today'
        elif 'yesterday' in query_lower:
            return 'yesterday'
        elif 'this week' in query_lower or 'past week' in query_lower:
            return 'this_week'
        elif 'this month' in query_lower or 'past month' in query_lower:
            return 'this_month'
        elif 'quarter' in query_lower:
            return 'this_quarter'
        elif 'this year' in query_lower or 'past year' in query_lower or 'ytd' in query_lower:
            return 'this_year'
        else:
            return 'today'  # Default timeframe
    
    def _extract_direction(self, query_lower: str) -> Optional[str]:
        """Extract price direction from the query"""
        if any(term in query_lower for term in ['up', 'rise', 'rising', 'gain', 'grew', 'higher', 'increased', 'positive']):
            return 'up'
        elif any(term in query_lower for term in ['down', 'fall', 'falling', 'drop', 'decline', 'lower', 'decreased', 'negative']):
            return 'down'
        else:
            return None
    
    def _extract_intent(self, query_lower: str) -> str:
        """Extract query intent"""
        if any(term in query_lower for term in ['why', 'reason', 'explain', 'caused', 'causing']):
            return 'price_movement'
        elif any(term in query_lower for term in ['how', 'performance', 'performing', 'trend', 'doing']):
            return 'performance'
        elif any(term in query_lower for term in ['news', 'headlines', 'articles', 'reported', 'announced']):
            return 'news_impact'
        elif any(term in query_lower for term in ['outlook', 'forecast', 'projection', 'future', 'expectation']):
            return 'outlook'
        elif any(term in query_lower for term in ['should', 'recommend', 'buy', 'sell', 'invest']):
            return 'recommendation'
        elif any(term in query_lower for term in ['macro', 'economy', 'economic', 'interest rate', 'inflation']):
            return 'macro'
        else:
            return 'price_movement'  # Default intent
    
    def _extract_using_gemini(self, query_text: str) -> Dict[str, Any]:
        """Extract query components using Gemini API with improved error handling"""
        cache_key = query_text.lower().replace(" ", "_")[:50]
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Check if we have cached results
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_result = json.load(f)
                logger.info(f"Using cached Gemini result for query: {query_text}")
                return cached_result
            except Exception as e:
                logger.error(f"Error loading cached results: {str(e)}")
        
        # Prepare the prompt for Gemini
        prompt = f"""
        Analyze this financial market query and extract the following components:
        
        Query: "{query_text}"
        
        1. Company/ETF/Fund/Index name
        2. Ticker symbol (if mentioned or if you can infer it)
        3. Timeframe (today, this week, this month, this quarter, this year)
        4. Direction (up, down, or neutral)
        5. The intent of the query (price movement, performance, news impact, outlook, recommendation, macro)
        
        If the query mentions Indian companies, use the NSE ticker format (e.g., JYOTHYLAB.NS).
        For example, "Jyothy Labs" ticker would be "JYOTHYLAB.NS".
        
        Return your answer in this JSON format:
        {{
          "company_name": "extracted company name or null",
          "tickers": ["primary ticker symbol"],
          "timeframe": "extracted timeframe",
          "direction": "extracted direction or null",
          "intent": "extracted intent",
          "confidence": "high/medium/low"
        }}
        
        Only output the JSON, nothing else. Fix any spelling errors in the company name.
        """
        
        # Try to make the request with retry logic
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting
                self._rate_limit()
                
                # Make API request to Gemini
                response = self._call_gemini_api(prompt)
                
                if not response:
                    logger.warning(f"Empty response from Gemini API (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        return self._default_components(query_text)
                
                # Extract JSON from response
                json_str = self._extract_json_from_text(response)
                if not json_str:
                    logger.warning(f"No JSON found in Gemini response (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return self._default_components(query_text)
                
                # Parse JSON
                try:
                    result = json.loads(json_str)
                    
                    # Validate the result format
                    if not isinstance(result, dict):
                        logger.warning(f"Invalid JSON format: not a dictionary")
                        continue
                        
                    if 'tickers' not in result or not result.get('tickers'):
                        logger.warning(f"Invalid JSON format: missing tickers")
                        # Don't retry here, just add some defaults
                        result['tickers'] = []
                    
                    # Transform to our standard format
                    components = {
                        'tickers': result.get('tickers', []),
                        'timeframe': result.get('timeframe', 'today'),
                        'direction': result.get('direction'),
                        'intent': result.get('intent', 'price_movement')
                    }
                    
                    # Add company name if available
                    if result.get('company_name'):
                        components['company_name'] = result['company_name']
                    
                    # Save the ticker mapping if we have both company name and ticker
                    if result.get('company_name') and result.get('tickers') and result['tickers']:
                        self._save_ticker_mapping(result['company_name'], result['tickers'][0])
                    
                    # Cache the results
                    try:
                        with open(cache_file, 'w') as f:
                            json.dump(components, f)
                    except Exception as e:
                        logger.error(f"Error caching results: {str(e)}")
                    
                    return components
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return self._default_components(query_text)
                
            except Exception as e:
                logger.error(f"Error in Gemini API request (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return self._default_components(query_text)
        
        # If we get here, all retries failed
        return self._default_components(query_text)
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call the Gemini API with the given prompt and improved error handling"""
        url = f"{self.base_url}?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 10,
                "maxOutputTokens": 1024
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)  # Add timeout
            
            # Handle HTTP errors explicitly
            if response.status_code != 200:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return ""
            
            response_json = response.json()
            if 'candidates' in response_json and response_json['candidates']:
                if 'content' in response_json['candidates'][0]:
                    content = response_json['candidates'][0]['content']
                    if 'parts' in content and content['parts']:
                        return content['parts'][0]['text'].strip()
            
            # If we get here, the response structure was unexpected
            logger.error(f"Unexpected response structure: {response_json}")
            return ""
            
        except requests.RequestException as e:
            logger.error(f"Network error during API request: {str(e)}")
            return ""
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
            return ""
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON content from text with improved reliability"""
        # First attempt: Try to find a complete JSON object
        try:
            # Find text between { and } with the most matching brackets
            pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}))*\}'
            matches = re.findall(pattern, text)
            
            if matches:
                # Try to validate each match as JSON
                for match in sorted(matches, key=len, reverse=True):
                    try:
                        # Test if this is valid JSON
                        json.loads(match)
                        return match
                    except json.JSONDecodeError:
                        continue
                
                # If no valid JSON found, return the longest match as a fallback
                return max(matches, key=len)
            
            # If no matches with regex, try to find the start and end of a JSON object
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                potential_json = text[start_idx:end_idx+1]
                try:
                    # Test if this is valid JSON
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting JSON from text: {str(e)}")
            return ""
    
    def _default_components(self, query_text: str) -> Dict[str, Any]:
        """Generate default components when API fails"""
        query_lower = query_text.lower()
        
        # Try a more aggressive approach to find company names in the query
        potential_company = None
        potential_ticker = None
        for company, ticker in self.ticker_mappings.items():
            if company in query_lower:
                potential_company = company
                potential_ticker = ticker
                break
        
        # If found a company, use it
        if potential_company:
            return {
                'tickers': [potential_ticker],
                'company_name': potential_company,
                'timeframe': self._extract_timeframe(query_lower),
                'direction': self._extract_direction(query_lower),
                'intent': self._extract_intent(query_lower)
            }
        
        # Otherwise just return the basics
        return {
            'tickers': [],
            'timeframe': self._extract_timeframe(query_lower),
            'direction': self._extract_direction(query_lower),
            'intent': self._extract_intent(query_lower)
        }