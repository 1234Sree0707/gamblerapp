"""
Integration Example: Using Input Validation in the Betting Application

This module demonstrates how to integrate the validation system into real
betting application workflows.
"""

from utils.input_validator import InputValidator
from utils.safe_input_handler import SafeInputHandler
from utils.validation_config import STANDARD_CONFIG, CONSERVATIVE_CONFIG
from utils.validation_types import ValidationResult


class BettingSessionExample:
    """Example of betting session with full validation"""
    
    def __init__(self):
        self.validator = InputValidator(STANDARD_CONFIG)
        self.handler = SafeInputHandler(self.validator, max_retries=3)
    
    def interactive_session_setup(self):
        """
        Interactive setup with user input and validation.
        
        Example flow:
        1. User provides all inputs interactively
        2. Each input validated individually
        3. Comprehensive validation at end
        4. Session created with validated inputs
        """
        print("\n" + "="*70)
        print("BETTING SESSION SETUP - WITH INTERACTIVE VALIDATION")
        print("="*70 + "\n")
        
        try:
            # Get all inputs interactively with validation
            inputs = self.handler.get_all_inputs()
            
            # Create session with validated inputs
            session = self._create_session(inputs)
            return session
            
        except (ValueError, KeyboardInterrupt) as e:
            print(f"\n✗ Session setup failed: {e}")
            return None
    
    def programmatic_validation(self, stake, bet, lower, upper, prob):
        """
        Programmatic validation without user input.
        
        Example: Validating inputs from API or file.
        """
        print("\n" + "="*70)
        print("BETTING SESSION SETUP - PROGRAMMATIC VALIDATION")
        print("="*70 + "\n")
        
        print(f"Validating inputs:")
        print(f"  Initial Stake: ${stake:.2f}")
        print(f"  Bet Amount: ${bet:.2f}")
        print(f"  Lower Limit: ${lower:.2f}")
        print(f"  Upper Limit: ${upper:.2f}")
        print(f"  Probability: {prob:.2f}")
        print()
        
        # Comprehensive validation
        result = self.validator.validate_all(stake, bet, lower, upper, prob)
        
        if not result.is_valid:
            print("✗ VALIDATION FAILED:\n")
            for error in result.get_error_messages():
                print(f"  ✗ {error}")
            return None
        
        print("✓ All inputs validated successfully!\n")
        
        # Create session
        inputs = {
            'initial_stake': stake,
            'bet_amount': bet,
            'lower_limit': lower,
            'upper_limit': upper,
            'probability': prob
        }
        session = self._create_session(inputs)
        return session
    
    def _create_session(self, inputs):
        """Create betting session from validated inputs"""
        return {
            'status': 'active',
            'initial_stake': inputs['initial_stake'],
            'current_stake': inputs['initial_stake'],
            'bet_amount': inputs['bet_amount'],
            'lower_limit': inputs['lower_limit'],
            'upper_limit': inputs['upper_limit'],
            'probability': inputs['probability'],
            'validated': True
        }


