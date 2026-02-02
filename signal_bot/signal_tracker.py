"""
Signal tracker module for storing and tracking trading signals and their performance.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class Signal(Base):
    """
    SQLAlchemy model for storing trading signals.
    """
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # LONG or SHORT
    entry_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Signal parameters
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    ema_short = Column(Float)
    ema_long = Column(Float)
    strength = Column(Float)
    
    # Target levels
    take_profit = Column(Float)
    stop_loss = Column(Float)
    
    # Tracking
    current_price = Column(Float)
    highest_price = Column(Float)
    lowest_price = Column(Float)
    last_update = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    exit_price = Column(Float)
    exit_timestamp = Column(DateTime)
    exit_reason = Column(String)  # TP, SL, or TIMEOUT
    profit_loss_percent = Column(Float)
    
    def __repr__(self):
        return f"<Signal(symbol={self.symbol}, type={self.signal_type}, price={self.entry_price})>"


class SignalTracker:
    """
    Manages signal storage and performance tracking.
    """
    
    def __init__(self, database_url: str):
        """
        Initialize the signal tracker with database connection.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Signal tracker initialized with database: {database_url}")
    
    def create_signal(
        self,
        symbol: str,
        signal_type: str,
        entry_price: float,
        indicators: Dict[str, float],
        strength: float,
        take_profit_percent: float = 2.0,
        stop_loss_percent: float = 1.0
    ) -> Signal:
        """
        Create and store a new trading signal.
        
        Args:
            symbol: Trading pair symbol
            signal_type: 'LONG' or 'SHORT'
            entry_price: Entry price for the signal
            indicators: Dictionary of indicator values
            strength: Signal strength score
            take_profit_percent: Take profit percentage
            stop_loss_percent: Stop loss percentage
            
        Returns:
            Created Signal object
        """
        session = self.SessionLocal()
        try:
            # Calculate targets
            if signal_type == 'LONG':
                take_profit = entry_price * (1 + take_profit_percent / 100)
                stop_loss = entry_price * (1 - stop_loss_percent / 100)
            else:  # SHORT
                take_profit = entry_price * (1 - take_profit_percent / 100)
                stop_loss = entry_price * (1 + stop_loss_percent / 100)
            
            now = datetime.utcnow()
            
            signal = Signal(
                symbol=symbol,
                signal_type=signal_type,
                entry_price=entry_price,
                timestamp=now,
                rsi=indicators.get('rsi'),
                macd=indicators.get('macd'),
                macd_signal=indicators.get('macd_signal'),
                ema_short=indicators.get('ema_short'),
                ema_long=indicators.get('ema_long'),
                strength=strength,
                take_profit=take_profit,
                stop_loss=stop_loss,
                current_price=entry_price,
                highest_price=entry_price,
                lowest_price=entry_price,
                last_update=now,
                is_active=True
            )
            
            session.add(signal)
            session.commit()
            session.refresh(signal)
            
            logger.info(f"Created signal: {symbol} {signal_type} @ {entry_price}")
            return signal
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating signal: {e}")
            raise
        finally:
            session.close()
    
    def update_signal(self, signal_id: int, current_price: float) -> Optional[Signal]:
        """
        Update signal with current price and check if targets are hit.
        
        Args:
            signal_id: Signal ID
            current_price: Current market price
            
        Returns:
            Updated Signal object or None
        """
        session = self.SessionLocal()
        try:
            signal = session.query(Signal).filter(Signal.id == signal_id).first()
            
            if not signal or not signal.is_active:
                return None
            
            # Update prices
            signal.current_price = current_price
            signal.highest_price = max(signal.highest_price, current_price)
            signal.lowest_price = min(signal.lowest_price, current_price)
            signal.last_update = datetime.utcnow()
            
            # Check if targets are hit
            exit_reason = None
            
            if signal.signal_type == 'LONG':
                if current_price >= signal.take_profit:
                    exit_reason = 'TP'
                elif current_price <= signal.stop_loss:
                    exit_reason = 'SL'
            else:  # SHORT
                if current_price <= signal.take_profit:
                    exit_reason = 'TP'
                elif current_price >= signal.stop_loss:
                    exit_reason = 'SL'
            
            # Close signal if target hit
            if exit_reason:
                signal.is_active = False
                signal.exit_price = current_price
                signal.exit_timestamp = datetime.utcnow()
                signal.exit_reason = exit_reason
                
                # Calculate P/L
                if signal.signal_type == 'LONG':
                    pnl = ((current_price - signal.entry_price) / signal.entry_price) * 100
                else:  # SHORT
                    pnl = ((signal.entry_price - current_price) / signal.entry_price) * 100
                
                signal.profit_loss_percent = round(pnl, 2)
                logger.info(f"Signal closed: {signal.symbol} {exit_reason} P/L: {pnl:.2f}%")
            
            session.commit()
            session.refresh(signal)
            return signal
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating signal: {e}")
            return None
        finally:
            session.close()
    
    def get_active_signals(self) -> List[Signal]:
        """
        Get all active signals.
        
        Returns:
            List of active Signal objects
        """
        session = self.SessionLocal()
        try:
            signals = session.query(Signal).filter(Signal.is_active == True).all()
            # Detach from session
            session.expunge_all()
            return signals
        finally:
            session.close()
    
    def close_expired_signals(self, hours: int = 24) -> List[Signal]:
        """
        Close signals that have been active for more than specified hours.
        
        Args:
            hours: Maximum hours to keep signal active
            
        Returns:
            List of closed signals
        """
        session = self.SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            expired_signals = session.query(Signal).filter(
                Signal.is_active == True,
                Signal.timestamp < cutoff_time
            ).all()
            
            for signal in expired_signals:
                signal.is_active = False
                signal.exit_timestamp = datetime.utcnow()
                signal.exit_reason = 'TIMEOUT'
                signal.exit_price = signal.current_price
                
                # Calculate P/L
                if signal.signal_type == 'LONG':
                    pnl = ((signal.current_price - signal.entry_price) / signal.entry_price) * 100
                else:  # SHORT
                    pnl = ((signal.entry_price - signal.current_price) / signal.entry_price) * 100
                
                signal.profit_loss_percent = round(pnl, 2)
                logger.info(f"Signal expired: {signal.symbol} P/L: {pnl:.2f}%")
            
            session.commit()
            return expired_signals
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error closing expired signals: {e}")
            return []
        finally:
            session.close()
    
    def get_signal_statistics(self, days: int = 30) -> Dict:
        """
        Get statistics for signals from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        session = self.SessionLocal()
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            closed_signals = session.query(Signal).filter(
                Signal.is_active == False,
                Signal.timestamp >= cutoff_time
            ).all()
            
            if not closed_signals:
                return {
                    'total_signals': 0,
                    'win_rate': 0,
                    'average_pnl': 0,
                    'total_pnl': 0
                }
            
            total = len(closed_signals)
            wins = sum(1 for s in closed_signals if s.profit_loss_percent and s.profit_loss_percent > 0)
            total_pnl = sum(s.profit_loss_percent for s in closed_signals if s.profit_loss_percent)
            avg_pnl = total_pnl / total if total > 0 else 0
            
            return {
                'total_signals': total,
                'win_rate': round((wins / total * 100) if total > 0 else 0, 2),
                'average_pnl': round(avg_pnl, 2),
                'total_pnl': round(total_pnl, 2),
                'wins': wins,
                'losses': total - wins
            }
            
        finally:
            session.close()
