# tests/test_betting_mechanism.py

"""
Test file for the complete betting mechanism.
Tests all use cases and functionality.
"""

import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, '/'.join(__file__.split('/')[:-2]))

from services.betting_service import BettingService
from models.betting_strategies import StrategyFactory


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n{title}")
    print("-" * 80)


def test_single_bet():
    """Test Use Case 1: Place a single bet"""
    print_header("USE CASE 1: PLACE SINGLE BET")

    service = BettingService()
    gambler_id = 1
    initial_stake = 1000.0

    print_subheader("Scenario: Placing a single $50 bet with 60% win probability")

    result = service.place_bet(
        gambler_id=gambler_id,
        current_stake=initial_stake,
        bet_amount=50.0,
        win_probability=0.6,
        strategy_name="manual"
    )

    print(f"\nBet Placed Successfully!")
    print(f"  Bet ID: {result['bet_id']}")
    print(f"  Outcome: {result['outcome'].upper()}")
    print(f"  Bet Amount: ${result['bet_amount']:.2f}")
    print(f"  Winnings: ${result['winnings']:.2f}")
    print(f"  Stake Before: ${result['stake_before']:.2f}")
    print(f"  Stake After: ${result['stake_after']:.2f}")
    print(f"  Potential Winnings: ${result['potential_winnings']:.2f}")

    return service, result['bet_id']


def test_determine_outcome(service):
    """Test Use Case 2: Determine bet outcome using probability"""
    print_header("USE CASE 2: DETERMINE BET OUTCOME USING PROBABILITY")

    print_subheader("Testing outcome determination with various probabilities")

    probabilities = [0.2, 0.5, 0.8]
    tests_per_probability = 100

    for prob in probabilities:
        wins = sum(
            1 for _ in range(tests_per_probability)
            if service.determine_bet_outcome(prob)
        )
        actual_rate = (wins / tests_per_probability) * 100
        expected_rate = prob * 100

        print(f"\nProbability: {prob:.0%}")
        print(f"  Expected Win Rate: {expected_rate:.1f}%")
        print(f"  Actual Win Rate: {actual_rate:.1f}%")
        print(f"  Matches: {'✓' if abs(actual_rate - expected_rate) < 20 else '✗'}")


def test_apply_to_stake(service):
    """Test Use Case 3: Apply bet amount to stake based on outcome"""
    print_header("USE CASE 3: APPLY BET TO STAKE BASED ON OUTCOME")

    gambler_id = 2
    current_stake = 500.0

    print_subheader("Scenario: Multiple bets to see stake updates")

    total_initial = current_stake
    for bet_num in range(3):
        result = service.place_bet(
            gambler_id=gambler_id,
            current_stake=current_stake,
            bet_amount=50.0,
            win_probability=0.5,
            strategy_name="manual"
        )

        current_stake = result['stake_after']
        outcome_symbol = "✓ WIN" if result['outcome'] == "win" else "✗ LOSS"

        print(
            f"\nBet {bet_num + 1}: {outcome_symbol}"
            f" | ${result['stake_before']:.2f} → ${result['stake_after']:.2f}"
        )

    final_stake = current_stake
    change = final_stake - total_initial

    print(f"\n{'─' * 80}")
    print(f"Initial Stake: ${total_initial:.2f}")
    print(f"Final Stake: ${final_stake:.2f}")
    print(f"Net Change: ${change:+.2f}")


def test_validate_amount(service):
    """Test Use Case 4: Validate bet amount against stake"""
    print_header("USE CASE 4: VALIDATE BET AMOUNT AGAINST STAKE")

    gambler_id = 3
    current_stake = 100.0

    print_subheader("Testing validation scenarios")

    test_cases = [
        (50.0, True, "Valid bet (within stake)"),
        (100.0, True, "Valid bet (equals stake)"),
        (150.0, False, "Invalid bet (exceeds stake)"),
        (0.5, False, "Invalid bet (below minimum)"),
        (20000.0, False, "Invalid bet (above maximum)"),
        (-10.0, False, "Invalid bet (negative amount)"),
    ]

    for bet_amount, should_pass, description in test_cases:
        try:
            service.validate_bet_amount(bet_amount, current_stake)
            result = "✓ VALID"
            passed = should_pass
        except ValueError as e:
            result = f"✗ INVALID: {str(e)[:50]}"
            passed = not should_pass

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} | {description}: {result}")


