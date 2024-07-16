import pandas as pd
import numpy as np
import random
from datetime import datetime

def getTickerPrice(ticker: str, date: pd.Timestamp) -> float:
    random.seed(0)
    return random.uniform(300, 400)

def calculate_max_drawdown(cumulative_values):
    peaks = cumulative_values.cummax()
    drawdowns = (peaks - cumulative_values) / np.abs(peaks)
    max_drawdown = drawdowns.max() * 100
    return max_drawdown

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    excess_returns = returns - risk_free_rate
    sharpe_ratio = excess_returns.mean() / excess_returns.std()
    return sharpe_ratio

def calculate_trade_performance(trades, market_data, risk_free_rate=0.01):
    trades['Size'] = trades['Size'].fillna(1)
    trades['Long_Short'] = trades['Side'].apply(lambda x: 1 if x == 'buy' else -1)
    trades['Trade_Value'] = trades['Size'] * trades['Price']

    # Sort trades by date
    trades = trades.sort_values(by='Date').reset_index(drop=True)
    all_dates = trades['Date'].unique()
    print(trades)
    open_long_positions = []
    open_short_positions = []
    closed_profits = []
    daily_portfolio_values = {}

    for current_date in all_dates:
        current_trades = trades[trades['Date'] == current_date]
        print('Current Trades\n', current_trades)
        for _, row in current_trades.iterrows():
            if row['Long_Short'] == 1:  # Buy
                remaining_size = row['Size']
                while remaining_size > 0 and open_short_positions:
                    short_size, short_price = open_short_positions.pop(0)
                    if short_size <= remaining_size:
                        profit = (short_price - row['Price']) * short_size
                        closed_profits.append(profit)
                        remaining_size -= short_size
                    else:
                        profit = (short_price - row['Price']) * remaining_size
                        closed_profits.append(profit)
                        open_short_positions.insert(0, (short_size - remaining_size, short_price))
                        remaining_size = 0
                if remaining_size > 0:
                    open_long_positions.append((remaining_size, row['Price']))
            else:  # Sell
                remaining_size = row['Size']
                while remaining_size > 0 and open_long_positions:
                    long_size, long_price = open_long_positions.pop(0)
                    if long_size <= remaining_size:
                        profit = (row['Price'] - long_price) * long_size
                        closed_profits.append(profit)
                        remaining_size -= long_size
                    else:
                        profit = (row['Price'] - long_price) * remaining_size
                        closed_profits.append(profit)
                        open_long_positions.insert(0, (long_size - remaining_size, long_price))
                        remaining_size = 0
                if remaining_size > 0:
                    open_short_positions.append((remaining_size, row['Price']))

        # Calculate the portfolio value for the current date
            portfolio_value = sum((getTickerPrice(row['Symbol'], current_date) - price) * size for size, price in open_long_positions) + \
                          sum((price - getTickerPrice(row['Symbol'], current_date)) * size for size, price in open_short_positions) + \
                          sum(closed_profits)
            print("CURRENTPORTFOLIO VALUE\n",sum((getTickerPrice(row['Symbol'], current_date) - price) * size for size, price in open_long_positions))
            print(sum((price - getTickerPrice(row['Symbol'], current_date)) * size for size, price in open_short_positions))
            print(sum(closed_profits))
            print(sum((getTickerPrice(row['Symbol'], current_date) - price) * size for size, price in open_long_positions) + \
                          sum((price - getTickerPrice(row['Symbol'], current_date)) * size for size, price in open_short_positions) + \
                          sum(closed_profits))
            print(current_date, "and", portfolio_value)
            print("OPEN LONG POSITIONS", open_long_positions)
            print("OPEN SHORT POSITIONS", open_short_positions)
            print("CLOSED PROFITS", closed_profits)
            print(row['Symbol'],(getTickerPrice(row['Symbol'], current_date)))
        daily_portfolio_values[current_date] = portfolio_value

    daily_portfolio_series = pd.Series(daily_portfolio_values).sort_index()

    gross_profit = sum([p for p in closed_profits if p > 0])
    gross_loss = sum([p for p in closed_profits if p < 0])
    net_profit = gross_profit + gross_loss

    # Calculate returns and other metrics
    portfolio_returns = daily_portfolio_series.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    z_scores = (portfolio_returns - portfolio_returns.mean()) / portfolio_returns.std()
    portfolio_returns = portfolio_returns[(z_scores > -3) & (z_scores < 3)]
    avg_trade_return = portfolio_returns.mean()
    avg_trade_volume = trades['Size'].mean()
    max_drawdown = calculate_max_drawdown(daily_portfolio_series)
    win_rate = len(portfolio_returns[portfolio_returns > 0]) / len(portfolio_returns) if len(portfolio_returns) > 0 else 0
    sharpe_ratio = calculate_sharpe_ratio(portfolio_returns, risk_free_rate)
    romad = net_profit / max_drawdown if max_drawdown != 0 else np.nan

    portfolio_metrics = {
        'Total Trades': len(trades),
        'Total Volume': trades['Size'].sum(),
        'Gross Profit': gross_profit,
        'Gross Loss': gross_loss,
        'Net Profit': net_profit,
        'Avg Trade Return': avg_trade_return,
        'Avg Trade Volume': avg_trade_volume,
        'Max Drawdown': max_drawdown,
        'Win Rate': win_rate,
        'Cumulative Return': daily_portfolio_series.iloc[-1],
        'Sharpe Ratio': sharpe_ratio,
        'ROMAD': romad
    }

    return portfolio_metrics

# Example market data
market_data = pd.DataFrame({
    'Date': pd.to_datetime(['2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05']),
    'Return': [0.01, 0.02, -0.01, 0.03, 0.02]
})

# Example trades data
data = {
    'Date': pd.to_datetime(['2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05']),
    'Symbol': ['AAPL', 'AAPL', 'AAPL', 'GOOGL', 'GOOGL'],
    'Side': ['buy', 'sell', 'buy', 'buy', 'sell'],
    'Size': [10, 10, 1, 5, 1],
    'Price': [150, 155, 160, 1200, 1190]
}

trades_df = pd.DataFrame(data)

portfolio_metrics = calculate_trade_performance(trades_df, market_data)
print(portfolio_metrics)
