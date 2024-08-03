import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from config import login, server, password
import time

# 初始化MT5
mt5.initialize()
authorized = mt5.login(login=login, password=password, server=server)
if not authorized:
    print(f"Failed to login to MT5: {mt5.last_error()}")
    mt5.shutdown()
    exit()

symbol = "BTCUSD"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
lot_size = 0.05  # 每次交易的手数
bars = 100  # 获取最近100个柱数据
slippage = 5  # 允许的价格滑点

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
    print(rates_frame)
    return rates_frame

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
    return bollingData.Upper_Band,bollingData.Lower_Band

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

# 当前订单是否获得收益
def checkCurrentIsprofit():
    orders = mt5.positions_get()
    if orders is None:
        print(f"No open orders found: {mt5.last_error()}")
        return None
    orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
    for index, order in orders_df.iterrows():
        if order['profit'] >= 5:
            set_protective_stop(order)
        else:
            print('当前订单无收益',order['ticket'])

def set_protective_stop(order):
    symbol = order['symbol']
    ticket = order['ticket']
    order_type = order['type']
    volume =order['volume']
    print(volume)
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
    result = mt5.order_send(request)
    print(result)
    if result.retcode == 10009:
        print('平仓成功')
    else:
        print('平仓失败')

def main():
    positions_total=mt5.positions_total()
    if positions_total >= 10:
        checkCurrentIsprofit()
        return
    data = get_historical_data(symbol, timeframe)
    upper,lower = CalculateBollingerBands(data)
    rsi = calculate_rsi(data)
    bid, ask = get_current_price(symbol)
    # 如果rsi指标小于30，执行买多操作
    if (rsi < 30 and ask < lower):
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask)
    # rsi指标大于70，执行做空操作
    elif (rsi > 76 and bid > upper):
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid)
    else:
        print('无信号')
        print(rsi)
        print(upper,lower)
        print(bid,ask)

while True:
    main()
    time.sleep(1)

