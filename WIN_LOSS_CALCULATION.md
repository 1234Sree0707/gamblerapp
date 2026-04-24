# WIN/LOSS CALCULATION SYSTEM DOCUMENTATION

## Overview

Complete system for calculating game outcomes, winnings, losses, and comprehensive statistics with multiple strategieand odds configurations.

## Architecture

### 1. Outcome Strategies (models/outcome_strategies.py)

Determines whether a bet wins based on probability.

#### RandomOutcomeStrategy
- Pure random probability
- 50% probability = exactly 50% chance of winning
- Ideal for: Fair/transparent betting

```python
from models.outcome_strategies import OutcomeStrategyFactory, OutcomeStrategyType

strategy = OutcomeStrategyFactory.create_strategy(OutcomeStrategyType.RANDOM)
is_winner = strategy.determine_outcome(0.5)  # 50% chance
```

#### WeightedProbabilityStrategy  
- Includes house edge for realistic casino simulation
- Reduces player's winning probability by house edge percentage
- Ideal for: Casino/realistic gaming

```python
strategy = OutcomeStrategyFactory.create_strategy(
    OutcomeStrategyType.HOUSE_EDGE,
    house_edge=0.02  # 2% house edge
)
```

### 2. Odds Configuration (models/odds_configuration.py)

Calculates winnings based on bet amount and odds.

#### Odds Types

1. **FIXED** - Simple multiplier
   - Bet $10, odds 2.0 = win $20
   - Most straightforward

2. **PROBABILITY_BASED** - Dynamic based on probability
   - Formula: winnings = bet / probability
   - 50% prob = 2x return, 10% prob = 10x return
   - Higher risk = higher reward

3. **AMERICAN** - Sports betting format
   - Negative odds (-110): favorite (lower payout)
   - Positive odds (+200): underdog (higher payout)

4. **DECIMAL** - European format
   - Bet $100, odds 2.5 = win $250
   - Common in Europe/Asia

#### Examples

```python
from models.odds_configuration import OddsConfiguration, OddsType

# Fixed odds
config = OddsConfiguration(OddsType.FIXED, base_odds=2.0)
winnings = config.calculate_winnings(100)  # $200

# Probability-based
config = OddsConfiguration(OddsType.PROBABILITY_BASED)
winnings = config.calculate_winnings(100, win_probability=0.5)  # $200

# American
config = OddsConfiguration(OddsType.AMERICAN, base_odds=-110)
winnings = config.calculate_winnings(100)  # ~$91

# Decimal
config = OddsConfiguration(OddsType.DECIMAL, base_odds=2.5)
winnings = config.calculate_winnings(100)  # $250
```

### 3. Game Result (models/game_result.py)

Records complete game outcome with all relevant data.

```python
from models.game_result import GameResult

result = GameResult(
    game_number=1,
    bet_amount=100,
    is_winner=True,
    stake_before=1000,
    stake_after=1200,
    winnings=200,
    odds=2.0,
    win_probability=0.5
)

print(result.outcome)  # "win"
print(result.roi_percentage)  # 20.0%
print(result.to_dict())  # Complete data dictionary
```

### 4. Win/Loss Statistics (models/game_result.py)

Comprehensive statistical analysis.

Tracks:
- Win/loss counts and rates
- Total amounts won/lost  
- Average win/loss
- Profit factor
- Largest win/loss
- Current and longest streaks

```python
from models.game_result import WinLossStatistics

stats = WinLossStatistics()

# Add results
for result in game_results:
    stats.add_result(result)

# Get metrics
print(f"Win rate: {stats.win_rate_percentage:.1f}%")
print(f"Profit factor: {stats.profit_factor:.2f}x")
print(f"Net P&L: ${stats.net_profit_loss:.2f}")
print(f"Current streak: {stats.current_streak}")
print(f"Longest win streak: {stats.longest_win_streak}")
```

### 5. Running Totals (models/game_result.py)

Real-time balance and performance tracking.

```python
from models.game_result import RunningTotals

totals = RunningTotals(initial_balance=1000)

# Update after each game
totals.update_balance(new_balance)

# Get summary
summary = totals.get_summary()
print(f"Current: ${summary['current_balance']:.2f}")
print(f"Peak: ${summary['peak_balance']:.2f}")
print(f"Drawdown: {summary['drawdown_percentage']:.1f}%")
print(f"ROI: {summary['roi_percentage']:.1f}%")
```

