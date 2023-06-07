import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Load data
def load_data(file_name):
    return pd.read_csv(file_name)

# Strategy selection
strategy = st.selectbox(
    'Select Strategy',
    ('SMACrossover', 'GoldenRatio')
)

# Account selection
account = st.selectbox(
    'Select Account',
    ('Signals', 'YY0222', 'BY1424')
)

# Load the appropriate data based on selections
if account == 'Signals':
    data = load_data(f"{strategy}_Signal.csv")
else:
    data = load_data(f"{strategy}_{account}.csv")

# Display the data
st.dataframe(data)

import plotly.graph_objects as go

# Convert 'Date' to datetime
data['Date'] = pd.to_datetime(data['Date'], format='%d-%b')

# Line plot for 'NetPnL' over time
st.line_chart(data.set_index('Date')['NetPnL'])

# Calculate running total of 'NetPnL'
data['Cumulative NetPnL'] = data['NetPnL'].cumsum()

# Calculate underwater curve (drawdown)
data['Underwater'] = data['Cumulative NetPnL'].cummax() - data['Cumulative NetPnL']

# Underwater plot using Plotly
fig = go.Figure(data=[
    go.Scatter(name='Underwater', x=data['Date'], y=data['Underwater'], fill='tonexty', line_color='indianred'),
    go.Scatter(name='NetPnL', x=data['Date'], y=data['Cumulative NetPnL'], line_color='deepskyblue'),
])
fig.update_layout(title='Underwater Plot', xaxis_title='Date', yaxis_title='Value')
st.plotly_chart(fig)

# Convert 'Date' to datetime
data['Date'] = pd.to_datetime(data['Date'], format='%d-%b')

# Line plot for 'NetPnL' over time
st.line_chart(data.set_index('Date')['NetPnL'])

# Calculate running total of 'NetPnL'
data['Cumulative NetPnL'] = data['NetPnL'].cumsum()

# Calculate underwater curve (drawdown)
data['Underwater'] = data['Cumulative NetPnL'].cummax() - data['Cumulative NetPnL']

# Underwater plot using Plotly
fig = go.Figure(data=[
    go.Scatter(name='Underwater', x=data['Date'], y=data['Underwater'], fill='tonexty', line_color='indianred'),
    go.Scatter(name='NetPnL', x=data['Date'], y=data['Cumulative NetPnL'], line_color='deepskyblue'),
])
fig.update_layout(title='Underwater Plot', xaxis_title='Date', yaxis_title='Value')
st.plotly_chart(fig)

def calculate_stats(file_name):
    # Read the CSV data
    data = pd.read_csv(file_name, sep="\t")

    # Calculate statistics
    allocated_capital = 1000000  # As per your requirement
    num_trading_days = len(data['Date'].unique())
    num_trades = len(data)
    gross_profit = data['Gross PnL'].sum()
    charges = data['Taxes'].abs().sum()  # Assuming taxes are the charges
    net_profit = data['NetPnL'].sum()
    returns = (net_profit / allocated_capital) * 100
    annualized_returns = (1 + net_profit / allocated_capital) ** (252/num_trading_days) - 1
    max_profit = data['NetPnL'].max()
    max_loss = data['NetPnL'].min()

    # Calculating win and loss days
    daily_pnl = data.groupby('Date')['NetPnL'].sum()
    num_win_days = len(daily_pnl[daily_pnl > 0])
    num_loss_days = len(daily_pnl[daily_pnl < 0])

    # Calculate max drawdown
    cumulative_pnl = daily_pnl.cumsum()
    running_max = np.maximum.accumulate(cumulative_pnl)
    drawdown = (running_max - cumulative_pnl) / running_max
    max_drawdown = drawdown.max() * 100

    # Calculate winning accuracy
    num_winning_trades = len(data[data['NetPnL'] > 0])
    winning_accuracy = (num_winning_trades / num_trades) * 100

    # Create stats dictionary
    stats = {
        "Allocated Capital": allocated_capital,
        "Number of trading days": num_trading_days,
        "Number of trades": num_trades,
        "Number of win days": num_win_days,
        "Number of loss days": num_loss_days,
        "Gross Profit": gross_profit,
        "Charges": charges,
        "Net Profit": net_profit,
        "Returns (%)": returns,
        "Annualized (%)": annualized_returns * 100,
        "Max Profit": max_profit,
        "Max Loss": max_loss,
        "Max Drawdown from Peak (%)": max_drawdown,
        "Winning Accuracy(%)": winning_accuracy,
    }
    
    return stats

stats = calculate_stats("SMACrossover_YY0222.csv")

# Display statistics in Streamlit
for key, value in stats.items():
    st.markdown(f"**{key}:** {value:,.2f}")
