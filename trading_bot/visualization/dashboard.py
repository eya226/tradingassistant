import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.data_handler import get_data
from analysis.indicators import calculate_sma, calculate_rsi, calculate_macd
from analysis.strategy import generate_signals
from analysis.backtester import run_backtest

# Initialize the Dash app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# --- App Layout ---
app.layout = dbc.Container(
    fluid=True,
    className="dashboard-container",
    children=[
        html.H1("Algorithmic Trading Bot Dashboard", className="text-center mb-4"),

        dbc.Row([
            dbc.Col(dbc.Input(id='stock-ticker-input', placeholder='Enter Stock Ticker (e.g., AAPL)...', type='text', value='AAPL'), width=9),
            dbc.Col(dbc.Button("Run Backtest", id='run-backtest-button', color="primary", className="w-100"), width=3),
        ], className="mb-4", justify="center"),

        dcc.Loading(id="loading-spinner", type="default", children=[
            html.Div(id='metrics-output'),
            html.Div(id='graphs-output')
        ]),
    ]
)

# --- Callback to run backtest and update dashboard ---
@app.callback(
    [Output('metrics-output', 'children'),
     Output('graphs-output', 'children')],
    [Input('run-backtest-button', 'n_clicks')],
    [State('stock-ticker-input', 'value')]
)
def update_dashboard(n_clicks, ticker):
    if n_clicks is None or not ticker:
        return html.Div(), html.Div()

    start_date = '2020-01-01'
    end_date = '2023-01-01'
    stock_data = get_data(ticker, start_date, end_date)

    if stock_data is None:
        return html.Div(f"Could not retrieve data for {ticker}.", className="text-danger text-center"), html.Div()

    # --- Calculations ---
    stock_data['SMA_50'] = calculate_sma(stock_data['Close'], 50)
    stock_data['RSI'] = calculate_rsi(stock_data['Close'])
    stock_data['MACD'], stock_data['Signal_Line'], _ = calculate_macd(stock_data['Close'])
    stock_data_with_signals = generate_signals(stock_data.copy())
    portfolio, metrics = run_backtest(stock_data_with_signals)

    # --- Create Visualizations ---

    # Chart 1: Stock Analysis
    fig_stock = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                              subplot_titles=(f'{ticker.upper()} Stock Analysis', 'RSI Oscillator'),
                              row_heights=[0.7, 0.3])

    fig_stock.add_trace(go.Candlestick(x=stock_data.index,
                                     open=stock_data['Open'], high=stock_data['High'],
                                     low=stock_data['Low'], close=stock_data['Close'],
                                     name='Price'), row=1, col=1)

    fig_stock.add_trace(go.Scatter(x=stock_data.index, y=stock_data['SMA_50'], mode='lines', name='SMA 50', line=dict(color='orange', width=1, dash='dash')), row=1, col=1)

    buy_signals = stock_data_with_signals[stock_data_with_signals['Signal'] == 1]
    sell_signals = stock_data_with_signals[stock_data_with_signals['Signal'] == -1]
    fig_stock.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='Buy Signal',
                                 marker=dict(color='#00FF00', size=12, symbol='triangle-up', line=dict(width=1, color='white'))), row=1, col=1)
    fig_stock.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', name='Sell Signal',
                                  marker=dict(color='#FF4136', size=12, symbol='triangle-down', line=dict(width=1, color='white'))), row=1, col=1)

    fig_stock.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI'], mode='lines', name='RSI', line=dict(color='cyan', width=1)), row=2, col=1)
    fig_stock.add_hline(y=70, line_dash="dash", line_color="#FF4136", row=2, col=1)
    fig_stock.add_hline(y=30, line_dash="dash", line_color="#00FF00", row=2, col=1)

    fig_stock.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                              xaxis_rangeslider_visible=False)

    # Chart 2: Portfolio Equity Curve with "Glow"
    fig_portfolio = go.Figure()
    # Background "glow" line
    fig_portfolio.add_trace(go.Scatter(x=portfolio.index, y=portfolio['Total'], mode='lines',
                                     line=dict(color='#00FF00', width=10, shape='spline'),
                                     opacity=0.3, name='Glow'))
    # Foreground line
    fig_portfolio.add_trace(go.Scatter(x=portfolio.index, y=portfolio['Total'], mode='lines',
                                     line=dict(color='#00FF00', width=3, shape='spline'),
                                     name='Portfolio Value'))

    fig_portfolio.update_layout(title='Portfolio Equity Curve', template='plotly_dark',
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                xaxis_title='Date', yaxis_title='Portfolio Value ($)')

    # --- Assemble Output Components ---
    metrics_display = dbc.Card(
        className="glass-card",
        body=True,
        children=[
            dbc.Row([
                dbc.Col(html.Div([html.H4("Total P/L", className="metric-label"), html.P(f"${metrics['Total P/L']:.2f}", className="metric-value positive-metric" if metrics['Total P/L'] >= 0 else "metric-value negative-metric")]), md=4, className="text-center"),
                dbc.Col(html.Div([html.H4("Number of Trades", className="metric-label"), html.P(f"{int(metrics['Number of Trades'])}", className="metric-value neutral-metric")]), md=4, className="text-center"),
                dbc.Col(html.Div([html.H4("Max Drawdown", className="metric-label"), html.P(f"{metrics['Maximum Drawdown (%)']:.2f}%", className="metric-value negative-metric")]), md=4, className="text-center"),
            ])
        ]
    )

    graphs_display = html.Div([
        dbc.Card(className="glass-card", body=True, children=[dcc.Graph(figure=fig_stock, config={'displayModeBar': False})]),
        dbc.Card(className="glass-card", body=True, children=[dcc.Graph(figure=fig_portfolio, config={'displayModeBar': False})])
    ])

    return metrics_display, graphs_display

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)