### 6. WinLossCalculator Service (services/win_loss_calculator.py)

Main orchestration service implementing all 6 use cases.

#### Initialization

```python
from services.win_loss_calculator import WinLossCalculator
from models.outcome_strategies import OutcomeStrategyType
from models.odds_configuration import OddsConfiguration, OddsType

# Create calculator  
calculator = WinLossCalculator(
    initial_balance=1000,
    outcome_strategy=OutcomeStrategyType.RANDOM,
    odds_configuration=OddsConfiguration(OddsType.FIXED, 2.0),
    house_edge=0.0
)
```

#### USE CASE 1: Determine Outcomes

```python
is_winner = calculator.determine_outcome(win_probability=0.5)
```

#### USE CASE 2 & 3: Calculate and Apply Results

```python
result = calculator.calculate_and_apply_result(
    bet_amount=100,
    win_probability=0.5,
    odds_value=None  # Optional override
)

print(result)  # GameResult object
print(result.outcome)  # "win" or "loss"
print(result.stake_after)  # New balance
```

#### USE CASE 4: Running Totals

```python
totals = calculator.get_running_totals()
print(f"Balance: ${totals['current_balance']:.2f}")
print(f"Change: ${totals['total_change']:+.2f}")
print(f"ROI: {totals['roi_percentage']:.1f}%")
```

#### USE CASE 5: Win/Loss Ratio

```python
ratios = calculator.compute_win_loss_ratio()
print(f"Win rate: {ratios['win_rate']:.1f}%")
print(f"Profit factor: {ratios['profit_factor']:.2f}x")
print(f"Net P&L: ${ratios['net_profit_loss']:.2f}")
```

#### USE CASE 6: Streak Tracking

```python
streaks = calculator.get_streak_info()
print(f"Current streak: {streaks['current_streak']}")
print(f"Longest win streak: {streaks['longest_win_streak']}")
print(f"Streak type: {streaks['streak_type']}")  # "winning", "losing", or "none"
```

#### Full Report

```python
report = calculator.get_full_report()
# Returns comprehensive summary with:
# - Game summary (total games, bets)
# - Outcomes (wins, losses, win rate)
# - Financial (won, lost, ROI, profit factor)
# - Balance tracking
# - Streaks
# - Extremes (largest win/loss, averages)
```

## Integration Examples

### Simple Game Loop

```python
calculator = WinLossCalculator(1000)

for i in range(10):
    result = calculator.calculate_and_apply_result(
        bet_amount=50,
        win_probability=0.5
    )
    print(f"Game {i+1}: {result.outcome}, Balance: ${result.stake_after:.2f}")

# Get final report
report = calculator.get_full_report()
print(json.dumps(report, indent=2))
```

### With Betting Service Integration

```python
# In betting_service.py
from services.win_loss_calculator import WinLossCalculator

class BettingService:
    def __init__(self):
        self.calculator = WinLossCalculator(
            initial_balance=1000,
            outcome_strategy=OutcomeStrategyType.HOUSE_EDGE,
            house_edge=0.02
        )
    
    def place_bet(self, bet_amount, win_probability):
        result = self.calculator.calculate_and_apply_result(
            bet_amount,
            win_probability
        )
        return result.to_dict()
    
    def get_stats(self):
        return self.calculator.get_full_report()
```

## Key Features

✅ **Multiple Outcome Strategies** - Random, weighted with house edge
✅ **Flexible Odds Systems** - Fixed, probability-based, American, decimal
✅ **Comprehensive Statistics** - 15+ different metrics
✅ **Real-time Tracking** - Running totals updated after each game
✅ **Streak Detection** - Automatic tracking of current and longest streaks
✅ **Balance History** - Complete progression tracking
✅ **Profit Factor Calculation** - Winnings to losses ratio
✅ **Performance Metrics** - Win rate, ROI, drawdown, and more

## Performance Considerations

- Statistics updated in O(1) after each game
- Balance history stored in list (linear memory)
- Suitable for 100s-1000s of games in session
- For 10,000+ games, consider archiving old data

## Error Handling

All methods include validation:
- Bet amount > 0
- Probability between 0-1
- Bet ≤ current balance
- Proper exception messages
- Comprehensive logging

## Logging

- DEBUG: Detailed calculation logs
- INFO: Game outcomes and major milestones
- ERROR: Exceptions and validation failures

