# models/outcome_strategies.py

import random
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class OutcomeStrategyType(Enum):
    """Types of outcome determination strategies"""
    RANDOM = "random"
    WEIGHTED_PROBABILITY = "weighted_probability"
    HOUSE_EDGE = "house_edge"


class OutcomeStrategy:
    """Base class for outcome determination strategies"""
    
    def determine_outcome(self, win_probability):
        """
        Determine if a bet wins based on probability.
        
        Args:
            win_probability (float): Probability of winning (0-1)
            
        Returns:
            bool: True if wins, False if loses
        """
        raise NotImplementedError


class RandomOutcomeStrategy(OutcomeStrategy):
    """
    Pure random outcome based on probability.
    
    Use Case: Simple probability-based betting without house edge.
    Example: 50% probability = exactly 50% chance of winning
    """
    
    def determine_outcome(self, win_probability):
        """Determine outcome using pure random probability"""
        if not (0 < win_probability < 1):
            raise ValueError(f"Win probability must be between 0 and 1, got {win_probability}")
        
        random_value = random.random()
        is_winner = random_value < win_probability
        
        logger.debug(
            f"Random outcome: random={random_value:.4f}, "
            f"threshold={win_probability:.4f}, winner={is_winner}"
        )
        
        return is_winner


class WeightedProbabilityStrategy(OutcomeStrategy):
    """
    Weighted probability with house edge for realistic casino simulation.
    
    Use Case: Simulate realistic casino where house has edge.
    The higher the bet probability, the more the house takes.
    """
    
    def __init__(self, house_edge=0.02):
        """
        Initialize with house edge percentage.
        
        Args:
            house_edge (float): House edge as decimal (0.02 = 2%)
        """
        if not (0 <= house_edge < 0.5):
            raise ValueError(f"House edge must be 0-0.5, got {house_edge}")
        
        self.house_edge = house_edge
    
    def determine_outcome(self, win_probability):
        """
        Determine outcome with house edge consideration.
        
        Formula: effective_prob = win_probability * (1 - house_edge)
        This means the player's actual winning chance is reduced.
        """
        if not (0 < win_probability < 1):
            raise ValueError(f"Win probability must be between 0 and 1, got {win_probability}")
        
        # Apply house edge - reduces player's winning probability
        effective_probability = win_probability * (1 - self.house_edge)
        
        random_value = random.random()
        is_winner = random_value < effective_probability
        
        logger.debug(
            f"Weighted outcome: original_prob={win_probability:.4f}, "
            f"house_edge={self.house_edge:.2%}, effective_prob={effective_probability:.4f}, "
            f"random={random_value:.4f}, winner={is_winner}"
        )
        
        return is_winner


class OutcomeStrategyFactory:
    """Factory for creating outcome strategies"""
    
    _strategies = {
        OutcomeStrategyType.RANDOM: RandomOutcomeStrategy,
        OutcomeStrategyType.WEIGHTED_PROBABILITY: WeightedProbabilityStrategy,
        OutcomeStrategyType.HOUSE_EDGE: WeightedProbabilityStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_type=OutcomeStrategyType.RANDOM, **kwargs):
        """
        Create an outcome strategy.
        
        Args:
            strategy_type (OutcomeStrategyType): Type of strategy to create
            **kwargs: Additional arguments for the strategy
            
        Returns:
            OutcomeStrategy: The created strategy
        """
        if isinstance(strategy_type, str):
            strategy_type = OutcomeStrategyType(strategy_type)
        
        if strategy_type not in cls._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = cls._strategies[strategy_type]
        
        if strategy_type == OutcomeStrategyType.WEIGHTED_PROBABILITY:
            return strategy_class(kwargs.get('house_edge', 0.02))
        
        return strategy_class()
    
    @classmethod
    def get_available_strategies(cls):
        """Get list of available strategy types"""
        return [s.value for s in OutcomeStrategyType]
