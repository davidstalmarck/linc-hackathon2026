# Trading Algorithm Simulator

A Python-based trading simulation framework for testing and visualizing algorithmic trading strategies.

## Installation

### Step 1: Install `uv` (Package Manager)

`uv` is a fast Python package manager. Install it for your platform:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

### Step 2: Install Dependencies

Navigate to the project directory and install all required packages:

```bash
uv sync
```

This will install:
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `matplotlib` - Plotting and visualization
- `jupyter` - Interactive notebooks

**Note:** If you don't have a `pyproject.toml` or prefer manual installation:
```bash
uv pip install pandas numpy matplotlib jupyter
```

## Quick Start

### Option 1: Full Run (Recommended for Quick Results)

Run the complete simulation with visualization:

```bash
uv run create_data.py   # Generate price data
uv run algorithm.py      # Run strategy and generate plots
```

This will:
- Execute the Moving Average Crossover strategy
- Generate `orders.csv` (all trades)
- Generate `portfolio.csv` (daily portfolio snapshots)
- Create `performance_plot.png` (comprehensive visualization)
- Display performance metrics (Sharpe ratio, profit/loss, etc.)

### Option 2: Interactive Exploration (Recommended for Learning)

Walk through the simulation step-by-step:

```bash
jupyter notebook algorithm.ipynb
```

The notebook contains:
- A suggested Moving Average (MA) crossover algorithm
- Step-by-step data exploration
- Interactive signal generation
- Portfolio simulation with the `TradingSimulator` class

Run each cell to understand how the framework works before building your own strategy.

## Files Overview

- **`create_data.py`** - Generates synthetic stock price data (`prices.csv`)
- **`algorithm.py`** - Complete trading strategy implementation (MA crossover example)
- **`algorithm.ipynb`** - Interactive Jupyter notebook for learning and experimentation
- **`trading_simulator.py`** - Core simulation engine (DO NOT MODIFY - see below)

## Generated Outputs

- **`prices.csv`** - Daily stock prices (Date, AAPL, GOOGL, MSFT, TSLA)
- **`orders.csv`** - Trade execution history (Date, Ticker, Action, Shares, Price, Total)
- **`portfolio.csv`** - Daily portfolio snapshots (Date, Cash, Holdings, Total Value)
- **`performance_plot.png`** - 4-panel visualization:
  - Portfolio vs individual stock performance (normalized)
  - Rolling Sharpe ratio over time
  - Cumulative profit/loss over time
  - Trade execution points

## Building Your Own Strategy

### Important: Do NOT Edit `trading_simulator.py`

The `TradingSimulator` class in `trading_simulator.py` is the **original reference implementation**.

**To customize the simulator:**

1. Create `custom_trading_simulator.py`
2. Define your `CustomTradingSimulator` class
3. Extend or modify the original `TradingSimulator`
4. Use your custom class in your algorithms

Example:
```python
from trading_simulator import TradingSimulator

class CustomTradingSimulator(TradingSimulator):
    def __init__(self, stocks, initial_cash=100000):
        super().__init__(stocks, initial_cash)
        # Add your custom initialization

    def execute_trade(self, date, ticker, signal, price):
        # Add your custom trading logic
        # e.g., dynamic position sizing, stop losses, etc.
        return super().execute_trade(date, ticker, signal, price)
```

### Modifying the Trading Strategy

Edit `algorithm.py` or create a new file to implement your strategy:

```python
def your_strategy(prices, **params):
    """Your custom trading strategy"""
    # Generate signals: 1 = Buy, -1 = Sell, 0 = Hold
    signals = pd.Series(0, index=prices.index)

    # Your logic here

    return signals
```

## Performance Metrics

The simulator automatically calculates:

- **Sharpe Ratio**: Risk-adjusted returns (>1 is good, >2 is excellent)
- **Net Profit/Loss**: Total gain/loss in dollars and percentage
- **Rolling Sharpe**: 30-day rolling Sharpe ratio for time-series analysis
- **Cumulative P/L**: Profit/loss evolution over time


## Tips

- Start with the notebook (`algorithm.ipynb`) to understand the data flow
- Test your strategy on different time periods by regenerating data
- Use the visualization to identify when your strategy performs well/poorly
- Keep `trading_simulator.py` unchanged for consistency across experiments

Good luck building your trading strategy! 📈