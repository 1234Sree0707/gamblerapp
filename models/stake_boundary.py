# models/stake_boundary.py


class StakeBoundary:

    def __init__(

        self,

        min_limit,

        max_limit

    ):

        self.min_limit = min_limit

        self.max_limit = max_limit

        self.warning_low = (

            min_limit * 1.2

        )

        self.warning_high = (

            max_limit * 0.8

        )

    def validate(self, amount):

        if amount < self.min_limit:

            return "LOW_LIMIT_EXCEEDED"

        if amount > self.max_limit:

            return "HIGH_LIMIT_EXCEEDED"

        if amount <= self.warning_low:

            return "LOW_WARNING"

        if amount >= self.warning_high:

            return "HIGH_WARNING"

        return "VALID"