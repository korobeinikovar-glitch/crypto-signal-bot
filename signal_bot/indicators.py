"""
Technical indicators module for calculating RSI, MACD, and EMA indicators.
"""
import pandas as pd
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: Price series (usually close prices)
        period: RSI period (default: 14)
        
    Returns:
        Series with RSI values
    """
    delta = data.diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(
    data: pd.Series, 
    fast: int = 12, 
    slow: int = 26, 
    signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        data: Price series (usually close prices)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
        
    Returns:
        Tuple of (macd_line, signal_line, histogram)
    """
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        data: Price series (usually close prices)
        period: EMA period
        
    Returns:
        Series with EMA values
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        data: Price series (usually close prices)
        period: SMA period
        
    Returns:
        Series with SMA values
    """
    return data.rolling(window=period).mean()


def add_indicators(
    df: pd.DataFrame,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    ema_short: int = 50,
    ema_long: int = 200
) -> pd.DataFrame:
    """
    Add all technical indicators to the dataframe.
    
    Args:
        df: DataFrame with OHLCV data
        rsi_period: RSI period
        macd_fast: MACD fast period
        macd_slow: MACD slow period
        macd_signal: MACD signal period
        ema_short: Short EMA period
        ema_long: Long EMA period
        
    Returns:
        DataFrame with indicators added
    """
    df = df.copy()
    
    # RSI
    df['rsi'] = calculate_rsi(df['close'], rsi_period)
    
    # MACD
    df['macd'], df['macd_signal'], df['macd_histogram'] = calculate_macd(
        df['close'], macd_fast, macd_slow, macd_signal
    )
    
    # EMAs
    df['ema_short'] = calculate_ema(df['close'], ema_short)
    df['ema_long'] = calculate_ema(df['close'], ema_long)
    
    # EMA cross signal (1 if short > long, -1 if short < long)
    df['ema_cross'] = np.where(df['ema_short'] > df['ema_long'], 1, -1)
    
    return df


def generate_signal(df: pd.DataFrame, rsi_oversold: int = 30, rsi_overbought: int = 70) -> str:
    """
    Generate trading signal based on technical indicators.
    
    Signal logic:
    - LONG: RSI oversold + MACD bullish + EMA50 > EMA200
    - SHORT: RSI overbought + MACD bearish + EMA50 < EMA200
    - NEUTRAL: No clear signal
    
    Args:
        df: DataFrame with indicators
        rsi_oversold: RSI oversold threshold
        rsi_overbought: RSI overbought threshold
        
    Returns:
        Signal string: 'LONG', 'SHORT', or 'NEUTRAL'
    """
    if df.empty or len(df) < 2:
        return 'NEUTRAL'
    
    # Get latest values
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    rsi = latest['rsi']
    macd = latest['macd']
    macd_signal = latest['macd_signal']
    macd_hist = latest['macd_histogram']
    prev_macd_hist = previous['macd_histogram']
    ema_cross = latest['ema_cross']
    
    # Check for NaN values
    if pd.isna([rsi, macd, macd_signal, macd_hist, prev_macd_hist, ema_cross]).any():
        return 'NEUTRAL'
    
    # LONG signal conditions
    long_conditions = [
        rsi < rsi_oversold,  # RSI oversold
        macd > macd_signal,  # MACD above signal line
        macd_hist > 0,  # MACD histogram positive
        prev_macd_hist <= 0,  # MACD histogram crossed from negative (bullish crossover)
        ema_cross == 1,  # EMA50 above EMA200 (bullish trend)
    ]
    
    # SHORT signal conditions
    short_conditions = [
        rsi > rsi_overbought,  # RSI overbought
        macd < macd_signal,  # MACD below signal line
        macd_hist < 0,  # MACD histogram negative
        prev_macd_hist >= 0,  # MACD histogram crossed from positive (bearish crossover)
        ema_cross == -1,  # EMA50 below EMA200 (bearish trend)
    ]
    
    # Require at least 3 out of 5 conditions for a signal
    if sum(long_conditions) >= 3:
        return 'LONG'
    elif sum(short_conditions) >= 3:
        return 'SHORT'
    else:
        return 'NEUTRAL'


def get_signal_strength(df: pd.DataFrame, signal: str) -> float:
    """
    Calculate signal strength score (0-100).
    
    Args:
        df: DataFrame with indicators
        signal: Signal type ('LONG', 'SHORT', or 'NEUTRAL')
        
    Returns:
        Strength score from 0 to 100
    """
    if df.empty or signal == 'NEUTRAL':
        return 0.0
    
    latest = df.iloc[-1]
    
    rsi = latest['rsi']
    macd_hist = abs(latest['macd_histogram'])
    ema_diff = abs(latest['ema_short'] - latest['ema_long'])
    price = latest['close']
    
    # Check for NaN values
    if pd.isna([rsi, macd_hist, ema_diff, price]).any():
        return 0.0
    
    # Calculate components
    rsi_strength = 0
    if signal == 'LONG':
        rsi_strength = max(0, 30 - rsi)  # More oversold = stronger
    elif signal == 'SHORT':
        rsi_strength = max(0, rsi - 70)  # More overbought = stronger
    
    # Normalize components to 0-100 scale
    rsi_score = min(100, (rsi_strength / 30) * 100)
    macd_score = min(100, (macd_hist / price * 1000) * 100)
    ema_score = min(100, (ema_diff / price * 100) * 100)
    
    # Weighted average
    strength = (rsi_score * 0.4 + macd_score * 0.3 + ema_score * 0.3)
    
    return round(strength, 2)
