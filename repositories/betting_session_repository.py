# repositories/betting_session_repository.py

from models.betting_session import BettingSession
import uuid


class BettingSessionRepository:
    """
    Repository for managing betting sessions.
    Handles persistence of session records.
    """

    def __init__(self):
        """Initialize with empty session storage"""
        self.sessions = {}  # session_id -> BettingSession
        self.gambler_sessions = {}  # gambler_id -> [session_ids]

    def create(self, gambler_id, initial_stake, strategy_name="default"):
        """
        Create and store a new betting session.
        
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
