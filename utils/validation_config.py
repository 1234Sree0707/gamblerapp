# utils/validation_config.py

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ValidationConfig:
    """
    Configurable validation rules.
    
    Centralizes all validation constraints and allows customization
    for different betting scenarios.
    """
    
    # Stake validation
    min_stake: float = 0.01
    max_stake: float = 1000000.00
    allow_zero_stake: bool = False
    
    # Bet amount validation
    min_bet: float = 0.01
    max_bet_multiplier: float = 1.0  # Multiplier of current stake
    
    # Limit boundary validation
    min_limit: float = 1.00
    max_limit: float = 100000.00
    
    # Probability validation
    min_probability: float = 0.0
    max_probability: float = 1.0
    
    # Odds validation
    min_odds: float = 0.01
    max_odds: float = 10000.0
    
    # Numeric input validation
    allow_negative_numbers: bool = False
    allow_infinity: bool = False
    allow_nan: bool = False
    
    # Validation mode
    strict_mode: bool = True  # If True, warnings become errors
    require_non_null: bool = True
    
    # Numeric precision
    decimal_places: int = 2
    epsilon: float = 1e-10  # For floating-point comparisons

    def get_stake_range(self) -> Tuple[float, float]:
        """Get allowed stake range"""
        return (self.min_stake, self.max_stake)

    def get_bet_range(self, current_stake: float) -> Tuple[float, float]:
        """Get allowed bet range based on current stake"""
        max_bet = min(current_stake * self.max_bet_multiplier, current_stake)
        return (self.min_bet, max_bet)

    def get_limit_range(self) -> Tuple[float, float]:
        """Get allowed limit range"""
        return (self.min_limit, self.max_limit)

    def get_probability_range(self) -> Tuple[float, float]:
        """Get allowed probability range"""
        return (self.min_probability, self.max_probability)

    def get_odds_range(self) -> Tuple[float, float]:
        """Get allowed odds range"""
        return (self.min_odds, self.max_odds)

    def __str__(self):
        """String representation of config"""
        return (
            f"ValidationConfig(\n"
            f"  stake_range: {self.get_stake_range()}\n"
            f"  bet_range: min={self.min_bet}\n"
            f"  limit_range: {self.get_limit_range()}\n"
            f"  probability_range: {self.get_probability_range()}\n"
            f"  odds_range: {self.get_odds_range()}\n"
            f"  strict_mode: {self.strict_mode}\n"
            f")"
        )


# Predefined configurations for different scenarios

CONSERVATIVE_CONFIG = ValidationConfig(
    min_stake=10.00,
    max_stake=10000.00,
    min_bet=1.00,
    max_bet_multiplier=0.1,  # Max 10% of stake
    min_probability=0.1,
    max_probability=0.9,
    strict_mode=True
)

STANDARD_CONFIG = ValidationConfig(
    min_stake=0.01,
    max_stake=100000.00,
    min_bet=0.01,
    max_bet_multiplier=1.0,
    min_probability=0.0,
    max_probability=1.0,
    strict_mode=True
)

AGGRESSIVE_CONFIG = ValidationConfig(
    min_stake=0.01,
    max_stake=1000000.00,
    min_bet=0.01,
    max_bet_multiplier=2.0,  # Max 200% of stake (with credit)
    min_probability=0.0,
    max_probability=1.0,
    strict_mode=False  # Warnings not treated as errors
)

DEVELOPMENT_CONFIG = ValidationConfig(
    min_stake=0.01,
    max_stake=1000000.00,
    min_bet=0.01,
    max_bet_multiplier=10.0,  # Very permissive
    allow_zero_stake=True,
    min_probability=0.0,
    max_probability=1.0,
    allow_infinity=False,
    allow_nan=False,
    strict_mode=False
)
