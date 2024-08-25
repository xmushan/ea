import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from config import login, password, server
import pytz
# 配置MetaTrader 5登录信息（请根据需要修改）
balance = 500
timezone = pytz.timezone("Asia/Shanghai")
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

# 设置交易品种和时间框架
symbol = "XAUUSDm"  # 黄金的交易对
timeframe = mt5.TIMEFRAME_M15  # 15分钟周期
start_date = datetime(2024, 8, 9)
end_date = datetime(2024, 8, 10)

# 获取历史数据
def get_historical_data(symbol, timeframe, start_date, end_date):
    # rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
    utc_from = datetime(2024, 8, 10, tzinfo=timezone)
    print(utc_from)
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, 100)
    if rates is None:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame.set_index('time', inplace=True)
    return rates_frame

data = get_historical_data(symbol, timeframe, start_date, end_date)

# 计算移动平均线
def calculate_moving_averages(data, short_window=5, long_window=20):
    data['sma_short'] = data['close'].rolling(window=short_window, min_periods=1).mean()
    data['sma_long'] = data['close'].rolling(window=long_window, min_periods=1).mean()

calculate_moving_averages(data)
print(data)

exit()
# 回测函数
def backtest(data, lot_size=1):
    global balance
    positions = 0
    data['balance'] = balance
    data['positions'] = positions
    data['cash'] = balance
    print(data)
    for i in range(1, len(data)):
        if i % 2 == 0:
            # 买入信号
            if True:
                balance += 10
        
        # elif data['sma_short'].iloc[i] < data['sma_long'].iloc[i] and data['sma_short'].iloc[i-1] >= data['sma_long'].iloc[i-1]:
        #     # 卖出信号
        #     if positions > 0:
        #         balance += positions * data['close'].iloc[i]
        #         positions = 0
        #         print(f"Sell at {data.index[i]}: balance = {balance}")
        
        data.loc[data.index[i], 'balance'] = balance
        data.loc[data.index[i], 'positions'] = positions
        data.loc[data.index[i], 'cash'] = balance + positions * data['close'].iloc[i]

    return data

# 执行回测
data = get_historical_data(symbol, timeframe, start_date, end_date)
if data is not None:
    calculate_moving_averages(data)
    result = backtest(data)
    
    # 绘制结果
    plt.figure(figsize=(14, 7))
    plt.plot(result.index, result['balance'], label='Account Balance', color='blue')
    plt.title('Account Balance Over Time')
    plt.xlabel('Date')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))  # 每小时标记一次
    plt.gcf().autofmt_xdate()  # 自动旋转日期标签
    plt.ylabel('Balance')
    plt.legend()
    plt.grid(True)
    plt.show()

# 关闭MetaTrader 5连接
mt5.shutdown()