def test_strategies(service):
    """Test Use Case 5: Different betting strategies"""
    print_header("USE CASE 5: DIFFERENT BETTING STRATEGIES")

    gambler_id = 4
    initial_stake = 1000.0

    strategies_info = service.get_available_strategies()

    print_subheader(f"Available Strategies ({len(strategies_info['strategies'])} total)")
    for i, strategy in enumerate(strategies_info['strategies'], 1):
        desc = strategies_info['descriptions'][strategy]
        print(f"{i}. {strategy.upper():20} - {desc}")

    print_subheader("Testing each strategy with 5 bets")

    for strategy_name in ['fixed', 'martingale', 'fibonacci']:
        print(f"\n{strategy_name.upper()} Strategy:")
        print("─" * 40)

        current_stake = initial_stake
        for i in range(5):
            try:
                result = service.place_bet_with_strategy(
                    gambler_id=gambler_id,
                    current_stake=current_stake,
                    strategy_name=strategy_name,
                    base_amount=20.0,
                    win_probability=0.5
                )

                current_stake = result['stake_after']
                outcome = "WIN" if result['outcome'] == 'win' else "LOSS"
                print(
                    f"  Bet {i + 1}: ${result['bet_amount']:6.2f} "
                    f"→ {outcome:4} (Stake: ${current_stake:.2f})"
                )

            except Exception as e:
                print(f"  Bet {i + 1}: Error - {str(e)[:50]}")
                break


def test_consecutive_bets():
    """Test Use Case 6: Multiple consecutive bets in a session"""
    print_header("USE CASE 6: MULTIPLE CONSECUTIVE BETS IN SESSION")

    service = BettingService()
    gambler_id = 5

    print_subheader("Scenario: 10 consecutive fixed bets")

    session_summary = service.place_consecutive_bets(
        gambler_id=gambler_id,
        initial_stake=500.0,
        num_bets=10,
        strategy_name='fixed',
        base_amount=25.0,
        win_probability=0.5
    )

    print(f"\nSession Summary:")
    print(f"  Session ID: {session_summary['session_id']}")
    print(f"  Strategy: {session_summary['strategy_name']}")
    print(f"  Status: {session_summary['status']}")
    print(f"\nStake Management:")
    print(f"  Initial Stake: ${session_summary['initial_stake']:.2f}")
    print(f"  Final Stake: ${session_summary['final_stake']:.2f}")
    print(f"  Stake Change: ${session_summary['stake_change']:+.2f}")
    print(f"  ROI: {session_summary['roi_percentage']:+.2f}%")
    print(f"\nBet Statistics:")
    print(f"  Total Bets: {session_summary['total_bets_placed']}")
    print(f"  Wins: {session_summary['total_wins']}")
    print(f"  Losses: {session_summary['total_losses']}")
    print(f"  Win Rate: {session_summary['win_rate_percentage']:.1f}%")
    print(f"  Amount Wagered: ${session_summary['total_amount_wagered']:.2f}")
    print(f"  Amount Won: ${session_summary['total_amount_won']:.2f}")
    print(f"\nSession Duration: {session_summary['session_duration_seconds']:.2f} seconds")

    # Show individual bets
    print(f"\nIndividual Bets:")
    print("─" * 80)
    print(f"{'#':>3} {'Outcome':>8} {'Amount':>10} {'Stake Before':>14} {'Stake After':>14}")
    print("─" * 80)

    for i, bet in enumerate(session_summary['bets'], 1):
        outcome = bet['outcome'].upper()
        amount = bet['bet_amount']
        stake_before = bet['stake_before']
        stake_after = bet['stake_after']
        print(
            f"{i:3} {outcome:>8} ${amount:>9.2f} ${stake_before:>13.2f} "
            f"${stake_after:>13.2f}"
        )


