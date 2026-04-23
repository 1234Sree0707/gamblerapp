# models/stake_transaction.py

from datetime import datetime


class StakeTransaction:

    """
    Represents a single stake change.

    Used for:
    - Audit trail
    - Balance tracking
    - Reporting
    - Bet traceability
    """

    def __init__(

        self,

        gambler_id,

        transaction_type,

        amount,

        balance_after,

        bet_id=None,

        created_at=None,

        transaction_id=None

    ):

        # Primary key (optional when creating)
        self.transaction_id = transaction_id

        # Foreign key to gambler
        self.gambler_id = gambler_id

        # Optional link to bet
        self.bet_id = bet_id

        # Transaction category
        self.transaction_type = transaction_type

        # Amount change (+ or -)
        self.amount = amount

        # Balance after transaction
        self.balance_after = balance_after

        # Timestamp
        self.created_at = (

            created_at

            if created_at

            else datetime.now()

        )

    # -----------------------------
    # Convert object to dictionary
    # -----------------------------

    def to_dict(self):

        return {

            "transaction_id":
                self.transaction_id,

            "gambler_id":
                self.gambler_id,

            "bet_id":
                self.bet_id,

            "transaction_type":
                self.transaction_type,

            "amount":
                self.amount,

            "balance_after":
                self.balance_after,

            "created_at":
                self.created_at

        }

    # -----------------------------
    # String representation
    # -----------------------------

    def __str__(self):

        return (

            f"StakeTransaction("
            f"id={self.transaction_id}, "
            f"type={self.transaction_type}, "
            f"amount={self.amount}, "
            f"balance={self.balance_after}"
            f")"
        )