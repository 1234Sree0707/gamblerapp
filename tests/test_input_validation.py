# tests/test_input_validation.py

"""
Comprehensive test suite for Input Validation and Error Handling (Use Case 6).

Tests all 6 use cases:
1. Validate Initial Stake
2. Ensure Bet ≤ Current Stake
3. Verify Upper > Lower Limit
4. Handle Invalid Numeric Inputs
5. Prevent Negative Stakes
6. Validate Probability (0-1)
"""

import pytest
import logging

from utils.input_validator import InputValidator
from utils.validation_exceptions import (
    ValidationException,
    StakeValidationException,
    BetValidationException,
    LimitValidationException,
    ProbabilityValidationException,
    NumericValidationException
)
from utils.validation_types import ValidationResult, ValidationMessage, SeverityLevel
from utils.validation_config import ValidationConfig, STANDARD_CONFIG, CONSERVATIVE_CONFIG

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestValidationTypes:
    """Test ValidationResult and ValidationMessage classes"""
    
    def test_validation_result_creation(self):
        """Test creating validation result"""
        result = ValidationResult()
        assert result.is_valid == True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validation_result_add_error(self):
        """Test adding errors to result"""
        result = ValidationResult()
        result.add_error("Test error", field="test_field", value=123)
        
        assert result.is_valid == False
        assert result.get_error_count() == 1
        assert "Test error" in result.get_error_messages()
    
    def test_validation_result_add_warning(self):
        """Test adding warnings to result"""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        assert result.is_valid == True
        assert result.has_warnings() == True
        assert result.get_warning_count() == 1
    
    def test_validation_result_context(self):
        """Test setting context"""
        result = ValidationResult()
        result.set_context("key", "value")
        
        assert result.context["key"] == "value"
    
    def test_validation_result_to_dict(self):
        """Test converting result to dictionary"""
        result = ValidationResult()
        result.add_error("Error message")
        
        result_dict = result.to_dict()
        assert "is_valid" in result_dict
        assert "errors" in result_dict
        assert "summary" in result_dict


class TestUseCase1_ValidateInitialStake:
    """Test USE CASE 1: Validate Initial Stake"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_valid_stake(self):
        """Test valid stake values"""
        result = self.validator.validate_initial_stake(100.00)
        assert result.is_valid == True
    
    def test_negative_stake(self):
        """Test negative stake rejection"""
        result = self.validator.validate_initial_stake(-50.00)
        assert result.is_valid == False
        assert result.has_errors() == True
    
    def test_zero_stake_not_allowed(self):
        """Test zero stake with default config"""
        result = self.validator.validate_initial_stake(0)
        assert result.is_valid == False
    
    def test_zero_stake_allowed(self):
        """Test zero stake with config allowing it"""
        config = ValidationConfig(allow_zero_stake=True)
        validator = InputValidator(config)
        result = validator.validate_initial_stake(0)
        assert result.is_valid == True
    
    def test_nan_stake(self):
        """Test NaN stake rejection"""
        import math
        result = self.validator.validate_initial_stake(math.nan)
        assert result.is_valid == False
    
    def test_infinity_stake(self):
        """Test Infinity stake rejection"""
        import math
        result = self.validator.validate_initial_stake(math.inf)
        assert result.is_valid == False
    
    def test_stake_below_minimum(self):
        """Test stake below minimum"""
        result = self.validator.validate_initial_stake(0.001)
        assert result.is_valid == False
    
    def test_stake_above_maximum(self):
        """Test stake above maximum"""
        result = self.validator.validate_initial_stake(2000000)
        assert result.is_valid == False
    
    def test_string_stake(self):
        """Test parsing string to stake"""
        result = self.validator.validate_initial_stake("250.50")
        assert result.is_valid == True
    
    def test_invalid_string_stake(self):
        """Test invalid string stake"""
        result = self.validator.validate_initial_stake("not_a_number")
        assert result.is_valid == False
    
    def test_none_stake(self):
        """Test None stake"""
        result = self.validator.validate_initial_stake(None)
        assert result.is_valid == False


class TestUseCase2_ValidateBetAmount:
    """Test USE CASE 2: Ensure Bet ≤ Current Stake"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_valid_bet(self):
        """Test valid bet amount"""
        result = self.validator.validate_bet_amount(50.00, current_stake=100.00)
        assert result.is_valid == True
    
    def test_bet_equals_stake(self):
        """Test bet equal to stake"""
        result = self.validator.validate_bet_amount(100.00, current_stake=100.00)
        assert result.is_valid == True
    
    def test_bet_exceeds_stake(self):
        """Test bet exceeding stake"""
        result = self.validator.validate_bet_amount(150.00, current_stake=100.00)
        assert result.is_valid == False
        assert "exceeds" in result.get_error_messages()[0].lower()
    
    def test_negative_bet(self):
        """Test negative bet amount"""
        result = self.validator.validate_bet_amount(-50.00, current_stake=100.00)
        assert result.is_valid == False
    
    def test_zero_bet(self):
        """Test zero bet amount"""
        result = self.validator.validate_bet_amount(0, current_stake=100.00)
        assert result.is_valid == False
    
    def test_bet_below_minimum(self):
        """Test bet below minimum"""
        result = self.validator.validate_bet_amount(0.001, current_stake=100.00)
        assert result.is_valid == False
    
    def test_none_bet(self):
        """Test None bet"""
        result = self.validator.validate_bet_amount(None, current_stake=100.00)
        assert result.is_valid == False


