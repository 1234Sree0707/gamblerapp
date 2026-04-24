# models/game_session_manager.py

import logging
from models.game_session import (
    GamingSession,
    SessionStatus,
    GameRecord,
    GameOutcome
)

logger = logging.getLogger(__name__)


class GameSessionManager:
    """
    Manages multiple gaming sessions.
    
    Features:
    - Prevents duplicate active sessions per gambler
    - Handles session lifecycle
    - Tracks active and completed sessions
    - Provides session retrieval and reporting
    """

    def __init__(self):
        """Initialize session manager"""
        self.sessions = {}  # session_id -> GamingSession
        self.gambler_sessions = {}  # gambler_id -> [session_ids]
        self.active_sessions = {}  # gambler_id -> session_id (only one active per gambler)

    def create_session(self, gambler_id, parameters, strategy_name="default"):
        """
        Create a new gaming session.
        
        Args:
            gambler_id (int): Gambler's ID
            parameters (SessionParameters): Session configuration
            strategy_name (str): Strategy name
            
        Returns:
            GamingSession: Created session
            
        Raises:
            ValueError: If gambler has active session
        """
        # Check for existing active session
        if gambler_id in self.active_sessions:
            active_session_id = self.active_sessions[gambler_id]
            active_session = self.sessions[active_session_id]

            if active_session.status in [
                SessionStatus.ACTIVE,
                SessionStatus.PAUSED
            ]:
                raise ValueError(
                    f"Gambler {gambler_id} already has active session "
                    f"{active_session_id}. End it first."
                )

        # Create session
        import uuid
        session_id = str(uuid.uuid4())

        session = GamingSession(
            session_id=session_id,
            gambler_id=gambler_id,
            parameters=parameters,
            strategy_name=strategy_name
        )

        # Store session
        self.sessions[session_id] = session

        # Track by gambler
        if gambler_id not in self.gambler_sessions:
            self.gambler_sessions[gambler_id] = []
        self.gambler_sessions[gambler_id].append(session_id)

        # Mark as active
        self.active_sessions[gambler_id] = session_id

        logger.info(
            f"Session created: {session_id} for gambler {gambler_id}"
        )

        return session

    def get_session(self, session_id):
        """Get session by ID"""
        return self.sessions.get(session_id)

    def get_active_session(self, gambler_id):
        """Get active session for gambler"""
        session_id = self.active_sessions.get(gambler_id)
        if session_id:
            return self.sessions.get(session_id)
        return None

    def get_gambler_sessions(self, gambler_id):
        """Get all sessions for gambler"""
        session_ids = self.gambler_sessions.get(gambler_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]

    def start_session(self, session_id):
        """Start a session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.start()
        logger.info(f"Session started: {session_id}")

    def play_game(
        self,
        session_id,
        bet_amount,
        win_probability,
        outcome_func
    ):
        """
        Play a game in the session.
        
        Args:
            session_id (str): Session ID
            bet_amount (float): Bet amount
            win_probability (float): Win probability
            outcome_func: Function to determine outcome
            
        Returns:
            GameRecord: The recorded game
            
        Raises:
            ValueError: If session not found or invalid state
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.status != SessionStatus.ACTIVE:
            raise ValueError(
                f"Session must be ACTIVE to play, current: {session.status.value}"
            )

        # Validate bet
        if not session.parameters.is_bet_valid(bet_amount, session.current_stake):
            raise ValueError(
                f"Bet ${bet_amount} invalid. Min: ${session.parameters.min_bet}, "
                f"Max: ${session.parameters.max_bet}, "
                f"Available: ${session.current_stake}"
            )

        # Determine outcome
        is_winner = outcome_func(win_probability)

        # Calculate stake
        stake_before = session.current_stake
        if is_winner:
            winnings = bet_amount * (1 / win_probability) if win_probability > 0 else bet_amount
            stake_after = stake_before + winnings
            outcome = GameOutcome.WIN
        else:
            winnings = -bet_amount
            stake_after = stake_before - bet_amount
            outcome = GameOutcome.LOSS

        # Ensure non-negative stake
        stake_after = max(0, stake_after)

        # Create game record
        import uuid
        game_record = GameRecord(
            game_id=str(uuid.uuid4()),
            session_id=session_id,
            game_number=session.game_count + 1,
            bet_amount=bet_amount,
            win_probability=win_probability,
            stake_before=stake_before,
            stake_after=stake_after,
            outcome=outcome,
            winnings=winnings
        )

        # Add to session (this also checks boundaries)
        session.add_game(game_record)

        logger.info(
            f"Game played: session={session_id}, "
            f"bet=${bet_amount}, outcome={outcome.value}, "
            f"stake: ${stake_before:.2f} → ${stake_after:.2f}"
        )

        return game_record

    def pause_session(self, session_id, reason=None):
        """Pause a session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        from models.game_session import PauseReason
        reason = reason or PauseReason.USER_REQUESTED

        session.pause(reason)
        logger.info(
            f"Session paused: {session_id}, reason={reason.value}"
        )

    def resume_session(self, session_id):
        """Resume a paused session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.resume()
        logger.info(f"Session resumed: {session_id}")

    def end_session(self, session_id, reason=None):
        """End a session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.end(reason)

        # Remove from active sessions
        if session.gambler_id in self.active_sessions:
            if self.active_sessions[session.gambler_id] == session_id:
                del self.active_sessions[session.gambler_id]

        logger.info(
            f"Session ended: {session_id}, reason={session.end_reason.value}"
        )

    def get_session_summary(self, session_id):
        """Get session summary"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.get_summary()

    def get_all_active_sessions(self):
        """Get all active sessions"""
        return [
            self.sessions[sid]
            for sid in self.active_sessions.values()
            if sid in self.sessions
        ]

    def get_all_sessions(self):
        """Get all sessions"""
        return list(self.sessions.values())

    def get_gambler_statistics(self, gambler_id):
        """Get aggregated statistics for gambler"""
        sessions = self.get_gambler_sessions(gambler_id)

        total_sessions = len(sessions)
        total_games = sum(s.game_count for s in sessions)
        total_wins = sum(s.total_wins for s in sessions)
        total_losses = sum(s.total_losses for s in sessions)
        total_wagered = sum(s.total_bets for s in sessions)
        total_won = sum(s.total_winnings for s in sessions)

        initial_stake = sum(s.initial_stake for s in sessions)
        final_stake = sum(s.current_stake for s in sessions)

        return {
            "total_sessions": total_sessions,
            "total_games": total_games,
            "total_wins": total_wins,
            "total_losses": total_losses,
            "win_rate_percentage": (
                (total_wins / total_games * 100) if total_games > 0 else 0
            ),
            "total_wagered": total_wagered,
            "total_won": total_won,
            "initial_total_stake": initial_stake,
            "final_total_stake": final_stake,
            "total_roi_percentage": (
                ((final_stake - initial_stake) / initial_stake * 100)
                if initial_stake > 0
                else 0
            )
        }
