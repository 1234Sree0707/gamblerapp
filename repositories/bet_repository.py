# repositories/bet_repository.py

from models.bet import Bet
from database.connection import get_connection
import uuid
import logging

logger = logging.getLogger(__name__)


class BetRepository:
    """
    Repository for managing bets.
    Handles persistence of bet records to database.
    """

    def create(
        self,
        gambler_id,
        bet_amount,
        win_probability,
        odds=1.0,
        stake_before=0,
        session_id=None,
        strategy_name=None
    ):
        """
        Create and store a new bet to database.
        
        Args:
            gambler_id (int): Gambler's ID
            bet_amount (float): Amount to bet
            win_probability (float): Probability of winning (0-1)
            odds (float): Odds for potential winnings
            stake_before (float): Stake before the bet
            session_id (str): Associated session ID
            strategy_name (str): Betting strategy used
            
        Returns:
            Bet: The created bet
        """
        bet_id = str(uuid.uuid4())

        bet = Bet(
            bet_id=bet_id,
            gambler_id=gambler_id,
            bet_amount=bet_amount,
            win_probability=win_probability,
            odds=odds,
            stake_before=stake_before,
            session_id=session_id,
            strategy_name=strategy_name
        )

        # Save to database
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO bets 
            (bet_id, gambler_id, bet_amount, win_probability, odds, 
             stake_before, session_id, strategy_name, is_settled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (bet_id, gambler_id, bet_amount, win_probability, odds,
                 stake_before, session_id, strategy_name, False)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Bet created in database: {bet_id}")

        except Exception as e:
            logger.error(f"Failed to create bet in database: {str(e)}")
            raise

        return bet

    def get_by_id(self, bet_id):
        """Get bet from database by ID"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM bets WHERE bet_id = %s"
            cursor.execute(query, (bet_id,))

            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result:
                bet = Bet(
                    bet_id=result['bet_id'],
                    gambler_id=result['gambler_id'],
                    bet_amount=result['bet_amount'],
                    win_probability=result['win_probability'],
                    odds=result['odds'],
                    stake_before=result['stake_before'],
                    session_id=result['session_id'],
                    strategy_name=result['strategy_name']
                )
                # Set attributes from database
                bet.stake_after = result['stake_after']
                bet.actual_winnings = result['actual_winnings']
                bet.is_settled = result['is_settled']
                if result['outcome']:
                    from models.bet import BetOutcome
                    bet.outcome = BetOutcome(result['outcome'])
                return bet
            return None

        except Exception as e:
            logger.error(f"Failed to get bet {bet_id}: {str(e)}")
            return None

    def settle(self, bet_id, is_winner, new_stake):
        """Settle a bet with outcome"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            outcome = "win" if is_winner else "loss"
            
            # Get bet to calculate winnings
            bet = self.get_by_id(bet_id)
            if not bet:
                raise ValueError(f"Bet {bet_id} not found")
            
            if is_winner:
                actual_winnings = new_stake - bet.stake_before
            else:
                actual_winnings = 0

            query = """
            UPDATE bets 
            SET outcome = %s, stake_after = %s, actual_winnings = %s, 
                is_settled = %s, updated_at = NOW()
            WHERE bet_id = %s
            """

            cursor.execute(
                query,
                (outcome, new_stake, actual_winnings, True, bet_id)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Bet settled in database: {bet_id}")

        except Exception as e:
            logger.error(f"Failed to settle bet {bet_id}: {str(e)}")
            raise

    def get_by_gambler(self, gambler_id):
        """Get all bets for a gambler from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM bets WHERE gambler_id = %s ORDER BY created_at"
            cursor.execute(query, (gambler_id,))

            results = cursor.fetchall()
            cursor.close()
            connection.close()

            bets = []
            for row in results:
                bet = Bet(
                    bet_id=row['bet_id'],
                    gambler_id=row['gambler_id'],
                    bet_amount=row['bet_amount'],
                    win_probability=row['win_probability'],
                    odds=row['odds'],
                    stake_before=row['stake_before'],
                    session_id=row['session_id'],
                    strategy_name=row['strategy_name']
                )
                # Set attributes from database
                bet.stake_after = row['stake_after']
                bet.actual_winnings = row['actual_winnings']
                bet.is_settled = row['is_settled']
                if row['outcome']:
                    from models.bet import BetOutcome
                    bet.outcome = BetOutcome(row['outcome'])
                bets.append(bet)

            return bets

        except Exception as e:
            logger.error(f"Failed to get bets for gambler {gambler_id}: {str(e)}")
            return []

    def get_statistics_by_gambler(self, gambler_id):
        """Get betting statistics for a gambler"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT 
                COUNT(*) as total_bets,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as total_won,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as total_lost,
                SUM(bet_amount) as total_amount_bet,
                SUM(CASE WHEN outcome = 'win' THEN actual_winnings ELSE 0 END) as total_won_amount
            FROM bets 
            WHERE gambler_id = %s AND is_settled = TRUE
            """

            cursor.execute(query, (gambler_id,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result and result['total_bets']:
                win_rate = (result['total_won'] / result['total_bets']) * 100
                return {
                    'total_bets': result['total_bets'],
                    'total_won': result['total_won'],
                    'total_lost': result['total_lost'],
                    'total_amount_bet': result['total_amount_bet'] or 0,
                    'total_won_amount': result['total_won_amount'] or 0,
                    'win_rate': win_rate
                }

            return {
                'total_bets': 0,
                'total_won': 0,
                'total_lost': 0,
                'total_amount_bet': 0,
                'total_won_amount': 0,
                'win_rate': 0
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
