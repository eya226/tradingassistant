import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.indicators import calculate_sma, calculate_rsi, calculate_macd

@pytest.fixture
def sample_stock_data():
    """Fixture to create a sample DataFrame of stock prices."""
    data = {
        'Close': [
            150.0, 152.5, 155.0, 153.0, 156.5, 158.0, 160.2, 159.5, 162.0, 163.5,
            161.0, 163.0, 165.5, 164.0, 166.5, 168.0, 170.5, 169.0, 172.0, 173.5,
            171.0, 173.0, 175.5, 174.0, 176.5, 178.0, 180.5, 179.0, 182.0, 183.5
        ]
    }
    return pd.DataFrame(data)

def test_calculate_sma(sample_stock_data):
    """Test the SMA calculation."""
    window = 5
    sma = calculate_sma(sample_stock_data['Close'], window)

    # The first 4 values should be NaN
    assert sma.isnull().sum() == window - 1
    # Manually calculate the 5th value
    expected_sma_5 = sample_stock_data['Close'].iloc[:5].mean()
    assert np.isclose(sma.iloc[4], expected_sma_5)
    # Check last value
    expected_sma_last = sample_stock_data['Close'].iloc[-5:].mean()
    assert np.isclose(sma.iloc[-1], expected_sma_last)

def test_calculate_rsi(sample_stock_data):
    """Test the RSI calculation."""
    rsi = calculate_rsi(sample_stock_data['Close'], window=14)

    # RSI will have NaNs at the beginning
    assert rsi.isnull().sum() > 0
    # Check that RSI values are within the 0-100 range
    assert rsi.dropna().between(0, 100).all()
    # A simple check on the last value. For this data, prices are mostly increasing, so RSI should be high.
    assert rsi.iloc[-1] > 70

def test_calculate_macd(sample_stock_data):
    """Test the MACD calculation."""
    macd_line, signal_line, histogram = calculate_macd(sample_stock_data['Close'])

    # Check that all three Series are returned and have the same index
    assert isinstance(macd_line, pd.Series)
    assert isinstance(signal_line, pd.Series)
    assert isinstance(histogram, pd.Series)
    assert macd_line.index.equals(signal_line.index)
    assert macd_line.index.equals(histogram.index)

    # Check the relationship: histogram should be macd_line - signal_line
    assert np.allclose(histogram.dropna(), (macd_line - signal_line).dropna())
    # Check one of the later values for a basic sanity check
    assert macd_line.iloc[-1] > 0 # Prices are trending up, so MACD should be positive
    assert signal_line.iloc[-1] > 0
