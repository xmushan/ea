import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from config import login, server, password

# 初始化MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# 登录到MetaTrader 5账户
if not mt5.login(login=login, password=password, server=server):
    print("Failed to login to MT5:", mt5.last_error())
    mt5.shutdown()
    quit()

print("Login successful")

# 设置交易品种为黄金
symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_H1  # 1小时周期
start_date = datetime(2024, 3, 1)
end_date = datetime(2024, 8, 1)

# 获取历史数据
rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
if rates is None:
    print(f"Failed to get data for {symbol}, error code =", mt5.last_error())
    mt5.shutdown()
    quit()

# 转换为 DataFrame
data = pd.DataFrame(rates)
data['time'] = pd.to_datetime(data['time'], unit='s')
data.set_index('time', inplace=True)

# 计算RSI和CCI指标
def calculate_indicators(data):
    data['rsi'] = talib.RSI(data['close'], timeperiod=14)
    data['cci'] = talib.CCI(data['high'], data['low'], data['close'], timeperiod=14)
    return data

# 回测函数
def backtest(data, lot_size=0.1, initial_balance=10000):
    balance = initial_balance
    positions = 0
    data['balance'] = np.nan  # 初始化 'balance' 列为 NaNs

    for i in range(1, len(data)):
        ask = data['close'].iloc[i]  # 假设使用收盘价作为开盘价
        bid = ask  # 黄金点差较小，简化处理

        rsi = data['rsi'].iloc[i]
        cci = data['cci'].iloc[i]
        upper = data['upper'].iloc[i]
        lower = data['lower'].iloc[i]
        middle = data['middle'].iloc[i]

        # 买入条件：RSI和CCI处于超卖区，且价格低于下轨
        if rsi <= 30 and cci <= -200 and ask < lower:
            positions = balance / ask  # 购买的手数
            balance = 0  # 全仓买入
            print(f"Opened position at {data.index[i]}: {positions} lots at price {ask}")
        
        # 卖出条件：RSI和CCI处于超买区，且价格高于上轨
        elif rsi >= 70 and cci >= 150 and bid > upper:
            if positions > 0:
                balance = positions * bid  # 卖出所有持仓
                positions = 0
                print(f"Closed position at {data.index[i]}: balance = {balance}")

        # 计算持仓价值
        data.loc[data.index[i], 'balance'] = balance + positions * ask

    return data

# 计算指标
data = calculate_indicators(data)

# 执行回测
result = backtest(data)

# 绘制结果
import matplotlib.pyplot as plt
plt.figure(figsize=(14, 7))
plt.plot(result['balance'], label='Equity Curve')
plt.title('Backtest Results for Gold (XAUUSD)')
plt.xlabel('Date')
plt.ylabel('Balance')
plt.legend()
plt.show()

