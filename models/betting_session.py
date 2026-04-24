# models/betting_session.py

from datetime import datetime
from enum import Enum


class SessionStatus(Enum):
    """Enum for session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class BettingSession:
    """
    Represents a complete gaming session.
    
    Features:
    - Tracks all bets in a gaming session
    - Records start/end times and session statistics
    - Generates comprehensive session summaries
    - Links bets to their strategies
    """

    def __init__(
        self,
        session_id,
        gambler_id,
        initial_stake,
        strategy_name="default",
        created_at=None
    ):
        # Identifiers
        self.session_id = session_id
        self.gambler_id = gambler_id

        # Session metadata
        self.strategy_name = strategy_name
        self.initial_stake = initial_stake
        self.current_stake = initial_stake
        self.final_stake = None

        # Session timing
        self.created_at = created_at if created_at else datetime.utcnow()
        self.ended_at = None
        self.status = SessionStatus.ACTIVE

        # Bet tracking
        self.bets = []
        self.total_bets_placed = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_amount_wagered = 0
        self.total_amount_won = 0

    def add_bet(self, bet):
        """Add a bet to the session"""
        self.bets.append(bet)
        self.total_bets_placed += 1
        self.total_amount_wagered += bet.bet_amount

    def settle_bet(self, bet):
        """Update session statistics after bet settlement"""
        if bet.is_winner:
            self.total_wins += 1
            self.total_amount_won += bet.actual_winnings
        else:
            self.total_losses += 1

        self.current_stake = bet.stake_after

    def end_session(self):
        """End the session and calculate final statistics"""
        self.ended_at = datetime.utcnow()
        self.final_stake = self.current_stake
        self.status = SessionStatus.COMPLETED

    def get_session_duration(self):
        """Get session duration in seconds"""
        end_time = self.ended_at if self.ended_at else datetime.utcnow()
        return (end_time - self.created_at).total_seconds()

    def calculate_roi(self):
        """Calculate Return on Investment"""
        if self.initial_stake == 0:
            return 0
        return ((self.current_stake - self.initial_stake) / self.initial_stake) * 100

    def calculate_win_rate(self):
        """Calculate win rate percentage"""
        if self.total_bets_placed == 0:
            return 0
        return (self.total_wins / self.total_bets_placed) * 100

    def get_summary(self):
        """Generate comprehensive session summary"""
        return {
            "session_id": self.session_id,
            "gambler_id": self.gambler_id,
            "strategy_name": self.strategy_name,
            "status": self.status.value,
            "initial_stake": self.initial_stake,
            "final_stake": self.final_stake,
            "stake_change": self.final_stake - self.initial_stake if self.final_stake else None,
            "roi_percentage": self.calculate_roi(),
            "total_bets_placed": self.total_bets_placed,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "win_rate_percentage": self.calculate_win_rate(),
            "total_amount_wagered": self.total_amount_wagered,
            "total_amount_won": self.total_amount_won,
            "session_duration_seconds": self.get_session_duration(),
            "created_at": self.created_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "bets": [bet.to_dict() for bet in self.bets]
        }

    def to_dict(self):
        """Convert session to dictionary"""
        return self.get_summary()

    def __repr__(self):
        return (
            f"BettingSession(id={self.session_id}, "
            f"bets={self.total_bets_placed}, "
            f"status={self.status.value})"
        )
