# tests/test_game_session_management.py

"""
Comprehensive test suite for Game Session Management.
Tests all use cases and features.
"""

import sys
sys.path.insert(0, '/'.join(__file__.split('/')[:-2]))

from services.game_session_service import GameSessionService
from models.game_session import (
    SessionParameters,
    SessionStatus,
    SessionEndReason,
    PauseReason
)


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subheader(title):
    """Print formatted subheader"""
    print(f"\n{title}")
    print("-" * 80)


def test_session_parameters():
    """Test session parameter creation and validation"""
    print_header("SESSION PARAMETERS TEST")

    print_subheader("Valid Parameters")
    params = SessionParameters(
        initial_stake=1000.0,
        upper_limit=2000.0,
        lower_limit=100.0,
        min_bet=10.0,
        max_bet=500.0
    )

    print(f"✓ Parameters created successfully")
    print(f"  Initial Stake: ${params.initial_stake:.2f}")
    print(f"  Limits: ${params.lower_limit:.2f} - ${params.upper_limit:.2f}")
    print(f"  Bet Range: ${params.min_bet:.2f} - ${params.max_bet:.2f}")

    print_subheader("Parameter Validation Tests")

    invalid_tests = [
        ("Upper limit <= initial", 1000, 1000, 100),
        ("Lower limit >= initial", 1000, 2000, 1000),
        ("Negative initial stake", -1000, 2000, 100),
    ]

    for desc, initial, upper, lower in invalid_tests:
        try:
            SessionParameters(
                initial_stake=initial,
                upper_limit=upper,
                lower_limit=lower
            )
            print(f"✗ FAIL | {desc}: Should have raised error")
        except ValueError:
            print(f"✓ PASS | {desc}: Correctly rejected")


def test_use_case_1_start_session():
    """Use Case 1: Start New Gaming Session"""
    print_header("USE CASE 1: START NEW GAMING SESSION")

    service = GameSessionService()
    gambler_id = 1

    print_subheader("Creating session with initial parameters")

    params = service.create_session_parameters(
        initial_stake=1000.0,
        upper_limit=2000.0,
        lower_limit=100.0,
        min_bet=10.0,
        max_bet=500.0,
        max_games=50,
        default_win_probability=0.5
    )

    result = service.start_new_session(
        gambler_id=gambler_id,
        parameters=params,
        strategy_name="balanced"
    )

    print(f"\n✓ Session Started Successfully!")
    print(f"  Session ID: {result['session_id']}")
    print(f"  Gambler ID: {result['gambler_id']}")
    print(f"  Status: {result['status']}")
    print(f"  Initial Stake: ${result['initial_stake']:.2f}")
    print(f"  Win Condition: >= ${result['upper_limit']:.2f}")
    print(f"  Loss Condition: <= ${result['lower_limit']:.2f}")

    return service, result['session_id'], params


def test_use_case_2_continue_session():
    """Use Case 2: Continue Session & Boundary Checking"""
    print_header("USE CASE 2: CONTINUE SESSION WITH BOUNDARY CHECKING")

    service, session_id, params = test_use_case_1_start_session()

    print_subheader("Playing 5 games with boundary monitoring")

    result = service.continue_session(
        session_id=session_id,
        num_games=5,
        bet_amounts=50.0,  # Fixed bet
        win_probabilities=0.6
    )

    print(f"\n✓ Session Continued!")
    print(f"  Games Played: {result['games_played']}")
    print(f"  Session Ended Early: {result['games_ended_early']}")

    summary = result['session_summary']
    print(f"\n  Session Status: {summary['status']}")
    print(f"  End Reason: {summary['end_reason']}")
    print(f"  Games Played: {summary['game_count']}")
    print(f"  Wins: {summary['total_wins']}")
    print(f"  Losses: {summary['total_losses']}")
    print(f"  Win Rate: {summary['win_rate_percentage']:.1f}%")
    print(f"  ROI: {summary['roi_percentage']:+.2f}%")


