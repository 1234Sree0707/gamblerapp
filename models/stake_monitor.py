# models/stake_monitor.py


class StakeMonitor:

    def __init__(self):

        self.history = []

        self.peak = 0

        self.lowest = None

    def record(self, amount):

        self.history.append(amount)

        if amount > self.peak:

            self.peak = amount

        if (

            self.lowest is None

            or amount < self.lowest

        ):

            self.lowest = amount

    def volatility(self):

        if len(self.history) < 2:

            return 0

        return (

            max(self.history)

            - min(self.history)

        )