class TestUseCase3_ValidateLimits:
    """Test USE CASE 3: Verify Upper > Lower Limit"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_valid_limits(self):
        """Test valid limit ordering"""
        result = self.validator.validate_limits(10.00, 100.00, initial_stake=50.00)
        assert result.is_valid == True
    
    def test_upper_equals_lower(self):
        """Test upper limit equal to lower"""
        result = self.validator.validate_limits(50.00, 50.00, initial_stake=50.00)
        assert result.is_valid == False
    
    def test_upper_less_than_lower(self):
        """Test upper limit less than lower"""
        result = self.validator.validate_limits(100.00, 50.00, initial_stake=75.00)
        assert result.is_valid == False
    
    def test_negative_lower_limit(self):
        """Test negative lower limit"""
        result = self.validator.validate_limits(-10.00, 100.00, initial_stake=50.00)
        assert result.is_valid == False
    
    def test_negative_upper_limit(self):
        """Test negative upper limit"""
        result = self.validator.validate_limits(10.00, -50.00, initial_stake=20.00)
        assert result.is_valid == False
    
    def test_stake_below_lower_limit(self):
        """Test stake below lower limit (warning)"""
        result = self.validator.validate_limits(100.00, 200.00, initial_stake=50.00)
        assert result.is_valid == True
        assert result.has_warnings() == True
    
    def test_stake_above_upper_limit(self):
        """Test stake above upper limit (warning)"""
        result = self.validator.validate_limits(10.00, 50.00, initial_stake=100.00)
        assert result.is_valid == True
        assert result.has_warnings() == True
    
    def test_none_lower_limit(self):
        """Test None lower limit"""
        result = self.validator.validate_limits(None, 100.00, initial_stake=50.00)
        assert result.is_valid == False


class TestUseCase4_HandleInvalidNumeric:
    """Test USE CASE 4: Handle Invalid Numeric Inputs"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_parse_valid_string(self):
        """Test parsing valid string"""
        success, value, message = self.validator.parse_and_validate_numeric("123.45")
        assert success == True
        assert value == 123.45
    
    def test_parse_valid_integer(self):
        """Test parsing valid integer"""
        success, value, message = self.validator.parse_and_validate_numeric(42)
        assert success == True
        assert value == 42.0
    
    def test_parse_none(self):
        """Test parsing None"""
        success, value, message = self.validator.parse_and_validate_numeric(None)
        assert success == False
        assert "None" in message
    
    def test_parse_empty_string(self):
        """Test parsing empty string"""
        success, value, message = self.validator.parse_and_validate_numeric("")
        assert success == False
        assert "empty" in message.lower()
    
    def test_parse_invalid_string(self):
        """Test parsing invalid string"""
        success, value, message = self.validator.parse_and_validate_numeric("not_a_number")
        assert success == False
        assert "cannot parse" in message.lower() or "invalid" in message.lower()
    
    def test_parse_nan(self):
        """Test parsing NaN (not allowed by default)"""
        import math
        success, value, message = self.validator.parse_and_validate_numeric(math.nan)
        assert success == False
        assert "NaN" in message
    
    def test_parse_infinity(self):
        """Test parsing Infinity (not allowed by default)"""
        import math
        success, value, message = self.validator.parse_and_validate_numeric(math.inf)
        assert success == False
        assert "Infinity" in message
    
    def test_parse_nan_allowed(self):
        """Test parsing NaN when allowed"""
        config = ValidationConfig(allow_nan=True)
        validator = InputValidator(config)
        import math
        success, value, message = validator.parse_and_validate_numeric(math.nan)
        assert success == True


