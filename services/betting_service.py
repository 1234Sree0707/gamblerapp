# services/betting_service.py

import random
import logging
from datetime import datetime
from models.betting_strategies import StrategyFactory
from repositories.bet_repository import BetRepository
from repositories.betting_session_repository import BettingSessionRepository

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BettingService:
    """
    Complete betting service implementing all use cases.
    
    Use Cases:
    1. Place Single Bet: placeBet() with specified amount and win probability
    2. Determine Outcome: determineBetOutcome() using random probability
    3. Apply to Stake: settleBet() automatically updates stake based on outcome
    4. Validate Amount: Built-in validation against stake and min/max limits
    5. Different Strategies: Multiple strategy implementations
    6. Multiple Consecutive Bets: placeConsecutiveBets() handles session betting
    
    Features:
    - Probability-based outcomes with configurable probabilities
    - Automatic stake management after each bet settlement
    - Strategy pattern for easy new strategy addition
    - Comprehensive validation: min/max limits, stake checks
    - Session tracking with complete audit trail
    - Automatic odds calculation based on probability
    - Real-time stake updates with detailed logging
    """

    def __init__(self):
        """Initialize the betting service with repositories"""
        self.bet_repository = BetRepository()
        self.session_repository = BettingSessionRepository()

        # Configuration
        self.min_bet = 1.0
        self.max_bet = 10000.0
        self.min_win_probability = 0.01  # 1%
        self.max_win_probability = 0.99  # 99%

    def validate_bet_amount(self, bet_amount, current_stake):
        """
        Validate bet amount against constraints.
        
        Args:
            bet_amount (float): Amount to bet
            current_stake (float): Available stake
            
        Returns:
            tuple: (is_valid, error_message)
            
        Raises:
            ValueError: If validation fails
        """
        if bet_amount <= 0:
            raise ValueError("Bet amount must be positive")

        if bet_amount < self.min_bet:
            raise ValueError(
                f"Bet amount ${bet_amount} below minimum ${self.min_bet}"
            )

        if bet_amount > self.max_bet:
            raise ValueError(
                f"Bet amount ${bet_amount} above maximum ${self.max_bet}"
            )

        if bet_amount > current_stake:
            raise ValueError(
                f"Bet amount ${bet_amount} exceeds available stake ${current_stake}"
            )

        return True, None

    def validate_win_probability(self, probability):
        """
        Validate win probability.
        
        Args:
            probability (float): Win probability (0-1)
            
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If invalid
        """
        if not (0 < probability < 1):
            raise ValueError(
                f"Win probability must be between 0 and 1, got {probability}"
            )
        return True

    def calculate_odds(self, win_probability):
        """
        Calculate odds from probability.
        
        Odds = 1 / probability
        Example: 50% probability = 2.0 odds
        
        Args:
            win_probability (float): Win probability (0-1)
            
        Returns:
            float: Calculated odds
        """
        if win_probability <= 0:
            return 1.0
        return 1.0 / win_probability

    def determine_bet_outcome(self, win_probability):
        """
        Determine bet outcome using probability.
        
        Uses random number generation to simulate realistic outcome.
        
        Args:
            win_probability (float): Probability of winning (0-1)
            
        Returns:
            bool: True if bet wins, False if loses
        """
        random_value = random.random()
        is_winner = random_value < win_probability

        logger.info(
            f"Bet outcome determined: random={random_value:.4f}, "
            f"threshold={win_probability:.4f}, winner={is_winner}"
        )

        return is_winner

    def place_bet(
        self,
        gambler_id,
        current_stake,
        bet_amount,
        win_probability,
        session_id=None,
        strategy_name="manual",
        auto_settle=True
    ):
        """
        Place a single bet with specified amount.
        
        Use Case 1: Place Single Bet
        Use Case 2: Determine Outcome using probability
        Use Case 3: Apply to Stake based on outcome
        Use Case 4: Validate before placing
        
        Args:
            gambler_id (int): Gambler placing the bet
            current_stake (float): Current available stake
            bet_amount (float): Amount to bet
            win_probability (float): Probability of winning (0-1)
            session_id (str): Optional session ID
            strategy_name (str): Strategy name
            auto_settle (bool): Automatically settle the bet
            
        Returns:
            dict: Bet result with outcome and new stake
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        self.validate_bet_amount(bet_amount, current_stake)
        self.validate_win_probability(win_probability)

        logger.info(
            f"Placing bet: gambler={gambler_id}, amount=${bet_amount}, "
            f"probability={win_probability:.2%}, stake=${current_stake}"
        )

        # Calculate odds
        odds = self.calculate_odds(win_probability)

        # Create bet record
        bet = self.bet_repository.create(
            gambler_id=gambler_id,
            bet_amount=bet_amount,
            win_probability=win_probability,
            odds=odds,
            stake_before=current_stake,
            session_id=session_id,
            strategy_name=strategy_name
        )

        logger.info(f"Bet created: {bet}")

        # Auto-settle if requested
        if auto_settle:
            return self.settle_bet(bet.bet_id, gambler_id)
        else:
            return {
                "success": True,
                "bet_id": bet.bet_id,
                "status": "pending",
                "stake": current_stake
            }

    def settle_bet(self, bet_id, gambler_id, new_stake=None):
        """
        Settle a bet with outcome and update stake.
        
        Use Case 3: Apply Bet Amount to Current Stake
        
        Args:
            bet_id (str): ID of bet to settle
            gambler_id (int): Gambler ID for validation
            new_stake (float): Updated stake (calculated if None)
            
        Returns:
            dict: Settlement result
            
        Raises:
            ValueError: If bet not found
        """
        bet = self.bet_repository.get_by_id(bet_id)
        if not bet:
            raise ValueError(f"Bet {bet_id} not found")

        if bet.gambler_id != gambler_id:
            raise ValueError("Gambler mismatch")

        # Determine outcome
        is_winner = self.determine_bet_outcome(bet.win_probability)

        # Calculate new stake
        if new_stake is None:
            if is_winner:
                new_stake = bet.stake_before + bet.actual_winnings
            else:
                new_stake = bet.stake_before - bet.bet_amount
        
        # Ensure non-negative stake
        new_stake = max(0, new_stake)

        # Settle the bet
        self.bet_repository.settle(bet_id, is_winner, new_stake)

        logger.info(
            f"Bet settled: {bet_id}, outcome={'WIN' if is_winner else 'LOSS'}, "
            f"stake_before=${bet.stake_before}, stake_after=${new_stake}"
        )

        return {
            "success": True,
            "bet_id": bet_id,
            "outcome": "win" if is_winner else "loss",
            "bet_amount": bet.bet_amount,
            "winnings": bet.actual_winnings,
            "stake_before": bet.stake_before,
            "stake_after": new_stake,
            "potential_winnings": bet.calculate_potential_winnings()
        }

    def place_bet_with_strategy(
        self,
        gambler_id,
        current_stake,
        strategy_name,
        base_amount,
        win_probability,
        session_id=None,
        auto_settle=True,
        **strategy_kwargs
    ):
        """
        Place a bet using a betting strategy.
        
        Use Case 5: Different Betting Strategies
        
        Args:
            gambler_id (int): Gambler ID
            current_stake (float): Current stake
            strategy_name (str): Name of strategy to use
            base_amount (float): Base bet amount for strategy
            win_probability (float): Win probability for this bet
            session_id (str): Optional session ID
            auto_settle (bool): Automatically settle
            **strategy_kwargs: Strategy-specific parameters
            
        Returns:
            dict: Bet result
            
        Raises:
            ValueError: If strategy not found
        """
        # Create strategy
        strategy = StrategyFactory.create_strategy(
            strategy_name,
            base_amount,
            **strategy_kwargs
        )

        # Calculate bet amount using strategy
        bet_amount = strategy.calculate_bet_amount(current_stake)

        logger.info(
            f"Strategy-based bet: strategy={strategy_name}, "
            f"bet_amount=${bet_amount}"
        )

        # Place the bet
        return self.place_bet(
            gambler_id=gambler_id,
            current_stake=current_stake,
            bet_amount=bet_amount,
            win_probability=win_probability,
            session_id=session_id,
            strategy_name=strategy_name,
            auto_settle=auto_settle
        )

    def place_consecutive_bets(
        self,
        gambler_id,
        initial_stake,
        num_bets,
        strategy_name="fixed",
        base_amount=10.0,
        win_probability=0.5,
        **strategy_kwargs
    ):
        """
        Place multiple consecutive bets in a session.
        
        Use Case 6: Multiple Consecutive Bets
        
        Args:
            gambler_id (int): Gambler ID
            initial_stake (float): Starting stake
            num_bets (int): Number of bets to place
            strategy_name (str): Betting strategy
            base_amount (float): Base bet amount
            win_probability (float): Win probability per bet
            **strategy_kwargs: Strategy parameters
            
        Returns:
            dict: Session summary with all bets
        """
        # Create session
        session = self.session_repository.create(
            gambler_id=gambler_id,
            initial_stake=initial_stake,
            strategy_name=strategy_name
        )

        logger.info(
            f"Starting betting session: {session.session_id}, "
            f"strategy={strategy_name}, num_bets={num_bets}"
        )

        # Create strategy
        strategy = StrategyFactory.create_strategy(
            strategy_name,
            base_amount,
            **strategy_kwargs
        )

        current_stake = initial_stake
        bets_placed = []

        for i in range(num_bets):
            try:
                # Calculate bet amount
                bet_amount = strategy.calculate_bet_amount(current_stake)

                # Place and settle bet
                result = self.place_bet(
                    gambler_id=gambler_id,
                    current_stake=current_stake,
                    bet_amount=bet_amount,
                    win_probability=win_probability,
                    session_id=session.session_id,
                    strategy_name=strategy_name,
                    auto_settle=True
                )

                # Get settled bet
                bet = self.bet_repository.get_by_id(result["bet_id"])
                bets_placed.append(bet)

                # Add to session
                session.add_bet(bet)
                session.settle_bet(bet)

                # Update current stake
                current_stake = result["stake_after"]

                # Update strategy based on outcome
                is_winner = result["outcome"] == "win"
                if hasattr(strategy, "on_win") and is_winner:
                    strategy.on_win()
                elif hasattr(strategy, "on_loss") and not is_winner:
                    strategy.on_loss()

                logger.info(
                    f"Bet {i + 1}/{num_bets}: {result['outcome'].upper()} "
                    f"(${result['bet_amount']} -> stake ${current_stake:.2f})"
                )

            except Exception as e:
                logger.error(f"Error placing bet {i + 1}: {str(e)}")
                break

        # End session
        session.end_session()
        self.session_repository.end_session(session.session_id)

        logger.info(f"Session ended: {session.session_id}")

        return session.get_summary()

    def get_bet(self, bet_id):
        """Get bet details"""
        bet = self.bet_repository.get_by_id(bet_id)
        if not bet:
            raise ValueError(f"Bet {bet_id} not found")
        return bet.to_dict()

    def get_gambler_bets(self, gambler_id):
        """Get all bets for a gambler"""
        bets = self.bet_repository.get_by_gambler(gambler_id)
        return [bet.to_dict() for bet in bets]

    def get_gambler_statistics(self, gambler_id):
        """Get betting statistics for a gambler"""
        return self.bet_repository.get_statistics_by_gambler(gambler_id)

    def start_session(self, gambler_id, initial_stake, strategy_name="default"):
        """
        Start a new betting session.
        
        Args:
            gambler_id (int): Gambler ID
            initial_stake (float): Starting stake
            strategy_name (str): Primary strategy for session
            
        Returns:
            BettingSession: The created session
        """
        session = self.session_repository.create(
            gambler_id=gambler_id,
            initial_stake=initial_stake,
            strategy_name=strategy_name
        )

        logger.info(
            f"Session started: {session.session_id}, "
            f"initial_stake=${initial_stake}"
        )

        return session

    def get_session(self, session_id):
        """Get session details"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session.to_dict()

    def get_active_sessions(self):
        """Get all active sessions"""
        sessions = self.session_repository.get_active_sessions()
        return [s.to_dict() for s in sessions]

    def get_available_strategies(self):
        """Get list of available betting strategies"""
        return {
            "strategies": StrategyFactory.get_available_strategies(),
            "descriptions": {
                "fixed": "Always bet the same amount",
                "percentage": "Bet a percentage of current stake (e.g., 5%)",
                "martingale": "Double bet after each loss, reset to base after win",
                "reverse_martingale": "Double bet after each win, reset after loss",
                "fibonacci": "Progress through Fibonacci sequence on losses",
                "d_alembert": "Gradually increase/decrease bet by fixed increment"
            }
        }
