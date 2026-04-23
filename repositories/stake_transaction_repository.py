# repositories/stake_transaction_repository.py

from database.connection import get_connection


class StakeTransactionRepository:

    def create(

        self,

        gambler_id,

        transaction_type,

        amount,

        balance_after

    ):

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO stake_transactions
        (
            gambler_id,
            transaction_type,
            amount,
            balance_after
        )
        VALUES (%s, %s, %s, %s)
        """

        values = (

            gambler_id,

            transaction_type,

            amount,

            balance_after

        )

        cursor.execute(query, values)

        connection.commit()

        cursor.close()

        connection.close()

    def get_by_gambler_id(

        self,

        gambler_id

    ):

        connection = get_connection()

        cursor = connection.cursor(

            dictionary=True

        )

        query = """
        SELECT *
        FROM stake_transactions
        WHERE gambler_id = %s
        """

        cursor.execute(

            query,

            (gambler_id,)

        )

        result = cursor.fetchall()

        cursor.close()

        connection.close()

        return result