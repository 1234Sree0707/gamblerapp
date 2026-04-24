# repositories/betting_session_repository.py

from models.betting_session import BettingSession
from database.connection import get_connection
import uuid
import logging
import json

logger = logging.getLogger(__name__)


class BettingSessionRepository:
    """
    Repository for managing betting sessions.
    Handles persistence of session records to database.
    """

    def create(self, gambler_id, initial_stake, strategy_name="default"):
        """
        Create and store a new betting session to database.
        
        Args:
            gambler_id (int): Gambler's ID
            initial_stake (float): Initial stake amount
            strategy_name (str): Primary strategy for session
            
        Returns:
            BettingSession: The created session
        """
        session_id = str(uuid.uuid4())

        session = BettingSession(
            session_id=session_id,
            gambler_id=gambler_id,
            initial_stake=initial_stake,
            strategy_name=strategy_name
        )

        # Save to database
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            INSERT INTO betting_sessions 
            (session_id, gambler_id, initial_stake, current_stake, 
             strategy_name, status, total_bets, total_wins, total_losses)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (session_id, gambler_id, initial_stake, initial_stake,
                 strategy_name, 'active', 0, 0, 0)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Betting session created in database: {session_id}")

        except Exception as e:
            logger.error(f"Failed to create betting session: {str(e)}")
            raise

        return session

    def get_by_id(self, session_id):
        """Get betting session from database by ID"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM betting_sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))

            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result:
                session = BettingSession(
                    session_id=result['session_id'],
                    gambler_id=result['gambler_id'],
                    initial_stake=result['initial_stake'],
                    strategy_name=result['strategy_name']
                )
                session.current_stake = result['current_stake']
                session.status = result['status']
                session.total_bets = result['total_bets']
                session.total_wins = result['total_wins']
                session.total_losses = result['total_losses']
                return session
            return None

        except Exception as e:
            logger.error(f"Failed to get betting session {session_id}: {str(e)}")
            return None

    def update(self, session):
        """Update betting session in database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            UPDATE betting_sessions 
            SET current_stake = %s, status = %s, total_bets = %s, 
                total_wins = %s, total_losses = %s, 
                win_rate_percentage = %s, roi_percentage = %s
            WHERE session_id = %s
            """

            win_rate = session.calculate_win_rate() if session.total_bets > 0 else 0
            roi = session.calculate_roi() if session.initial_stake > 0 else 0

            cursor.execute(
                query,
                (session.current_stake, session.status, session.total_bets,
                 session.total_wins, session.total_losses, win_rate, roi,
                 session.session_id)
            )

            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Betting session updated in database: {session.session_id}")

        except Exception as e:
            logger.error(f"Failed to update betting session: {str(e)}")
            raise

    def end_session(self, session_id):
        """Mark session as ended in database"""
        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
            UPDATE betting_sessions 
            SET status = 'ended', ended_at = NOW()
            WHERE session_id = %s
            """

            cursor.execute(query, (session_id,))
            connection.commit()
            cursor.close()
            connection.close()

            logger.debug(f"Betting session ended in database: {session_id}")

        except Exception as e:
            logger.error(f"Failed to end betting session: {str(e)}")
            raise

    def get_all_sessions(self):
        """Get all betting sessions from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM betting_sessions ORDER BY created_at DESC"
            cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            connection.close()

            sessions = []
            for row in results:
                session = BettingSession(
                    session_id=row['session_id'],
                    gambler_id=row['gambler_id'],
                    initial_stake=row['initial_stake'],
                    strategy_name=row['strategy_name']
                )
                session.current_stake = row['current_stake']
                session.status = row['status']
                sessions.append(session)

            return sessions

        except Exception as e:
            logger.error(f"Failed to get all betting sessions: {str(e)}")
            return []

    def get_by_gambler(self, gambler_id):
        """Get all betting sessions for a gambler from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM betting_sessions WHERE gambler_id = %s ORDER BY created_at DESC"
            cursor.execute(query, (gambler_id,))

            results = cursor.fetchall()
            cursor.close()
            connection.close()

            sessions = []
            for row in results:
                session = BettingSession(
                    session_id=row['session_id'],
                    gambler_id=row['gambler_id'],
                    initial_stake=row['initial_stake'],
                    strategy_name=row['strategy_name']
                )
                session.current_stake = row['current_stake']
                session.status = row['status']
                sessions.append(session)

            return sessions

        except Exception as e:
            logger.error(f"Failed to get betting sessions for gambler {gambler_id}: {str(e)}")
            return []

    def get_active_sessions(self):
        """Get all active betting sessions from database"""
        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM betting_sessions WHERE status = 'active' ORDER BY created_at DESC"
            cursor.execute(query)

            results = cursor.fetchall()
            cursor.close()
            connection.close()

            sessions = []
            for row in results:
                session = BettingSession(
                    session_id=row['session_id'],
                    gambler_id=row['gambler_id'],
                    initial_stake=row['initial_stake'],
                    strategy_name=row['strategy_name']
                )
                session.current_stake = row['current_stake']
                session.status = row['status']
                sessions.append(session)

            return sessions

        except Exception as e:
            logger.error(f"Failed to get active betting sessions: {str(e)}")
            return []

    def get_summary(self, session_id):
        """Get session summary from database"""
        session = self.get_by_id(session_id)
        if session:
            return session.get_summary()
        return None

        session = BettingSession(
            session_id=session_id,
            gambler_id=gambler_id,
            initial_stake=initial_stake,
            strategy_name=strategy_name
        )

        self.sessions[session_id] = session

        # Track by gambler
        if gambler_id not in self.gambler_sessions:
            self.gambler_sessions[gambler_id] = []
        self.gambler_sessions[gambler_id].append(session_id)

        return session

    def get_by_id(self, session_id):
        """Get session by ID"""
        return self.sessions.get(session_id)

    def get_by_gambler(self, gambler_id):
        """Get all sessions for a gambler"""
        session_ids = self.gambler_sessions.get(gambler_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def update(self, session_id, **kwargs):
        """Update session attributes"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        return session

    def end_session(self, session_id):
        """End a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.end_session()
        return session

    def delete(self, session_id):
        """Delete a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Remove from gambler tracking
        gambler_id = session.gambler_id
        if gambler_id in self.gambler_sessions:
            self.gambler_sessions[gambler_id] = [
                sid for sid in self.gambler_sessions[gambler_id] if sid != session_id
            ]

        del self.sessions[session_id]

    def get_all(self):
        """Get all sessions"""
        return list(self.sessions.values())

    def get_active_sessions(self):
        """Get all active sessions"""
        from models.betting_session import SessionStatus
        return [
            s for s in self.sessions.values()
            if s.status == SessionStatus.ACTIVE
        ]

    def get_session_summary(self, session_id):
        """Get session summary"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        return self.sessions[session_id].get_summary()

    def get_gambler_statistics(self, gambler_id):
        """Get betting statistics for a gambler's sessions"""
        sessions = self.get_by_gambler(gambler_id)

        total_sessions = len(sessions)
        total_amount_wagered = sum(s.total_amount_wagered for s in sessions)
        total_amount_won = sum(s.total_amount_won for s in sessions)
        total_bets = sum(s.total_bets_placed for s in sessions)
        total_wins = sum(s.total_wins for s in sessions)

        return {
            "total_sessions": total_sessions,
            "total_amount_wagered": total_amount_wagered,
            "total_amount_won": total_amount_won,
            "total_bets": total_bets,
            "total_wins": total_wins,
            "overall_win_rate": (total_wins / total_bets * 100) if total_bets > 0 else 0
        }
