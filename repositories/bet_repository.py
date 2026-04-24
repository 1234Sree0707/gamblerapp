# repositories/bet_repository.py

from models.bet import Bet
from datetime import datetime
import uuid


class BetRepository:
    """
    Repository for managing bets.
    Handles persistence of bet records.
    """

    def __init__(self):
        """Initialize with empty bet storage"""
        self.bets = {}  # bet_id -> Bet
        self.gambler_bets = {}  # gambler_id -> [bet_ids]
        self.session_bets = {}  # session_id -> [bet_ids]

    def create(
        self,
        gambler_id,
        bet_amount,
        win_probability,
        odds=1.0,
        stake_before=0,
        session_id=None,
        strategy_name=None
    ):
        """
        Create and store a new bet.
        
        Args:
            gambler_id (int): Gambler's ID
            bet_amount (float): Amount to bet
            win_probability (float): Probability of winning (0-1)
            odds (float): Odds for potential winnings
            stake_before (float): Stake before the bet
            session_id (str): Associated session ID
            strategy_name (str): Betting strategy used
            
        Returns:
            Bet: The created bet
        """
        bet_id = str(uuid.uuid4())

        bet = Bet(
            bet_id=bet_id,
            gambler_id=gambler_id,
            bet_amount=bet_amount,
            win_probability=win_probability,
            odds=odds,
            stake_before=stake_before,
            session_id=session_id,
            strategy_name=strategy_name
        )

        self.bets[bet_id] = bet

        # Track by gambler
        if gambler_id not in self.gambler_bets:
            self.gambler_bets[gambler_id] = []
        self.gambler_bets[gambler_id].append(bet_id)

        # Track by session
        if session_id:
            if session_id not in self.session_bets:
                self.session_bets[session_id] = []
            self.session_bets[session_id].append(bet_id)

        return bet

    def get_by_id(self, bet_id):
        """Get bet by ID"""
        return self.bets.get(bet_id)

    def get_by_gambler(self, gambler_id):
        """Get all bets for a gambler"""
        bet_ids = self.gambler_bets.get(gambler_id, [])
        return [self.bets[bid] for bid in bet_ids if bid in self.bets]

    def get_by_session(self, session_id):
        """Get all bets in a session"""
        bet_ids = self.session_bets.get(session_id, [])
        return [self.bets[bid] for bid in bet_ids if bid in self.bets]

    def update(self, bet_id, **kwargs):
        """Update bet attributes"""
        if bet_id not in self.bets:
            raise ValueError(f"Bet {bet_id} not found")

        bet = self.bets[bet_id]
        for key, value in kwargs.items():
            if hasattr(bet, key):
                setattr(bet, key, value)

        return bet

    def settle(self, bet_id, is_winner, stake_after):
        """
        Settle a bet with outcome.
        
        Args:
            bet_id (str): Bet ID
            is_winner (bool): Whether bet won
            stake_after (float): Stake after settlement
        """
        if bet_id not in self.bets:
            raise ValueError(f"Bet {bet_id} not found")

        bet = self.bets[bet_id]
        bet.settle(is_winner, stake_after)
        return bet

    def delete(self, bet_id):
        """Delete a bet"""
        if bet_id not in self.bets:
            raise ValueError(f"Bet {bet_id} not found")

        bet = self.bets[bet_id]

        # Remove from gambler tracking
        gambler_id = bet.gambler_id
        if gambler_id in self.gambler_bets:
            self.gambler_bets[gambler_id] = [
                bid for bid in self.gambler_bets[gambler_id] if bid != bet_id
            ]

        # Remove from session tracking
        session_id = bet.session_id
        if session_id and session_id in self.session_bets:
            self.session_bets[session_id] = [
                bid for bid in self.session_bets[session_id] if bid != bet_id
            ]

        del self.bets[bet_id]

    def get_all(self):
        """Get all bets"""
        return list(self.bets.values())

    def get_statistics_by_gambler(self, gambler_id):
        """Get betting statistics for a gambler"""
        bets = self.get_by_gambler(gambler_id)

        total_bet = sum(b.bet_amount for b in bets)
        total_won = sum(b.actual_winnings for b in bets if b.is_winner)
        total_lost = sum(abs(b.actual_winnings) for b in bets if b.is_winner is False)
        wins = sum(1 for b in bets if b.is_winner)
        losses = sum(1 for b in bets if b.is_winner is False)
        pending = sum(1 for b in bets if b.is_winner is None)

        return {
            "total_bets": len(bets),
            "total_amount_bet": total_bet,
            "total_won": total_won,
            "total_lost": total_lost,
            "wins": wins,
            "losses": losses,
            "pending": pending,
            "win_rate": (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        }