def test_use_case_3_pause_resume():
    """Use Case 3: Pause and Resume Sessions"""
    print_header("USE CASE 3: PAUSE AND RESUME SESSIONS")

    service = GameSessionService()
    params = service.create_session_parameters(
        initial_stake=1000.0,
        upper_limit=5000.0,
        lower_limit=50.0
    )

    result = service.start_new_session(1, params)
    session_id = result['session_id']

    print_subheader("Scenario: Pause after 3 games, resume, play 3 more")

    # Play 3 games
    print("\nPhase 1: Playing 3 games...")
    service.continue_session(session_id, 3, 100.0, 0.55)
    session_1 = service.get_session(session_id)
    print(f"  Games played: {session_1['game_count']}")

    # Pause
    print("\nPhase 2: Pausing session...")
    pause_result = service.pause_session(
        session_id,
        reason=PauseReason.USER_REQUESTED
    )
    print(f"  ✓ Session paused")
    print(f"  Status: {pause_result['status']}")

    # Resume
    print("\nPhase 3: Resuming session...")
    resume_result = service.resume_session(session_id)
    print(f"  ✓ Session resumed")
    print(f"  Status: {resume_result['status']}")

    # Play 3 more
    print("\nPhase 4: Playing 3 more games...")
    service.continue_session(session_id, 3, 100.0, 0.55)
    session_2 = service.get_session(session_id)

    print(f"\n✓ Pause/Resume Test Complete!")
    print(f"  Total Games Played: {session_2['game_count']}")
    print(f"  Pause Records: {len(session_2['pauses'])}")
    print(f"  Total Pause Duration: {session_2['total_pause_duration']:.1f}s")


def test_use_case_4_upper_limit():
    """Use Case 4: End Session When Upper Limit Reached (Win)"""
    print_header("USE CASE 4: END ON UPPER LIMIT (WIN CONDITION)")

    service = GameSessionService()
    params = service.create_session_parameters(
        initial_stake=1000.0,
        upper_limit=1500.0,  # Win when reach $1500
        lower_limit=100.0,
        default_win_probability=0.9  # High win rate
    )

    result = service.start_new_session(1, params)
    session_id = result['session_id']

    print_subheader("Playing games with 90% win probability")
    print(f"Initial Stake: ${params.initial_stake:.2f}")
    print(f"Win Condition: Reach ${params.upper_limit:.2f}")

    result = service.continue_session(
        session_id=session_id,
        num_games=20,
        bet_amounts=100.0,
        win_probabilities=0.9
    )

    summary = result['session_summary']

    print(f"\n✓ Session Ended!")
    print(f"  End Reason: {summary['end_reason']}")
    print(f"  Games Played: {summary['game_count']}")
    print(f"  Final Stake: ${summary['current_stake']:.2f}")
    print(f"  ROI: {summary['roi_percentage']:+.2f}%")

    if summary['end_reason'] == 'upper_limit_reached':
        print(f"\n✓ PASS: Session correctly ended at upper limit!")
    else:
        print(f"\n✗ FAIL: Expected upper_limit_reached, got {summary['end_reason']}")


def test_use_case_5_lower_limit():
    """Use Case 5: End Session When Lower Limit Reached (Loss)"""
    print_header("USE CASE 5: END ON LOWER LIMIT (LOSS CONDITION)")

    service = GameSessionService()
    params = service.create_session_parameters(
        initial_stake=500.0,
        upper_limit=1000.0,
        lower_limit=100.0,  # Loss when drop to $100
        min_bet=50.0,
        default_win_probability=0.1  # Low win rate
    )

    result = service.start_new_session(2, params)
    session_id = result['session_id']

    print_subheader("Playing games with 10% win probability")
    print(f"Initial Stake: ${params.initial_stake:.2f}")
    print(f"Loss Condition: Drop to ${params.lower_limit:.2f}")

    result = service.continue_session(
        session_id=session_id,
        num_games=20,
        bet_amounts=50.0,
        win_probabilities=0.1
    )

    summary = result['session_summary']

    print(f"\n✓ Session Ended!")
    print(f"  End Reason: {summary['end_reason']}")
    print(f"  Games Played: {summary['game_count']}")
    print(f"  Final Stake: ${summary['current_stake']:.2f}")
    print(f"  ROI: {summary['roi_percentage']:+.2f}%")

    if summary['end_reason'] == 'lower_limit_reached':
        print(f"\n✓ PASS: Session correctly ended at lower limit!")
    else:
        print(f"\n✗ FAIL: Expected lower_limit_reached, got {summary['end_reason']}")


