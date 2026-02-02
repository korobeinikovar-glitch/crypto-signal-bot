"""
Bybit data module for fetching OHLCV candlestick data using Bybit public API.
"""
import requests
import pandas as pd
from typing import Optional, List, Dict
import time
import logging

logger = logging.getLogger(__name__)


class BybitDataFetcher:
    """
    Fetches OHLCV (Open, High, Low, Close, Volume) data from Bybit public API.
    Uses the public endpoints, so no authentication is required.
    """
    
    BASE_URL = "https://api.bybit.com"
    
    def __init__(self, testnet: bool = False):
        """
        Initialize the Bybit data fetcher.
        
        Args:
            testnet: Whether to use testnet (default: False)
        """
        if testnet:
            self.BASE_URL = "https://api-testnet.bybit.com"
        self.session = requests.Session()
    
    def get_klines(
        self, 
        symbol: str, 
        interval: str = '15', 
        limit: int = 200
    ) -> Optional[pd.DataFrame]:
        """
        Fetch candlestick/kline data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Time interval in minutes ('1', '5', '15', '60', '240', 'D')
            limit: Number of candles to fetch (max 200)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            endpoint = f"{self.BASE_URL}/v5/market/kline"
            
            # Calculate start time (limit candles ago)
            end_time = int(time.time() * 1000)
            interval_ms = self._interval_to_ms(interval)
            start_time = end_time - (interval_ms * limit)
            
            params = {
                'category': 'linear',  # USDT perpetual
                'symbol': symbol,
                'interval': interval,
                'start': start_time,
                'end': end_time,
                'limit': limit
            }
            
            logger.info(f"Fetching klines for {symbol} with interval {interval}")
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('retCode') != 0:
                logger.error(f"Bybit API error: {data.get('retMsg')}")
                return None
            
            result = data.get('result', {})
            klines = result.get('list', [])
            
            if not klines:
                logger.warning(f"No klines data returned for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            df['turnover'] = df['turnover'].astype(float)
            
            # Sort by timestamp ascending
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"Successfully fetched {len(df)} candles for {symbol}")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching klines for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching klines for {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Latest price as float or None if error
        """
        try:
            endpoint = f"{self.BASE_URL}/v5/market/tickers"
            params = {
                'category': 'linear',
                'symbol': symbol
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('retCode') != 0:
                logger.error(f"Bybit API error: {data.get('retMsg')}")
                return None
            
            result = data.get('result', {})
            tickers = result.get('list', [])
            
            if not tickers:
                return None
            
            price = float(tickers[0].get('lastPrice', 0))
            return price if price > 0 else None
            
        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {e}")
            return None
    
    def get_multiple_symbols_data(
        self, 
        symbols: List[str], 
        interval: str = '15', 
        limit: int = 200
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch klines data for multiple symbols.
        
        Args:
            symbols: List of trading pair symbols
            interval: Time interval
            limit: Number of candles to fetch
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        for symbol in symbols:
            df = self.get_klines(symbol, interval, limit)
            if df is not None:
                results[symbol] = df
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def _interval_to_ms(self, interval: str) -> int:
        """
        Convert interval string to milliseconds.
        
        Args:
            interval: Time interval ('1', '5', '15', '60', '240', 'D')
            
        Returns:
            Interval in milliseconds
        """
        interval_map = {
            '1': 60 * 1000,
            '3': 3 * 60 * 1000,
            '5': 5 * 60 * 1000,
            '15': 15 * 60 * 1000,
            '30': 30 * 60 * 1000,
            '60': 60 * 60 * 1000,
            '120': 120 * 60 * 1000,
            '240': 240 * 60 * 1000,
            '360': 360 * 60 * 1000,
            '720': 720 * 60 * 1000,
            'D': 24 * 60 * 60 * 1000,
            'W': 7 * 24 * 60 * 60 * 1000,
            'M': 30 * 24 * 60 * 60 * 1000,
        }
        return interval_map.get(interval, 15 * 60 * 1000)
