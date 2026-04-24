# repositories/gambler_repository.py

import logging
from database.connection import get_connection

logger = logging.getLogger(__name__)


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

    # VERIFY BALANCE
    def verify_balance(
        self,
        gambler_id,
        expected_stake
    ):
        """
        Verify that gambler's balance was updated correctly.
        
        Args:
            gambler_id (int): Gambler ID
            expected_stake (float): Expected balance
            
        Returns:
            bool: True if balance matches expected value
        """
        try:
            gambler = self.get_by_id(gambler_id)
            if not gambler:
                logger.warning(f"Gambler {gambler_id} not found")
                return False
            
            actual_stake = gambler.get('current_stake', 0)
            
            # Allow for small floating point differences
            difference = abs(actual_stake - expected_stake)
            if difference < 0.01:
                logger.debug(
                    f"✓ Balance verified: gambler {gambler_id}, "
                    f"stake=${actual_stake:.2f}"
                )
                return True
            else:
                logger.warning(
                    f"✗ Balance mismatch for gambler {gambler_id}: "
                    f"expected ${expected_stake:.2f}, got ${actual_stake:.2f}"
                )
                return False
        except Exception as e:
            logger.error(f"Error verifying balance: {str(e)}")
            return False


    # UPDATE BALANCE
    def update_balance(
        self,
        gambler_id,
        current_stake
    ):
        """
        Update gambler's current_stake in database.
        
        Args:
            gambler_id (int): Gambler ID
            current_stake (float): New balance
            
        Raises:
            Exception: If database operation fails
        """
        connection = None
        try:
            connection = get_connection()

            cursor = connection.cursor()

            query = """
            UPDATE gamblers
            SET
                current_stake = %s
            WHERE id = %s
            """

            cursor.execute(
                query,
                (current_stake, gambler_id)
            )

            connection.commit()
            
            rows_affected = cursor.rowcount
            
            if rows_affected == 0:
                logger.warning(
                    f"No rows updated for gambler_id: {gambler_id}. "
                    f"Gambler may not exist."
                )
            else:
                logger.debug(
                    f"Database: Updated gambler {gambler_id} stake to ${current_stake:.2f}"
                )

            cursor.close()
            
        except Exception as e:
            logger.error(
                f"Database error updating balance for gambler {gambler_id}: {str(e)}"
            )
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()


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