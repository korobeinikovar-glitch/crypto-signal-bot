"""
Configuration module for the crypto signal bot.
Contains settings for API access, database paths, and bot parameters.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Bybit API Configuration
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
BYBIT_TESTNET = os.getenv('BYBIT_TESTNET', 'False').lower() == 'true'

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'signals.db'))
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Trading Parameters
DEFAULT_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
TIMEFRAME = '15'  # 15 minute candles
CANDLES_LIMIT = 200  # Number of candles to fetch for analysis

# Indicator Parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

EMA_SHORT = 50
EMA_LONG = 200

# Signal Tracking Parameters
SIGNAL_TRACKING_HOURS = 24  # Track signals for 24 hours
TAKE_PROFIT_PERCENT = 2.0  # 2% take profit
STOP_LOSS_PERCENT = 1.0  # 1% stop loss

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'bot.log'))
