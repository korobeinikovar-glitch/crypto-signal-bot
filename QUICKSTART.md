# Quick Start Guide

This guide will help you get started with the Crypto Signal Bot in minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for API access)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/korobeinikovar-glitch/crypto-signal-bot.git
cd crypto-signal-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## Basic Usage

### Run Demo (No Internet Required)

To see how the components work with sample data:

```bash
python demo.py
```

This will demonstrate:
- Technical indicator calculations (RSI, MACD, EMA)
- Signal generation logic
- Signal tracking with take-profit/stop-loss

### Run the Bot Once

To analyze markets and generate signals (requires internet):

```bash
python -m signal_bot.main
```

This will:
1. Fetch latest market data from Bybit
2. Calculate technical indicators
3. Generate LONG/SHORT/NEUTRAL signals
4. Store signals in database
5. Update active signals
6. Show performance statistics

### Run Continuously

For automated operation, edit `signal_bot/main.py`:

```python
# Change this line in the main() function:
bot.run_once()

# To this:
bot.run_continuous(interval_minutes=15)
```

Then run:

```bash
python -m signal_bot.main
```

The bot will run every 15 minutes (or your chosen interval).

## Configuration

### Quick Config

Create a `.env` file (optional):

```bash
cp .env.example .env
```

Edit `.env` to customize:

```bash
# Leave empty to use public API
BYBIT_API_KEY=
BYBIT_API_SECRET=
BYBIT_TESTNET=False

# Database location
DATABASE_PATH=signals.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

### Advanced Config

Edit `signal_bot/config.py` to customize:

- Trading pairs to monitor
- Timeframe (15min, 1hour, etc.)
- Indicator parameters (RSI periods, MACD settings)
- Risk management (take-profit %, stop-loss %)
- Signal tracking duration

## Understanding Output

### Signal Types

- **LONG**: Bullish signal - price expected to go up
- **SHORT**: Bearish signal - price expected to go down
- **NEUTRAL**: No clear signal

### Signal Strength

Signals are scored 0-100:
- **0-30**: Weak signal (not tracked)
- **30-50**: Moderate signal (not tracked)
- **50-70**: Strong signal (tracked)
- **70-100**: Very strong signal (tracked)

Only signals with strength ≥ 50 are tracked for performance.

### Example Output

```
==================================================
ANALYSIS RESULTS
==================================================
BTCUSDT: LONG (Strength: 75.50) @ $45000.00
ETHUSDT: NEUTRAL (Strength: 35.20) @ $2500.00
SOLUSDT: SHORT (Strength: 68.30) @ $150.00
==================================================

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

## Viewing Signal History

Signals are stored in SQLite database (`signals.db`). You can query it:

```bash
sqlite3 signals.db "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10;"
```

Or use a GUI tool like [DB Browser for SQLite](https://sqlitebrowser.org/).

## Troubleshooting

### "No data available" error

- Check your internet connection
- Verify Bybit API is accessible
- Try with testnet: set `BYBIT_TESTNET=True` in `.env`

### Import errors

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

### Permission errors

If you get database permission errors:

```bash
chmod 666 signals.db
```

## Next Steps

1. **Customize signals**: Edit `signal_bot/indicators.py` to adjust logic
2. **Add symbols**: Edit `DEFAULT_SYMBOLS` in `signal_bot/config.py`
3. **Integrate notifications**: Add Telegram bot integration
4. **Backtest strategies**: Use historical data to test signal accuracy
5. **Add custom indicators**: Extend `indicators.py` with your own

## Getting Help

- 📖 Read the full [README.md](README.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/korobeinikovar-glitch/crypto-signal-bot/issues)
- 💬 Ask questions in discussions

## Important Notes

⚠️ **This bot does NOT execute trades automatically!**

It only:
- Analyzes market data
- Generates signals
- Tracks signal performance

You must manually decide whether to act on signals.

⚠️ **Trading involves risk!**

- Past performance does not guarantee future results
- Always do your own research (DYOR)
- Never invest more than you can afford to lose
- This is for educational purposes only

## Example Workflow

1. **Morning**: Run bot to analyze markets
   ```bash
   python -m signal_bot.main
   ```

2. **Review**: Check generated signals and their strength

3. **Research**: Investigate high-strength signals further

4. **Decide**: Make your own trading decisions

5. **Evening**: Run bot again to update signal tracking

6. **Weekly**: Review statistics to evaluate signal quality
   ```bash
   python -c "from signal_bot.signal_tracker import SignalTracker; \
             t = SignalTracker('sqlite:///signals.db'); \
             print(t.get_signal_statistics(days=7))"
   ```

Happy trading! 🚀
