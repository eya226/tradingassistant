import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.strategy import generate_signals
from analysis.backtester import run_backtest

@pytest.fixture
def sample_backtest_data():
    """Fixture to create a sample DataFrame for backtesting."""
    data = {
        'Close': [100, 105, 110, 108, 104, 106, 112, 115, 113, 110],
        'MACD':        [-0.5, -0.2,  0.1,  0.3,  0.2, -0.1, -0.3,  0.2,  0.4,  0.1],
        'Signal_Line': [-0.3, -0.25, 0.0,  0.1,  0.15, 0.0, -0.2,  0.0,  0.2,  0.15]
    }
    return pd.DataFrame(data, index=pd.to_datetime(pd.date_range('2023-01-01', periods=10)))

def test_generate_signals(sample_backtest_data):
    """Test the signal generation logic."""
    data = generate_signals(sample_backtest_data)
    signals = data['Signal']

    assert isinstance(signals, pd.Series)
    assert signals.isin([-1, 0, 1]).all()
    # Check for specific expected signals based on the fixture data
    # Buy signal at index 1 (MACD crosses above Signal_Line)
    assert signals.iloc[1] == 1
    # Sell signal at index 5 (MACD crosses below Signal_Line)
    assert signals.iloc[5] == -1
    # Another buy signal at index 7
    assert signals.iloc[7] == 1
    # Check that other signals are 0
    assert signals.iloc[0] == 0
    assert signals.iloc[2] == 0

def test_run_backtest_simple_trade():
    """Test backtester with a single profitable trade."""
    data = pd.DataFrame({
        'Close':       [100, 110, 120, 115],
        'Signal':      [  0,   1,  -1,   0] # Buy at 110, Sell at 120
    }, index=pd.to_datetime(pd.date_range('2023-01-01', periods=4)))

    initial_capital = 10000
    shares_per_trade = 10
    portfolio, metrics = run_backtest(data, initial_capital, shares_per_trade)

    # Expected P/L = (120 - 110) * 10 = 100
    assert np.isclose(metrics['Total P/L'], 100.0)
    assert metrics['Number of Trades'] == 1
    # Final portfolio value should be initial capital + P/L
    assert np.isclose(portfolio['Total'].iloc[-1], initial_capital + 100)

def test_run_backtest_no_trades():
    """Test backtester when no signals are generated."""
    data = pd.DataFrame({
        'Close':  [100, 105, 110, 108],
        'Signal': [0, 0, 0, 0]
    }, index=pd.to_datetime(pd.date_range('2023-01-01', periods=4)))

    initial_capital = 50000
    portfolio, metrics = run_backtest(data, initial_capital)

    assert metrics['Total P/L'] == 0
    assert metrics['Number of Trades'] == 0
    assert metrics['Maximum Drawdown (%)'] == 0
    assert portfolio['Total'].iloc[-1] == initial_capital

def test_backtest_metrics(sample_backtest_data):
    """Test the performance metrics calculation in a more complex scenario."""
    data = generate_signals(sample_backtest_data)
    _, metrics = run_backtest(data, initial_capital=100000, shares_per_trade=10)

    # Basic sanity checks for the metrics
    assert 'Total P/L' in metrics
    assert 'Total P/L (%)' in metrics
    assert 'Number of Trades' in metrics
    assert 'Maximum Drawdown (%)' in metrics

    # In this scenario:
    # 1. Buy at 105 (price at index 1)
    # 2. Sell at 106 (price at index 5). Profit = 10 * (106-105) = +10
    # 3. Buy at 115 (price at index 7). Held to end.
    # 4. Final price is 110. Unrealized P/L = 10 * (110-115) = -50
    # Total P/L = +10 (realized) - 50 (unrealized) = -40
    assert np.isclose(metrics['Total P/L'], -40)
    # There are 4 signals (at indices 1, 5, 7, 9), so 2 full trades.
    assert metrics['Number of Trades'] == 2.0
    assert metrics['Maximum Drawdown (%)'] < 0 # Should be some drawdown
    assert metrics['Maximum Drawdown (%)'] > -1 # Should not be a total loss