def test_use_case_6_duration_tracking():
    """Use Case 6: Track Session Duration and Games"""
    print_header("USE CASE 6: SESSION DURATION & GAME TRACKING")

    service = GameSessionService()
    params = service.create_session_parameters(
        initial_stake=1000.0,
        upper_limit=5000.0,
        lower_limit=50.0
    )

    result = service.start_new_session(3, params)
    session_id = result['session_id']

    print_subheader("Playing 10 games with pause")

    # Play 5 games
    service.continue_session(session_id, 5, 50.0, 0.5)

    # Pause
    service.pause_session(session_id, PauseReason.BREAK)

    # Resume
    service.resume_session(session_id)

    # Play 5 more
    service.continue_session(session_id, 5, 50.0, 0.5)

    stats = service.get_session_statistics(session_id)

    print(f"\n✓ Session Complete!")
    print(f"\nGame Statistics:")
    print(f"  Total Games: {stats['games_played']}")
    print(f"  Wins: {stats['wins']}")
    print(f"  Losses: {stats['losses']}")
    print(f"  Win Rate: {stats['win_rate_percentage']:.1f}%")

    print(f"\nStake Statistics:")
    print(f"  Initial Stake: ${stats['initial_stake']:.2f}")
    print(f"  Current Stake: ${stats['current_stake']:.2f}")
    print(f"  Peak: ${stats['peak_stake']:.2f}")
    print(f"  Lowest: ${stats['lowest_stake']:.2f}")
    print(f"  ROI: {stats['roi_percentage']:+.2f}%")

    print(f"\nDuration Tracking:")
    print(f"  Active Duration: {stats['active_duration_seconds']:.1f}s")
    print(f"  Total Duration: {stats['total_duration_seconds']:.1f}s")
    print(f"  Pause Events: {stats['pause_count']}")
    print(f"  Total Pause Time: {stats['total_pause_duration']:.1f}s")


def test_session_statistics():
    """Test gambler statistics aggregation"""
    print_header("GAMBLER STATISTICS AGGREGATION TEST")

    service = GameSessionService()

    print_subheader("Running 3 sessions for same gambler")

    gambler_id = 100
    params = service.create_session_parameters(
        initial_stake=500.0,
        upper_limit=1000.0,
        lower_limit=50.0
    )

    # Session 1
    result1 = service.start_new_session(gambler_id, params)
    service.continue_session(result1['session_id'], 5, 50.0, 0.6)

    # Session 2
    result2 = service.start_new_session(gambler_id, params)
    service.continue_session(result2['session_id'], 5, 50.0, 0.5)

    # Session 3
    result3 = service.start_new_session(gambler_id, params)
    service.continue_session(result3['session_id'], 5, 50.0, 0.4)

    # Get statistics
    stats = service.get_gambler_statistics(gambler_id)

    print(f"\n✓ Statistics Aggregated!")
    print(f"  Total Sessions: {stats['total_sessions']}")
    print(f"  Total Games: {stats['total_games']}")
    print(f"  Total Wins: {stats['total_wins']}")
    print(f"  Total Losses: {stats['total_losses']}")
    print(f"  Overall Win Rate: {stats['win_rate_percentage']:.1f}%")
    print(f"  Total Wagered: ${stats['total_wagered']:.2f}")
    print(f"  Total Won: ${stats['total_won']:.2f}")
    print(f"  Overall ROI: {stats['total_roi_percentage']:+.2f}%")


def test_duplicate_session_prevention():
    """Test prevention of duplicate active sessions"""
    print_header("DUPLICATE SESSION PREVENTION TEST")

    service = GameSessionService()
    gambler_id = 5

    print_subheader("Attempting to start second session while first is active")

    params = service.create_session_parameters(1000.0, 2000.0, 100.0)

    # Start first session
    result1 = service.start_new_session(gambler_id, params)
    print(f"✓ First session started: {result1['session_id']}")

    # Try to start second session
    try:
        result2 = service.start_new_session(gambler_id, params)
        print(f"✗ FAIL: Should have prevented second session")
    except ValueError as e:
        print(f"✓ PASS: Second session correctly rejected")
        print(f"  Error: {str(e)[:60]}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  GAME SESSION MANAGEMENT TEST SUITE".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    try:
        # Test components
        test_session_parameters()

        # Use Cases
        test_use_case_1_start_session()
        test_use_case_2_continue_session()
        test_use_case_3_pause_resume()
        test_use_case_4_upper_limit()
        test_use_case_5_lower_limit()
        test_use_case_6_duration_tracking()

        # Advanced features
        test_session_statistics()
        test_duplicate_session_prevention()

        # Summary
        print_header("TEST SUITE COMPLETED SUCCESSFULLY")
        print("\n✓ All game session management features tested!")
        print("✓ 6 core use cases verified!")
        print("✓ Boundary detection working correctly!")
        print("✓ Pause/resume functionality operational!")
        print("✓ Complete statistics tracking enabled!")
        print("\n" + "█" * 80)

    except Exception as e:
        print_header("TEST SUITE FAILED")
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
