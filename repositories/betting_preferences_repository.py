# repositories/betting_preferences_repository.py

from database.connection import get_connection


class BettingPreferencesRepository:

    # CREATE
    def create(
        self,
        gambler_id,
        min_bet,
        max_bet,
        strategy,
        auto_play=None,
        session_limit=None
    ):

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        INSERT INTO betting_preferences
        (
            gambler_id,
            min_bet,
            max_bet,
            preferred_strategy,
            auto_play,
            session_limit
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            gambler_id,
            min_bet,
            max_bet,
            strategy,
            auto_play,
            session_limit
        )

        cursor.execute(query, values)

        connection.commit()

        preferences_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return preferences_id

    # READ
    def get_by_gambler_id(self, gambler_id):

        connection = get_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        query = """
        SELECT *
        FROM betting_preferences
        WHERE gambler_id = %s
        """

        cursor.execute(
            query,
            (gambler_id,)
        )

        preferences = cursor.fetchone()

        cursor.close()
        connection.close()

        return preferences

    # UPDATE
    def update(
        self,
        gambler_id,
        min_bet,
        max_bet,
        strategy,
        auto_play=None,
        session_limit=None
    ):

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        UPDATE betting_preferences
        SET
            min_bet = %s,
            max_bet = %s,
            preferred_strategy = %s,
            auto_play = %s,
            session_limit = %s
        WHERE gambler_id = %s
        """

        values = (
            min_bet,
            max_bet,
            strategy,
            auto_play,
            session_limit,
            gambler_id
        )

        cursor.execute(query, values)

        connection.commit()

        cursor.close()
        connection.close()

    # DELETE
    def delete(self, gambler_id):

        connection = get_connection()

        cursor = connection.cursor()

        query = """
        DELETE FROM betting_preferences
        WHERE gambler_id = %s
        """

        cursor.execute(
            query,
            (gambler_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()