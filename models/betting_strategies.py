# models/betting_strategies.py

from abc import ABC, abstractmethod
import math


class BettingStrategy(ABC):
    """
    Abstract base class for betting strategies.
    All strategies implement calculate_bet_amount().
    """

    def __init__(self, base_amount):
        """
        Initialize strategy with base amount.
        
        Args:
            base_amount (float): The base/minimum bet amount
        """
        self.base_amount = base_amount
        self.bet_count = 0

    @abstractmethod
    def calculate_bet_amount(self, current_stake):
        """
        Calculate bet amount based on strategy.
        
        Args:
            current_stake (float): Current game stake
            
        Returns:
            float: The bet amount to place
        """
        pass

    def reset(self):
        """Reset strategy state"""
        self.bet_count = 0

    def __repr__(self):
        return f"{self.__class__.__name__}(base_amount={self.base_amount})"


class FixedAmountStrategy(BettingStrategy):
    """
    Always bet the same amount regardless of wins/losses.
    
    Example: Always bet $10
    """

    def calculate_bet_amount(self, current_stake):
        """Always return the base amount"""
        self.bet_count += 1
        return self.base_amount


class PercentageStrategy(BettingStrategy):
    """
    Bet a percentage of current stake.
    
    Example: Bet 5% of current stake
    """

    def __init__(self, base_amount, percentage=5.0):
        """
        Initialize percentage strategy.
        
        Args:
            base_amount (float): Minimum bet amount
            percentage (float): Percentage of stake to bet (default 5%)
        """
        super().__init__(base_amount)
        self.percentage = percentage

    def calculate_bet_amount(self, current_stake):
        """Bet a percentage of current stake"""
        self.bet_count += 1
        percentage_amount = (current_stake * self.percentage) / 100
        # Ensure minimum of base_amount
        return max(percentage_amount, self.base_amount)


class MartingaleStrategy(BettingStrategy):
    """
    Double bet after each loss, reset to base after win.
    
    Strategy:
    - Start with base amount
    - If loss: double the bet
    - If win: reset to base amount
    
    This aims to recover losses with winnings.
    """

    def __init__(self, base_amount):
        super().__init__(base_amount)
        self.current_multiplier = 1

    def calculate_bet_amount(self, current_stake):
        """Calculate bet using martingale progression"""
        self.bet_count += 1
        return self.base_amount * self.current_multiplier

    def on_loss(self):
        """Double the multiplier after a loss"""
        self.current_multiplier *= 2

    def on_win(self):
        """Reset to base after a win"""
        self.current_multiplier = 1

    def reset(self):
        """Reset strategy state"""
        super().reset()
        self.current_multiplier = 1


class ReverseMartingaleStrategy(BettingStrategy):
    """
    Double bet after each win, reset after loss.
    
    Strategy:
    - Start with base amount
    - If win: double the bet (ride winning streak)
    - If loss: reset to base amount
    
    This aims to maximize winnings during hot streaks.
    """

    def __init__(self, base_amount):
        super().__init__(base_amount)
        self.current_multiplier = 1

    def calculate_bet_amount(self, current_stake):
        """Calculate bet using reverse martingale progression"""
        self.bet_count += 1
        return self.base_amount * self.current_multiplier

    def on_win(self):
        """Double the multiplier after a win"""
        self.current_multiplier *= 2

    def on_loss(self):
        """Reset to base after a loss"""
        self.current_multiplier = 1

    def reset(self):
        """Reset strategy state"""
        super().reset()
        self.current_multiplier = 1


class FibonacciStrategy(BettingStrategy):
    """
    Progress through Fibonacci sequence on losses.
    
    Sequence: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55...
    
    Strategy:
    - Start at position 0 in sequence
    - If loss: move to next position
    - If win: move back two positions (or to start if near start)
    
    More conservative than Martingale.
    """

    FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

    def __init__(self, base_amount):
        super().__init__(base_amount)
        self.position = 0

    def calculate_bet_amount(self, current_stake):
        """Calculate bet using Fibonacci sequence"""
        self.bet_count += 1
        fib_multiplier = self.FIBONACCI[min(self.position, len(self.FIBONACCI) - 1)]
        return self.base_amount * fib_multiplier

    def on_loss(self):
        """Move to next position in sequence after loss"""
        if self.position < len(self.FIBONACCI) - 1:
            self.position += 1

    def on_win(self):
        """Move back two positions after win"""
        self.position = max(0, self.position - 2)

    def reset(self):
        """Reset strategy state"""
        super().reset()
        self.position = 0


class DAlembertStrategy(BettingStrategy):
    """
    Gradually increase/decrease bet by fixed increment.
    
    Strategy:
    - If loss: increase bet by increment (usually 1 unit)
    - If win: decrease bet by increment
    - Bet can't go below base amount
    
    More conservative than Martingale, gradual progression.
    """

    def __init__(self, base_amount, increment=1.0):
        """
        Initialize D'Alembert strategy.
        
        Args:
            base_amount (float): Base bet amount
            increment (float): Amount to increase/decrease per bet
        """
        super().__init__(base_amount)
        self.increment = increment
        self.current_level = 0

    def calculate_bet_amount(self, current_stake):
        """Calculate bet using D'Alembert progression"""
        self.bet_count += 1
        bet = self.base_amount + (self.increment * self.current_level)
        return max(bet, self.base_amount)  # Never go below base

    def on_loss(self):
        """Increase level after loss"""
        self.current_level += 1

    def on_win(self):
        """Decrease level after win"""
        self.current_level = max(0, self.current_level - 1)

    def reset(self):
        """Reset strategy state"""
        super().reset()
        self.current_level = 0


# Strategy factory for easy creation
class StrategyFactory:
    """Factory for creating betting strategies"""

    STRATEGIES = {
        "fixed": FixedAmountStrategy,
        "percentage": PercentageStrategy,
        "martingale": MartingaleStrategy,
        "reverse_martingale": ReverseMartingaleStrategy,
        "fibonacci": FibonacciStrategy,
        "d_alembert": DAlembertStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_name, base_amount, **kwargs):
        """
        Create a strategy instance.
        
        Args:
            strategy_name (str): Name of strategy
            base_amount (float): Base bet amount
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            BettingStrategy: Strategy instance
            
        Raises:
            ValueError: If strategy name not found
        """
        if strategy_name not in cls.STRATEGIES:
            available = ", ".join(cls.STRATEGIES.keys())
            raise ValueError(
                f"Unknown strategy '{strategy_name}'. Available: {available}"
            )

        strategy_class = cls.STRATEGIES[strategy_name]
        return strategy_class(base_amount, **kwargs)

    @classmethod
    def get_available_strategies(cls):
        """Get list of available strategy names"""
        return list(cls.STRATEGIES.keys())
