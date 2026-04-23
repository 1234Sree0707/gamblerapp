# repositories/gambler_repository.py

from database.connection import get_connection


class GamblerRepository:

    # CREATE
    def create(
        self,
        name,
        email,
        initial_stake,
        win_threshold,
        loss_threshold
    ):

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO gamblers
        (
            name,
            email,
            initial_stake,
            current_stake,
            win_threshold,
            loss_threshold
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            initial_stake,
            initial_stake,
            win_threshold,
            loss_threshold
        )

        cursor.execute(query, values)

        connection.commit()

        gambler_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return gambler_id


    # READ
    def get_by_id(self, gambler_id):

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT *
        FROM gamblers
        WHERE id = %s
        """

        cursor.execute(
            query,
            (gambler_id,)
        )

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result


    # RESET PROFILE
    def reset_profile(self, gambler_id):

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        UPDATE gamblers
        SET
            current_stake = initial_stake,
            total_bets = 0,
            total_wins = 0,
            total_losses = 0
        WHERE id = %s
        """

        cursor.execute(
            query,
            (gambler_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()