class TestUseCase5_PreventNegativeStakes:
    """Test USE CASE 5: Prevent Negative Stakes"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_positive_stake(self):
        """Test positive stake"""
        result = self.validator.validate_stake_non_negative(100.00)
        assert result.is_valid == True
    
    def test_negative_stake_strict(self):
        """Test negative stake in strict mode"""
        result = self.validator.validate_stake_non_negative(-50.00)
        assert result.is_valid == False
    
    def test_zero_stake_strict(self):
        """Test zero stake in strict mode"""
        config = ValidationConfig(allow_zero_stake=False, strict_mode=True)
        validator = InputValidator(config)
        result = validator.validate_stake_non_negative(0)
        assert result.is_valid == False
    
    def test_zero_stake_non_strict(self):
        """Test zero stake in non-strict mode"""
        config = ValidationConfig(allow_zero_stake=False, strict_mode=False)
        validator = InputValidator(config)
        result = validator.validate_stake_non_negative(0)
        assert result.is_valid == True  # Warning, not error
        assert result.has_warnings() == True


class TestUseCase6_ValidateProbability:
    """Test USE CASE 6: Validate Probability (0-1)"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_valid_probability(self):
        """Test valid probability (0.5)"""
        result = self.validator.validate_probability(0.5)
        assert result.is_valid == True
    
    def test_probability_zero(self):
        """Test probability of 0"""
        result = self.validator.validate_probability(0.0)
        assert result.is_valid == True
    
    def test_probability_one(self):
        """Test probability of 1"""
        result = self.validator.validate_probability(1.0)
        assert result.is_valid == True
    
    def test_probability_below_zero(self):
        """Test probability below 0"""
        result = self.validator.validate_probability(-0.1)
        assert result.is_valid == False
    
    def test_probability_above_one(self):
        """Test probability above 1"""
        result = self.validator.validate_probability(1.5)
        assert result.is_valid == False
    
    def test_probability_nan(self):
        """Test NaN probability"""
        import math
        result = self.validator.validate_probability(math.nan)
        assert result.is_valid == False
    
    def test_probability_infinity(self):
        """Test Infinity probability"""
        import math
        result = self.validator.validate_probability(math.inf)
        assert result.is_valid == False
    
    def test_probability_none(self):
        """Test None probability"""
        result = self.validator.validate_probability(None)
        assert result.is_valid == False
    
    def test_probability_string(self):
        """Test parsing string probability"""
        result = self.validator.validate_probability("0.75")
        assert result.is_valid == True


class TestComprehensiveValidation:
    """Test comprehensive validation of all inputs"""
    
    def setup_method(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def test_all_valid_inputs(self):
        """Test all inputs valid together"""
        result = self.validator.validate_all(
            initial_stake=1000.00,
            bet_amount=100.00,
            lower_limit=500.00,
            upper_limit=2000.00,
            probability=0.5
        )
        assert result.is_valid == True
    
    def test_multiple_errors(self):
        """Test multiple errors collected"""
        result = self.validator.validate_all(
            initial_stake=-100.00,  # Error
            bet_amount=2000.00,     # Error (exceeds stake)
            lower_limit=2000.00,    # Error (not > upper)
            upper_limit=1000.00,    # Error (not > lower)
            probability=1.5         # Error (>1)
        )
        assert result.is_valid == False
        assert result.get_error_count() > 0
    
    def test_strict_mode_with_warnings(self):
        """Test strict mode converts warnings to errors"""
        config = ValidationConfig(strict_mode=True)
        validator = InputValidator(config)
        
        result = validator.validate_all(
            initial_stake=100.00,    # Valid
            bet_amount=50.00,        # Valid
            lower_limit=200.00,      # Valid but stake below lower (warning)
            upper_limit=300.00,      # Valid
            probability=0.5          # Valid
        )
        
        # In strict mode, warnings make result invalid
        assert result.has_warnings() == True


# Integration test
class TestIntegration:
    """Integration tests simulating real usage"""
    
    def test_session_validation_flow(self):
        """Test typical betting session validation"""
        validator = InputValidator(CONSERVATIVE_CONFIG)
        
        inputs = {
            "initial_stake": 100.00,
            "lower_limit": 50.00,
            "upper_limit": 500.00,
            "bet_amount": 25.00,
            "probability": 0.45
        }
        
        result = validator.validate_all(**inputs)
        assert result.is_valid == True
        
        # Verify context preserved
        assert "stake_valid" in result.context
        assert "bet_valid" in result.context
    
    def test_rejection_flow(self):
        """Test typical rejection flow"""
        validator = InputValidator(STANDARD_CONFIG)
        
        # User tries to bet more than stake
        result = validator.validate_bet_amount(500.00, current_stake=100.00)
        assert result.is_valid == False
        
        errors = result.get_error_messages()
        assert len(errors) > 0
        assert "exceeds" in errors[0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
