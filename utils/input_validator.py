# utils/input_validator.py

import math
import logging
from typing import Optional, Tuple, Any

from utils.validation_exceptions import (
    ValidationException,
    StakeValidationException,
    BetValidationException,
    LimitValidationException,
    ProbabilityValidationException,
    NumericValidationException,
    RangeValidationException,
    NullValidationException
)
from utils.validation_types import ValidationResult
from utils.validation_config import ValidationConfig, STANDARD_CONFIG

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Comprehensive input validation implementing all 6 use cases.
    
    Use Cases:
    1. Validate Initial Stake
    2. Ensure Bet ≤ Current Stake
    3. Verify Upper > Lower Limit
    4. Handle Invalid Numeric Inputs
    5. Prevent Negative Stakes
    6. Validate Probability (0-1)
    """

    def __init__(self, config: ValidationConfig = None):
        """
        Initialize validator with configuration.
        
        Args:
            config: ValidationConfig instance (uses STANDARD_CONFIG if None)
        """
        self.config = config or STANDARD_CONFIG
        self.logger = logger

    def validate_initial_stake(self, stake: Any) -> ValidationResult:
        """
        USE CASE 1: Validate Initial Stake
        
        Checks:
        - Positive value
        - Within min/max range
        - Not NaN or Infinity
        - Not negative
        
        Args:
            stake: The initial stake value
            
        Returns:
            ValidationResult with detailed error/warning messages
        """
        result = ValidationResult()
        result.set_context("use_case", "validate_initial_stake")
        result.set_context("input_value", stake)
        
        # Check for null
        if stake is None:
            result.add_error("Stake cannot be None", field="stake", value=stake)
            return result
        
        # Parse numeric value
        try:
            stake_float = float(stake)
        except (ValueError, TypeError):
            result.add_error(
                f"Stake must be a valid number, got: {type(stake).__name__}",
                field="stake",
                value=stake
            )
            return result
        
        # Check for NaN
        if math.isnan(stake_float):
            result.add_error(
                "Stake cannot be NaN (Not a Number)",
                field="stake",
                value=stake
            )
            return result
        
        # Check for Infinity
        if math.isinf(stake_float):
            result.add_error(
                "Stake cannot be Infinity",
                field="stake",
                value=stake
            )
            return result
        
        # Check for negative values
        if stake_float < 0:
            result.add_error(
                f"Stake cannot be negative: {stake_float}",
                field="stake",
                value=stake
            )
            return result
        
        # Check for zero (if not allowed)
        if stake_float == 0 and not self.config.allow_zero_stake:
            result.add_error(
                "Stake cannot be zero",
                field="stake",
                value=stake
            )
            return result
        
        # Check min/max range
        min_stake, max_stake = self.config.get_stake_range()
        
        if stake_float < min_stake:
            result.add_error(
                f"Stake {stake_float} is below minimum {min_stake}",
                field="stake",
                value=stake
            )
            return result
        
        if stake_float > max_stake:
            result.add_error(
                f"Stake {stake_float} exceeds maximum {max_stake}",
                field="stake",
                value=stake
            )
            return result
        
        result.set_context("validated_value", stake_float)
        self.logger.debug(f"✓ Initial stake validation passed: {stake_float}")
        return result

    def validate_bet_amount(self, bet_amount: Any, current_stake: float) -> ValidationResult:
        """
        USE CASE 2: Ensure Bet ≤ Current Stake
        
        Checks:
        - Bet doesn't exceed stake
        - Within min/max bet limits
        - Positive value
        - Valid numeric
        
        Args:
            bet_amount: The bet amount
            current_stake: Current available stake
            
        Returns:
            ValidationResult with detailed messages
        """
        result = ValidationResult()
        result.set_context("use_case", "validate_bet_amount")
        result.set_context("input_value", bet_amount)
        result.set_context("current_stake", current_stake)
        
        # Check for null
        if bet_amount is None:
            result.add_error("Bet amount cannot be None", field="bet_amount")
            return result
        
        # Parse numeric value
        try:
            bet_float = float(bet_amount)
        except (ValueError, TypeError):
            result.add_error(
                f"Bet amount must be a valid number, got: {type(bet_amount).__name__}",
                field="bet_amount",
                value=bet_amount
            )
            return result
        
        # Check for NaN
        if math.isnan(bet_float):
            result.add_error("Bet amount cannot be NaN", field="bet_amount")
            return result
        
        # Check for Infinity
        if math.isinf(bet_float):
            result.add_error("Bet amount cannot be Infinity", field="bet_amount")
            return result
        
        # Check for negative
        if bet_float < 0:
            result.add_error(
                f"Bet amount cannot be negative: {bet_float}",
                field="bet_amount",
                value=bet_amount
            )
            return result
        
        # Check min/max range
        min_bet, max_bet = self.config.get_bet_range(current_stake)
        
        if bet_float < min_bet:
            result.add_error(
                f"Bet {bet_float} is below minimum {min_bet}",
                field="bet_amount",
                value=bet_amount
            )
            return result
        
        # Key check: Bet must not exceed current stake
        if bet_float > current_stake:
            result.add_error(
                f"Bet {bet_float} exceeds current stake {current_stake}",
                field="bet_amount",
                value=bet_amount
            )
            return result
        
        if bet_float > max_bet:
            result.add_error(
                f"Bet {bet_float} exceeds maximum allowed {max_bet}",
                field="bet_amount",
                value=bet_amount
            )
            return result
        
        result.set_context("validated_value", bet_float)
        self.logger.debug(f"✓ Bet amount validation passed: {bet_float}")
        return result

    def validate_limits(self, lower_limit: Any, upper_limit: Any, initial_stake: float) -> ValidationResult:
        """
        USE CASE 3: Verify Upper > Lower Limit
        
        Checks:
        - Upper limit > lower limit
        - Initial stake between limits
        - Non-negative limits
        - Valid numerics
        
        Args:
            lower_limit: The lower boundary
            upper_limit: The upper boundary
            initial_stake: Initial stake value
            
        Returns:
            ValidationResult with detailed messages
        """
        result = ValidationResult()
        result.set_context("use_case", "validate_limits")
        result.set_context("lower_limit", lower_limit)
        result.set_context("upper_limit", upper_limit)
        result.set_context("initial_stake", initial_stake)
        
        # Check for nulls
        if lower_limit is None:
            result.add_error("Lower limit cannot be None", field="lower_limit")
            return result
        
        if upper_limit is None:
            result.add_error("Upper limit cannot be None", field="upper_limit")
            return result
        
        # Parse numeric values
        try:
            lower_float = float(lower_limit)
            upper_float = float(upper_limit)
        except (ValueError, TypeError) as e:
            result.add_error(f"Limits must be valid numbers: {str(e)}")
            return result
        
        # Check for NaN/Infinity
        if math.isnan(lower_float) or math.isnan(upper_float):
            result.add_error("Limits cannot be NaN")
            return result
        
        if math.isinf(lower_float) or math.isinf(upper_float):
            result.add_error("Limits cannot be Infinity")
            return result
        
        # Check for negative limits
        if lower_float < 0:
            result.add_error(
                f"Lower limit cannot be negative: {lower_float}",
                field="lower_limit",
                value=lower_limit
            )
            return result
        
        if upper_float < 0:
            result.add_error(
                f"Upper limit cannot be negative: {upper_float}",
                field="upper_limit",
                value=upper_limit
            )
            return result
        
        # Key check: Upper must be greater than lower
        if upper_float <= lower_float:
            result.add_error(
                f"Upper limit {upper_float} must be greater than lower limit {lower_float}",
                field="upper_limit",
                value=upper_limit
            )
            return result
        
        # Check if stake is between limits
        if initial_stake < lower_float:
            result.add_warning(
                f"Initial stake {initial_stake} is below lower limit {lower_float}",
                field="initial_stake",
                value=initial_stake
            )
        
        if initial_stake > upper_float:
            result.add_warning(
                f"Initial stake {initial_stake} is above upper limit {upper_float}",
                field="initial_stake",
                value=initial_stake
            )
        
        result.set_context("validated_lower", lower_float)
        result.set_context("validated_upper", upper_float)
        self.logger.debug(f"✓ Limits validation passed: [{lower_float}, {upper_float}]")
        return result

    def parse_and_validate_numeric(self, value: Any, field_name: str = "value") -> Tuple[bool, Optional[float], str]:
        """
        USE CASE 4: Handle Invalid Numeric Inputs
        
        Gracefully handles:
        - Null and empty values
        - Invalid strings
        - NaN and Infinity
        - Type mismatches
        
        Args:
            value: The value to parse
            field_name: Name of the field (for error messages)
            
        Returns:
            Tuple of (success: bool, parsed_value: Optional[float], error_message: str)
        """
        result_success = True
        result_value = None
        result_message = ""
        
        # Check for null
        if value is None:
            return False, None, f"{field_name}: Value cannot be None"
        
        # Check for empty string
        if isinstance(value, str) and value.strip() == "":
            return False, None, f"{field_name}: Value cannot be empty"
        
        # Try to parse
        try:
            parsed = float(value)
        except ValueError:
            return False, None, f"{field_name}: Cannot parse '{value}' as number (invalid format)"
        except TypeError:
            return False, None, f"{field_name}: Type {type(value).__name__} cannot be converted to number"
        except Exception as e:
            return False, None, f"{field_name}: Unexpected error parsing value: {str(e)}"
        
        # Check for NaN
        if math.isnan(parsed):
            if not self.config.allow_nan:
                return False, None, f"{field_name}: Value is NaN (Not a Number)"
            result_message = f"{field_name}: Warning - Value is NaN"
        
        # Check for Infinity
        if math.isinf(parsed):
            if not self.config.allow_infinity:
                return False, None, f"{field_name}: Value is Infinity"
            result_message = f"{field_name}: Warning - Value is Infinity"
        
        return True, parsed, result_message

    def validate_stake_non_negative(self, stake: Any) -> ValidationResult:
        """
        USE CASE 5: Prevent Negative Stakes
        
        Checks:
        - Strict negative prevention
        - Optional zero-stake handling
        - Strict mode enforcement
        
        Args:
            stake: The stake value to validate
            
        Returns:
            ValidationResult with detailed messages
        """
        result = ValidationResult()
        result.set_context("use_case", "validate_stake_non_negative")
        result.set_context("input_value", stake)
        
        # Parse numeric
        success, parsed_stake, message = self.parse_and_validate_numeric(stake, "stake")
        
        if not success:
            result.add_error(message, field="stake", value=stake)
            return result
        
        # Strict negative check
        if parsed_stake < 0:
            result.add_error(
                f"Stake cannot be negative: {parsed_stake}",
                field="stake",
                value=stake
            )
            return result
        
        # Zero-stake handling
        if parsed_stake == 0:
            if not self.config.allow_zero_stake:
                if self.config.strict_mode:
                    result.add_error(
                        "Stake cannot be zero (strict mode)",
                        field="stake",
                        value=stake
                    )
                else:
                    result.add_warning(
                        "Stake is zero (not recommended)",
                        field="stake",
                        value=stake
                    )
                    if self.config.strict_mode:
                        result.is_valid = False
                
                return result
        
        result.set_context("validated_value", parsed_stake)
        self.logger.debug(f"✓ Stake non-negative validation passed: {parsed_stake}")
        return result

    def validate_probability(self, probability: Any) -> ValidationResult:
        """
        USE CASE 6: Validate Probability (0-1)
        
        Ensures:
        - 0.0 ≤ probability ≤ 1.0
        - Configurable min/max ranges
        - Handles NaN and Infinity
        - Valid numeric
        
        Args:
            probability: The probability value (should be 0-1)
            
        Returns:
            ValidationResult with detailed messages
        """
        result = ValidationResult()
        result.set_context("use_case", "validate_probability")
        result.set_context("input_value", probability)
        
        # Check for null
        if probability is None:
            result.add_error("Probability cannot be None", field="probability")
            return result
        
        # Parse numeric
        try:
            prob_float = float(probability)
        except (ValueError, TypeError):
            result.add_error(
                f"Probability must be a valid number, got: {type(probability).__name__}",
                field="probability",
                value=probability
            )
            return result
        
        # Check for NaN
        if math.isnan(prob_float):
            result.add_error("Probability cannot be NaN", field="probability")
            return result
        
        # Check for Infinity
        if math.isinf(prob_float):
            result.add_error("Probability cannot be Infinity", field="probability")
            return result
        
        # Key check: Must be in [0, 1] range
        min_prob, max_prob = self.config.get_probability_range()
        
        if prob_float < min_prob:
            result.add_error(
                f"Probability {prob_float} is below minimum {min_prob}",
                field="probability",
                value=probability
            )
            return result
        
        if prob_float > max_prob:
            result.add_error(
                f"Probability {prob_float} exceeds maximum {max_prob}",
                field="probability",
                value=probability
            )
            return result
        
        result.set_context("validated_value", prob_float)
        self.logger.debug(f"✓ Probability validation passed: {prob_float}")
        return result

    def validate_all(
        self,
        initial_stake: float,
        bet_amount: float,
        lower_limit: float,
        upper_limit: float,
        probability: float
    ) -> ValidationResult:
        """
        Comprehensive validation of all inputs.
        
        Args:
            initial_stake: Initial stake
            bet_amount: Bet amount
            lower_limit: Lower boundary
            upper_limit: Upper boundary
            probability: Win probability
            
        Returns:
            Combined ValidationResult
        """
        combined_result = ValidationResult()
        combined_result.set_context("use_case", "validate_all")
        
        # Run all validations
        stake_result = self.validate_initial_stake(initial_stake)
        bet_result = self.validate_bet_amount(bet_amount, initial_stake)
        limits_result = self.validate_limits(lower_limit, upper_limit, initial_stake)
        prob_result = self.validate_probability(probability)
        
        # Combine results
        results = [stake_result, bet_result, limits_result, prob_result]
        
        for res in results:
            combined_result.errors.extend(res.errors)
            combined_result.warnings.extend(res.warnings)
            if not res.is_valid:
                combined_result.is_valid = False
        
        if self.config.strict_mode and combined_result.has_warnings():
            combined_result.is_valid = False
        
        combined_result.set_context("stake_valid", stake_result.is_valid)
        combined_result.set_context("bet_valid", bet_result.is_valid)
        combined_result.set_context("limits_valid", limits_result.is_valid)
        combined_result.set_context("probability_valid", prob_result.is_valid)
        
        if combined_result.is_valid:
            self.logger.info("✓ All validations passed")
        else:
            self.logger.warning(f"✗ Validation failed: {combined_result.get_summary()}")
        
        return combined_result
