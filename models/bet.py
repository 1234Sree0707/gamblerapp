# models/bet.py

from datetime import datetime
from enum import Enum


class BetOutcome(Enum):
    """Enum for bet outcomes"""
    WIN = "win"
    LOSS = "loss"
    PENDING = "pending"


class Bet:
    """
    Represents a single bet with complete tracking.
    
    Features:
    - Complete bet tracking with IDs, amounts, probabilities
    - Automatic potential win calculation based on odds
    - Tracks stake before/after each bet
    - Settlement logic for win/loss outcomes
    """

    def __init__(
        self,
        bet_id,
        gambler_id,
        bet_amount,
        win_probability,
        odds=1.0,
        stake_before=0,
        session_id=None,
        strategy_name=None,
        created_at=None
    ):
        # Unique identifier
        self.bet_id = bet_id

        # Foreign keys
        self.gambler_id = gambler_id
        self.session_id = session_id

        # Bet details
        self.bet_amount = bet_amount
        self.win_probability = win_probability
        self.odds = odds

        # Stake tracking
        self.stake_before = stake_before
        self.stake_after = None

        # Outcome tracking
        self.outcome = BetOutcome.PENDING
        self.is_winner = None
        self.actual_winnings = 0
        self.is_settled = False

        # Strategy tracking
        self.strategy_name = strategy_name or "default"

        # Timestamps
        self.created_at = created_at if created_at else datetime.utcnow()
        self.settled_at = None

    def calculate_potential_winnings(self):
        """Calculate potential winnings based on odds"""
        return self.bet_amount * self.odds

    def settle(self, is_winner, stake_after):
        """
        Settle the bet with outcome and final stake.
        
        Args:
            is_winner (bool): Whether the bet won
            stake_after (float): Stake balance after settlement
        """
        self.is_winner = is_winner
        self.stake_after = stake_after
        self.settled_at = datetime.utcnow()
        self.is_settled = True

        if is_winner:
            self.outcome = BetOutcome.WIN
            self.actual_winnings = self.calculate_potential_winnings()
        else:
            self.outcome = BetOutcome.LOSS
            self.actual_winnings = -self.bet_amount

    def to_dict(self):
        """Convert bet to dictionary"""
        return {
            "bet_id": self.bet_id,
            "gambler_id": self.gambler_id,
            "session_id": self.session_id,
            "bet_amount": self.bet_amount,
            "win_probability": self.win_probability,
            "odds": self.odds,
            "potential_winnings": self.calculate_potential_winnings(),
            "stake_before": self.stake_before,
            "stake_after": self.stake_after,
            "outcome": self.outcome.value if self.outcome else "pending",
            "is_winner": self.is_winner,
            "is_settled": self.is_settled,
            "actual_winnings": self.actual_winnings,
            "strategy_name": self.strategy_name,
            "created_at": self.created_at.isoformat(),
            "settled_at": self.settled_at.isoformat() if self.settled_at else None
        }

    def __repr__(self):
        return (
            f"Bet(id={self.bet_id}, amount={self.bet_amount}, "
            f"probability={self.win_probability}, outcome={self.outcome.value})"
        )
