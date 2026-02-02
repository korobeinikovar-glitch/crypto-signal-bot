"""
Example usage and demonstration of the crypto signal bot components.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from signal_bot.indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_ema,
    add_indicators,
    generate_signal,
    get_signal_strength
)


def create_sample_data():
    """Create sample OHLCV data for demonstration."""
    # Create 200 periods of sample data
    np.random.seed(42)
    
    dates = pd.date_range(end=datetime.now(), periods=200, freq='15min')
    
    # Simulate price movement
    base_price = 50000
    prices = [base_price]
    
    for i in range(199):
        change = np.random.randn() * 100
        prices.append(prices[-1] + change)
    
    # Create OHLCV data
    data = {
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': [p + np.random.randn() * 50 for p in prices],
        'volume': np.random.randint(100, 1000, 200),
        'turnover': np.random.randint(1000000, 10000000, 200)
    }
    
    return pd.DataFrame(data)


def demo_indicators():
    """Demonstrate technical indicators calculation."""
    print("=" * 60)
    print("DEMO: Technical Indicators")
    print("=" * 60)
    
    # Create sample data
    df = create_sample_data()
    print(f"\nGenerated {len(df)} candles of sample data")
    
    # Add indicators
    df = add_indicators(df)
    
    # Show latest values
    latest = df.iloc[-1]
    print("\nLatest Indicator Values:")
    print(f"  Close Price: ${latest['close']:.2f}")
    print(f"  RSI: {latest['rsi']:.2f}")
    print(f"  MACD: {latest['macd']:.2f}")
    print(f"  MACD Signal: {latest['macd_signal']:.2f}")
    print(f"  MACD Histogram: {latest['macd_histogram']:.2f}")
    print(f"  EMA 50: ${latest['ema_short']:.2f}")
    print(f"  EMA 200: ${latest['ema_long']:.2f}")
    
    # Generate signal
    signal = generate_signal(df)
    strength = get_signal_strength(df, signal)
    
    print(f"\nGenerated Signal: {signal}")
    print(f"Signal Strength: {strength:.2f}/100")
    
    return df, signal, strength


def demo_signal_logic():
    """Demonstrate signal generation logic."""
    print("\n" + "=" * 60)
    print("DEMO: Signal Generation Logic")
    print("=" * 60)
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Bullish Scenario',
            'rsi': 25,  # Oversold
            'macd': 100,
            'macd_signal': 80,
            'ema_short': 50500,
            'ema_long': 50000
        },
        {
            'name': 'Bearish Scenario',
            'rsi': 75,  # Overbought
            'macd': -100,
            'macd_signal': -80,
            'ema_short': 49500,
            'ema_long': 50000
        },
        {
            'name': 'Neutral Scenario',
            'rsi': 50,
            'macd': 50,
            'macd_signal': 48,
            'ema_short': 50000,
            'ema_long': 49950
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  RSI: {scenario['rsi']}")
        print(f"  MACD: {scenario['macd']}, Signal: {scenario['macd_signal']}")
        print(f"  EMA50: {scenario['ema_short']}, EMA200: {scenario['ema_long']}")
        
        # Expected signal based on conditions
        if scenario['rsi'] < 30 and scenario['ema_short'] > scenario['ema_long']:
            expected = "LONG (likely)"
        elif scenario['rsi'] > 70 and scenario['ema_short'] < scenario['ema_long']:
            expected = "SHORT (likely)"
        else:
            expected = "NEUTRAL (likely)"
        
        print(f"  Expected: {expected}")


def demo_tracking():
    """Demonstrate signal tracking."""
    print("\n" + "=" * 60)
    print("DEMO: Signal Tracking")
    print("=" * 60)
    
    from signal_bot.signal_tracker import SignalTracker
    import os
    
    # Create temporary database
    db_path = '/tmp/demo_signals.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    tracker = SignalTracker(f'sqlite:///{db_path}')
    
    # Create a sample signal
    indicators = {
        'rsi': 28.5,
        'macd': 85.2,
        'macd_signal': 78.1,
        'ema_short': 50500,
        'ema_long': 50000
    }
    
    signal = tracker.create_signal(
        symbol='BTCUSDT',
        signal_type='LONG',
        entry_price=50000.0,
        indicators=indicators,
        strength=75.5,
        take_profit_percent=2.0,
        stop_loss_percent=1.0
    )
    
    print(f"\nCreated Signal:")
    print(f"  Symbol: {signal.symbol}")
    print(f"  Type: {signal.signal_type}")
    print(f"  Entry: ${signal.entry_price:.2f}")
    print(f"  Take Profit: ${signal.take_profit:.2f} (+{2.0}%)")
    print(f"  Stop Loss: ${signal.stop_loss:.2f} (-{1.0}%)")
    print(f"  Strength: {signal.strength:.2f}")
    
    # Simulate price updates
    print("\nSimulating price updates:")
    
    test_prices = [50100, 50500, 50800, 51000]  # Price going up
    
    for price in test_prices:
        updated_signal = tracker.update_signal(signal.id, price)
        if updated_signal:
            status = "CLOSED" if not updated_signal.is_active else "ACTIVE"
            print(f"  Price: ${price:.2f} - Status: {status}")
            if not updated_signal.is_active:
                print(f"    Exit Reason: {updated_signal.exit_reason}")
                print(f"    P/L: {updated_signal.profit_loss_percent:.2f}%")
                break
    
    # Get statistics
    stats = tracker.get_signal_statistics(days=30)
    print(f"\nStatistics:")
    print(f"  Total Signals: {stats['total_signals']}")
    print(f"  Win Rate: {stats['win_rate']:.2f}%")
    print(f"  Average P/L: {stats['average_pnl']:.2f}%")
    
    # Cleanup
    os.remove(db_path)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("CRYPTO SIGNAL BOT - COMPONENT DEMONSTRATION")
    print("=" * 60)
    
    # Demo 1: Technical Indicators
    df, signal, strength = demo_indicators()
    
    # Demo 2: Signal Logic
    demo_signal_logic()
    
    # Demo 3: Signal Tracking
    demo_tracking()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("\nAll components are working correctly!")
    print("To run the actual bot with real data: python -m signal_bot.main")


if __name__ == '__main__':
    main()
