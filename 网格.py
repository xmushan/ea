import MetaTrader5 as mt5
import pandas as pd
import sys
from datetime import datetime, timezone
from config import login,server,password
import time

# 登录到MT5
mt5.initialize(login=login, server=server,password=password)
authorized=mt5.login(login=login, server=server,password=password)
print(authorized)
# 设置交易参数
symbol = "GOLD_"  # 交易符号
lot_size = 0.01  # 每次交易的手数
# 做空区间网格区间大小
sell_grid_size = 10
# 做多区间网格区间大小
buy_grid_size = 5
max_orders = 10  # 最大订单数量
max_price = 2500  # 最大价格区间
min_price = 2250  # 最小价格区间
take_profit_pips = 10  # 止盈点数
# 获取当前价格
def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return tick.bid, tick.ask

# 计算网格级别价格
def calculate_grid_levels(base_price, max_orders):
    levels = {'buy': [], 'sell': []}
    for i in range(1, max_orders + 1):
        levels['buy'].append(base_price - i * buy_grid_size)
        levels['sell'].append(base_price + i * sell_grid_size)
    return levels

# 开仓函数
def open_order(symbol, lot, order_type, price, tp_price,slippage=5):
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': lot,
        'type': order_type,
        'price': price,
        'tp': tp_price,
        'slippage': slippage,
        'magic': 234000,
        'comment': 'Grid strategy',
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print(result)
    return result

# 获取当前订单列表
def get_open_orders(symbol):
    positions = mt5.positions_get(symbol=symbol)
    orders = {'buy': [], 'sell': []}
    for pos in positions:
        if pos.type == mt5.ORDER_TYPE_BUY:
            orders['buy'].append(pos.price_open)
        elif pos.type == mt5.ORDER_TYPE_SELL:
            orders['sell'].append(pos.price_open)
    return orders

# 主交易循环
def grid_trading(symbol, lot_size, max_orders, max_price, min_price):
    bid, ask = get_current_price(symbol)
    base_price = (bid + ask) / 2
    levels = calculate_grid_levels(base_price, max_orders)
    while True:
        positions_total=mt5.positions_total()
        if positions_total >= 10:
            print('已达最大持仓数量')
            return
        bid, ask = get_current_price(symbol)
        current_price = (bid + ask) / 2
        if current_price < min_price or current_price > max_price:
            print(f"Current price {current_price} is out of the trading range.")
            time.sleep(60)
            continue
        open_orders = get_open_orders(symbol)
        for buy_level in levels['buy']:
            tp_price = buy_level + take_profit_pips
            if current_price <= buy_level and buy_level >= min_price:
                if buy_level not in open_orders['buy']:
                    result = open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY,tp_price,ask)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"Buy order placed at {buy_level}")
                    else:
                        print(f"Failed to place buy order at {buy_level}: {result.comment}")
            else:
                print('无做多信号',current_price,buy_level)
        for sell_level in levels['sell']:
            tp_price = sell_level - take_profit_pips
            if current_price >= sell_level and sell_level <= max_price:
                if sell_level not in open_orders['sell']:
                    result = open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL,tp_price ,bid)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"Sell order placed at {sell_level}")
                    else:
                        print(f"Failed to place sell order at {sell_level}: {result.comment}")
            print('无做空信号',current_price,sell_level)
        time.sleep(60)

# 开始网格交易
grid_trading(symbol, lot_size, max_orders, max_price, min_price)
