#!/usr/bin/env python3
"""
Quick Verification Script for Use Case 6: Input Validation and Error Handling

This script verifies all components of the validation system are working correctly.
"""

import sys
import math
from utils.validation_exceptions import (
    ValidationException,
    ValidationErrorType,
    StakeValidationException,
    BetValidationException,
    LimitValidationException,
    ProbabilityValidationException,
    NumericValidationException
)
from utils.validation_types import ValidationResult, ValidationMessage, SeverityLevel
from utils.validation_config import (
    ValidationConfig,
    STANDARD_CONFIG,
    CONSERVATIVE_CONFIG,
    AGGRESSIVE_CONFIG,
    DEVELOPMENT_CONFIG
)
from utils.input_validator import InputValidator
from utils.safe_input_handler import SafeInputHandler


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70)


def print_subheader(text):
    """Print formatted subheader"""
    print("\n" + "-"*70)
    print(text)
    print("-"*70)


def verify_exceptions():
    """Verify exception hierarchy"""
    print_subheader("1. VERIFYING EXCEPTION HIERARCHY")
    
    tests_passed = 0
    tests_total = 0
    
    # Test base exception
    tests_total += 1
    try:
        exc = ValidationException(
            "Test", ValidationErrorType.STAKE_ERROR, "test", 100
        )
        assert exc.error_type == ValidationErrorType.STAKE_ERROR
        assert "[STAKE_ERROR]" in str(exc)
        print("✓ ValidationException")
        tests_passed += 1
    except AssertionError as e:
        print(f"✗ ValidationException: {e}")
    
    # Test specific exceptions
    exceptions_to_test = [
        (StakeValidationException("Test", value=-50), "StakeValidationException"),
        (BetValidationException("Test", value=1000), "BetValidationException"),
        (LimitValidationException("Test", value=50), "LimitValidationException"),
        (ProbabilityValidationException("Test", value=1.5), "ProbabilityValidationException"),
    ]
    
    for exc, name in exceptions_to_test:
        tests_total += 1
        try:
            assert exc.error_type in ValidationErrorType.__members__.values()
            print(f"✓ {name}")
            tests_passed += 1
        except AssertionError:
            print(f"✗ {name}")
    
    return tests_passed, tests_total


def verify_validation_result():
    """Verify ValidationResult class"""
    print_subheader("2. VERIFYING VALIDATION RESULT")
    
    tests_passed = 0
    tests_total = 0
    
    # Test creation
    tests_total += 1
    try:
        result = ValidationResult()
        assert result.is_valid is True
        assert len(result.errors) == 0
        print("✓ ValidationResult creation")
        tests_passed += 1
    except AssertionError:
        print("✗ ValidationResult creation")
    
    # Test add_error
    tests_total += 1
    try:
        result = ValidationResult()
        result.add_error("Error message", field="test")
        assert result.is_valid is False
        assert result.get_error_count() == 1
        print("✓ add_error()")
        tests_passed += 1
    except AssertionError:
        print("✗ add_error()")
    
    # Test add_warning
    tests_total += 1
    try:
        result = ValidationResult()
        result.add_warning("Warning message")
        assert result.is_valid is True
        assert result.has_warnings() is True
        print("✓ add_warning()")
        tests_passed += 1
    except AssertionError:
        print("✗ add_warning()")
    
    # Test context
    tests_total += 1
    try:
        result = ValidationResult()
        result.set_context("key", "value")
        assert result.context["key"] == "value"
        print("✓ set_context()")
        tests_passed += 1
    except AssertionError:
        print("✗ set_context()")
    
    # Test to_dict
    tests_total += 1
    try:
        result = ValidationResult()
        result.add_error("Error")
        result_dict = result.to_dict()
        assert "is_valid" in result_dict
        assert "errors" in result_dict
        print("✓ to_dict()")
        tests_passed += 1
    except AssertionError:
        print("✗ to_dict()")
    
    return tests_passed, tests_total


def verify_validation_config():
    """Verify ValidationConfig"""
    print_subheader("3. VERIFYING VALIDATION CONFIG")
    
    tests_passed = 0
    tests_total = 0
    
    # Test STANDARD_CONFIG
    tests_total += 1
    try:
        assert STANDARD_CONFIG.min_stake == 0.01
        assert STANDARD_CONFIG.max_stake == 100000.00
        print("✓ STANDARD_CONFIG")
        tests_passed += 1
    except AssertionError:
        print("✗ STANDARD_CONFIG")
    
    # Test CONSERVATIVE_CONFIG
    tests_total += 1
    try:
        assert CONSERVATIVE_CONFIG.min_stake == 10.00
        assert CONSERVATIVE_CONFIG.max_bet_multiplier == 0.1
        print("✓ CONSERVATIVE_CONFIG")
        tests_passed += 1
    except AssertionError:
        print("✗ CONSERVATIVE_CONFIG")
    
    # Test range methods
    tests_total += 1
    try:
        config = STANDARD_CONFIG
        stake_range = config.get_stake_range()
        assert stake_range == (0.01, 100000.00)
        print("✓ get_stake_range()")
        tests_passed += 1
    except AssertionError:
        print("✗ get_stake_range()")
    
    return tests_passed, tests_total


