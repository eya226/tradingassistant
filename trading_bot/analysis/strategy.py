import pandas as pd

def generate_signals(data):
    """
    Generates trading signals based on the MACD indicator.

    Args:
        data (pd.DataFrame): A DataFrame with at least 'MACD' and 'Signal_Line' columns.

    Returns:
        pd.DataFrame: The input DataFrame with a new 'Signal' column.
                      -  1: Buy signal
                      - -1: Sell signal
                      -  0: No signal
    """
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0

    # Generate buy signals
    signals.loc[(data['MACD'] > data['Signal_Line']) & (data['MACD'].shift(1) <= data['Signal_Line'].shift(1)), 'Signal'] = 1

    # Generate sell signals
    signals.loc[(data['MACD'] < data['Signal_Line']) & (data['MACD'].shift(1) >= data['Signal_Line'].shift(1)), 'Signal'] = -1

    data['Signal'] = signals['Signal']
    return data
