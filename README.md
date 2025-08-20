# Algorithmic Trading Bot and Backtesting Dashboard

## Project Overview

This project is a comprehensive algorithmic trading bot that includes data acquisition, technical indicator calculation, a backtesting engine, and an interactive web-based dashboard for visualization. It is designed to allow users to test and analyze trading strategies on historical stock data.

## Features

- **Data Acquisition:** Downloads daily historical stock data (Open, High, Low, Close, Volume) for any given ticker using the `yfinance` library.
- **Data Processing:** Cleans and prepares the data for analysis using the `pandas` library.
- **Technical Indicators:** Calculates three key technical indicators from scratch using `pandas` and `numpy`:
    - Simple Moving Average (SMA)
    - Relative Strength Index (RSI)
    - Moving Average Convergence Divergence (MACD)
- **Backtesting Engine:** A robust engine that simulates a trading strategy on historical data. It calculates critical performance metrics, including:
    - Total Profit/Loss (P/L)
    - Number of Trades
    - Maximum Drawdown
- **Interactive Dashboard:** A web application built with **Plotly** and **Dash** that provides a user-friendly interface to:
    - Enter a stock ticker.
    - Run a backtest with the click of a button.
    - Visualize the stock's price action with buy/sell signals overlaid.
    - Analyze the portfolio's equity curve over time.
    - View key performance metrics in a clean, high-tech interface.
- **Unit Tests:** The project is supported by a suite of unit tests written with `pytest` to ensure the core logic is reliable and accurate.

## Tech Stack

- **Language:** Python
- **Libraries:**
    - `pandas` & `numpy` for data manipulation and analysis.
    - `yfinance` for financial data.
    - `plotly` & `dash` for the interactive web dashboard.
    - `pytest` for unit testing.

## Installation & Usage

To run the dashboard on your local machine, follow these steps:

1.  **Prerequisites:** Ensure you have Python 3 installed.
2.  **Clone the repository and navigate to the project directory.**
3.  **(Recommended) Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # On Windows: venv\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install yfinance pandas dash dash-bootstrap-components plotly
    ```
5.  **Run the application:**
    ```bash
    python3 trading_bot/visualization/dashboard.py
    ```
6.  **Open your web browser** and navigate to the URL shown in your terminal (usually `http://127.0.0.1:8050/`).

## Methodology

The default trading strategy implemented is a **MACD Crossover Strategy**:
-   A **BUY** signal is generated when the MACD line crosses above the Signal line.
-   A **SELL** signal is generated when the MACD line crosses below the Signal line.

This strategy is implemented in `trading_bot/analysis/strategy.py`. The backtesting engine is designed to be modular, so this strategy can easily be replaced with a more complex one.

## Future Work

-   Implement more complex, multi-indicator trading strategies.
-   Allow users to configure strategy parameters (e.g., indicator windows, stop-loss/take-profit levels) from the dashboard.
-   Expand the backtesting engine to handle multiple assets simultaneously.
-   Add more advanced performance metrics (e.g., Sharpe Ratio, Sortino Ratio).
