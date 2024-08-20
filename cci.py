import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time as timeSleep
from datetime import datetime, timezone

# symbol = "GOLD_"  # 交易符号
symbol = "XAUUSDm"  # 交易符号
# symbol = "XAUUSDc"  # 交易符号
# symbol = "BTCUSDc"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
lot_size = 0.02  # 每次交易的手数
bars = 100  # 获取最近100个柱数据
slippage = 5  # 允许的价格滑点
last_kline_time = None  # 用于存储上一次K线时间戳
profit = 5 # 单比订单盈利额
totalProfit = 10 # 总盈利额度
retracement = -50 # 最大回撤
bars = 100  # 获取最近100个柱数据

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

# 获取当前K线时间戳
def get_current_kline_time(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    utc_time = datetime.fromtimestamp(rates_frame['time'].iloc[-1], tz=timezone.utc)
    return utc_time

# 计算布林带
def CalculateBollingerBands(data): 
    df = pd.DataFrame(data)
    # 计算20日简单移动平均线（SMA）
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    # 计算布林带的标准差
    df['STD_20'] = df['close'].rolling(window=20).std()
    # 计算布林带上轨和下轨
    df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)
    bollingData = df[['close', 'SMA_20', 'Upper_Band', 'Lower_Band','open']].iloc[-1]
    return bollingData.Upper_Band,bollingData.Lower_Band,bollingData.SMA_20

def set_protective_stop(order,symbol=symbol):
    # symbol = order['symbol']
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

def calculate_cci(data,period=14):
    data['time'] = pd.to_datetime(data['time'], unit='s')
    # 计算典型价格 (Typical Price)
    data['TP'] = (data['high'] + data['low'] + data['close']) / 3
    # 计算14周期的移动平均
    data['SMA'] = data['TP'].rolling(window=period).mean()
    # 计算偏差
    data['Mean Deviation'] = data['TP'].rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    # 计算CCI
    data['CCI'] = (data['TP'] - data['SMA']) / (0.015 * data['Mean Deviation'])
    # 获取最后一条数据的CCI值
    last_cci = data['CCI'].iloc[-1]
    return last_cci

# 计算RSI
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    # 使用指数移动平均计算平均增益和损失
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# 开仓函数
def open_order(symbol, lot, order_type, price):
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

# 当前订单是否获得收益
def checkCurrentIsprofit(flag = True,isAll = False):
    orders = mt5.positions_get()
    total = 0
    if not orders:
        return
    orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
    for index, order in orders_df.iterrows():
        total = total + order['profit']
    # 最大回撤金额
    if (total < retracement):
        for index, order in orders_df.iterrows():
            set_protective_stop(order)
            timeSleep.sleep(3600)
        return
    if (flag == False):
        for index, order in orders_df.iterrows():
            set_protective_stop(order)
        return
    if (isAll == True and total >= totalProfit):
        for index, order in orders_df.iterrows():
            set_protective_stop(order)
        return
    for index, order in orders_df.iterrows():
        if order['profit'] >= profit:
            set_protective_stop(order)

def judegeOrder():
    positions_total=mt5.positions_total()
    if (positions_total >=5):
        checkCurrentIsprofit(True,True)
        return
    data = get_historical_data(symbol, timeframe)
    cci = calculate_cci(data,15)
    rsi = calculate_rsi(data,25)
    bid, ask = get_current_price(symbol)
    upper,lower,middle = CalculateBollingerBands(data)
    if (25 <= rsi <= 60):
        # 多
        if (cci <= -120 and rsi and ask < lower):
            open_order(symbol, 0.01, mt5.ORDER_TYPE_BUY, ask)
        if (cci <= -150 and ask < lower):
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask)
        if (cci <= -180 and ask < lower):
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask)
        if (cci <= -250 and ask < lower):
            open_order(symbol, 0.05, mt5.ORDER_TYPE_BUY, ask)
        # 空
        if (cci >= 120 and bid > upper):
            open_order(symbol, 0.01, mt5.ORDER_TYPE_SELL, ask)
        if (cci >= 150 and bid > upper):
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, ask)
        if (cci >= 180 and bid > upper):
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, ask)
        if (cci >= 250 and bid > upper):
            open_order(symbol, 0.05, mt5.ORDER_TYPE_SELL, ask)
        if (-20 <= cci <= 30):
            checkCurrentIsprofit()
    
