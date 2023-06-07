import os
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect, KiteTicker
from dotenv import load_dotenv
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

load_dotenv("brokers.env")

def read_brokers_env():
    subscribed_users = []
    for key, value in os.environ.items():
        if key.startswith("kite_api_key_"):
            username = key.split("_")[-1]
            subscribed_users.append(username)
    return subscribed_users

def create_kiteTicker_instance(username):
    api_key = os.getenv(f"kite_api_key_{username}")
    api_secret = os.getenv(f"kite_api_sec_{username}")
    access_token = os.getenv(f"kite_access_tkn_{username}")

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    kws = KiteTicker(api_key, access_token)
    return kws

def sma_crossover_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0.0

    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()

    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()

    return signals

def plot_graph(data, signals):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=data.index, y=signals['short_mavg'], mode='lines', name='Short Moving Average'))
    fig.add_trace(go.Scatter(x=data.index, y=signals['long_mavg'], mode='lines', name='Long Moving Average'))

    fig.add_trace(go.Scatter(x=signals[signals.positions == 1.0].index, y=data.loc[signals.positions == 1.0].Close, mode='markers', name='Buy', marker=dict(color='green', size=10, symbol='circle')))
    fig.add_trace(go.Scatter(x=signals[signals.positions == -1.0].index, y=data.loc[signals.positions == -1.0].Close, mode='markers', name='Sell', marker=dict(color='red', size=10, symbol='circle')))

    fig.update_layout(title='SMA Crossover Strategy', xaxis_title='Date', yaxis_title='Price')

    return fig

def main():
    subscribed_users = read_brokers_env()

    for username in subscribed_users:
        kws = create_kiteTicker_instance(username)

        # Fetch historical data and calculate signals
        data = pd.DataFrame(kws.historical_data(256265, "2021-01-01", "2021-12-31", "day", "full"))
        data.set_index('date', inplace=True)
        signals = sma_crossover_strategy(data, 5, 20)

        # Plot the graph
        fig = plot_graph(data, signals)

        # Create a Dash app to display the graph
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Graph(id='live_plot', figure=fig)
        ])

        if __name__ == '__main__':
            app.run_server(debug=True)

main()