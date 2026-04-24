# GAME SESSION MANAGEMENT - Complete Implementation

## Overview

A comprehensive game session management system with automatic boundary detection, pause/resume functionality, and complete session tracking.

## 6 Core Use Cases Implemented

### ✅ Use Case 1: Start New Gaming Session
- Initialize session with configurable parameters
- Set upper/lower stakes boundaries
- Configure bet and game limits
- Default win probability settings

### ✅ Use Case 2: Continue Session with Boundary Checking
- Play multiple consecutive games
- Automatic boundary monitoring after each game
- Continuous stake validation
- Early termination on limit reached

### ✅ Use Case 3a: Pause Session
- Pause active gaming sessions
- Track pause reason
- Record pause duration
- Support multiple pause/resume cycles

### ✅ Use Case 3b: Resume Session
- Resume paused sessions
- Continue from pause state
- Maintain pause history
- Track total pause duration

### ✅ Use Case 4: End on Upper Limit (Win Condition)
- Automatic detection when stake >= upper limit
- Session terminates with ENDED_WIN status
- Complete statistics generation
- ROI calculation at win point

### ✅ Use Case 5: End on Lower Limit (Loss Condition)
- Automatic detection when stake <= lower limit
- Session terminates with ENDED_LOSS status
- Loss tracking and analysis
- Prevents further stake losses

### ✅ Use Case 6: Track Duration & Games
- Complete session timing (active vs pause)
- Game-by-game history
- Win/loss statistics
- Performance metrics

## File Structure

```
models/
├── game_session.py              # Core session models
│   ├── SessionStatus (enum)
│   ├── SessionEndReason (enum)
│   ├── GameOutcome (enum)
│   ├── PauseReason (enum)
│   ├── GameRecord (class)
│   ├── PauseRecord (class)
│   ├── SessionParameters (class)
│   └── GamingSession (class)
└── game_session_manager.py      # Session lifecycle management

repositories/
└── game_session_repository.py   # Session persistence

services/
└── game_session_service.py      # Main orchestration service

tests/
└── test_game_session_management.py  # Comprehensive test suite
```

## Key Components

### 1. SessionStatus Enum

```python
INITIALIZED  - Session created, not yet started
ACTIVE       - Session running, games being played
PAUSED       - Session temporarily paused
ENDED_WIN    - Session ended (upper limit reached)
ENDED_LOSS   - Session ended (lower limit reached)
ENDED_MANUAL - Session ended by user request
ENDED_TIMEOUT- Session exceeded max duration
```

### 2. SessionEndReason Enum

```python
UPPER_LIMIT_REACHED  - Won (reached win threshold)
LOWER_LIMIT_REACHED  - Lost (dropped below loss threshold)
MANUAL_END          - User ended session
SESSION_TIMEOUT     - Max duration exceeded
MAX_GAMES_REACHED   - Max games limit reached
USER_REQUEST        - User requested end
```

### 3. GameRecord Class

Tracks each game played:
```python
GameRecord(
    game_id,           # Unique UUID
    session_id,        # Parent session
    game_number,       # Sequential game number
    bet_amount,        # Amount wagered
    win_probability,   # Probability used
    stake_before,      # Previous stake
    stake_after,       # New stake
    outcome,           # WIN/LOSS/TIE
    winnings,          # +/- amount
    duration,          # Game duration
    created_at         # Timestamp
)
```

### 4. PauseRecord Class

Tracks pause/resume cycles:
```python
PauseRecord(
    pause_id,          # Unique UUID
    session_id,        # Parent session
    reason,            # PauseReason enum
    paused_at,         # Pause timestamp
    resumed_at,        # Resume timestamp
    pause_duration     # Duration in seconds
)
```

### 5. SessionParameters Class

Configurable session boundaries:
```python
SessionParameters(
    initial_stake=1000.0,           # Starting amount
    upper_limit=2000.0,             # Win condition
    lower_limit=100.0,              # Loss condition
    min_bet=1.0,                    # Minimum bet
    max_bet=500.0,                  # Maximum bet
    max_games=100,                  # Max games per session
    max_duration_seconds=3600,      # 1 hour max
    default_win_probability=0.5     # 50% default
)
```

Includes validation:
- `is_within_stake_limits(stake)` - Check if within boundaries
- `is_stake_above_upper_limit(stake)` - Check win condition
- `is_stake_below_lower_limit(stake)` - Check loss condition
- `is_bet_valid(amount, current_stake)` - Validate bet

