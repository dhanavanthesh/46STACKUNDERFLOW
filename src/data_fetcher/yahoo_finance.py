 
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class YahooFinanceFetcher:
    def __init__(self):
        self.data_dir = "data/market_data"
        os.makedirs(self.data_dir, exist_ok=True)

    def get_stock_data(self, ticker, period="1d", interval="1m"):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            info = stock.info
            
            # Save data
            data = {
                "price_data": hist.to_dict(orient='records'),
                "info": info,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to file
            file_path = os.path.join(self.data_dir, f"{ticker}_data.json")
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None

    def get_holdings_data(self, etf_ticker):
        """Fetch ETF holdings data"""
        try:
            etf = yf.Ticker(etf_ticker)
            holdings = etf.holdings
            
            # Save holdings data
            file_path = os.path.join(self.data_dir, f"{etf_ticker}_holdings.json")
            with open(file_path, 'w') as f:
                json.dump(holdings, f)
            
            return holdings
        except Exception as e:
            print(f"Error fetching holdings for {etf_ticker}: {str(e)}")
            return None