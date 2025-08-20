import pandas as pd
import numpy as np

def run_backtest(data, initial_capital=100000, shares_per_trade=10):
    """
    Runs a backtest on the given data and trading signals.

    Args:
        data (pd.DataFrame): DataFrame with price data and a 'Signal' column.
        initial_capital (float): The starting capital for the backtest.
        shares_per_trade (int): The number of shares to trade on each signal.

    Returns:
        tuple: A tuple containing:
               - pd.DataFrame: A DataFrame with the portfolio's history.
               - dict: A dictionary with performance metrics.
    """
    # Determine the number of shares held over time
    positions = data['Signal'].cumsum() * shares_per_trade

    # Create a portfolio DataFrame to track performance
    portfolio = pd.DataFrame(index=data.index)

    # Calculate the value of stock holdings
    portfolio['Holdings'] = positions * data['Close']

    # Calculate cash flow from trades
    position_changes = positions.diff().fillna(0)
    trade_costs = position_changes * data['Close']
    portfolio['Cash'] = initial_capital - trade_costs.cumsum()

    # Calculate total portfolio value
    portfolio['Total'] = portfolio['Cash'] + portfolio['Holdings']

    # Calculate portfolio returns
    portfolio['Returns'] = portfolio['Total'].pct_change().fillna(0)

    # --- Performance Metrics ---
    total_pnl = portfolio['Total'].iloc[-1] - initial_capital
    if initial_capital == 0:
        total_return_pct = 0.0
    else:
        total_return_pct = (total_pnl / initial_capital) * 100

    num_trades = data['Signal'].abs().sum() / 2

    # Max Drawdown Calculation
    cumulative_returns = (1 + portfolio['Returns']).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()

    metrics = {
        'Total P/L': total_pnl,
        'Total P/L (%)': total_return_pct,
        'Number of Trades': num_trades,
        'Maximum Drawdown (%)': max_drawdown * 100
    }

    return portfolio, metrics

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.data_handler import get_data
    from analysis.indicators import calculate_macd
    from analysis.strategy import generate_signals

    ticker = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2023-01-01'

    # 1. Get Data
    stock_data = get_data(ticker, start_date, end_date)

    if stock_data is not None:
        # 2. Calculate Indicators
        stock_data['MACD'], stock_data['Signal_Line'], _ = calculate_macd(stock_data['Close'])

        # 3. Generate Signals
        stock_data_with_signals = generate_signals(stock_data)

        # 4. Run Backtest
        portfolio, metrics = run_backtest(stock_data_with_signals)

        # 5. Print Results
        print(f"Backtest Results for {ticker}")
        print("---------------------------------")
        for key, value in metrics.items():
            print(f"{key}: {value:.2f}")
        print("---------------------------------")

        print("\nFinal Portfolio Snapshot:")
        print(portfolio.tail())
    else:
        print(f"Could not run backtest for {ticker}.")