def verify_input_validator():
    """Verify InputValidator use cases"""
    print_subheader("4. VERIFYING INPUT VALIDATOR (6 USE CASES)")
    
    validator = InputValidator(STANDARD_CONFIG)
    tests_passed = 0
    tests_total = 0
    
    # USE CASE 1: Validate Initial Stake
    tests_total += 1
    try:
        result = validator.validate_initial_stake(100.0)
        assert result.is_valid is True
        
        result = validator.validate_initial_stake(-50.0)
        assert result.is_valid is False
        print("✓ USE CASE 1: validate_initial_stake()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ USE CASE 1: {e}")
    
    # USE CASE 2: Validate Bet Amount
    tests_total += 1
    try:
        result = validator.validate_bet_amount(50.0, current_stake=100.0)
        assert result.is_valid is True
        
        result = validator.validate_bet_amount(150.0, current_stake=100.0)
        assert result.is_valid is False
        print("✓ USE CASE 2: validate_bet_amount()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ USE CASE 2: {e}")
    
    # USE CASE 3: Validate Limits
    tests_total += 1
    try:
        result = validator.validate_limits(10.0, 100.0, initial_stake=50.0)
        assert result.is_valid is True
        
        result = validator.validate_limits(100.0, 50.0, initial_stake=75.0)
        assert result.is_valid is False
        print("✓ USE CASE 3: validate_limits()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ USE CASE 3: {e}")
    
    # USE CASE 4: Parse and Validate Numeric
    tests_total += 1
    try:
        success, value, msg = validator.parse_and_validate_numeric("123.45")
        assert success is True and value == 123.45
        
        success, value, msg = validator.parse_and_validate_numeric("not_a_number")
        assert success is False
        print("✓ USE CASE 4: parse_and_validate_numeric()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ USE CASE 4: {e}")
    
    # USE CASE 5: Validate Stake Non-Negative
    tests_total += 1
    try:
        result = validator.validate_stake_non_negative(100.0)
        assert result.is_valid is True
        
        result = validator.validate_stake_non_negative(-50.0)
        assert result.is_valid is False
        print("✓ USE CASE 5: validate_stake_non_negative()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ USE CASE 5: {e}")
    
    # USE CASE 6: Validate Probability
    tests_total += 1
    try:
        result = validator.validate_probability(0.75)
        assert result.is_valid is True
        
        result = validator.validate_probability(1.5)
        assert result.is_valid is False
        print("✓ USE CASE 6: validate_probability()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ USE CASE 6: {e}")
    
    # Comprehensive validation
    tests_total += 1
    try:
        result = validator.validate_all(
            initial_stake=100.0,
            bet_amount=50.0,
            lower_limit=10.0,
            upper_limit=200.0,
            probability=0.75
        )
        assert result.is_valid is True
        print("✓ validate_all() - Comprehensive validation")
        tests_passed += 1
    except Exception as e:
        print(f"✗ validate_all(): {e}")
    
    return tests_passed, tests_total


def verify_safe_input_handler():
    """Verify SafeInputHandler"""
    print_subheader("5. VERIFYING SAFE INPUT HANDLER")
    
    tests_passed = 0
    tests_total = 0
    
    validator = InputValidator(STANDARD_CONFIG)
    handler = SafeInputHandler(validator, max_retries=1, show_range=True)
    
    # Test creation
    tests_total += 1
    try:
        assert handler.validator is not None
        assert handler.max_retries == 1
        print("✓ SafeInputHandler creation")
        tests_passed += 1
    except Exception as e:
        print(f"✗ SafeInputHandler creation: {e}")
    
    # Test validate_existing_inputs
    tests_total += 1
    try:
        result = handler.validate_existing_inputs(
            initial_stake=100.0,
            bet_amount=50.0,
            lower_limit=10.0,
            upper_limit=200.0,
            probability=0.75
        )
        assert result.is_valid is True
        print("✓ validate_existing_inputs()")
        tests_passed += 1
    except Exception as e:
        print(f"✗ validate_existing_inputs(): {e}")
    
    return tests_passed, tests_total


def verify_edge_cases():
    """Verify edge cases and special values"""
    print_subheader("6. VERIFYING EDGE CASES")
    
    validator = InputValidator(STANDARD_CONFIG)
    tests_passed = 0
    tests_total = 0
    
    # Test NaN
    tests_total += 1
    try:
        result = validator.validate_initial_stake(float('nan'))
        assert result.is_valid is False and "NaN" in result.get_error_messages()[0]
        print("✓ NaN detection")
        tests_passed += 1
    except Exception as e:
        print(f"✗ NaN detection: {e}")
    
    # Test Infinity
    tests_total += 1
    try:
        result = validator.validate_initial_stake(float('inf'))
        assert result.is_valid is False and "Infinity" in result.get_error_messages()[0]
        print("✓ Infinity detection")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Infinity detection: {e}")
    
    # Test None
    tests_total += 1
    try:
        result = validator.validate_initial_stake(None)
        assert result.is_valid is False and "None" in result.get_error_messages()[0]
        print("✓ None detection")
        tests_passed += 1
    except Exception as e:
        print(f"✗ None detection: {e}")
    
    # Test probability boundaries
    tests_total += 1
    try:
        result = validator.validate_probability(0.0)
        assert result.is_valid is True
        result = validator.validate_probability(1.0)
        assert result.is_valid is True
        print("✓ Probability boundaries (0.0, 1.0)")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Probability boundaries: {e}")
    
    return tests_passed, tests_total


def main():
    """Run verification"""
    print_header("INPUT VALIDATION SYSTEM - VERIFICATION")
    
    total_passed = 0
    total_tests = 0
    
    # Run all verifications
    passed, total = verify_exceptions()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_validation_result()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_validation_config()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_input_validator()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_safe_input_handler()
    total_passed += passed
    total_tests += total
    
    passed, total = verify_edge_cases()
    total_passed += passed
    total_tests += total
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {percentage:.1f}%")
    
    if total_passed == total_tests:
        print("\n✓ ALL VERIFICATION TESTS PASSED!")
        print("✓ Use Case 6 implementation is complete and working correctly")
        return 0
    else:
        print(f"\n✗ {total_tests - total_passed} tests failed")
        print("✗ Please review the implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