### 6. GamingSession Class

Main session entity:

**Lifecycle Methods:**
- `start()` - Initialize session
- `add_game(game_record)` - Add game (auto-checks boundaries)
- `pause(reason)` - Pause session
- `resume()` - Resume session
- `end(reason)` - End session

**Tracking Methods:**
- `get_active_duration()` - Active play time
- `get_total_duration()` - Total time including pauses
- `is_duration_exceeded()` - Check timeout
- `calculate_roi()` - Return on investment
- `calculate_win_rate()` - Win rate percentage
- `calculate_average_bet()` - Average bet amount

**Statistics:**
- `game_count` - Total games played
- `total_wins` - Number of wins
- `total_losses` - Number of losses
- `total_bets` - Total amount wagered
- `total_winnings` - Total amount won
- `peak_stake` - Highest stake reached
- `lowest_stake` - Lowest stake reached

### 7. GameSessionManager Class

Manages session lifecycle:

**Core Methods:**
- `create_session(gambler_id, parameters)` - Create new session
- `start_session(session_id)` - Start session
- `play_game(session_id, bet, probability, outcome_func)` - Play game
- `pause_session(session_id, reason)` - Pause
- `resume_session(session_id)` - Resume
- `end_session(session_id, reason)` - End session

**Validation:**
- Prevents duplicate active sessions per gambler
- Validates session state before operations
- Checks boundary conditions after each game

### 8. GameSessionService Class

Main orchestration service implementing all 6 use cases:

**Use Case 1: Start Session**
```python
result = service.start_new_session(
    gambler_id=1,
    parameters=params,
    strategy_name="balanced"
)
```

**Use Case 2: Continue Session**
```python
result = service.continue_session(
    session_id=session_id,
    num_games=10,
    bet_amounts=50.0,
    win_probabilities=0.6
)
```

**Use Case 3a: Pause**
```python
result = service.pause_session(
    session_id=session_id,
    reason=PauseReason.BREAK
)
```

**Use Case 3b: Resume**
```python
result = service.resume_session(session_id)
```

**Use Case 4 & 5: Boundary Detection**
- Automatic in `play_game()` and `continue_session()`
- No need to call explicitly
- Returns `end_reason` in results

**Use Case 6: Statistics**
```python
stats = service.get_session_statistics(session_id)
# Returns: games_played, wins, losses, durations, etc.
```

## Key Features

### 🎯 Automatic Boundary Detection

Sessions automatically end when:
- **Win Condition**: `stake >= upper_limit` → ENDED_WIN
- **Loss Condition**: `stake <= lower_limit` → ENDED_LOSS
- **Max Games**: Reached `max_games` limit → ENDED_TIMEOUT
- **Duration Timeout**: Exceeded `max_duration_seconds` → ENDED_TIMEOUT

### ⏸️ Complete Pause System

- Multiple pause/resume cycles per session
- Pause reasons tracked (break, maintenance, network, etc.)
- Pause duration calculated automatically
- Active time tracked separately from pause time

### 📊 Real-Time Monitoring

- Boundary check after each game
- Continuous stake validation
- ROI calculation in real-time
- Win rate updates after each game

### 🔒 Session Timeout Protection

- Maximum session duration configurable
- Prevents excessively long sessions
- Automatically ends if timeout exceeded
- Tracks active vs. pause duration separately

### 📈 Detailed Statistics

Session summary includes:
```json
{
    "session_id": "uuid",
    "gambler_id": 1,
    "status": "ended_win",
    "end_reason": "upper_limit_reached",
    "game_count": 25,
    "total_wins": 15,
    "total_losses": 10,
    "win_rate_percentage": 60.0,
    "initial_stake": 1000.0,
    "current_stake": 2500.0,
    "peak_stake": 2500.0,
    "lowest_stake": 800.0,
    "roi_percentage": 150.0,
    "total_bets": 10000.0,
    "average_bet": 400.0,
    "active_duration_seconds": 185.5,
    "total_duration_seconds": 245.2,
    "pause_count": 2,
    "total_pause_duration": 59.7,
    "games": [...],
    "pauses": [...]
}
```

### 📋 Complete Audit Trail

- Every game recorded with full details
- Every pause/resume tracked
- Game-by-game stake history
- Outcome and timestamp for each event

## Response Formats

