import pytest
import pandas as pd
from unittest.mock import MagicMock
import sys
import os

# Add the parent directory to the path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.data_handler import get_data

@pytest.fixture
def mock_yfinance(mocker):
    """Fixture to mock the yfinance.download function."""
    return mocker.patch('yfinance.download')

def test_get_data_success(mock_yfinance):
    """Test successful data retrieval and processing."""
    # Create a sample DataFrame that yfinance.download might return
    mock_df = pd.DataFrame({
        ('Open', 'AAPL'): [100, 101],
        ('High', 'AAPL'): [102, 103],
        ('Low', 'AAPL'): [99, 100],
        ('Close', 'AAPL'): [101, 102],
        ('Volume', 'AAPL'): [1000, 1100]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
    mock_yfinance.return_value = mock_df

    # Call the function under test
    result_df = get_data('AAPL', '2023-01-01', '2023-01-02')

    # Assertions
    mock_yfinance.assert_called_once_with('AAPL', start='2023-01-01', end='2023-01-02', progress=False)
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    # Check that columns are flattened
    assert all(col in result_df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    assert result_df.shape == (2, 5)

def test_get_data_failure_empty(mock_yfinance):
    """Test the case where yfinance returns an empty DataFrame."""
    mock_yfinance.return_value = pd.DataFrame()

    result_df = get_data('INVALID', '2023-01-01', '2023-01-02')

    assert result_df is None
    mock_yfinance.assert_called_once_with('INVALID', start='2023-01-01', end='2023-01-02', progress=False)

def test_get_data_exception(mock_yfinance):
    """Test the case where yfinance raises an exception."""
    mock_yfinance.side_effect = Exception("Network error")

    result_df = get_data('AAPL', '2023-01-01', '2023-01-02')

    assert result_df is None

def test_get_data_with_na(mock_yfinance):
    """Test that rows with NaN values are dropped."""
    mock_df = pd.DataFrame({
        ('Open', 'AAPL'): [100, 101, 102],
        ('High', 'AAPL'): [102, 103, 104],
        ('Low', 'AAPL'): [99, 100, 101],
        ('Close', 'AAPL'): [101, pd.NA, 103],
        ('Volume', 'AAPL'): [1000, 1100, 1200]
    })
    mock_yfinance.return_value = mock_df

    result_df = get_data('AAPL', '2023-01-01', '2023-01-03')

    assert result_df is not None
    assert result_df.shape[0] == 2 # Expecting the row with NA to be dropped
    assert result_df['Close'].isnull().sum() == 0
