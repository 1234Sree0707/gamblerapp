# models/game_session.py

from enum import Enum
from datetime import datetime
import uuid


class SessionStatus(Enum):
    """Enum for session status"""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED_WIN = "ended_win"
    ENDED_LOSS = "ended_loss"
    ENDED_MANUAL = "ended_manual"
    ENDED_TIMEOUT = "ended_timeout"


class SessionEndReason(Enum):
    """Enum for why a session ended"""
    UPPER_LIMIT_REACHED = "upper_limit_reached"
    LOWER_LIMIT_REACHED = "lower_limit_reached"
    MANUAL_END = "manual_end"
    SESSION_TIMEOUT = "session_timeout"
    MAX_GAMES_REACHED = "max_games_reached"
    USER_REQUEST = "user_request"


class GameOutcome(Enum):
    """Enum for game outcomes"""
    WIN = "win"
    LOSS = "loss"
    TIE = "tie"


class PauseReason(Enum):
    """Enum for pause reasons"""
    USER_REQUESTED = "user_requested"
    BREAK = "break"
    MAINTENANCE = "maintenance"
    NETWORK_ISSUE = "network_issue"
    OTHER = "other"


class GameRecord:
    """
    Records a single game played in a session.
    
    Features:
    - Complete game tracking
    - Bet and outcome recording
    - Stake changes
    - Duration tracking
    - Links to session and strategy
    """

    def __init__(
        self,
        game_id,
        session_id,
        game_number,
        bet_amount,
        win_probability,
        stake_before,
        stake_after,
        outcome,
        winnings,
        duration=None,
        created_at=None
    ):
        # Identifiers
        self.game_id = game_id
        self.session_id = session_id
        self.game_number = game_number

        # Bet details
        self.bet_amount = bet_amount
        self.win_probability = win_probability
        self.outcome = outcome
        self.winnings = winnings

        # Stake tracking
        self.stake_before = stake_before
        self.stake_after = stake_after

        # Timing
        self.created_at = created_at if created_at else datetime.utcnow()
        self.duration = duration  # in seconds

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "game_id": self.game_id,
            "session_id": self.session_id,
            "game_number": self.game_number,
            "bet_amount": self.bet_amount,
            "win_probability": self.win_probability,
            "outcome": self.outcome.value if self.outcome else None,
            "winnings": self.winnings,
            "stake_before": self.stake_before,
            "stake_after": self.stake_after,
            "duration": self.duration,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return (
            f"GameRecord(id={self.game_id}, game#{self.game_number}, "
            f"outcome={self.outcome.value}, stake: ${self.stake_before:.2f} → ${self.stake_after:.2f})"
        )


class PauseRecord:
    """
    Records a pause/resume cycle.
    
    Features:
    - Pause time tracking
    - Reason for pause
    - Complete pause history
    """

    def __init__(
        self,
        pause_id,
        session_id,
        reason,
        paused_at=None
    ):
        # Identifiers
        self.pause_id = pause_id
        self.session_id = session_id
        self.reason = reason

        # Timing
        self.paused_at = paused_at if paused_at else datetime.utcnow()
        self.resumed_at = None
        self.pause_duration = 0

    def resume(self):
        """Record resume time"""
        self.resumed_at = datetime.utcnow()
        self.pause_duration = (
            self.resumed_at - self.paused_at
        ).total_seconds()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "pause_id": self.pause_id,
            "session_id": self.session_id,
            "reason": self.reason.value if self.reason else None,
            "paused_at": self.paused_at.isoformat(),
            "resumed_at": self.resumed_at.isoformat() if self.resumed_at else None,
            "pause_duration": self.pause_duration
        }

    def __repr__(self):
        return (
            f"PauseRecord(id={self.pause_id}, reason={self.reason.value}, "
            f"duration={self.pause_duration}s)"
        )


