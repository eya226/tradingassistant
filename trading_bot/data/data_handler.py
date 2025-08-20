import yfinance as yf
import pandas as pd

def get_data(ticker, start_date, end_date):
    """
    Downloads historical stock data from Yahoo Finance.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date for the data in 'YYYY-MM-DD' format.
        end_date (str): The end date for the data in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the historical stock data
                          (Open, High, Low, Close, Volume), or None if the
                          download fails.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            print(f"No data found for ticker {ticker} from {start_date} to {end_date}.")
            return None

        # If columns are multi-indexed (e.g. ('Close', 'AAPL')), flatten them for a single ticker
        if isinstance(data.columns, pd.MultiIndex):
            if len(data.columns.get_level_values(1).unique()) == 1:
                 data.columns = data.columns.droplevel(1)

        # Basic data cleaning: drop rows with any missing values
        data.dropna(inplace=True)
        return data
    except Exception as e:
        print(f"An error occurred while downloading data for {ticker}: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    ticker_symbol = 'AAPL'
    start = '2020-01-01'
    end = '2023-01-01'
    stock_data = get_data(ticker_symbol, start, end)
    if stock_data is not None:
        print(f"Successfully downloaded data for {ticker_symbol}.")
        print("First 5 rows:")
        print(stock_data.head())
        print("\nLast 5 rows:")
        print(stock_data.tail())
    else:
        print(f"Failed to download data for {ticker_symbol}.")
