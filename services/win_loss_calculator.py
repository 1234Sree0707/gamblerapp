# services/win_loss_calculator.py

import logging
from models.outcome_strategies import OutcomeStrategyFactory, OutcomeStrategyType
from models.odds_configuration import OddsConfiguration, OddsType
from models.game_result import GameResult, WinLossStatistics, RunningTotals

logger = logging.getLogger(__name__)


class WinLossCalculator:
    """
    Comprehensive win/loss calculation service implementing all 6 use cases:
    
    1. Determine Outcomes: Multiple outcome strategies (random, weighted)
    2. Calculate Winnings: Automatic calculation based on odds
    3. Calculate Losses: Automatic deduction from stake
    4. Maintain Running Totals: Real-time tracking
    5. Compute Win/Loss Ratio: Instant ratio calculation
    6. Track Consecutive Streaks: Current and longest streaks
    """
    
    def __init__(
        self,
        initial_balance,
        outcome_strategy=OutcomeStrategyType.RANDOM,
        odds_configuration=None,
        house_edge=0.0
    ):
        """
        Initialize calculator.
        
        Args:
            initial_balance (float): Starting balance
            outcome_strategy (OutcomeStrategyType): How to determine outcomes
            odds_configuration (OddsConfiguration): How to calculate winnings
            house_edge (float): House edge percentage (0-0.5)
        """
        self.initial_balance = initial_balance
        
        # Setup outcome strategy
        if isinstance(outcome_strategy, str):
            outcome_strategy = OutcomeStrategyType(outcome_strategy)
        self.outcome_strategy = OutcomeStrategyFactory.create_strategy(
            outcome_strategy,
            house_edge=house_edge
        )
        
        # Setup odds configuration
        self.odds_config = odds_configuration or OddsConfiguration(
            OddsType.FIXED,
            base_odds=2.0
        )
        
        # Initialize tracking
        self.statistics = WinLossStatistics()
        self.running_totals = RunningTotals(initial_balance)
        self.game_count = 0
    
    # USE CASE 1: Determine Outcomes
    def determine_outcome(self, win_probability):
        """
        Determine game outcome using configured strategy.
        
        Args:
            win_probability (float): Probability of winning (0-1)
            
        Returns:
            bool: True if wins, False if loses
        """
        is_winner = self.outcome_strategy.determine_outcome(win_probability)
        
        logger.info(
            f"Outcome determined: {'WIN' if is_winner else 'LOSS'} "
            f"(probability={win_probability:.2%})"
        )
        
        return is_winner
    
    # USE CASE 2: Calculate Winnings
    def calculate_winnings(
        self,
        bet_amount,
        is_winner,
        win_probability=None,
        odds_value=None
    ):
        """
        Calculate winnings based on bet and outcome.
        
        Args:
            bet_amount (float): Amount bet
            is_winner (bool): Whether bet won
            win_probability (float): Win probability (for some odds types)
            odds_value (float): Explicit odds override
            
        Returns:
            float: Winnings amount
        """
        if not is_winner:
            winnings = 0
        else:
            winnings = self.odds_config.calculate_winnings(
                bet_amount,
                win_probability,
                odds_value
            )
        
        logger.debug(
            f"Winnings calculated: bet=${bet_amount}, "
            f"winner={'yes' if is_winner else 'no'}, winnings=${winnings:.2f}"
        )
        
        return winnings
    
    # USE CASE 3: Calculate Losses & Apply to Stake
    def calculate_and_apply_result(
        self,
        bet_amount,
        win_probability,
        odds_value=None
    ):
        """
        Play a complete game: determine outcome, calculate winnings, update stake.
        
        Args:
            bet_amount (float): Amount to bet
            win_probability (float): Probability of winning
            odds_value (float): Optional custom odds
            
        Returns:
            GameResult: Complete game result
        """
        # Validate inputs
        if bet_amount <= 0:
            raise ValueError(f"Bet amount must be positive, got {bet_amount}")
        
        if not (0 < win_probability < 1):
            raise ValueError(
                f"Win probability must be 0-1, got {win_probability}"
            )
        
        # Get stake before
        stake_before = self.running_totals.current_balance
        
        if bet_amount > stake_before:
            raise ValueError(
                f"Bet ${bet_amount} exceeds balance ${stake_before}"
            )
        
        # Determine outcome
        is_winner = self.determine_outcome(win_probability)
        
        # Calculate winnings
        winnings = self.calculate_winnings(
            bet_amount,
            is_winner,
            win_probability,
            odds_value
        )
        
        # Calculate new stake
        if is_winner:
            stake_after = stake_before + winnings
        else:
            stake_after = stake_before - bet_amount
        
        # Ensure non-negative stake
        stake_after = max(0, stake_after)
        
        # Create and record result
        self.game_count += 1
        game_result = GameResult(
            game_number=self.game_count,
            bet_amount=bet_amount,
            is_winner=is_winner,
            stake_before=stake_before,
            stake_after=stake_after,
            winnings=winnings,
            odds=odds_value or self.odds_config.base_odds,
            win_probability=win_probability
        )
        
        # Update tracking
        self.statistics.add_result(game_result)
        self.running_totals.update_balance(stake_after)
        
        logger.info(
            f"Game {self.game_count}: {game_result.outcome.upper()} "
            f"bet=${bet_amount}, stake=${ stake_before:.2f}→${stake_after:.2f}"
        )
        
        return game_result
    
    # USE CASE 4: Maintain Running Totals
    def get_running_totals(self):
        """Get current running totals"""
        return self.running_totals.get_summary()
    
    # USE CASE 5: Compute Win/Loss Ratio
    def compute_win_loss_ratio(self):
        """
        Compute comprehensive win/loss metrics.
        
        Returns:
            dict: Win/loss statistics
        """
        return{
            'win_rate': self.statistics.win_rate_percentage,
            'loss_rate': self.statistics.loss_rate_percentage,
            'win_loss_ratio': (
                self.statistics.total_wins / max(1, self.statistics.total_losses)
            ),
            'profit_factor': self.statistics.profit_factor,
            'roi': self.statistics.roi_percentage,
            'total_wins': self.statistics.total_wins,
            'total_losses': self.statistics.total_losses,
            'net_profit_loss': self.statistics.net_profit_loss
        }
    
    # USE CASE 6: Track Consecutive Streaks
    def get_streak_info(self):
        """Get current and longest streak information"""
        return {
            'current_streak': self.statistics.current_streak,
            'longest_win_streak': self.statistics.longest_win_streak,
            'longest_loss_streak': self.statistics.longest_loss_streak,
            'streak_type': (
                'winning' if self.statistics.current_streak > 0
                else 'losing' if self.statistics.current_streak < 0
                else 'none'
            ),
            'streak_count': abs(self.statistics.current_streak)
        }
    
    # COMPREHENSIVE REPORTS
    def get_full_report(self):
        """Get comprehensive performance report"""
        return {
            'game_summary': {
                'total_games': self.statistics.total_games,
                'total_bets': self.statistics.total_bet_amount,
            },
            'outcomes': {
                'wins': self.statistics.total_wins,
                'losses': self.statistics.total_losses,
                'win_rate': f"{self.statistics.win_rate_percentage:.1f}%",
            },
            'financial': {
                'total_won': self.statistics.total_amount_won,
                'total_lost': self.statistics.total_amount_lost,
                'net_profit_loss': self.statistics.net_profit_loss,
                'roi': f"{self.statistics.roi_percentage:+.2f}%",
                'profit_factor': f"{self.statistics.profit_factor:.2f}x",
            },
            'balance': self.running_totals.get_summary(),
            'streaks': self.get_streak_info(),
            'extremes': {
                'largest_win': self.statistics.largest_win,
                'largest_loss': self.statistics.largest_loss,
                'average_win': self.statistics.average_win,
                'average_loss': self.statistics.average_loss,
            }
        }
    
    def __repr__(self):
        return (
            f"WinLossCalculator(games={self.game_count}, "
            f"balance=${self.running_totals.current_balance:.2f}, "
            f"roi={self.statistics.roi_percentage:.1f}%)"
        )
