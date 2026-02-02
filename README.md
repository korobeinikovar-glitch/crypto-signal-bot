# Crypto Signal Bot

A cryptocurrency analysis bot using the Bybit public API for generating trade signals and providing statistical analyses. The bot analyzes USDT Perpetual market pairs and issues LONG/SHORT trade signals (without executing trades) while tracking their performance.

## Features

- 📊 **Technical Analysis**: RSI, MACD, EMA50/200 indicators
- 🎯 **Signal Generation**: Automated LONG/SHORT signals based on multiple indicators
- 📈 **Performance Tracking**: Tracks signals with take-profit and stop-loss levels
- 💾 **Database Storage**: SQLite database for signal history
- 🔄 **Real-time Updates**: Updates active signals with current prices
- 📉 **Statistics**: Win rate, P/L analysis, and performance metrics

## Architecture

```
signal_bot/
 ├─ main.py                 # Entry point: bot orchestrator
 ├─ config.py               # Configurations for API keys, database paths
 ├─ bybit_data.py           # Bybit API for OHLCV data collection
 ├─ indicators.py           # RSI, MACD, EMA technical indicators
 └─ signal_tracker.py       # Signal performance tracking
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/korobeinikovar-glitch/crypto-signal-bot.git
cd crypto-signal-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file for configuration:
```bash
# Bybit API (optional, public endpoints used by default)
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
BYBIT_TESTNET=False

# Database
DATABASE_PATH=signals.db

# Telegram Bot (optional, for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

## Usage

### Run the Bot Once

To analyze all symbols and generate signals for one cycle:

```bash
python -m signal_bot.main
```

### Run Continuously

For continuous operation (uncomment in `main.py`):

```python
# In main.py, change:
bot.run_once()
# To:
bot.run_continuous(interval_minutes=15)
```

Then run:
```bash
python -m signal_bot.main
```

## Signal Logic

The bot generates signals based on the following criteria:

### LONG Signal (Bullish)
- RSI < 30 (oversold)
- MACD > Signal line (bullish momentum)
- MACD histogram crossed from negative to positive
- EMA50 > EMA200 (bullish trend)
- At least 3 out of 5 conditions must be met

### SHORT Signal (Bearish)
- RSI > 70 (overbought)
- MACD < Signal line (bearish momentum)
- MACD histogram crossed from positive to negative
- EMA50 < EMA200 (bearish trend)
- At least 3 out of 5 conditions must be met

### Signal Strength
- Signals are scored 0-100 based on indicator strength
- Only signals with strength ≥ 50 are tracked

## Configuration

Key parameters in `config.py`:

```python
# Trading pairs
DEFAULT_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']

# Timeframe
TIMEFRAME = '15'  # 15-minute candles

# Indicator parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

EMA_SHORT = 50
EMA_LONG = 200

# Risk management
TAKE_PROFIT_PERCENT = 2.0  # 2%
STOP_LOSS_PERCENT = 1.0    # 1%
SIGNAL_TRACKING_HOURS = 24
```

## Example Output

```
==================================================
Bot cycle starting at 2026-02-02 09:35:15
==================================================

Analyzing BTCUSDT...
BTCUSDT: LONG (strength: 72.50) @ $45000.00

Analyzing ETHUSDT...
ETHUSDT: NEUTRAL (strength: 35.20) @ $2500.00

==================================================
ANALYSIS RESULTS
==================================================
BTCUSDT: LONG (Strength: 72.50) @ $45000.00
ETHUSDT: NEUTRAL (Strength: 35.20) @ $2500.00

==================================================
SIGNAL STATISTICS (Last 30 days)
==================================================
Total Signals: 25
Wins: 15
Losses: 10
Win Rate: 60.00%
Average P/L: 0.85%
Total P/L: 21.25%
==================================================
```

## Database Schema

The bot uses SQLite to store signals with the following fields:

- **Entry**: symbol, signal_type, entry_price, timestamp
- **Indicators**: rsi, macd, ema_short, ema_long, strength
- **Targets**: take_profit, stop_loss
- **Tracking**: current_price, highest_price, lowest_price
- **Exit**: exit_price, exit_reason (TP/SL/TIMEOUT), profit_loss_percent

## API Rate Limits

The bot uses Bybit public API endpoints which have rate limits:
- 120 requests per second for public endpoints
- Small delays are built-in between requests (0.1-0.5 seconds)

## Disclaimer

⚠️ **This bot is for educational and analytical purposes only.**

- Does NOT execute actual trades
- Past performance does not guarantee future results
- Always do your own research before trading
- Cryptocurrency trading involves substantial risk of loss

## Development

### Project Structure

```
crypto-signal-bot/
├── signal_bot/
│   ├── __init__.py
│   ├── config.py
│   ├── bybit_data.py
│   ├── indicators.py
│   ├── signal_tracker.py
│   └── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Adding New Indicators

To add custom indicators, modify `indicators.py`:

```python
def calculate_custom_indicator(data: pd.Series, period: int) -> pd.Series:
    # Your indicator logic
    return result
```

### Adding New Symbols

Edit `config.py`:

```python
DEFAULT_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'NEWTOKEN']
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub Issues page.