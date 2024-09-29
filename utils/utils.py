import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime,timezone
import time as timeSleep

# 买价(Bid) – 卖价(Ask)
slippage = 5  # 允许的价格滑点
last_kline_time = None  # 用于存储上一次K线时间戳
bars = 100
lossAcount = 0 # 亏损次数

# 获取历史数据
def get_historical_data(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    return rates_frame


# 获取当前价格
def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return tick.bid, tick.ask

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
    data['rsi'] = rsi
    return rsi.iloc[-1]

def calculate_cci(data,period=14):
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data['TP'] = (data['high'] + data['low'] + data['close']) / 3
    data['SMA'] = data['TP'].rolling(window=period).mean()
    data['Mean Deviation'] = data['TP'].rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    data['CCI'] = (data['TP'] - data['SMA']) / (0.015 * data['Mean Deviation'])
    last_cci = data['CCI'].iloc[-1]
    data['sma_short'] = data['close'].rolling(window=14).mean()
    data['sma_long_ma'] = data['close'].rolling(window=21).mean()
    return last_cci

# 获取当前K线时间戳
def get_current_kline_time(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    utc_time = datetime.fromtimestamp(rates_frame['time'].iloc[-1], tz=timezone.utc)
    return utc_time


# 计算简单移动平均线
def get_sma(data, sma_period):
    # 计算简单移动平均线
    data['sma'] = data['close'].rolling(window=sma_period).mean()
    # 返回最新一条SMA值
    latest_sma = data['sma'].iloc[-1]
    return latest_sma

# 开仓函数
def open_order(symbol, lot, order_type, price,timeframe):
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': lot,
        'type': order_type,
        'price': price,
        'deviation': slippage,
        'magic': 234000,
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == 10009:
        print('success')
    else:
        print(result)


def CalculateBollingerBands(data): 
    df = pd.DataFrame(data)
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['STD_20'] = df['close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)
    
    # 将布林带的三个值添加到数据框中作为新列
    data['SMA_20'] = df['SMA_20']
    data['Upper_Band'] = df['Upper_Band']
    data['Lower_Band'] = df['Lower_Band']
    
    # 提取最后一行的布林带数据
    last_row = df.iloc[-1]
    upper_band = last_row['Upper_Band']
    lower_band = last_row['Lower_Band']
    sma_20 = last_row['SMA_20']
    
    return upper_band, lower_band, sma_20

# 当前订单是否获得收益
def checkAllIsprofit(retracement = -15,profit = 5):
    orders = mt5.positions_get()
    if not orders:
        return
    orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
    # 单笔最大回撤金额
    for index, order in orders_df.iterrows():
        if (order['profit'] <= retracement):
            set_protective_stop(order)
    for index, order in orders_df.iterrows():
        if order['profit'] >= profit:
            set_protective_stop(order)



# 当前订单是否获得收益
def checkCurrentIsprofit(symbol, retracement=-10, profit=5, order_type=None,onCallBack = None):
    orders = mt5.positions_get()
    if not orders:
        return
    orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
    filtered_orders_df = orders_df[orders_df['symbol'] == symbol]
    if order_type:
        # 过滤多单或空单
        if order_type == 'buy':
            filtered_orders_df = filtered_orders_df[filtered_orders_df['type'] == mt5.ORDER_TYPE_BUY]
        elif order_type == 'sell':
            filtered_orders_df = filtered_orders_df[filtered_orders_df['type'] == mt5.ORDER_TYPE_SELL]
        else:
            return
    # if filtered_orders_df.empty:
    #     print("没有符合订单")
    # 单笔最大回撤金额
    for index, order in orders_df[orders_df['symbol'] == symbol].iterrows():
        if order['profit'] <= retracement:
            set_protective_stop(order)
            if onCallBack: 
                onCallBack(order)
    if (onCallBack == None):
        for index, order in filtered_orders_df.iterrows():
            if order['profit'] >= profit:
                set_protective_stop(order)


def set_protective_stop(order):
    symbol = order['symbol']
    ticket = order['ticket']
    order_type = order['type']
    volume =order['volume']
    close_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': volume,
        'type': close_type,
        'position': ticket,
        'comment': 'Close order',
        "type_time": mt5.ORDER_TIME_GTC, # 订单到期类型
        "type_filling": mt5.ORDER_FILLING_IOC, #订单成交类型
    }
    res =  mt5.order_send(request)
    print(res)