class ValidationErrorHandlingExample:
    """Example of handling various validation errors"""
    
    def __init__(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def handle_invalid_stake(self):
        """Handle stake validation errors"""
        print("\n" + "-"*70)
        print("ERROR HANDLING EXAMPLE 1: Invalid Stake")
        print("-"*70 + "\n")
        
        invalid_stakes = [
            ("negative", -100.0),
            ("too_low", 0.001),
            ("too_high", 2000000.0),
            ("nan", float('nan')),
            ("infinity", float('inf')),
            ("invalid_type", "abc"),
            ("none", None),
        ]
        
        for test_name, stake in invalid_stakes:
            result = self.validator.validate_initial_stake(stake)
            print(f"Test: {test_name}")
            print(f"  Input: {stake}")
            print(f"  Valid: {result.is_valid}")
            if result.has_errors():
                print(f"  Error: {result.get_error_messages()[0]}")
            print()
    
    def handle_bet_exceeds_stake(self):
        """Handle bet amount validation errors"""
        print("\n" + "-"*70)
        print("ERROR HANDLING EXAMPLE 2: Bet Exceeds Stake")
        print("-"*70 + "\n")
        
        scenarios = [
            ("valid_bet", 50.0, 100.0),
            ("equals_stake", 100.0, 100.0),
            ("exceeds_stake", 150.0, 100.0),
            ("below_minimum", 0.001, 100.0),
            ("negative_bet", -50.0, 100.0),
        ]
        
        for test_name, bet, stake in scenarios:
            result = self.validator.validate_bet_amount(bet, stake)
            print(f"Test: {test_name}")
            print(f"  Bet: ${bet:.2f}, Stake: ${stake:.2f}")
            print(f"  Valid: {result.is_valid}")
            if result.has_errors():
                print(f"  Error: {result.get_error_messages()[0]}")
            print()
    
    def handle_invalid_limits(self):
        """Handle limit validation errors"""
        print("\n" + "-"*70)
        print("ERROR HANDLING EXAMPLE 3: Invalid Limits")
        print("-"*70 + "\n")
        
        scenarios = [
            ("valid", 10.0, 100.0, 50.0),
            ("upper_equals_lower", 50.0, 50.0, 50.0),
            ("upper_less_than_lower", 100.0, 50.0, 75.0),
            ("negative_lower", -10.0, 100.0, 50.0),
            ("stake_outside_range", 10.0, 20.0, 50.0),
        ]
        
        for test_name, lower, upper, stake in scenarios:
            result = self.validator.validate_limits(lower, upper, stake)
            print(f"Test: {test_name}")
            print(f"  Limits: ${lower:.2f} - ${upper:.2f}, Stake: ${stake:.2f}")
            print(f"  Valid: {result.is_valid}")
            if result.has_errors():
                print(f"  Error: {result.get_error_messages()[0]}")
            if result.has_warnings():
                print(f"  Warning: {result.get_warning_messages()[0]}")
            print()
    
    def handle_invalid_probability(self):
        """Handle probability validation errors"""
        print("\n" + "-"*70)
        print("ERROR HANDLING EXAMPLE 4: Invalid Probability")
        print("-"*70 + "\n")
        
        invalid_probs = [
            ("valid", 0.5),
            ("zero_boundary", 0.0),
            ("one_boundary", 1.0),
            ("below_range", -0.1),
            ("above_range", 1.5),
            ("nan", float('nan')),
            ("infinity", float('inf')),
        ]
        
        for test_name, prob in invalid_probs:
            result = self.validator.validate_probability(prob)
            print(f"Test: {test_name}")
            print(f"  Probability: {prob}")
            print(f"  Valid: {result.is_valid}")
            if result.has_errors():
                print(f"  Error: {result.get_error_messages()[0]}")
            print()


class ConfigurationExample:
    """Example of using different validation configurations"""
    
    def conservative_betting(self):
        """Example: Conservative betting with strict rules"""
        print("\n" + "-"*70)
        print("CONFIGURATION EXAMPLE 1: Conservative Betting")
        print("-"*70 + "\n")
        print("Configuration limits:")
        print(f"  Min Stake: ${CONSERVATIVE_CONFIG.min_stake:.2f}")
        print(f"  Max Stake: ${CONSERVATIVE_CONFIG.max_stake:.2f}")
        print(f"  Max Bet Multiplier: {CONSERVATIVE_CONFIG.max_bet_multiplier * 100:.0f}%")
        print(f"  Probability Range: {CONSERVATIVE_CONFIG.min_probability} - {CONSERVATIVE_CONFIG.max_probability}")
        print()
        
        validator = InputValidator(CONSERVATIVE_CONFIG)
        
        # Test: Conservative minimum stake
        result = validator.validate_initial_stake(5.0)
        print(f"Bet $5 stake (below conservative minimum):")
        print(f"  Valid: {result.is_valid}")
        if result.has_errors():
            print(f"  Error: {result.get_error_messages()[0]}")
        print()
        
        # Test: Conservative bet limit (10% of stake)
        result = validator.validate_bet_amount(20.0, 100.0)
        print(f"Bet $20 on $100 stake (20% - exceeds 10% limit):")
        print(f"  Valid: {result.is_valid}")
        if result.has_errors():
            print(f"  Error: {result.get_error_messages()[0]}")
        print()
    
    def standard_betting(self):
        """Example: Standard betting with moderate rules"""
        print("\n" + "-"*70)
        print("CONFIGURATION EXAMPLE 2: Standard Betting")
        print("-"*70 + "\n")
        print("Configuration limits:")
        print(f"  Min Stake: ${STANDARD_CONFIG.min_stake:.2f}")
        print(f"  Max Stake: ${STANDARD_CONFIG.max_stake:.2f}")
        print(f"  Max Bet Multiplier: {STANDARD_CONFIG.max_bet_multiplier * 100:.0f}%")
        print()
        
        validator = InputValidator(STANDARD_CONFIG)
        
        # Test: Standard minimum stake
        result = validator.validate_initial_stake(0.5)
        print(f"Bet $0.50 stake (above standard minimum):")
        print(f"  Valid: {result.is_valid}")
        print()


class ComprehensiveValidationExample:
    """Example of comprehensive multi-field validation"""
    
    def __init__(self):
        self.validator = InputValidator(STANDARD_CONFIG)
    
    def validate_complete_bet(self, stake, bet, lower, upper, prob):
        """Validate complete bet with all fields together"""
        print("\n" + "-"*70)
        print("COMPREHENSIVE VALIDATION EXAMPLE")
        print("-"*70 + "\n")
        
        print("Input Values:")
        print(f"  Initial Stake: ${stake:.2f}")
        print(f"  Bet Amount: ${bet:.2f}")
        print(f"  Lower Limit: ${lower:.2f}")
        print(f"  Upper Limit: ${upper:.2f}")
        print(f"  Probability: {prob:.2f}")
        print()
        
        result = self.validator.validate_all(stake, bet, lower, upper, prob)
        
        print("Validation Result:")
        print(f"  Overall Valid: {result.is_valid}")
        print(f"  Error Count: {result.get_error_count()}")
        print(f"  Warning Count: {result.get_warning_count()}")
        print()
        
        if result.has_errors():
            print("Errors:")
            for error in result.get_error_messages():
                print(f"  ✗ {error}")
            print()
        
        if result.has_warnings():
            print("Warnings:")
            for warning in result.get_warning_messages():
                print(f"  ⚠ {warning}")
            print()
        
        print(f"Result: {'✓ PASSED' if result.is_valid else '✗ FAILED'}")
        
        return result


def main():
    """Run all examples"""
    
    print("\n" + "="*70)
    print("INPUT VALIDATION INTEGRATION EXAMPLES")
    print("="*70)
    
    # Example 1: Interactive Session
    print("\n" + "▶" * 35)
    session = BettingSessionExample()
    print("[ EXAMPLE 1: INTERACTIVE SESSION SETUP ]")
    print("▶" * 35)
    # Uncomment to run interactive example:
    # session.interactive_session_setup()
    
    print("\n[Skipping interactive example - would require user input]")
    print("To test interactively, uncomment the session.interactive_session_setup() call")
    
    # Example 2: Programmatic Validation
    print("\n" + "▶" * 35)
    print("[ EXAMPLE 2: PROGRAMMATIC VALIDATION ]")
    print("▶" * 35)
    session.programmatic_validation(
        stake=100.0,
        bet=50.0,
        lower=10.0,
        upper=200.0,
        prob=0.75
    )
    
    # Example 3: Error Handling
    print("\n" + "▶" * 35)
    print("[ EXAMPLE 3: ERROR HANDLING ]")
    print("▶" * 35)
    error_handler = ValidationErrorHandlingExample()
    error_handler.handle_invalid_stake()
    error_handler.handle_bet_exceeds_stake()
    error_handler.handle_invalid_limits()
    error_handler.handle_invalid_probability()
    
    # Example 4: Configuration
    print("\n" + "▶" * 35)
    print("[ EXAMPLE 4: CONFIGURATION EXAMPLES ]")
    print("▶" * 35)
    config_example = ConfigurationExample()
    config_example.conservative_betting()
    config_example.standard_betting()
    
    # Example 5: Comprehensive Validation
    print("\n" + "▶" * 35)
    print("[ EXAMPLE 5: COMPREHENSIVE VALIDATION ]")
    print("▶" * 35)
    comp_example = ComprehensiveValidationExample()
    
    # Valid bet
    comp_example.validate_complete_bet(100.0, 50.0, 10.0, 200.0, 0.75)
    
    # Invalid bet
    comp_example.validate_complete_bet(-100.0, 150.0, 100.0, 50.0, 1.5)
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
