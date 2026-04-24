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

from models.transaction_type import (
    TransactionType
)


def main():

    print("===================================")
    print(" Gambling Application Started ")
    print("===================================")

    # Initialize database
    init_db()

    profile_service = GamblerProfileService()

    stake_service = StakeManagementService()
    
    betting_service = BettingService()

    print("\n--- Create Gambler Profile ---")

    print("\nEnter gambler details:")

    print(
        "\nName: Full name of the gambler "
        "(used for identification)"
    )
    name = input("Enter Name: ")

    print(
        "\nEmail: Contact email of the gambler"
    )
    email = input("Enter Email: ")

    print(
        "\nInitial Stake: Starting amount of money "
        "the gambler begins with"
    )
    initial_stake = float(
        input("Enter Initial Stake: ")
    )

    print(
        "\nWin Threshold: Amount at which gambler "
        "decides to stop after winning"
    )
    win_threshold = float(
        input("Enter Win Threshold: ")
    )

    print(
        "\nLoss Threshold: Minimum amount before "
        "gambler stops to avoid further losses"
    )
    loss_threshold = float(
        input("Enter Loss Threshold: ")
    )

    gambler_id = profile_service.create_gambler(

        name=name,

        email=email,

        initial_stake=initial_stake,

        win_threshold=win_threshold,

        loss_threshold=loss_threshold

    )

    print(
        "\nGambler created successfully!"
    )

    print(
        "Gambler ID:",
        gambler_id
    )

    print("\n--- Initialize Stake ---")

    status = stake_service.initialize(

        gambler_id,

        amount=initial_stake

    )

    print(
        "Stake initialization status:",
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
        bet_amount = float(input("Enter bet amount: $"))
        
        print("\nEnter win probability (0.1 - 0.9):")
        win_prob = float(input("Win probability: "))
        
        try:
            result = betting_service.place_bet(
                gambler_id=gambler_id,
                current_stake=current_balance,
                bet_amount=bet_amount,
                win_probability=win_prob,
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
        
        strategy_choice = int(input("Select strategy (1-6): ")) - 1
        strategy_name = strategies_list[strategy_choice]
        
        base_bet = float(input("Enter base bet amount: $"))
        num_bets = int(input("Number of bets to place: "))
        win_prob = float(input("Win probability per bet (0.1-0.9): "))
        
        try:
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
            
        except Exception as e:
            print(f"✗ Session Error: {str(e)}")

    # ===================================
    # END BETTING MECHANISM
    # ===================================

    # Legacy features (kept for compatibility)
    print("\n--- Deposit Funds ---")

    print(
        "\nDeposit Amount: Money added to the "
        "current balance"
    )

    deposit_amount = float(
        input("Enter Deposit Amount: ")
    )

    current_balance = stake_service.deposit(

        gambler_id,

        current_balance,

        deposit_amount

    )

    print(
        "Balance after deposit:",
        current_balance
    )

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