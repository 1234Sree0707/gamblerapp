# services/stake_management_service.py

from repositories.stake_transaction_repository import (
    StakeTransactionRepository
)

from models.transaction_type import (
    TransactionType
)

from models.stake_boundary import (
    StakeBoundary
)

from models.stake_monitor import (
    StakeMonitor
)

from models.stake_history_report import (
    StakeHistoryReport
)


class StakeManagementService:

    def __init__(self):

        self.repository = (
            StakeTransactionRepository()
        )

        self.monitor = StakeMonitor()

        self.boundary = StakeBoundary(

            min_limit=100,

            max_limit=10000

        )

    # Initialize stake

    def initialize(

        self,

        gambler_id,

        amount

    ):

        status = self.boundary.validate(

            amount

        )

        self.monitor.record(

            amount

        )

        self.repository.create(

            gambler_id,

            TransactionType
            .INITIAL_STAKE.value,

            amount,

            amount

        )

        return status

    # Calculate after bet

    def calculate(

        self,

        gambler_id,

        current_balance,

        change_amount,

        transaction_type

    ):

        new_balance = (

            current_balance
            + change_amount

        )

        self.monitor.record(

            new_balance

        )

        self.repository.create(

            gambler_id,

            transaction_type,

            change_amount,

            new_balance

        )

        return new_balance

    # Deposit funds

    def deposit(

        self,

        gambler_id,

        current_balance,

        amount

    ):

        if amount < 0:

            raise ValueError(

                "Deposit amount must be positive"

            )

        new_balance = (

            current_balance
            + amount

        )

        self.monitor.record(

            new_balance

        )

        self.repository.create(

            gambler_id,

            TransactionType
            .DEPOSIT.value,

            amount,

            new_balance

        )

        return new_balance

    # Withdraw funds

    def withdraw(

        self,

        gambler_id,

        current_balance,

        amount

    ):

        if amount <= 0:

            raise ValueError(

                "Withdrawal amount must be positive"

            )

        if amount > current_balance:

            raise ValueError(

                "Insufficient balance"

            )

        new_balance = (

            current_balance
            - amount

        )

        self.monitor.record(

            new_balance

        )

        self.repository.create(

            gambler_id,

            TransactionType
            .WITHDRAWAL.value,

            -amount,

            new_balance

        )

        return new_balance

    # Validate boundaries

    def validate(

        self,

        amount

    ):

        return self.boundary.validate(

            amount

        )

    # Monitor fluctuations

    def monitor_stats(self):

        return {

            "peak":

                self.monitor.peak,

            "lowest":

                self.monitor.lowest,

            "volatility":

                self.monitor.volatility()

        }

    # Generate report

    def generate_report(

        self,

        gambler_id

    ):

        transactions = (

            self.repository
            .get_by_gambler_id(
                gambler_id
            )

        )

        report = StakeHistoryReport(

            transactions

        )

        return {

            "total_transactions":

                report.total_transactions(),

            "net_profit_loss":

                report.net_profit_loss(),

            "breakdown":

                report.transaction_breakdown()

        }