class SessionParameters:
    """
    Configurable session parameters.
    
    Features:
    - Boundary limits (upper/lower)
    - Bet limits (min/max)
    - Game and duration limits
    - Default probabilities
    - Automatic validation
    """

    def __init__(
        self,
        initial_stake=1000.0,
        upper_limit=2000.0,
        lower_limit=100.0,
        min_bet=1.0,
        max_bet=500.0,
        max_games=100,
        max_duration_seconds=3600,  # 1 hour
        default_win_probability=0.5
    ):
        # Stake boundaries
        self.initial_stake = initial_stake
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit

        # Bet limits
        self.min_bet = min_bet
        self.max_bet = max_bet

        # Game limits
        self.max_games = max_games
        self.max_duration_seconds = max_duration_seconds

        # Defaults
        self.default_win_probability = default_win_probability

        # Validation
        self.validate()

    def validate(self):
        """Validate parameters"""
        if self.initial_stake <= 0:
            raise ValueError("Initial stake must be positive")

        if self.upper_limit <= self.initial_stake:
            raise ValueError(
                "Upper limit must be greater than initial stake"
            )

        if self.lower_limit >= self.initial_stake:
            raise ValueError(
                "Lower limit must be less than initial stake"
            )

        if self.lower_limit <= 0:
            raise ValueError("Lower limit must be positive")

        if self.min_bet <= 0 or self.max_bet <= 0:
            raise ValueError("Bet limits must be positive")

        if self.min_bet > self.max_bet:
            raise ValueError("Min bet cannot exceed max bet")

        if self.max_games <= 0:
            raise ValueError("Max games must be positive")

        if self.max_duration_seconds <= 0:
            raise ValueError("Max duration must be positive")

        if not (0 < self.default_win_probability < 1):
            raise ValueError(
                "Default win probability must be between 0 and 1"
            )

    def is_within_stake_limits(self, stake):
        """Check if stake is within limits"""
        return self.lower_limit <= stake <= self.upper_limit

    def is_stake_above_upper_limit(self, stake):
        """Check if stake exceeded upper limit"""
        return stake >= self.upper_limit

    def is_stake_below_lower_limit(self, stake):
        """Check if stake below lower limit"""
        return stake <= self.lower_limit

    def is_bet_valid(self, bet_amount, current_stake):
        """Validate bet amount"""
        return (
            self.min_bet <= bet_amount <= self.max_bet
            and bet_amount <= current_stake
        )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "initial_stake": self.initial_stake,
            "upper_limit": self.upper_limit,
            "lower_limit": self.lower_limit,
            "min_bet": self.min_bet,
            "max_bet": self.max_bet,
            "max_games": self.max_games,
            "max_duration_seconds": self.max_duration_seconds,
            "default_win_probability": self.default_win_probability
        }


