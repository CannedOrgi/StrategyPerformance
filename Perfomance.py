import pandas as pd
import numpy as np
import random
from datetime import datetime

def getTickerPrice(ticker: str, date: pd.Timestamp) -> float:
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

    grouped = trades.groupby('Symbol')
    metrics = []

    portfolio_values = []
    cumulative_value = 0
    open_long_positions = []
    open_short_positions = []
    closed_profits = []

    for symbol, group in grouped:
        group = group.sort_values(by='Date')
        group['Cumulative_Size'] = group['Size'].cumsum()

        symbol_portfolio_values = []

        for index, row in group.iterrows():
            current_price = getTickerPrice(symbol, row['Date'])
            print(f"CURRENT PRICE for {symbol} on {row['Date']}: {current_price}")

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

            symbol_portfolio_values.append(sum(closed_profits))
            cumulative_value = sum(closed_profits)

        portfolio_values.extend(symbol_portfolio_values)

    cumulative_values = pd.Series(portfolio_values[1:])
    print("CUMULATIVEVALS", cumulative_values)

    gross_profit = sum([p for p in closed_profits if p > 0])
    gross_loss = sum([p for p in closed_profits if p < 0])
    net_profit = gross_profit + gross_loss

    # Valuing open positions at the last available market price
    last_date = trades['Date'].max()
    final_prices = {symbol: getTickerPrice(symbol, last_date) for symbol in trades['Symbol'].unique()}
    open_position_value = sum((final_prices[symbol] - price) * size for size, price in open_long_positions) + \
                          sum((price - final_prices[symbol]) * size for size, price in open_short_positions)

    avg_trade_return = cumulative_values.pct_change().replace([np.inf, -np.inf], np.nan).dropna().mean()
    avg_trade_volume = trades['Size'].mean()
    max_drawdown = calculate_max_drawdown(cumulative_values)
    win_rate = len([p for p in closed_profits if p > 0]) / len(closed_profits) if len(closed_profits) > 0 else 0

    sharpe_ratio = calculate_sharpe_ratio(cumulative_values.pct_change().replace([np.inf, -np.inf], np.nan).dropna(), risk_free_rate)
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
        'Cumulative Return': cumulative_value + open_position_value,
        'Open Position Value': open_position_value,
        'Sharpe Ratio': sharpe_ratio,
        'ROMAD': romad
    }

    return portfolio_metrics

market_data = pd.DataFrame({
    'Date': pd.to_datetime(['2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05']),
    'Return': [0.01, 0.02, -0.01, 0.03, 0.02]
})

data = {
    'Date': pd.to_datetime([
        '2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05',
        '2024-07-06', '2024-07-07', '2024-07-08', '2024-07-09', '2024-07-10',
        '2024-07-11', '2024-07-12', '2024-07-13', '2024-07-14', '2024-07-15',
        '2024-07-16', '2024-07-17', '2024-07-18', '2024-07-19', '2024-07-20',
        '2024-07-21', '2024-07-22', '2024-07-23', '2024-07-24', '2024-07-25',
        '2024-07-26', '2024-07-27', '2024-07-28', '2024-07-29', '2024-07-30',
        '2024-08-01', '2024-08-02', '2024-08-03', '2024-08-04', '2024-08-05',
        '2024-08-06', '2024-08-07', '2024-08-08', '2024-08-09', '2024-08-10',
        '2024-08-11', '2024-08-12', '2024-08-13', '2024-08-14', '2024-08-15',
        '2024-08-16', '2024-08-17', '2024-08-18', '2024-08-19', '2024-08-20',
        '2024-08-21', '2024-08-22', '2024-08-23', '2024-08-24', '2024-08-25',
        '2024-08-26', '2024-08-27', '2024-08-28', '2024-08-29', '2024-08-30',
        '2024-09-01', '2024-09-02', '2024-09-03', '2024-09-04', '2024-09-05',
        '2024-09-06', '2024-09-07', '2024-09-08', '2024-09-09', '2024-09-10',
        '2024-09-11', '2024-09-12', '2024-09-13', '2024-09-14', '2024-09-15',
        '2024-09-16', '2024-09-17', '2024-09-18', '2024-09-19', '2024-09-20',
        '2024-09-21', '2024-09-22', '2024-09-23', '2024-09-24', '2024-09-25',
        '2024-09-26', '2024-09-27', '2024-09-28', '2024-09-29', '2024-09-30',
        '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05',
        '2024-10-06', '2024-10-07', '2024-10-08', '2024-10-09', '2024-10-10'
    ]),
    'Symbol': [
        'AAPL', 'AAPL', 'AAPL', 'GOOGL', 'GOOGL', 'MSFT', 'MSFT', 'MSFT',
        'TSLA', 'TSLA', 'AMZN', 'AMZN', 'NFLX', 'NFLX', 'FB', 'FB', 'AAPL',
        'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NFLX', 'FB', 'AAPL', 'GOOGL',
        'MSFT', 'TSLA', 'AMZN', 'NFLX', 'FB', 'AAPL', 'AAPL', 'GOOGL',
        'GOOGL', 'MSFT', 'MSFT', 'TSLA', 'TSLA', 'AMZN', 'AMZN', 'NFLX',
        'NFLX', 'FB', 'FB', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NFLX',
        'FB', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NFLX', 'FB', 'AAPL',
        'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NFLX', 'FB', 'AAPL', 'GOOGL',
        'MSFT', 'TSLA', 'AMZN', 'NFLX', 'FB', 'AAPL', 'GOOGL', 'MSFT', 'TSLA',
        'AMZN', 'NFLX', 'FB', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NFLX',
        'FB', 'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NFLX', 'FB', 'AAPL',
        'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'TSLA', 'TSLA'
    ],
    'Side': [
        'buy', 'sell', 'buy', 'buy', 'sell', 'buy', 'sell', 'buy',
        'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'buy', 'sell',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell', 'buy', 'sell', 'buy', 'sell', 'buy',
        'sell', 'buy', 'sell'
    ],
    'Size': [
        10, 10, None, 5, None, 15, None, 20, 8, None, 25, None, 12, None, 18, None,
        15, None, 10, None, 8, None, 12, None, 20, None, 25, None, 18, None,
        10, 10, None, 5, None, 15, None, 20, 8, None, 25, None, 12, None, 18, None,
        15, None, 10, None, 8, None, 12, None, 20, None, 25, None, 18, None,
        10, 10, None, 5, None, 15, None, 20, 8, None, 25, None, 12, None, 18, None,
        15, None, 10, None, 8, None, 12, None, 20, None, 25, None, 18, None,
        10, 10, None, 5, None, 15, None, 20, 8, None
    ],
    'Price': [
    150, 155, 160, 1200, 1190, 300, 310, 315, 600, 590, 3500, 3400, 500, 490,
    200, 190, 165, 1185, 295, 585, 3450, 485, 205, 170, 1195, 305, 575, 3500,
    480, 210, 150, 155, 160, 1200, 1190, 300, 310, 315, 600, 590, 3500, 3400,
    500, 490, 200, 190, 165, 1185, 295, 585, 3450, 485, 205, 170, 1195, 305,
    575, 3500, 480, 210, 150, 155, 160, 1200, 1190, 300, 310, 315, 600, 590,
    3500, 3400, 500, 490, 200, 190, 165, 1185, 295, 585, 3450, 485, 205, 170,
    1195, 305, 575, 3500, 480, 210, 150, 155, 160, 1200, 1190, 300, 310, 315,
    600, 590
]}
trades_df = pd.DataFrame(data)

metrics_df = calculate_trade_performance(trades_df, market_data)
print(metrics_df)