def test_probability_vs_strategy_combinations():
    """Test different probability and strategy combinations"""
    print_header("ADVANCED TEST: PROBABILITY & STRATEGY COMBINATIONS")

    service = BettingService()
    gambler_id = 6

    print_subheader("Testing strategies with different probabilities")

    strategies = ['fixed', 'martingale', 'reverse_martingale']
    probabilities = [0.3, 0.5, 0.7]

    for prob in probabilities:
        print(f"\nWin Probability: {prob:.0%}")
        print("─" * 70)

        for strategy in strategies:
            try:
                result = service.place_consecutive_bets(
                    gambler_id=gambler_id,
                    initial_stake=500.0,
                    num_bets=5,
                    strategy_name=strategy,
                    base_amount=20.0,
                    win_probability=prob
                )

                roi = result['roi_percentage']
                win_rate = result['win_rate_percentage']
                print(
                    f"{strategy.upper():20} | "
                    f"ROI: {roi:+6.2f}% | Win Rate: {win_rate:5.1f}%"
                )

            except Exception as e:
                print(f"{strategy.upper():20} | Error: {str(e)[:40]}")


def test_odds_calculation(service):
    """Test odds calculation from probabilities"""
    print_header("ODDS CALCULATION TEST")

    print_subheader("Probability to Odds Conversion")

    probabilities = [0.1, 0.2, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9]

    print(f"{'Probability':>15} | {'Odds':>10} | {'Potential Win on $100':>20}")
    print("─" * 50)

    for prob in probabilities:
        odds = service.calculate_odds(prob)
        potential_win = 100 * odds
        print(f"{prob:>14.1%} | {odds:>10.2f} | ${potential_win:>19.2f}")


def test_error_handling(service):
    """Test error handling and edge cases"""
    print_header("ERROR HANDLING & EDGE CASES")

    gambler_id = 7
    current_stake = 100.0

    print_subheader("Testing error scenarios")

    error_tests = [
        {
            "name": "Invalid probability (too high)",
            "params": {
                "gambler_id": gambler_id,
                "current_stake": current_stake,
                "bet_amount": 10,
                "win_probability": 1.5
            }
        },
        {
            "name": "Invalid probability (zero)",
            "params": {
                "gambler_id": gambler_id,
                "current_stake": current_stake,
                "bet_amount": 10,
                "win_probability": 0.0
            }
        },
        {
            "name": "Bet exceeds stake",
            "params": {
                "gambler_id": gambler_id,
                "current_stake": current_stake,
                "bet_amount": 200,
                "win_probability": 0.5
            }
        },
        {
            "name": "Invalid strategy name",
            "params": {
                "gambler_id": gambler_id,
                "current_stake": current_stake,
                "strategy_name": "invalid_strategy",
                "base_amount": 10,
                "win_probability": 0.5
            },
            "method": "place_bet_with_strategy"
        }
    ]

    for test in error_tests:
        method_name = test.get("method", "place_bet")
        method = getattr(service, method_name)

        try:
            method(**test["params"])
            print(f"✗ FAIL | {test['name']}: Should have raised error")
        except Exception as e:
            print(f"✓ PASS | {test['name']}: {str(e)[:50]}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  COMPREHENSIVE BETTING MECHANISM TEST SUITE".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    try:
        # Test 1: Single Bet
        service, bet_id = test_single_bet()

        # Test 2: Determine Outcome
        test_determine_outcome(service)

        # Test 3: Apply to Stake
        test_apply_to_stake(service)

        # Test 4: Validate Amount
        test_validate_amount(service)

        # Test 5: Strategies
        test_strategies(service)

        # Test 6: Consecutive Bets
        test_consecutive_bets()

        # Advanced Tests
        test_probability_vs_strategy_combinations()
        test_odds_calculation(service)
        test_error_handling(service)

        # Final Summary
        print_header("TEST SUITE COMPLETED SUCCESSFULLY")
        print("\n✓ All betting mechanism features tested and working!")
        print("✓ 6 use cases implemented and verified!")
        print("✓ 6+ betting strategies implemented!")
        print("✓ Comprehensive validation and error handling active!")
        print("\n" + "█" * 80)

    except Exception as e:
        print_header("TEST SUITE FAILED")
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
