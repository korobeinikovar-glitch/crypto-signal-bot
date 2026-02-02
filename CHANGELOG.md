# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-02

### Added

#### Core Features
- **Bybit Data Fetcher** (`bybit_data.py`)
  - Integration with Bybit public API v5
  - OHLCV (candlestick) data fetching for USDT Perpetual contracts
  - Support for multiple timeframes (1m, 5m, 15m, 1h, 4h, 1D, etc.)
  - Latest price fetching for active signal tracking
  - Automatic retry and error handling
  - Rate limiting protection

- **Technical Indicators** (`indicators.py`)
  - RSI (Relative Strength Index) calculation
  - MACD (Moving Average Convergence Divergence) with histogram
  - EMA (Exponential Moving Average) - configurable periods
  - SMA (Simple Moving Average) support
  - Multi-indicator signal generation logic
  - Signal strength scoring (0-100 scale)
  - Configurable thresholds (oversold/overbought)

- **Signal Tracking** (`signal_tracker.py`)
  - SQLAlchemy-based database integration
  - Signal storage with full indicator data
  - Take-profit and stop-loss level tracking
  - Automatic signal closure on target hit
  - Signal expiration after configurable time
  - Performance statistics (win rate, P/L, etc.)
  - Support for both LONG and SHORT signals

- **Main Bot Orchestrator** (`main.py`)
  - Automated analysis of multiple symbols
  - Signal generation and storage
  - Active signal updates with current prices
  - Periodic execution support (run once or continuous)
  - Comprehensive logging
  - Statistics reporting

#### Configuration
- **Configuration Module** (`config.py`)
  - Environment variable support via `.env` file
  - Configurable API keys (optional for public endpoints)
  - Database path configuration
  - Telegram bot token support (for future notifications)
  - Adjustable indicator parameters
  - Risk management settings (TP/SL percentages)
  - Logging configuration

#### Documentation
- Comprehensive README with installation and usage instructions
- Quick Start Guide for new users
- Demo script showcasing all features
- Example .env configuration file
- MIT License
- Code comments and docstrings throughout

#### Development & Distribution
- `requirements.txt` with all dependencies
- `setup.py` for package distribution
- `.gitignore` for clean repository
- Modular, maintainable code structure
- Type hints and proper error handling

### Technical Details

#### Signal Generation Logic
Signals are generated using a multi-indicator approach requiring at least 3 out of 5 conditions:

**LONG Signal Conditions:**
1. RSI below oversold threshold (default: 30)
2. MACD above signal line (bullish)
3. MACD histogram positive
4. MACD histogram crossed from negative (bullish crossover)
5. EMA50 above EMA200 (bullish trend)

**SHORT Signal Conditions:**
1. RSI above overbought threshold (default: 70)
2. MACD below signal line (bearish)
3. MACD histogram negative
4. MACD histogram crossed from positive (bearish crossover)
5. EMA50 below EMA200 (bearish trend)

#### Default Settings
- **Symbols**: BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT, XRPUSDT
- **Timeframe**: 15 minutes
- **RSI Period**: 14
- **MACD**: 12/26/9
- **EMA**: 50/200
- **Take Profit**: 2%
- **Stop Loss**: 1%
- **Signal Tracking**: 24 hours

### Dependencies
- pandas >= 2.0.0 (data manipulation)
- numpy >= 1.24.0 (numerical computing)
- requests >= 2.31.0 (HTTP requests)
- aiogram >= 3.0.0 (Telegram bot framework)
- sqlalchemy >= 2.0.0 (database ORM)
- matplotlib >= 3.7.0 (visualization)
- scikit-learn >= 1.3.0 (machine learning tools)
- python-dotenv >= 1.0.0 (environment variables)
- pybit >= 5.6.0 (Bybit API wrapper)
- ta >= 0.11.0 (technical analysis library)

### Security
- No hardcoded credentials
- Environment variable support for sensitive data
- `.gitignore` excludes sensitive files
- Public API endpoints used by default (no authentication required)

### Known Limitations
- Does not execute actual trades (analysis only)
- Requires internet connection for real-time data
- Limited to Bybit USDT Perpetual contracts
- No backtesting functionality (yet)
- No real-time notifications (Telegram integration planned)

## [Unreleased]

### Planned Features
- Telegram bot notifications for new signals
- Web dashboard for signal monitoring
- Backtesting framework
- Additional technical indicators (Bollinger Bands, Stochastic, etc.)
- Support for other exchanges (Binance, etc.)
- Advanced signal filtering and portfolio management
- Paper trading mode for signal validation
- REST API for external integrations

---

## Version History

- **1.0.0** (2026-02-02) - Initial release with core functionality
