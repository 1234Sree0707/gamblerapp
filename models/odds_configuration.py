# models/odds_configuration.py

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class OddsType(Enum):
    """Types of odds calculation systems"""
    FIXED = "fixed"  # Fixed multiplier (e.g., 2x bet)
    PROBABILITY_BASED = "probability_based"  # Based on win probability
    AMERICAN = "american"  # American odds (-110, +200, etc.)
    DECIMAL = "decimal"  # European decimal odds (1.5, 2.0, etc.)


class OddsConfiguration:
    """
    Configures how winnings are calculated based on bet odds.
    
    Use Cases:
    1. Fixed Odds: Simple multiplier (bet $10, odds 2.0 = win $20)
    2. Probability-based: Higher payout for lower probability wins
    3. American: Sports betting format
    4. Decimal: European betting format
    """
    
    def __init__(self, odds_type=OddsType.FIXED, base_odds=2.0):
        """
        Initialize odds configuration.
        
        Args:
            odds_type (OddsType): Type of odds calculation
            base_odds (float): Base odds multiplier or reference value
        """
        self.odds_type = odds_type
        self.base_odds = base_odds
    
    def calculate_winnings(self, bet_amount, win_probability=None, odds_value=None):
        """
        Calculate winnings based on odds configuration.
        
        Args:
            bet_amount (float): Amount betted
            win_probability (float): Win probability (0-1), used for some odds types
            odds_value (float): Explicit odds value, overrides odds_type calculation
            
        Returns:
            float: Calculated winnings
        """
        if odds_value:
            return self._apply_fixed_odds(bet_amount, odds_value)
        
        if self.odds_type == OddsType.FIXED:
            return self._apply_fixed_odds(bet_amount, self.base_odds)
        
        elif self.odds_type == OddsType.PROBABILITY_BASED:
            if win_probability is None:
                raise ValueError("Probability-based odds requires win_probability")
            return self._apply_probability_based_odds(bet_amount, win_probability)
        
        elif self.odds_type == OddsType.AMERICAN:
            if odds_value is None:
                odds_value = self._convert_to_american_odds(self.base_odds)
            return self._apply_american_odds(bet_amount, odds_value)
        
        elif self.odds_type == OddsType.DECIMAL:
            if odds_value is None:
                odds_value = self.base_odds
            return self._apply_decimal_odds(bet_amount, odds_value)
        
        else:
            raise ValueError(f"Unknown odds type: {self.odds_type}")
    
    def _apply_fixed_odds(self, bet_amount, multiplier):
        """
        Apply fixed odds multiplier.
        
        Example: bet=$100, multiplier=2.0 → winnings=$200
        """
        winnings = bet_amount * multiplier
        logger.debug(f"Fixed odds: bet=${bet_amount}, multiplier={multiplier}, winnings=${winnings:.2f}")
        return winnings
    
    def _apply_probability_based_odds(self, bet_amount, win_probability):
        """
        Apply probability-based odds.
        
        Formula: winnings = bet / win_probability
        Higher probability = lower payout
        Lower probability = higher payout
        
        Example: bet=$100, prob=0.5 → winnings=$200 (2:1)
        Example: bet=$100, prob=0.1 → winnings=$1000 (10:1)
        """
        if win_probability <= 0:
            raise ValueError(f"Win probability must be > 0, got {win_probability}")
        
        winnings = bet_amount / win_probability
        logger.debug(
            f"Probability-based odds: bet=${bet_amount}, "
            f"prob={win_probability:.2%}, winnings=${winnings:.2f}"
        )
        return winnings
    
    def _apply_american_odds(self, bet_amount, american_odds):
        """
        Apply American odds format.
        
        Negative odds (e.g., -110): favorite
          winnings = (bet * 100) / abs(odds)
          
        Positive odds (e.g., +200): underdog
          winnings = (bet * odds) / 100
        """
        if american_odds > 0:
            # Underdog odds
            winnings = (bet_amount * american_odds) / 100
        else:
            # Favorite odds
            winnings = (bet_amount * 100) / abs(american_odds)
        
        logger.debug(
            f"American odds: bet=${bet_amount}, odds={american_odds}, "
            f"winnings=${winnings:.2f}"
        )
        return winnings
    
    def _apply_decimal_odds(self, bet_amount, decimal_odds):
        """
        Apply decimal (European) odds format.
        
        Formula: winnings = bet * odds
        
        Example: bet=$100, odds=2.5 → winnings=$250
        """
        if decimal_odds < 1:
            raise ValueError(f"Decimal odds must be >= 1.0, got {decimal_odds}")
        
        winnings = bet_amount * decimal_odds
        logger.debug(
            f"Decimal odds: bet=${bet_amount}, odds={decimal_odds}, "
            f"winnings=${winnings:.2f}"
        )
        return winnings
    
    def _convert_to_american_odds(self, decimal_odds):
        """Convert decimal odds to American format"""
        if decimal_odds < 2:
            # Favorite (negative)
            return int(-(100 / (decimal_odds - 1)))
        else:
            # Underdog (positive)
            return int((decimal_odds - 1) * 100)
    
    def calculate_odds_value(self, win_probability):
        """Calculate odds value from probability"""
        if self.odds_type == OddsType.PROBABILITY_BASED:
            return 1 / win_probability if win_probability > 0 else float('inf')
        return self.base_odds
    
    def __repr__(self):
        return f"OddsConfiguration(type={self.odds_type.value}, base_odds={self.base_odds})"
