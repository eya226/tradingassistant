import pandas as pd
import numpy as np

def calculate_sma(data, window):
    """
    Calculates the Simple Moving Average (SMA).

    Args:
        data (pd.Series): A pandas Series of prices.
        window (int): The window size for the moving average.

    Returns:
        pd.Series: A pandas Series with the SMA values.
    """
    return data.rolling(window=window).mean()

def calculate_rsi(data, window=14):
    """
    Calculates the Relative Strength Index (RSI).

    Args:
        data (pd.Series): A pandas Series of prices.
        window (int): The window size for RSI calculation.

    Returns:
        pd.Series: A pandas Series with the RSI values.
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, slow_window=26, fast_window=12, signal_window=9):
    """
    Calculates the Moving Average Convergence Divergence (MACD).

    Args:
        data (pd.Series): A pandas Series of prices.
        slow_window (int): The window for the slow EMA.
        fast_window (int): The window for the fast EMA.
        signal_window (int): The window for the signal line.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing the MACD line,
                                                 the signal line, and the histogram.
    """
    fast_ema = data.ewm(span=fast_window, adjust=False).mean()
    slow_ema = data.ewm(span=slow_window, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

if __name__ == '__main__':
    # To test the indicators, we first need to get some data.
    # We can reuse the get_data function from our data_handler.
    # To do this, we need to make sure the trading_bot directory is in the Python path.
    import sys
    import os
    # Add the parent directory to the path to allow imports from other modules
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data.data_handler import get_data

    ticker_symbol = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    stock_data = get_data(ticker_symbol, start_date, end_date)

    if stock_data is not None:
        close_prices = stock_data['Close']

        # Calculate and display SMA
        stock_data['SMA_50'] = calculate_sma(close_prices, 50)
        print("SMA_50 calculated:")
        print(stock_data[['Close', 'SMA_50']].tail())

        # Calculate and display RSI
        stock_data['RSI'] = calculate_rsi(close_prices)
        print("\nRSI calculated:")
        print(stock_data[['Close', 'RSI']].tail())

        # Calculate and display MACD
        stock_data['MACD'], stock_data['Signal_Line'], stock_data['Histogram'] = calculate_macd(close_prices)
        print("\nMACD calculated:")
        print(stock_data[['Close', 'MACD', 'Signal_Line', 'Histogram']].tail())
    else:
        print(f"Could not retrieve data for {ticker_symbol} to test indicators.")
