from database.init_db import init_db

from services.gambler_profile_service import (
    GamblerProfileService
)

from services.stake_management_service import (
    StakeManagementService
)

from models.transaction_type import (
    TransactionType
)


def main():

    print("Starting application...")

    # -----------------------------
    # Initialize database tables
    # -----------------------------

    init_db()

    # -----------------------------
    # Use Case 1 Service
    # -----------------------------

    profile_service = (
        GamblerProfileService()
    )

    # -----------------------------
    # Use Case 2 Service
    # -----------------------------

    stake_service = (
        StakeManagementService()
    )

    print("\nCreating gambler...")

    gambler_id = profile_service.create_gambler(

        name="John",

        email="john@email.com",

        initial_stake=1000,

        win_threshold=5000,

        loss_threshold=100

    )

    print(
        "Gambler created with ID:",
        gambler_id
    )

    print("\nInitializing stake...")

    status = stake_service.initialize(

        gambler_id,

        amount=1000

    )

    print(
        "Stake initialization status:",
        status
    )

    current_balance = 1000

    print("\nDepositing funds...")

    current_balance = stake_service.deposit(

        gambler_id,

        current_balance,

        amount=500

    )

    print(
        "Balance after deposit:",
        current_balance
    )

    print("\nPlacing bet...")

    current_balance = stake_service.calculate(

        gambler_id,

        current_balance,

        change_amount=-200,

        transaction_type=(
            TransactionType
            .BET_PLACED
            .value
        )
    )

    print(
        "Balance after bet:",
        current_balance
    )

    print("\nProcessing bet win...")

    current_balance = stake_service.calculate(

        gambler_id,

        current_balance,

        change_amount=400,

        transaction_type=(
            TransactionType
            .BET_WIN
            .value
        )
    )

    print(
        "Balance after win:",
        current_balance
    )

    print("\nValidating boundaries...")

    validation = stake_service.validate(

        current_balance
    )

    print(
        "Boundary validation:",
        validation
    )

    print("\nMonitoring stake statistics...")

    stats = stake_service.monitor_stats()

    print(
        "Peak:",
        stats["peak"]
    )

    print(
        "Lowest:",
        stats["lowest"]
    )

    print(
        "Volatility:",
        stats["volatility"]
    )

    print("\nGenerating stake report...")

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

    print("\nApplication finished successfully.")


if __name__ == "__main__":

    main()