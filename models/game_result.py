# models/game_result.py

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GameResult:
    """
    Records complete game outcome and financial impact.
    
    Captures:
    - Game outcome (win/loss/push)
    - Winnings calculation
    - Stake changes
    - Detailed result information
    """
    
    def __init__(
        self,
        game_number,
        bet_amount,
        is_winner,
        stake_before,
        stake_after,
        winnings=0,
        odds=1.0,
        win_probability=None
    ):
        """Initialize game result"""
        self.game_number = game_number
        self.bet_amount = bet_amount
        self.is_winner = is_winner
        self.stake_before = stake_before
        self.stake_after = stake_after
        self.winnings = winnings
        self.odds = odds
        self.win_probability = win_probability
        self.timestamp = datetime.utcnow()
    
    @property
    def outcome(self):
        """Get outcome string"""
        return "win" if self.is_winner else "loss"
    
    @property
    def stake_change(self):
        """Calculate net stake change"""
        return self.stake_after - self.stake_before
    
    @property
    def roi_percentage(self):
        """Calculate ROI percentage"""
        if self.stake_before == 0:
            return 0
        return (self.stake_change / self.stake_before) * 100
    
    def __repr__(self):
        return (
            f"GameResult(game={self.game_number}, "
            f"outcome={self.outcome}, "
            f"bet=${self.bet_amount}, "
            f"stake_change=${self.stake_change:+.2f})"
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'game_number': self.game_number,
            'bet_amount': self.bet_amount,
            'outcome': self.outcome,
            'is_winner': self.is_winner,
            'stake_before': self.stake_before,
            'stake_after': self.stake_after,
            'winnings': self.winnings,
            'stake_change': self.stake_change,
            'roi_percentage': self.roi_percentage,
            'odds': self.odds,
            'win_probability': self.win_probability,
            'timestamp': self.timestamp.isoformat()
        }


class WinLossStatistics:
    """
    Comprehensive statistical analysis of win/loss patterns.
    
    Tracks:
    - Win/loss counts and rates
    - Total amounts won/lost
    - Average win/loss amounts
    - Profit factor
    - Largest win/loss
    - Streak analysis
    """
    
    def __init__(self):
        """Initialize statistics"""
        self.total_games = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_pushes = 0
        
        self.total_amount_won = 0.0
        self.total_amount_lost = 0.0
        self.total_bet_amount = 0.0
        
        self.largest_win = 0.0
        self.largest_loss = 0.0
        
        self.current_streak = 0  # Positive for wins, negative for losses
        self.longest_win_streak = 0
        self.longest_loss_streak = 0
        
        self.game_results = []
    
    def add_result(self, game_result):
        """Add a game result to statistics"""
        self.game_results.append(game_result)
        self.total_games += 1
        self.total_bet_amount += game_result.bet_amount
        
        # Track wins/losses
        if game_result.is_winner:
            self.total_wins += 1
            self.total_amount_won += game_result.winnings
            self.largest_win = max(self.largest_win, game_result.winnings)
            
            # Update streaks
            if self.current_streak >= 0:
                self.current_streak += 1
            else:
                self.current_streak = 1
            self.longest_win_streak = max(self.longest_win_streak, self.current_streak)
        else:
            self.total_losses += 1
            self.total_amount_lost += abs(game_result.stake_change)
            self.largest_loss = max(self.largest_loss, abs(game_result.stake_change))
            
            # Update streaks
            if self.current_streak <= 0:
                self.current_streak -= 1
            else:
                self.current_streak = -1
            self.longest_loss_streak = max(self.longest_loss_streak, abs(self.current_streak))
        
        logger.debug(f"Statistics updated: {self.win_rate_percentage:.1f}% win rate")
    
    @property
    def win_rate_percentage(self):
        """Calculate win rate percentage"""
        if self.total_games == 0:
            return 0
        return (self.total_wins / self.total_games) * 100
    
    @property
    def loss_rate_percentage(self):
        """Calculate loss rate percentage"""
        if self.total_games == 0:
            return 0
        return (self.total_losses / self.total_games) * 100
    
    @property
    def average_win(self):
        """Calculate average win amount"""
        if self.total_wins == 0:
            return 0
        return self.total_amount_won / self.total_wins
    
    @property
    def average_loss(self):
        """Calculate average loss amount"""
        if self.total_losses == 0:
            return 0
        return self.total_amount_lost / self.total_losses
    
    @property
    def profit_factor(self):
        """Calculate profit factor (winnings / losses)"""
        if self.total_amount_lost == 0:
            return float('inf') if self.total_amount_won > 0 else 1.0
        return self.total_amount_won / self.total_amount_lost
    
    @property
    def net_profit_loss(self):
        """Calculate net profit or loss"""
        return self.total_amount_won - self.total_amount_lost
    
    @property
    def roi_percentage(self):
        """Calculate return on investment percentage"""
        if self.total_bet_amount == 0:
            return 0
        return (self.net_profit_loss / self.total_bet_amount) * 100
    
    def get_summary(self):
        """Get comprehensive statistics summary"""
        return {
            'total_games': self.total_games,
            'total_wins': self.total_wins,
            'total_losses': self.total_losses,
            'win_rate_percentage': self.win_rate_percentage,
            'loss_rate_percentage': self.loss_rate_percentage,
            'total_amount_bet': self.total_bet_amount,
            'total_amount_won': self.total_amount_won,
            'total_amount_lost': self.total_amount_lost,
            'net_profit_loss': self.net_profit_loss,
            'roi_percentage': self.roi_percentage,
            'average_win': self.average_win,
            'average_loss': self.average_loss,
            'profit_factor': self.profit_factor,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'current_streak': self.current_streak,
            'longest_win_streak': self.longest_win_streak,
            'longest_loss_streak': self.longest_loss_streak
        }


