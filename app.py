from database.init_db import init_db

from services.gambler_profile_service import (
    GamblerProfileService
)

from services.stake_management_service import (
    StakeManagementService
)

from services.betting_service import (
    BettingService
)

from services.game_session_service import (
    GameSessionService
)

from models.transaction_type import (
    TransactionType
)

# Use Case 6: Input Validation and Error Handling
from utils.input_validator import InputValidator
from utils.safe_input_handler import SafeInputHandler
from utils.validation_config import STANDARD_CONFIG


def main():

    print("===================================")
    print(" Gambling Application Started ")
    print("===================================")

    # Initialize database
    init_db()

    # Initialize validation system
    validator = InputValidator(STANDARD_CONFIG)
    input_handler = SafeInputHandler(validator, max_retries=3, show_range=True)

    profile_service = GamblerProfileService()

    stake_service = StakeManagementService()
    
    betting_service = BettingService()
    
    game_session_service = GameSessionService()

    print("\n--- Create Gambler Profile ---")

    print("\nEnter gambler details:")

    # Get name
    print("\nName: Full name of the gambler (used for identification)")
    name = input("Enter Name: ").strip()
    
    while not name:
        print("✗ Name cannot be empty")
        name = input("Enter Name: ").strip()

    # Get email
    print("\nEmail: Contact email of the gambler")
    email = input("Enter Email: ").strip()
    
    while not email:
        print("✗ Email cannot be empty")
        email = input("Enter Email: ").strip()

    # Get initial stake with validation
    print("\nInitial Stake: Starting amount of money the gambler begins with")
    try:
        initial_stake = input_handler.get_initial_stake()
    except (ValueError, KeyboardInterrupt):
        print("✗ Failed to get initial stake. Using default: $100.00")
        initial_stake = 100.0

    # Get limits with validation
    print("\nWin/Loss Thresholds: Limits for automatic session stopping")
    try:
        loss_threshold, win_threshold = input_handler.get_limits(initial_stake)
    except (ValueError, KeyboardInterrupt):
        print("✗ Failed to get limits. Using defaults")
        loss_threshold = initial_stake * 0.5
        win_threshold = initial_stake * 2.0

    gambler_id = profile_service.create_gambler(

        name=name,

        email=email,

        initial_stake=initial_stake,

        win_threshold=win_threshold,

        loss_threshold=loss_threshold

    )

    print(
        "\n✓ Gambler created successfully!"
    )

    print(
        "  Gambler ID:",
        gambler_id
    )

    print("\n--- Initialize Stake ---")

    status = stake_service.initialize(

        gambler_id,

        amount=initial_stake

    )

    print(
        "  Stake initialization status:",
        status
    )

    current_balance = initial_stake

    # ===================================
    # BETTING MECHANISM - NEW FEATURES
    # ===================================
    
    print("\n--- BETTING MECHANISM FEATURES ---")
    
    print("\nAvailable Betting Strategies:")
    strategies = betting_service.get_available_strategies()
    for i, strategy in enumerate(strategies['strategies'], 1):
        desc = strategies['descriptions'][strategy]
        print(f"  {i}. {strategy.upper()} - {desc}")
    
    print("\nChoose betting experience:")
    print("  1. Single Bet")
    print("  2. Multiple Consecutive Bets (Session)")
    print("  3. Skip Betting")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n--- Place Single Bet ---")
        
        try:
            bet_amount = input_handler.get_bet_amount(current_balance)
            probability = input_handler.get_probability()
        except (ValueError, KeyboardInterrupt):
            print("✗ Failed to get bet details. Skipping bet.")
            bet_amount = None
        
        if bet_amount:
            try:
                result = betting_service.place_bet(
                    gambler_id=gambler_id,
                    current_stake=current_balance,
                    bet_amount=bet_amount,
                    win_probability=probability,
                    strategy_name="manual"
                )
                
                print("\n✓ Bet Placed Successfully!")
                print(f"  Outcome: {result['outcome'].upper()}")
                print(f"  Bet Amount: ${result['bet_amount']:.2f}")
                print(f"  Winnings: ${result['winnings']:.2f}")
                print(f"  Stake Before: ${result['stake_before']:.2f}")
                print(f"  Stake After: ${result['stake_after']:.2f}")
                
                current_balance = result['stake_after']
                
            except ValueError as e:
                print(f"✗ Bet Error: {str(e)}")
    
    elif choice == "2":
        print("\n--- Multiple Consecutive Bets ---")
        
        print("\nSelect Strategy:")
        strategies_list = betting_service.get_available_strategies()['strategies']
        for i, strategy in enumerate(strategies_list, 1):
            print(f"  {i}. {strategy.upper()}")
        
        try:
            strategy_choice = int(input("Select strategy (1-6): ")) - 1
            strategy_name = strategies_list[strategy_choice]
            
            base_bet = input_handler.get_bet_amount(current_balance)
            
            num_bets = int(input("Number of bets to place: "))
            
            win_prob = input_handler.get_probability()
            
            session_result = betting_service.place_consecutive_bets(
                gambler_id=gambler_id,
                initial_stake=current_balance,
                num_bets=num_bets,
                strategy_name=strategy_name,
                base_amount=base_bet,
                win_probability=win_prob
            )
            
            print("\n✓ Session Completed!")
            print(f"\nSession Summary:")
            print(f"  Strategy: {session_result['strategy_name'].upper()}")
            print(f"  Initial Stake: ${session_result['initial_stake']:.2f}")
            print(f"  Final Stake: ${session_result['final_stake']:.2f}")
            print(f"  Change: ${session_result['stake_change']:+.2f}")
            print(f"  ROI: {session_result['roi_percentage']:+.2f}%")
            print(f"\n  Total Bets: {session_result['total_bets_placed']}")
            print(f"  Wins: {session_result['total_wins']}")
            print(f"  Losses: {session_result['total_losses']}")
            print(f"  Win Rate: {session_result['win_rate_percentage']:.1f}%")
            print(f"  Amount Wagered: ${session_result['total_amount_wagered']:.2f}")
            print(f"  Amount Won: ${session_result['total_amount_won']:.2f}")
            
            current_balance = session_result['final_stake']
            
        except (ValueError, KeyboardInterrupt, IndexError) as e:
            print(f"✗ Session Error: {str(e)}")

    # ===================================
    # END BETTING MECHANISM
    # ===================================

    # ===================================
    # GAME SESSION MANAGEMENT - NEW FEATURES
    # ===================================
    
    print("\n--- GAME SESSION MANAGEMENT ---")
    print("\nStart a gaming session with automatic boundary detection?")
    print("  1. Yes - Start new session")
    print("  2. No - Skip to legacy features")
    
    session_choice = input("Enter choice (1-2): ").strip()
    
    if session_choice == "1":
        print("\n--- Configure Session Parameters ---")
        
        try:
            initial_stake = current_balance
            
            print("\n1. Set Loss Threshold (minimum balance to stop)")
            loss_threshold = input_handler.get_numeric_input(
                "Enter loss threshold: $",
                allow_empty=False
            )
            
            print("\n2. Set Win Threshold (maximum balance to stop)")
            win_threshold = input_handler.get_numeric_input(
                "Enter win threshold: $",
                allow_empty=False
            )
            
            print("\n3. Set Bet Range")
            min_bet = input_handler.get_numeric_input(
                "Enter minimum bet: $",
                allow_empty=False
            )
            
            max_bet = input_handler.get_numeric_input(
                "Enter maximum bet: $",
                allow_empty=False
            )
            
            # Validate bet range
            if max_bet <= min_bet:
                print("✗ Maximum bet must be greater than minimum bet")
                raise ValueError("Invalid bet range")
            
            max_games = int(input("Enter maximum games per session: "))
            
            # Create session parameters
            params = game_session_service.create_session_parameters(
                initial_stake=initial_stake,
                upper_limit=win_threshold,
                lower_limit=loss_threshold,
                min_bet=min_bet,
                max_bet=max_bet,
                max_games=max_games,
                default_win_probability=0.5
            )
            
            # Start session
            session_result = game_session_service.start_new_session(
                gambler_id=gambler_id,
                parameters=params,
                strategy_name="balanced"
            )
            
            session_id = session_result['session_id']
            print(f"\n✓ Gaming Session Started!")
            print(f"  Session ID: {session_id}")
            print(f"  Initial Stake: ${session_result['initial_stake']:.2f}")
            print(f"  Win at: >= ${session_result['upper_limit']:.2f}")
            print(f"  Stop at: <= ${session_result['lower_limit']:.2f}")
            
            # Play games
            print("\n--- Play Games ---")
            play_games = input("Play games now? (y/n): ").lower() == 'y'
            
            if play_games:
                num_games = int(input("Number of games to play: "))
                
                try:
                    bet_amount = input_handler.get_bet_amount(current_balance)
                    win_probability = input_handler.get_probability()
                except (ValueError, KeyboardInterrupt):
                    print("✗ Failed to get game parameters. Skipping games.")
                    bet_amount = None
                
                if bet_amount:
                    try:
                        game_result = game_session_service.continue_session(
                            session_id=session_id,
                            num_games=num_games,
                            bet_amounts=bet_amount,
                            win_probabilities=win_probability
                        )
                        
                        summary = game_result['session_summary']
                        
                        print(f"\n✓ Gaming Session Complete!")
                        print(f"  Games Played: {summary['game_count']}")
                        print(f"  Wins: {summary['total_wins']}")
                        print(f"  Losses: {summary['total_losses']}")
                        print(f"  Win Rate: {summary['win_rate_percentage']:.1f}%")
                        print(f"  Initial Stake: ${summary['initial_stake']:.2f}")
                        print(f"  Final Stake: ${summary['current_stake']:.2f}")
                        print(f"  ROI: {summary['roi_percentage']:+.2f}%")
                        print(f"  Session Status: {summary['status']}")
                        print(f"  End Reason: {summary['end_reason']}")
                        
                        # Show duration tracking
                        print(f"\n  Active Duration: {summary['active_duration_seconds']:.1f}s")
                        print(f"  Total Duration: {summary['total_duration_seconds']:.1f}s")
                        print(f"  Pause Events: {len(summary['pauses'])}")
                        
                        current_balance = summary['current_stake']
                        
                    except Exception as e:
                        print(f"✗ Gaming Error: {str(e)}")
            
        except (ValueError, KeyboardInterrupt) as e:
            print(f"✗ Session Configuration Error: {str(e)}")

    # ===================================
    # END GAME SESSION MANAGEMENT
    # ===================================

    # Legacy features (kept for compatibility)
    print("\n--- Deposit Funds ---")

    print("\nDeposit Amount: Money added to the current balance")
    
    try:
        deposit_amount = input_handler.get_numeric_input(
            "Enter Deposit Amount: $",
            allow_empty=False
        )
        
        current_balance = stake_service.deposit(
            gambler_id,
            current_balance,
            deposit_amount
        )

        print(f"✓ Balance after deposit: ${current_balance:.2f}")
    except (ValueError, KeyboardInterrupt):
        print("✗ Failed to process deposit")

    print("\n--- Validate Stake Boundaries ---")

    validation = stake_service.validate(

        current_balance
    )

    print(
        "Boundary validation result:",
        validation
    )

    print("\n--- Stake Monitoring ---")

    stats = stake_service.monitor_stats()

    print(
        "Peak Balance:",
        stats["peak"]
    )

    print(
        "Lowest Balance:",
        stats["lowest"]
    )

    print(
        "Volatility:",
        stats["volatility"]
    )

    print("\n--- Stake History Report ---")

    report = stake_service.generate_report(

        gambler_id
    )

    print(
        "Total transactions:",
        report["total_transactions"]
    )

    print(
        "Net profit/loss:",
        report["net_profit_loss"]
    )

    print(
        "Transaction breakdown:",
        report["breakdown"]
    )
    
    # Show betting statistics if any bets were placed
    print("\n--- Betting Statistics ---")
    try:
        bet_stats = betting_service.get_gambler_statistics(gambler_id)
        print(f"Total Bets Placed: {bet_stats['total_bets']}")
        print(f"Total Amount Bet: ${bet_stats['total_amount_bet']:.2f}")
        print(f"Total Won: ${bet_stats['total_won']:.2f}")
        print(f"Total Lost: ${bet_stats['total_lost']:.2f}")
        print(f"Win Rate: {bet_stats['win_rate']:.1f}%")
    except:
        print("No betting statistics available yet")

    print("\n===================================")
    print(" Final Balance: $" + str(round(current_balance, 2)))
    print(" Application finished successfully ")
    print("===================================")


if __name__ == "__main__":

    main()