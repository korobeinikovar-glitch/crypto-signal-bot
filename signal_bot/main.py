"""
Main entry point for the crypto signal bot.
Orchestrates data fetching, indicator calculation, signal generation, and tracking.
"""
import logging
import time
from datetime import datetime
from typing import Dict, List

from signal_bot import config
from signal_bot.bybit_data import BybitDataFetcher
from signal_bot.indicators import add_indicators, generate_signal, get_signal_strength
from signal_bot.signal_tracker import SignalTracker

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CryptoSignalBot:
    """
    Main bot class that orchestrates all components.
    """
    
    def __init__(self):
        """Initialize the bot with all necessary components."""
        logger.info("Initializing Crypto Signal Bot...")
        
        # Initialize components
        self.data_fetcher = BybitDataFetcher(testnet=config.BYBIT_TESTNET)
        self.signal_tracker = SignalTracker(config.DATABASE_URL)
        
        # Configuration
        self.symbols = config.DEFAULT_SYMBOLS
        self.timeframe = config.TIMEFRAME
        self.candles_limit = config.CANDLES_LIMIT
        
        logger.info(f"Bot initialized with symbols: {self.symbols}")
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """
        Analyze a single symbol and generate signal.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing {symbol}...")
        
        # Fetch market data
        df = self.data_fetcher.get_klines(
            symbol=symbol,
            interval=self.timeframe,
            limit=self.candles_limit
        )
        
        if df is None or df.empty:
            logger.warning(f"No data available for {symbol}")
            return {
                'symbol': symbol,
                'signal': 'NEUTRAL',
                'error': 'No data available'
            }
        
        # Add technical indicators
        df = add_indicators(
            df,
            rsi_period=config.RSI_PERIOD,
            macd_fast=config.MACD_FAST,
            macd_slow=config.MACD_SLOW,
            macd_signal=config.MACD_SIGNAL,
            ema_short=config.EMA_SHORT,
            ema_long=config.EMA_LONG
        )
        
        # Generate signal
        signal = generate_signal(
            df,
            rsi_oversold=config.RSI_OVERSOLD,
            rsi_overbought=config.RSI_OVERBOUGHT
        )
        
        # Get latest values
        latest = df.iloc[-1]
        
        # Calculate signal strength
        strength = get_signal_strength(df, signal)
        
        result = {
            'symbol': symbol,
            'signal': signal,
            'strength': strength,
            'price': latest['close'],
            'timestamp': latest['timestamp'],
            'indicators': {
                'rsi': latest['rsi'],
                'macd': latest['macd'],
                'macd_signal': latest['macd_signal'],
                'ema_short': latest['ema_short'],
                'ema_long': latest['ema_long']
            }
        }
        
        logger.info(f"{symbol}: {signal} (strength: {strength:.2f}) @ ${latest['close']:.2f}")
        
        return result
    
    def analyze_all_symbols(self) -> List[Dict]:
        """
        Analyze all configured symbols.
        
        Returns:
            List of analysis results
        """
        logger.info(f"Starting analysis of {len(self.symbols)} symbols...")
        
        results = []
        for symbol in self.symbols:
            try:
                result = self.analyze_symbol(symbol)
                results.append(result)
                
                # Create signal if not NEUTRAL and strength is high enough
                if result['signal'] != 'NEUTRAL' and result.get('strength', 0) >= 50:
                    self.signal_tracker.create_signal(
                        symbol=symbol,
                        signal_type=result['signal'],
                        entry_price=result['price'],
                        indicators=result['indicators'],
                        strength=result['strength'],
                        take_profit_percent=config.TAKE_PROFIT_PERCENT,
                        stop_loss_percent=config.STOP_LOSS_PERCENT
                    )
                
                # Small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        return results
    
    def update_active_signals(self):
        """
        Update all active signals with current prices.
        """
        active_signals = self.signal_tracker.get_active_signals()
        
        if not active_signals:
            logger.info("No active signals to update")
            return
        
        logger.info(f"Updating {len(active_signals)} active signals...")
        
        for signal in active_signals:
            try:
                # Get current price
                current_price = self.data_fetcher.get_latest_price(signal.symbol)
                
                if current_price:
                    self.signal_tracker.update_signal(signal.id, current_price)
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error updating signal for {signal.symbol}: {e}")
        
        # Close expired signals
        expired = self.signal_tracker.close_expired_signals(
            hours=config.SIGNAL_TRACKING_HOURS
        )
        
        if expired:
            logger.info(f"Closed {len(expired)} expired signals")
    
    def print_statistics(self):
        """
        Print signal statistics.
        """
        stats = self.signal_tracker.get_signal_statistics(days=30)
        
        logger.info("=" * 50)
        logger.info("SIGNAL STATISTICS (Last 30 days)")
        logger.info("=" * 50)
        logger.info(f"Total Signals: {stats['total_signals']}")
        logger.info(f"Wins: {stats.get('wins', 0)}")
        logger.info(f"Losses: {stats.get('losses', 0)}")
        logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
        logger.info(f"Average P/L: {stats['average_pnl']:.2f}%")
        logger.info(f"Total P/L: {stats['total_pnl']:.2f}%")
        logger.info("=" * 50)
    
    def run_once(self):
        """
        Run one iteration of the bot.
        """
        logger.info("=" * 50)
        logger.info(f"Bot cycle starting at {datetime.utcnow()}")
        logger.info("=" * 50)
        
        # Analyze all symbols
        results = self.analyze_all_symbols()
        
        # Print results
        logger.info("\n" + "=" * 50)
        logger.info("ANALYSIS RESULTS")
        logger.info("=" * 50)
        
        for result in results:
            if 'error' in result:
                logger.warning(f"{result['symbol']}: {result['error']}")
            else:
                logger.info(
                    f"{result['symbol']}: {result['signal']} "
                    f"(Strength: {result['strength']:.2f}) @ ${result['price']:.2f}"
                )
        
        # Update active signals
        logger.info("\n" + "=" * 50)
        logger.info("UPDATING ACTIVE SIGNALS")
        logger.info("=" * 50)
        self.update_active_signals()
        
        # Print statistics
        self.print_statistics()
        
        logger.info("\n" + "=" * 50)
        logger.info("Bot cycle completed")
        logger.info("=" * 50 + "\n")
    
    def run_continuous(self, interval_minutes: int = 15):
        """
        Run the bot continuously with specified interval.
        
        Args:
            interval_minutes: Minutes between each analysis cycle
        """
        logger.info(f"Starting continuous mode (interval: {interval_minutes} minutes)")
        
        try:
            while True:
                self.run_once()
                
                logger.info(f"Sleeping for {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error in bot: {e}", exc_info=True)


def main():
    """
    Main entry point for the bot.
    """
    try:
        bot = CryptoSignalBot()
        
        # Run once for demonstration
        # For continuous operation, use: bot.run_continuous(interval_minutes=15)
        bot.run_once()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