class RunningTotals:
    """
    Real-time cumulative tracking of balance and performance.
    
    Maintains:
    - Running balance history
    - Cumulative profit/loss
    - Peak and lowest balance
    - Balance progression
    """
    
    def __init__(self, initial_balance):
        """Initialize running totals"""
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        self.lowest_balance = initial_balance
        
        self.cumulative_profit_loss = 0.0
        self.balance_history = [initial_balance]
    
    def update_balance(self, new_balance):
        """Update current balance and history"""
        self.current_balance = new_balance
        self.balance_history.append(new_balance)
        
        # Track peak and lowest
        self.peak_balance = max(self.peak_balance, new_balance)
        self.lowest_balance = min(self.lowest_balance, new_balance)
        
        # Calculate cumulative P&L
        self.cumulative_profit_loss = new_balance - self.initial_balance
        
        logger.debug(
            f"Balance updated: ${new_balance:.2f}, "
            f"P&L: ${self.cumulative_profit_loss:+.2f}"
        )
    
    @property
    def total_change(self):
        """Total change from initial balance"""
        return self.current_balance - self.initial_balance
    
    @property
    def roi_percentage(self):
        """Return on investment percentage"""
        if self.initial_balance == 0:
            return 0
        return (self.total_change / self.initial_balance) * 100
    
    @property
    def drawdown_percentage(self):
        """Maximum drawdown from peak"""
        if self.peak_balance == 0:
            return 0
        return ((self.lowest_balance - self.peak_balance) / self.peak_balance) * 100
    
    def get_summary(self):
        """Get balance summary"""
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'total_change': self.total_change,
            'roi_percentage': self.roi_percentage,
            'peak_balance': self.peak_balance,
            'lowest_balance': self.lowest_balance,
            'drawdown_percentage': self.drawdown_percentage,
            'cumulative_profit_loss': self.cumulative_profit_loss,
            'balance_history_count': len(self.balance_history)
        }