class GamingSession:
    """
    Represents a complete gaming session.
    
    Features:
    - Start/pause/resume/end functionality
    - Automatic boundary monitoring
    - Game record tracking
    - Pause history
    - Duration tracking
    - Complete statistics
    """

    def __init__(
        self,
        session_id,
        gambler_id,
        parameters,
        strategy_name="default",
        created_at=None
    ):
        # Identifiers
        self.session_id = session_id
        self.gambler_id = gambler_id
        self.strategy_name = strategy_name

        # Parameters
        self.parameters = parameters

        # Status
        self.status = SessionStatus.INITIALIZED
        self.end_reason = None

        # Stake tracking
        self.current_stake = parameters.initial_stake
        self.initial_stake = parameters.initial_stake
        self.peak_stake = parameters.initial_stake
        self.lowest_stake = parameters.initial_stake

        # Game tracking
        self.games = []
        self.game_count = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_bets = 0.0
        self.total_winnings = 0.0

        # Pause tracking
        self.pauses = []
        self.total_pause_duration = 0

        # Timing
        self.created_at = created_at if created_at else datetime.utcnow()
        self.started_at = None
        self.ended_at = None
        self.active_start = None  # For pause tracking

    def start(self):
        """Start the session"""
        if self.status != SessionStatus.INITIALIZED:
            raise ValueError(
                f"Cannot start session in {self.status.value} state"
            )

        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.active_start = self.started_at

    def add_game(self, game_record):
        """Add a game record"""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(
                f"Cannot add game while session is {self.status.value}"
            )

        self.games.append(game_record)
        self.game_count += 1
        self.current_stake = game_record.stake_after
        self.total_bets += game_record.bet_amount

        # Track wins/losses
        if game_record.outcome == GameOutcome.WIN:
            self.total_wins += 1
            self.total_winnings += game_record.winnings
        elif game_record.outcome == GameOutcome.LOSS:
            self.total_losses += 1

        # Update peak and lowest
        if game_record.stake_after > self.peak_stake:
            self.peak_stake = game_record.stake_after
        if game_record.stake_after < self.lowest_stake:
            self.lowest_stake = game_record.stake_after

        # Check boundaries
        self._check_boundaries()

    def pause(self, reason=PauseReason.USER_REQUESTED):
        """Pause the session"""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(
                f"Cannot pause session in {self.status.value} state"
            )

        self.status = SessionStatus.PAUSED
        pause_record = PauseRecord(
            pause_id=str(uuid.uuid4()),
            session_id=self.session_id,
            reason=reason
        )
        self.pauses.append(pause_record)

    def resume(self):
        """Resume the session"""
        if self.status != SessionStatus.PAUSED:
            raise ValueError(
                f"Cannot resume session in {self.status.value} state"
            )

        # Calculate pause duration
        self.pauses[-1].resume()
        self.total_pause_duration += self.pauses[-1].pause_duration

        self.status = SessionStatus.ACTIVE
        self.active_start = datetime.utcnow()

    def end(self, reason=None):
        """End the session"""
        if self.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            raise ValueError(
                f"Cannot end session in {self.status.value} state"
            )

        # Set end reason if not already set
        if not self.end_reason:
            self.end_reason = reason or SessionEndReason.USER_REQUEST

        # Update status based on end reason
        if self.end_reason == SessionEndReason.UPPER_LIMIT_REACHED:
            self.status = SessionStatus.ENDED_WIN
        elif self.end_reason == SessionEndReason.LOWER_LIMIT_REACHED:
            self.status = SessionStatus.ENDED_LOSS
        elif self.end_reason == SessionEndReason.SESSION_TIMEOUT:
            self.status = SessionStatus.ENDED_TIMEOUT
        else:
            self.status = SessionStatus.ENDED_MANUAL

        self.ended_at = datetime.utcnow()

    def _check_boundaries(self):
        """Check if boundaries are reached"""
        if self.parameters.is_stake_above_upper_limit(self.current_stake):
            self.end_reason = SessionEndReason.UPPER_LIMIT_REACHED
            self.end()

        if self.parameters.is_stake_below_lower_limit(self.current_stake):
            self.end_reason = SessionEndReason.LOWER_LIMIT_REACHED
            self.end()

        if self.game_count >= self.parameters.max_games:
            self.end_reason = SessionEndReason.MAX_GAMES_REACHED
            self.end()

    def get_active_duration(self):
        """Get active play duration in seconds"""
        if not self.started_at:
            return 0

        end_time = self.ended_at if self.ended_at else datetime.utcnow()
        total_time = (end_time - self.started_at).total_seconds()

        return total_time - self.total_pause_duration

    def get_total_duration(self):
        """Get total session duration including pauses"""
        if not self.started_at:
            return 0

        end_time = self.ended_at if self.ended_at else datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

    def is_duration_exceeded(self):
        """Check if max duration exceeded"""
        return (
            self.get_active_duration()
            >= self.parameters.max_duration_seconds
        )

    def calculate_roi(self):
        """Calculate Return on Investment"""
        if self.initial_stake == 0:
            return 0

        profit = self.current_stake - self.initial_stake
        return (profit / self.initial_stake) * 100

    def calculate_win_rate(self):
        """Calculate win rate percentage"""
        if self.game_count == 0:
            return 0

        return (self.total_wins / self.game_count) * 100

    def calculate_average_bet(self):
        """Calculate average bet amount"""
        if self.game_count == 0:
            return 0

        return self.total_bets / self.game_count

    def get_summary(self):
        """Generate complete session summary"""
        return {
            "session_id": self.session_id,
            "gambler_id": self.gambler_id,
            "strategy_name": self.strategy_name,
            "status": self.status.value,
            "end_reason": self.end_reason.value if self.end_reason else None,
            "initial_stake": self.initial_stake,
            "current_stake": self.current_stake,
            "peak_stake": self.peak_stake,
            "lowest_stake": self.lowest_stake,
            "stake_change": self.current_stake - self.initial_stake,
            "roi_percentage": self.calculate_roi(),
            "game_count": self.game_count,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "win_rate_percentage": self.calculate_win_rate(),
            "total_bets": self.total_bets,
            "total_winnings": self.total_winnings,
            "average_bet": self.calculate_average_bet(),
            "games_played": self.game_count,
            "pause_count": len(self.pauses),
            "total_pause_duration": self.total_pause_duration,
            "active_duration_seconds": self.get_active_duration(),
            "total_duration_seconds": self.get_total_duration(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "games": [game.to_dict() for game in self.games],
            "pauses": [pause.to_dict() for pause in self.pauses],
            "parameters": self.parameters.to_dict()
        }

    def to_dict(self):
        """Convert to dictionary"""
        return self.get_summary()

    def __repr__(self):
        return (
            f"GamingSession(id={self.session_id}, games={self.game_count}, "
            f"status={self.status.value}, stake=${self.current_stake:.2f})"
        )
