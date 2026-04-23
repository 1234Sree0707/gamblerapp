# models/stake_history_report.py


class StakeHistoryReport:

    def __init__(

        self,

        transactions

    ):

        self.transactions = transactions

    def total_transactions(self):

        return len(self.transactions)

    def net_profit_loss(self):

        total = 0

        for t in self.transactions:

            total += t["amount"]

        return total

    def transaction_breakdown(self):

        breakdown = {}

        for t in self.transactions:

            t_type = t["transaction_type"]

            breakdown[t_type] = (

                breakdown.get(

                    t_type,

                    0

                ) + 1

            )

        return breakdown