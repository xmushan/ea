import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime,timezone
import time as timeSleep


slippage = 5  # 允许的价格滑点
last_kline_time = None  # 用于存储上一次K线时间戳

# 获取当前K线时间戳
def get_current_kline_time(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    utc_time = datetime.fromtimestamp(rates_frame['time'].iloc[-1], tz=timezone.utc)
    return utc_time


# 开仓函数
def open_order(symbol, lot, order_type, price,timeframe):
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
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
    if (last_kline_time == current_kline_time):
        print('当前K线下过单')
        return
    result = mt5.order_send(request)
    if result.retcode == 10009:
        last_kline_time = current_kline_time
        print('success')
    else:
        print(result)

# 当前订单是否获得收益
def checkCurrentIsprofit(symbol,retracement = -30,profit = 5):
    orders = mt5.positions_get()
    if not orders:
        return
    orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
    filtered_orders_df = orders_df.loc[orders_df['symbol'] == symbol]
    for index, order in filtered_orders_df.iterrows():
        total = total + order['profit']
    # 单笔最大回撤金额
    for index, order in filtered_orders_df.iterrows():
        if (order['profit'] <= retracement):
            set_protective_stop(order)
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
