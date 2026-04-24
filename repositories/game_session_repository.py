# repositories/game_session_repository.py

from database.connection import get_connection
import logging

logger = logging.getLogger(__name__)


class GameSessionRepository:
    """
    Repository for managing gaming sessions.
    Handles persistence of session records to database.
    """

    def create(self, session):
        """
        Store a gaming session to database.
        
        Args:
            session (GamingSession): The session to store
            
        Returns:
            str: Session ID
        """
        try:
            connection = get_connection()
            cursor = connection.cursor()

            params = session.parameters
            query = """
            INSERT INTO game_sessions 
            (session_id, gambler_id, initial_stake, current_stake, 
             upper_limit, lower_limit, min_bet, max_bet, max_games, 
             strategy_name, status, started_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """

            cursor.execute(
                query,
                (session.session_id, session.gambler_id, session.initial_stake,
                 session.current_stake, params.upper_limit, params.lower_limit,
                 params.min_bet, params.max_bet, params.max_games,
                 'default', session.status.value)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Game session created in database: {session.session_id}")
            return session.session_id

        except Exception as e:
            logger.error(f"Failed to create game session: {str(e)}")
            raise

    def update(self, session):
        """Update gaming session in database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            UPDATE game_sessions 
            SET current_stake = %s, status = %s, game_count = %s, 
                total_wins = %s, total_losses = %s, 
                total_amount_wagered = %s, total_amount_won = %s,
                end_reason = %s, ended_at = NOW()
            WHERE session_id = %s
            """

            end_reason = session.end_reason.value if session.end_reason else None

            cursor.execute(
                query,
                (session.current_stake, session.status.value, session.game_count,
                 session.total_wins, session.total_losses, session.total_bets,
                 sum(gr.winnings for gr in session.game_history),
                 end_reason, session.session_id)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Game session updated in database: {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to update game session: {str(e)}")
            raise

    def get_by_id(self, session_id):
        """Get gaming session from database by ID"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM game_sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))

            result = cursor.fetchone()
            cursor.close()
            connection.close()

            return result if result else None

        except Exception as e:
            logger.error(f"Failed to get game session {session_id}: {str(e)}")
            return None

    def get_by_gambler(self, gambler_id):
        """Get all gaming sessions for a gambler from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM game_sessions WHERE gambler_id = %s ORDER BY created_at DESC"
            cursor.execute(query, (gambler_id,))

            results = cursor.fetchall()
            cursor.close()
            connection.close()

            return results if results else []

        except Exception as e:
            logger.error(f"Failed to get game sessions for gambler {gambler_id}: {str(e)}")
            return []

    def get_active_sessions(self):
        """Get all active gaming sessions from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM game_sessions WHERE status = 'active' ORDER BY created_at DESC"
            cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            connection.close()

            return results if results else []

        except Exception as e:
            logger.error(f"Failed to get active game sessions: {str(e)}")
            return []

    def end_session(self, session_id):
        """Mark gaming session as ended in database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            UPDATE game_sessions 
            SET status = 'ended', ended_at = NOW()
            WHERE session_id = %s
            """

            cursor.execute(query, (session_id,))
            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Game session ended in database: {session_id}")

        except Exception as e:
            logger.error(f"Failed to end game session: {str(e)}")
            raise

    def save_game_record(self, session_id, gambler_id, game_record):
        """Save individual game record to database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO game_records 
            (session_id, gambler_id, game_number, bet_amount, outcome, 
             winnings, stake_before, stake_after)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (session_id, gambler_id, game_record.game_number,
                 game_record.bet_amount, game_record.outcome.value,
                 game_record.winnings, game_record.stake_before,
                 game_record.stake_after)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Game record saved for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to save game record: {str(e)}")
            raise

    def delete(self, session_id):
        """Delete gaming session from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = "DELETE FROM game_sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Game session deleted from database: {session_id}")

        except Exception as e:
            logger.error(f"Failed to delete game session: {str(e)}")
            raise
        if session.gambler_id not in self.gambler_sessions:
            self.gambler_sessions[session.gambler_id] = []
        self.gambler_sessions[session.gambler_id].append(session.session_id)

        return session.session_id

    def get_by_id(self, session_id):
        """Get session by ID"""
        return self.sessions.get(session_id)

    def get_by_gambler(self, gambler_id):
        """Get all sessions for a gambler"""
        session_ids = self.gambler_sessions.get(gambler_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def update(self, session):
        """
        Update a session.
        
        Args:
            session (GamingSession): Updated session
        """
        self.sessions[session.session_id] = session.to_dict()

    def delete(self, session_id):
        """Delete a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session_data = self.sessions[session_id]
        gambler_id = session_data["gambler_id"]

        # Remove from gambler tracking
        if gambler_id in self.gambler_sessions:
            self.gambler_sessions[gambler_id] = [
                sid for sid in self.gambler_sessions[gambler_id]
                if sid != session_id
            ]

        del self.sessions[session_id]

    def get_all(self):
        """Get all sessions"""
        return list(self.sessions.values())

    def get_active_sessions(self):
        """Get all active sessions"""
        from models.game_session import SessionStatus
        return [
            s for s in self.sessions.values()
            if s["status"] in ["active", "paused"]
        ]

    def get_completed_sessions(self):
        """Get all completed sessions"""
        return [
            s for s in self.sessions.values()
            if s["status"].startswith("ended_")
        ]

    def get_session_count_by_gambler(self, gambler_id):
        """Get session count for gambler"""
        return len(self.get_by_gambler(gambler_id))

    def get_total_games_by_gambler(self, gambler_id):
        """Get total games played by gambler"""
        sessions = self.get_by_gambler(gambler_id)
        return sum(s["game_count"] for s in sessions)

    def get_statistics(self):
        """Get overall statistics"""
        sessions = self.get_all()

        total_sessions = len(sessions)
        total_games = sum(s["game_count"] for s in sessions)
        total_wins = sum(s["total_wins"] for s in sessions)
        total_wagered = sum(s["total_bets"] for s in sessions)

        return {
            "total_sessions": total_sessions,
            "total_games": total_games,
            "total_wins": total_wins,
            "total_wagered": total_wagered,
            "overall_win_rate": (
                (total_wins / total_games * 100) if total_games > 0 else 0
            )
        }
