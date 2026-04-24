# services/game_session_service.py

import random
import logging
from models.game_session import (
    GamingSession,
    SessionParameters,
    SessionStatus,
    SessionEndReason,
    PauseReason,
    GameRecord,
    GameOutcome
)
from models.game_session_manager import GameSessionManager
from repositories.game_session_repository import GameSessionRepository
from services.gambler_profile_service import GamblerProfileService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameSessionService:
    """
    Comprehensive game session management service.
    
    Implements all use cases:
    1. Start New Session - startNewSession() with parameter validation
    2. Continue Session - continueSession() plays games while checking boundaries
    3. Pause/Resume - pauseSession() / resumeSession() with tracking
    4. End on Upper Limit - Automatic detection when win threshold reached
    5. End on Lower Limit - Automatic detection when loss threshold reached
    6. Track Duration & Games - Complete tracking of all metrics
    
    Features:
    - Automatic boundary detection and session closure
    - Comprehensive pause system with full tracking
    - Real-time monitoring and validation
    - Session timeout protection
    - Detailed statistics and audit trail
    - Complete game-by-game history
    """

    def __init__(self):
        """Initialize the game session service"""
        self.manager = GameSessionManager()
        self.repository = GameSessionRepository()
        self.gambler_profile_service = GamblerProfileService()

    def create_session_parameters(
        self,
        initial_stake=1000.0,
        upper_limit=2000.0,
        lower_limit=100.0,
        min_bet=1.0,
        max_bet=500.0,
        max_games=100,
        max_duration_seconds=3600,
        default_win_probability=0.5
    ):
        """
        Create session parameters.
        
        Args:
            initial_stake: Starting stake
            upper_limit: Win condition (stake >= upper_limit)
            lower_limit: Loss condition (stake <= lower_limit)
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
            max_games: Maximum games per session
            max_duration_seconds: Maximum session duration
            default_win_probability: Default win probability for games
            
        Returns:
            SessionParameters: Configured parameters
            
        Raises:
            ValueError: If parameters invalid
        """
        params = SessionParameters(
            initial_stake=initial_stake,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            min_bet=min_bet,
            max_bet=max_bet,
            max_games=max_games,
            max_duration_seconds=max_duration_seconds,
            default_win_probability=default_win_probability
        )

        logger.info(
            f"Session parameters created: initial=${initial_stake}, "
            f"limits=${lower_limit}-${upper_limit}"
        )

        return params

    def start_new_session(
        self,
        gambler_id,
        parameters,
        strategy_name="default"
    ):
        """
        Use Case 1: Start New Gambling Session
        
        Initializes a new gaming session with specified parameters.
        
        Args:
            gambler_id (int): Gambler's ID
            parameters (SessionParameters): Session configuration
            strategy_name (str): Betting strategy for session
            
        Returns:
            dict: Session details
            
        Raises:
            ValueError: If gambler has active session
        """
        logger.info(
            f"Starting new session for gambler {gambler_id}, "
            f"strategy={strategy_name}"
        )

        # Create session
        session = self.manager.create_session(
            gambler_id=gambler_id,
            parameters=parameters,
            strategy_name=strategy_name
        )

        # Start session
        self.manager.start_session(session.session_id)

        # Store in repository
        self.repository.create(session)

        return {
            "success": True,
            "session_id": session.session_id,
            "gambler_id": gambler_id,
            "status": session.status.value,
            "initial_stake": session.initial_stake,
            "upper_limit": parameters.upper_limit,
            "lower_limit": parameters.lower_limit
        }

    def play_game(
        self,
        session_id,
        bet_amount,
        win_probability=None
    ):
        """
        Play a single game in the session.
        
        Args:
            session_id (str): Session ID
            bet_amount (float): Bet amount
            win_probability (float): Win probability (uses default if None)
            
        Returns:
            dict: Game result
            
        Raises:
            ValueError: If session invalid or game cannot be played
        """
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Use default probability if not specified
        if win_probability is None:
            win_probability = session.parameters.default_win_probability

        logger.info(
            f"Playing game in session {session_id}: "
            f"bet=${bet_amount}, prob={win_probability:.2%}"
        )

        # Play the game
        game_record = self.manager.play_game(
            session_id=session_id,
            bet_amount=bet_amount,
            win_probability=win_probability,
            outcome_func=self._determine_outcome
        )

        # Update repository
        self.repository.update(session)

        # Check if session ended
        end_status = None
        if session.end_reason:
            end_status = session.end_reason.value

        return {
            "success": True,
            "game_number": game_record.game_number,
            "bet_amount": game_record.bet_amount,
            "outcome": game_record.outcome.value,
            "winnings": game_record.winnings,
            "stake_before": game_record.stake_before,
            "stake_after": game_record.stake_after,
            "session_status": session.status.value,
            "session_ended": session.status.value.startswith("ended_"),
            "end_reason": end_status,
            "games_played": session.game_count,
            "current_stake": session.current_stake
        }

    def continue_session(
        self,
        session_id,
        num_games,
        bet_amounts,
        win_probabilities=None
    ):
        """
        Use Case 2: Continue Session
        
        Plays multiple games while continuously checking boundary limits.
        Automatically ends when limits reached.
        
        Args:
            session_id (str): Session ID
            num_games (int): Number of games to attempt
            bet_amounts (float, list, or callable): Bet amounts per game
            win_probabilities (float, list, or callable): Win probabilities
            
        Returns:
            dict: Session results with all game outcomes
            
        Raises:
            ValueError: If session not found or invalid
        """
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        logger.info(
            f"Continuing session {session_id}: "
            f"attempting {num_games} games"
        )

        games_played = []
        games_ended_early = False

        for i in range(num_games):
            # Check if session ended
            if session.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
                games_ended_early = True
                logger.info(
                    f"Session ended after {i} games: "
                    f"{session.status.value}-{session.end_reason.value}"
                )
                break

            # Get bet amount
            if callable(bet_amounts):
                bet = bet_amounts(session.current_stake)
            elif isinstance(bet_amounts, (int, float)):
                bet = bet_amounts
            else:
                bet = bet_amounts[i] if i < len(bet_amounts) else bet_amounts[-1]

            # Get win probability
            if win_probabilities is None:
                prob = session.parameters.default_win_probability
            elif callable(win_probabilities):
                prob = win_probabilities()
            elif isinstance(win_probabilities, (int, float)):
                prob = win_probabilities
            else:
                prob = (
                    win_probabilities[i]
                    if i < len(win_probabilities)
                    else win_probabilities[-1]
                )

            try:
                result = self.play_game(session_id, bet, prob)
                games_played.append(result)

            except Exception as e:
                logger.error(f"Error playing game {i + 1}: {str(e)}")
                break

        # Update repository
        self.repository.update(session)

        # Update gambler balance in profile
        self.gambler_profile_service.update_balance(
            session.gambler_id,
            session.current_stake
        )

        return {
            "success": True,
            "session_id": session_id,
            "games_played": len(games_played),
            "games_ended_early": games_ended_early,
            "session_status": session.status.value,
            "session_summary": session.get_summary(),
            "games": games_played
        }

    def pause_session(
        self,
        session_id,
        reason=PauseReason.USER_REQUESTED
    ):
        """
        Use Case 3a: Pause Session
        
        Pauses an active gaming session.
        
        Args:
            session_id (str): Session ID
            reason (PauseReason): Reason for pause
            
        Returns:
            dict: Pause details
            
        Raises:
            ValueError: If session not found or invalid state
        """
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.status != SessionStatus.ACTIVE:
            raise ValueError(
                f"Can only pause ACTIVE session, current: {session.status.value}"
            )

        self.manager.pause_session(session_id, reason)
        self.repository.update(session)

        logger.info(
            f"Session paused: {session_id}, reason={reason.value}"
        )

        return {
            "success": True,
            "session_id": session_id,
            "status": session.status.value,
            "pause_count": len(session.pauses),
            "total_pause_duration": session.total_pause_duration
        }

    def resume_session(self, session_id):
        """
        Use Case 3b: Resume Session
        
        Resumes a paused gaming session.
        
        Args:
            session_id (str): Session ID
            
        Returns:
            dict: Resume details
            
        Raises:
            ValueError: If session not found or not paused
        """
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.status != SessionStatus.PAUSED:
            raise ValueError(
                f"Can only resume PAUSED session, current: {session.status.value}"
            )

        self.manager.resume_session(session_id)
        self.repository.update(session)

        logger.info(f"Session resumed: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "status": session.status.value,
            "total_pause_duration": session.total_pause_duration
        }

    def end_session(
        self,
        session_id,
        reason=SessionEndReason.USER_REQUEST
    ):
        """
        Manually end a session.
        
        Args:
            session_id (str): Session ID
            reason (SessionEndReason): Reason for ending
            
        Returns:
            dict: Session summary
            
        Raises:
            ValueError: If session not found or invalid state
        """
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.status in [SessionStatus.ENDED_WIN, SessionStatus.ENDED_LOSS,
                               SessionStatus.ENDED_MANUAL, SessionStatus.ENDED_TIMEOUT]:
            raise ValueError(
                f"Session already ended: {session.status.value}"
            )

        self.manager.end_session(session_id, reason)
        self.repository.update(session)

        # Update gambler balance in profile
        self.gambler_profile_service.update_balance(
            session.gambler_id,
            session.current_stake
        )

        logger.info(
            f"Session ended: {session_id}, reason={session.end_reason.value}"
        )

        return session.get_summary()

    def _determine_outcome(self, win_probability):
        """Determine game outcome using probability"""
        return random.random() < win_probability

    def get_session(self, session_id):
        """Get session details"""
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return session.get_summary()

    def get_active_session(self, gambler_id):
        """Get active session for gambler"""
        session = self.manager.get_active_session(gambler_id)
        if not session:
            return None

        return session.get_summary()

    def get_gambler_sessions(self, gambler_id):
        """Get all sessions for gambler"""
        sessions = self.manager.get_gambler_sessions(gambler_id)
        return [s.get_summary() for s in sessions]

    def get_gambler_statistics(self, gambler_id):
        """Get aggregated statistics for gambler"""
        return self.manager.get_gambler_statistics(gambler_id)

    def get_all_active_sessions(self):
        """Get all active sessions"""
        sessions = self.manager.get_all_active_sessions()
        return [s.get_summary() for s in sessions]

    def get_session_statistics(self, session_id):
        """Get session statistics"""
        session = self.manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        summary = session.get_summary()
        return {
            "session_id": session.session_id,
            "games_played": session.game_count,
            "wins": session.total_wins,
            "losses": session.total_losses,
            "win_rate_percentage": session.calculate_win_rate(),
            "initial_stake": session.initial_stake,
            "current_stake": session.current_stake,
            "peak_stake": session.peak_stake,
            "lowest_stake": session.lowest_stake,
            "roi_percentage": session.calculate_roi(),
            "total_bets": session.total_bets,
            "average_bet": session.calculate_average_bet(),
            "active_duration_seconds": session.get_active_duration(),
            "total_duration_seconds": session.get_total_duration(),
            "pause_count": len(session.pauses),
            "total_pause_duration": session.total_pause_duration,
            "status": session.status.value,
            "end_reason": session.end_reason.value if session.end_reason else None
        }