### Start Session Response
```json
{
    "success": true,
    "session_id": "uuid",
    "gambler_id": 1,
    "status": "active",
    "initial_stake": 1000.0,
    "upper_limit": 2000.0,
    "lower_limit": 100.0
}
```

### Play Game Response
```json
{
    "success": true,
    "game_number": 5,
    "bet_amount": 50.0,
    "outcome": "win",
    "winnings": 83.33,
    "stake_before": 950.0,
    "stake_after": 1033.33,
    "session_status": "active",
    "session_ended": false,
    "end_reason": null,
    "games_played": 5,
    "current_stake": 1033.33
}
```

### Continue Session Response
```json
{
    "success": true,
    "session_id": "uuid",
    "games_played": 10,
    "games_ended_early": true,
    "session_status": "ended_win",
    "session_summary": {...},
    "games": [...]
}
```

## Gambler Statistics

Aggregated across all sessions:
```python
{
    "total_sessions": 5,
    "total_games": 100,
    "total_wins": 55,
    "total_losses": 45,
    "win_rate_percentage": 55.0,
    "total_wagered": 50000.0,
    "total_won": 15000.0,
    "initial_total_stake": 10000.0,
    "final_total_stake": 25000.0,
    "total_roi_percentage": 150.0
}
```

## Error Handling

Validates and prevents:
- Duplicate active sessions per gambler
- Invalid parameter ranges
- Negative stakes
- Bets exceeding available stake
- Invalid state transitions
- Probability outside 0-1 range

## Logging

Comprehensive logging at key points:
```
INFO: Session created: session_id for gambler gambler_id
INFO: Session started: session_id
INFO: Game played: session=id, bet=$50, outcome=win, stake: $1000 → $1050
INFO: Session paused: session_id, reason=user_requested
INFO: Session resumed: session_id
INFO: Session ended: session_id, reason=upper_limit_reached
```

## Integration with Existing Systems

Works seamlessly with:
- **BettingService** for individual bets
- **GamblerProfileService** for gambler management
- **StakeManagementService** for stake tracking
- **app.py** for user interface

## Testing

Run comprehensive test suite:
```bash
python tests/test_game_session_management.py
```

Tests cover:
- ✓ Session parameter validation
- ✓ Session creation and lifecycle
- ✓ Game playing with boundary detection
- ✓ Pause/resume functionality
- ✓ Upper limit (win) detection
- ✓ Lower limit (loss) detection
- ✓ Duration tracking
- ✓ Statistics aggregation
- ✓ Duplicate session prevention
- ✓ Error handling

## Usage Example

```python
from services.game_session_service import GameSessionService
from models.game_session import PauseReason

service = GameSessionService()

# Create parameters
params = service.create_session_parameters(
    initial_stake=1000.0,
    upper_limit=2000.0,
    lower_limit=100.0,
    default_win_probability=0.55
)

# Start session
result = service.start_new_session(gambler_id=1, parameters=params)
session_id = result['session_id']

# Play 10 games
game_result = service.continue_session(
    session_id=session_id,
    num_games=10,
    bet_amounts=100.0,
    win_probabilities=0.55
)

# Get session summary
summary = game_result['session_summary']
print(f"Games: {summary['game_count']}")
print(f"Wins: {summary['total_wins']}")
print(f"ROI: {summary['roi_percentage']:.2f}%")
print(f"Status: {summary['status']}")
print(f"End Reason: {summary['end_reason']}")
```

## Files Created

1. ✅ `models/game_session.py` (500+ lines) - Enums, GameRecord, PauseRecord, SessionParameters, GamingSession
2. ✅ `models/game_session_manager.py` (300+ lines) - Session lifecycle management
3. ✅ `repositories/game_session_repository.py` (150 lines) - Session persistence
4. ✅ `services/game_session_service.py` (400+ lines) - Main service implementing 6 use cases
5. ✅ `tests/test_game_session_management.py` (600+ lines) - Comprehensive test suite
6. ✅ `app.py` - Updated with game session integration

**Total: ~2000+ lines of production-ready code**

## Status: ✅ COMPLETE & TESTED

All 6 use cases implemented:
- ✓ Start new session
- ✓ Continue with boundary checking
- ✓ Pause session
- ✓ Resume session
- ✓ Auto-end on upper limit (win)
- ✓ Auto-end on lower limit (loss)
- ✓ Complete duration and game tracking

Ready for production deployment!
