# utils/safe_input_handler.py

import logging
from typing import Optional, Callable

from utils.input_validator import InputValidator
from utils.validation_types import ValidationResult
from utils.validation_config import ValidationConfig, STANDARD_CONFIG

logger = logging.getLogger(__name__)


class SafeInputHandler:
    """
    Interactive console input handler with validation.
    
    Features:
    - Retry loops for invalid inputs
    - User-friendly prompts
    - Real-time validation feedback
    - Customizable validation rules
    """

    def __init__(
        self,
        validator: InputValidator = None,
        max_retries: int = 3,
        show_range: bool = True
    ):
        """
        Initialize safe input handler.
        
        Args:
            validator: InputValidator instance
            max_retries: Maximum retry attempts
            show_range: Whether to show valid ranges in prompts
        """
        self.validator = validator or InputValidator(STANDARD_CONFIG)
        self.max_retries = max_retries
        self.show_range = show_range
        self.logger = logger

    def get_initial_stake(self) -> float:
        """
        Get validated initial stake from user.
        
        Returns:
            Validated initial stake value
        """
        config = self.validator.config
        min_stake, max_stake = config.get_stake_range()
        
        for attempt in range(self.max_retries):
            try:
                if self.show_range:
                    prompt = f"Enter initial stake (${min_stake:.2f} - ${max_stake:.2f}): $"
                else:
                    prompt = "Enter initial stake: $"
                
                user_input = input(prompt).strip()
                
                result = self.validator.validate_initial_stake(user_input)
                
                if result.is_valid:
                    value = float(user_input)
                    print(f"✓ Stake set to ${value:.2f}")
                    return value
                else:
                    print(f"✗ Error: {result.get_error_messages()[0]}")
                    if attempt < self.max_retries - 1:
                        print(f"  Try again ({self.max_retries - attempt - 1} attempts left)\n")
            
            except KeyboardInterrupt:
                print("\n✗ Input cancelled by user")
                raise
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
        
        raise ValueError(f"Invalid stake after {self.max_retries} attempts")

    def get_bet_amount(self, current_stake: float) -> float:
        """
        Get validated bet amount from user.
        
        Args:
            current_stake: Current available stake
            
        Returns:
            Validated bet amount
        """
        config = self.validator.config
        min_bet, max_bet = config.get_bet_range(current_stake)
        
        for attempt in range(self.max_retries):
            try:
                if self.show_range:
                    prompt = f"Enter bet amount (${min_bet:.2f} - ${max_bet:.2f}): $"
                else:
                    prompt = "Enter bet amount: $"
                
                user_input = input(prompt).strip()
                
                result = self.validator.validate_bet_amount(user_input, current_stake)
                
                if result.is_valid:
                    value = float(user_input)
                    print(f"✓ Bet set to ${value:.2f}")
                    return value
                else:
                    print(f"✗ Error: {result.get_error_messages()[0]}")
                    if attempt < self.max_retries - 1:
                        print(f"  Try again ({self.max_retries - attempt - 1} attempts left)\n")
            
            except KeyboardInterrupt:
                print("\n✗ Input cancelled by user")
                raise
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
        
        raise ValueError(f"Invalid bet amount after {self.max_retries} attempts")

    def get_limits(self, initial_stake: float) -> tuple:
        """
        Get validated lower and upper limits from user.
        
        Args:
            initial_stake: Initial stake value
            
        Returns:
            Tuple of (lower_limit, upper_limit)
        """
        config = self.validator.config
        min_limit, max_limit = config.get_limit_range()
        
        for attempt in range(self.max_retries):
            try:
                if self.show_range:
                    print(f"Valid range: ${min_limit:.2f} - ${max_limit:.2f}\n")
                
                lower_input = input("Enter lower limit: $").strip()
                upper_input = input("Enter upper limit: $").strip()
                
                result = self.validator.validate_limits(
                    lower_input,
                    upper_input,
                    initial_stake
                )
                
                if result.is_valid:
                    lower = float(lower_input)
                    upper = float(upper_input)
                    print(f"✓ Limits set to: ${lower:.2f} - ${upper:.2f}")
                    
                    if result.has_warnings():
                        for warning in result.get_warning_messages():
                            print(f"  ⚠ {warning}")
                    
                    return lower, upper
                else:
                    print(f"✗ Error: {result.get_error_messages()[0]}")
                    if attempt < self.max_retries - 1:
                        print(f"  Try again ({self.max_retries - attempt - 1} attempts left)\n")
            
            except KeyboardInterrupt:
                print("\n✗ Input cancelled by user")
                raise
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
        
        raise ValueError(f"Invalid limits after {self.max_retries} attempts")

    def get_probability(self) -> float:
        """
        Get validated probability from user (0-1).
        
        Returns:
            Validated probability value
        """
        for attempt in range(self.max_retries):
            try:
                if self.show_range:
                    prompt = "Enter win probability (0.0 - 1.0): "
                else:
                    prompt = "Enter win probability: "
                
                user_input = input(prompt).strip()
                
                result = self.validator.validate_probability(user_input)
                
                if result.is_valid:
                    value = float(user_input)
                    percentage = value * 100
                    print(f"✓ Probability set to {value:.2f} ({percentage:.1f}%)")
                    return value
                else:
                    print(f"✗ Error: {result.get_error_messages()[0]}")
                    if attempt < self.max_retries - 1:
                        print(f"  Try again ({self.max_retries - attempt - 1} attempts left)\n")
            
            except KeyboardInterrupt:
                print("\n✗ Input cancelled by user")
                raise
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
        
        raise ValueError(f"Invalid probability after {self.max_retries} attempts")

    def get_numeric_input(
        self,
        prompt: str,
        validation_func: Optional[Callable[[float], ValidationResult]] = None,
        allow_empty: bool = False
    ) -> Optional[float]:
        """
        Get generic numeric input with optional validation.
        
        Args:
            prompt: User prompt to display
            validation_func: Optional function to validate input
            allow_empty: Whether to allow empty input (returns None)
            
        Returns:
            Validated numeric value or None if empty allowed
        """
        for attempt in range(self.max_retries):
            try:
                user_input = input(prompt).strip()
                
                if not user_input and allow_empty:
                    return None
                
                success, value, message = self.validator.parse_and_validate_numeric(user_input)
                
                if not success:
                    print(f"✗ Error: {message}")
                    if attempt < self.max_retries - 1:
                        print(f"  Try again ({self.max_retries - attempt - 1} attempts left)\n")
                    continue
                
                # Apply custom validation if provided
                if validation_func:
                    result = validation_func(value)
                    if not result.is_valid:
                        print(f"✗ Error: {result.get_error_messages()[0]}")
                        if attempt < self.max_retries - 1:
                            print(f"  Try again ({self.max_retries - attempt - 1} attempts left)\n")
                        continue
                
                print(f"✓ Value accepted: {value}")
                return value
            
            except KeyboardInterrupt:
                print("\n✗ Input cancelled by user")
                raise
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
        
        raise ValueError(f"Invalid input after {self.max_retries} attempts")

    def get_all_inputs(self) -> dict:
        """
        Get all required inputs for a betting session.
        
        Returns:
            Dictionary with all validated inputs
        """
        print("\n" + "="*50)
        print("BETTING SESSION SETUP")
        print("="*50 + "\n")
        
        try:
            initial_stake = self.get_initial_stake()
            print()
            
            lower_limit, upper_limit = self.get_limits(initial_stake)
            print()
            
            bet_amount = self.get_bet_amount(initial_stake)
            print()
            
            probability = self.get_probability()
            print()
            
            # Comprehensive validation
            result = self.validator.validate_all(
                initial_stake,
                bet_amount,
                lower_limit,
                upper_limit,
                probability
            )
            
            if not result.is_valid:
                print("✗ Validation failed!")
                print(result)
                raise ValueError("One or more inputs failed validation")
            
            print("✓ All inputs validated successfully!\n")
            
            return {
                "initial_stake": initial_stake,
                "lower_limit": lower_limit,
                "upper_limit": upper_limit,
                "bet_amount": bet_amount,
                "probability": probability
            }
        
        except (ValueError, KeyboardInterrupt) as e:
            print(f"✗ Input setup failed: {str(e)}")
            raise
