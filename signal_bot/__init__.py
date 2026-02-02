"""
Crypto Signal Bot - A cryptocurrency analysis bot using Bybit public API.

This package provides tools for:
- Fetching OHLCV data from Bybit
- Calculating technical indicators (RSI, MACD, EMA)
- Generating LONG/SHORT trading signals
- Tracking signal performance
"""

__version__ = '1.0.0'
__author__ = 'Crypto Signal Bot'

from signal_bot.bybit_data import BybitDataFetcher
from signal_bot.indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_ema,
    add_indicators,
    generate_signal,
    get_signal_strength
)
from signal_bot.signal_tracker import SignalTracker, Signal
from signal_bot.main import CryptoSignalBot

__all__ = [
    'BybitDataFetcher',
    'calculate_rsi',
    'calculate_macd',
    'calculate_ema',
    'add_indicators',
    'generate_signal',
    'get_signal_strength',
    'SignalTracker',
    'Signal',
    'CryptoSignalBot',
]
