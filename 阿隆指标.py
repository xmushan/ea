import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta,timezone
from config import login,server,password
import time

# 初始化MT5
mt5.initialize()
globalData = {
    'currentOrderTime': 0
}

authorized = mt5.login(login=login, password=password, server=server)
if not authorized:
    print(f"Failed to login to MT5: {mt5.last_error()}")
    mt5.shutdown()
    exit()

symbol = "GOLD_"  # 交易符号
timeframe = mt5.TIMEFRAME_H1  # 时间框架
period = 25  # 阿隆指标周期
lot_size = 0.01  # 每次交易的手数
slippage = 5  # 允许的价格滑点
take_profit_pips = 500  # 止盈点数
stop_loss_pips = 1000  # 止损点数

# 获取历史数据
def get_historical_data(symbol, timeframe, period):
    utc_from = datetime.now() - timedelta(days=period)
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, period)
    if rates is None:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    return pd.DataFrame(rates)

# 计算阿隆指标
def calculate_aroon(data, period):
    aroon_up = []
    aroon_down = []
    
    for i in range(period, len(data)):
        high = data['high'][i-period:i]
        low = data['low'][i-period:i]
        highest_idx = high.idxmax()
        lowest_idx = low.idxmin()
        
        aroon_up.append(100 * (period - (i - highest_idx)) / period)
        aroon_down.append(100 * (period - (i - lowest_idx)) / period)
    
    return aroon_up, aroon_down

# 开仓函数
def open_order(symbol, lot, order_type, price, sl_price, tp_price):
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': lot,
        'type': order_type,
        'price': price,
        'sl': sl_price,
        'tp': tp_price,
        'deviation': slippage,
        'magic': 234000,
        'comment': 'Aroon strategy',
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == 10009:
        print(result)
        print('success')

# 主交易逻辑
def aroon_strategy(symbol, period):
    data = get_historical_data(symbol, timeframe, period * 2)
    if data is None:
        return
    
    aroon_up, aroon_down = calculate_aroon(data, period)
    print(aroon_up,aroon_down)
    if aroon_up[-1] > 50 and aroon_down[-1] < 50:
        bid, ask = mt5.symbol_info_tick(symbol).bid, mt5.symbol_info_tick(symbol).ask
        sl_price = bid - stop_loss_pips * mt5.symbol_info(symbol).point
        tp_price = bid + take_profit_pips * mt5.symbol_info(symbol).point
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask, sl_price, tp_price)
        print("Buy signal detected")
        
    elif aroon_up[-1] < 50 and aroon_down[-1] > 50:
        bid, ask = mt5.symbol_info_tick(symbol).bid, mt5.symbol_info_tick(symbol).ask
        sl_price = ask + stop_loss_pips * mt5.symbol_info(symbol).point
        tp_price = ask - take_profit_pips * mt5.symbol_info(symbol).point
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid, sl_price, tp_price)
        print("Sell signal detected")

# 执行策略

while True:
    aroon_strategy(symbol, period)
    time.sleep(1800)
    

# 关闭MT5连接
# mt5.shutdown()
