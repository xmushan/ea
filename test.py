import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def backtest_vibrate_strategy(data, initial_balance=500, lot_size=0.1, points_value=10):
    balance = initial_balance
    total_trades = 0
    losing_trades = 0
    max_drawdown = 0
    peak_balance = initial_balance
    open_trades = []  # 当前开仓的订单
    open_price_history = []
    time_history = []
    buy_signals = []  # 记录买入信号的时间和价格
    sell_signals = []  # 记录卖出信号的时间和价格

    for i in range(len(data)):
        # 获取当前数据的指标
        indicator_data = {
            'rsi': data['rsi'].iloc[i],
            'cci': data['CCI'].iloc[i],
            'upper': data['Upper_Band'].iloc[i],
            'lower': data['Lower_Band'].iloc[i],
            'middle': data['SMA_20'].iloc[i],
            'ask': data['open'].iloc[i],
            'bid': data['high'].iloc[i],
            'close': data['close'].iloc[i],
            'sma_short': data['sma_short'].iloc[i],
            'sma_long_ma': data['sma_long_ma'].iloc[i]
        }

        # 检查当前开仓的订单是否满足平仓条件
        closed_trades = []
        for trade in open_trades:
            action = trade['action']  # 使用订单中的action
            if i < len(data) - 1:
                next_open_price = data['open'].iloc[i + 1]
                pnl = calculate_pnl(action, indicator_data, lot_size, points_value, next_open_price)
                
                # 判断是否达到平仓条件
                if pnl > 10 or pnl < -50:
                    balance += pnl
                    closed_trades.append(trade)
                    total_trades += 1
                    if pnl < 0:
                        losing_trades += 1
                    # 更新最大回撤
                    if balance > peak_balance:
                        peak_balance = balance
                    drawdown = peak_balance - balance
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

        # 移除已平仓的订单
        open_trades = [trade for trade in open_trades if trade not in closed_trades]

        # 判断是否下单，确保最大下单数量不超过5单
        if len(open_trades) < 5:
            action = determine_trade_action(indicator_data)
            if action is not None:
                open_trades.append({'action': action, 'entry_price': indicator_data['ask'] if action == 'buy' else indicator_data['bid']})
                # 记录买入或卖出信号
                if action == 'buy':
                    buy_signals.append((data['time'].iloc[i], data['open'].iloc[i]))
                elif action == 'sell':
                    sell_signals.append((data['time'].iloc[i], data['open'].iloc[i]))

        # 记录当前的开盘价和时间
        open_price_history.append(data['open'].iloc[i])
        time_history.append(data['time'].iloc[i])

    # 绘制开盘价曲线
    plt.figure(figsize=(12, 8))
    plt.plot(time_history, open_price_history, label='Open Price Over Time', color='orange')
    
    # 绘制买入信号
    if buy_signals:
        buy_times, buy_prices = zip(*buy_signals)
        plt.scatter(buy_times, buy_prices, marker='^', color='green', label='Buy Signal', s=100)

    # 绘制卖出信号
    if sell_signals:
        sell_times, sell_prices = zip(*sell_signals)
        plt.scatter(sell_times, sell_prices, marker='v', color='red', label='Sell Signal', s=100)

    plt.xlabel('Time')
    plt.ylabel('Open Price')
    plt.title('Open Price over Time with Trade Signals')
    plt.grid(True)
    plt.legend()

    # 创建表格数据
    cell_text = [
        ['Final Balance', f'{balance:.2f}'],
        ['Total Trades', total_trades],
        ['Losing Trades', losing_trades],
        ['Max Drawdown', f'{max_drawdown:.2f}']
    ]

    # 在图上添加表格
    plt.table(cellText=cell_text, colLabels=['Metric', 'Value'], loc='bottom', cellLoc='center', bbox=[0, -0.3, 1, 0.2])

    plt.subplots_adjust(left=0.2, bottom=0.4)  # 调整图形和表格的布局
    plt.show()

    return balance, open_price_history, time_history, total_trades, losing_trades, max_drawdown

def determine_trade_action(indicator_data):
    rsi = indicator_data['rsi']
    cci = indicator_data['cci']
    upper = indicator_data['upper']
    lower = indicator_data['lower']
    middle = indicator_data['middle']
    ask = indicator_data['ask']
    bid = indicator_data['bid']
    sma_short = indicator_data['sma_short']
    sma_long_ma = indicator_data['sma_long_ma']
    is_uptrend = sma_short > sma_long_ma
    is_downtrend = sma_short < sma_long_ma

    if is_uptrend:
        if (rsi >= 75 or cci >= 250) and bid > upper:
            return 'sell'
        elif (rsi <= 40 and cci <= -100 and ask < lower):
            return 'buy'
        elif 50 <= rsi <= 65 and cci >= 20 and ask < middle:
            return 'buy'
        elif (rsi <= 30 or cci <= -250) and ask < lower:
            return 'buy'
    elif is_downtrend:
        if (rsi <= 30 or cci <= -250) and ask < lower:
            return 'buy'
        elif rsi <= 50 and cci <= -50 and ask > middle:
            return 'sell'
        elif (rsi >= 70 or cci >= 230) and bid > upper:
            return 'sell'
        elif (55 <= rsi <= 65 and cci >= 100 and bid >= upper):
            return 'sell'
    return None

def calculate_pnl(action, indicator_data, lot_size, points_value, next_open_price):
    if action == 'buy':
        entry_price = indicator_data['ask']
        exit_price = next_open_price  # 使用下一个K线的开盘价作为平仓价格
        profit_points = exit_price - entry_price
    elif action == 'sell':
        entry_price = indicator_data['bid']
        exit_price = next_open_price  # 使用下一个K线的开盘价作为平仓价格
        profit_points = entry_price - exit_price
    else:
        profit_points = 0

    pnl = profit_points * lot_size * points_value
    return pnl
