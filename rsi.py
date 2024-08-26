import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime,time
from config import login, server, password
import time as timeSleep
from strategy import vibrate,tend
import pytz
from utils import checkCurrentIsprofit

# 初始化MT5
mt5.initialize()
authorized = mt5.login(login=login, password=password, server=server)

print('登录成功')
if not authorized:
    print(f"Failed to login to MT5: {mt5.last_error()}")
    mt5.login(login=login, password=password, server=server)
    # mt5.shutdown()
    # exit()
# symbol = "GOLD_"  # 交易符号
symbol = "XAUUSDm"  # 交易符号
# symbol = "XAUUSDc"  # 交易符号
# symbol = "BTCUSDc"  # 交易符号
# symbol = "BTCUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
lot_size = 0.03  # 每次交易的手数
bars = 500  # 获取最近100个柱数据


# 获取当前价格
def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return tick.bid, tick.ask

# 获取历史数据
def get_historical_data(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    return rates_frame

 # 计算移动均线
def calculate_ma(symbol, timeframe, ma_period):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, ma_period + 100)
    if bars is None or len(bars) < ma_period:
        mt5.shutdown()
        raise ValueError("获取数据不足，无法计算均线")
    df = pd.DataFrame(bars)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['MA'] = df['close'].rolling(window=ma_period).mean()
    last_ma = df['MA'].iloc[-1]
    return last_ma

# 计算RSI
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_cci(data,period=14):
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data['TP'] = (data['high'] + data['low'] + data['close']) / 3
    data['SMA'] = data['TP'].rolling(window=period).mean()
    data['Mean Deviation'] = data['TP'].rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    data['CCI'] = (data['TP'] - data['SMA']) / (0.015 * data['Mean Deviation'])
    last_cci = data['CCI'].iloc[-1]
    return last_cci

# 计算简单移动平均线
def get_sma(data, sma_period):
    # 计算简单移动平均线
    data['sma'] = data['close'].rolling(window=sma_period).mean()
    
    # 返回最新一条SMA值
    latest_sma = data['sma'].iloc[-1]
    return latest_sma


# 计算布林带
def CalculateBollingerBands(data): 
    df = pd.DataFrame(data)
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['STD_20'] = df['close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)
    bollingData = df[['close', 'SMA_20', 'Upper_Band', 'Lower_Band','open']].iloc[-1]
    return bollingData.Upper_Band,bollingData.Lower_Band,bollingData.SMA_20


def is_within_business_hours(data,timezone_str='Asia/Shanghai'):
    global timeframe
    # 获取指定时区的当前时间
    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone).time()
    # 亚洲盘时间
    asiaStartTime = time(7, 0, 0)
    asiaEndTime = time(15, 30, 0)
    # 欧洲盘时间
    EuropeStartTime = time(15, 30, 0)
    EuropeEndTime = time(20, 30, 0)
    # 美盘时间
    UsaStartTime = time(20, 30, 0)
    UsaopeEndTime = time(7, 0, 0)
    # 判断亚洲盘时间
    if asiaStartTime <= current_time <= asiaEndTime:
        vibrate(data,symbol,0.02,timeframe)
        return
    # # 判断欧洲盘时间
    if EuropeStartTime <= current_time <= EuropeEndTime:
        # timeframe = mt5.TIMEFRAME_M30
        # tend(data,symbol,timeframe)
        vibrate(data,symbol,0.02,timeframe)
        return
    # # 判断美盘时间（跨午夜）
    if (current_time >= UsaStartTime) or (current_time <= UsaopeEndTime):
        vibrate(data,symbol,0.02,timeframe)
        return


def main():
    positions_total=mt5.positions_total()
    if positions_total >= 5:
        checkCurrentIsprofit(symbol)
        print('已达当前最大订单量')
        return
    short_ma = calculate_ma(symbol, timeframe, 50)  # 50周期均线
    long_ma = calculate_ma(symbol, timeframe, 200)  # 200周期均线
    data = get_historical_data(symbol, timeframe)
    sma_short = get_sma(data, 14)
    sma_long_ma = get_sma(data, 21)
    upper,lower,middle = CalculateBollingerBands(data)
    rsi = calculate_rsi(data,25)
    cci = calculate_cci(data,20)
    bid, ask = get_current_price(symbol)
    indicatorData = {
        'rsi': rsi,
        'cci': cci,
        'upper': upper,
        'lower': lower,
        'middle': middle,
        'ask': ask,
        'bid': bid,
        'sma_short': sma_short,
        'sma_long_ma': sma_long_ma,
        'shortMa': short_ma,
        'longMa': long_ma,
    }
    print(indicatorData)
    is_within_business_hours(indicatorData)

while True:
    main()
    timeSleep.sleep(1)

