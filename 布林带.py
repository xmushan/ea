import MetaTrader5 as mt5
import sys
from config import login,server,password
from datetime import datetime,timezone
import pandas as pd
import pytz
import time
from strategy import calculate_moving_average


BTCUSD = "BTCUSD"
GOLD = 'GOLD_'


globalData = {
    # 订单亏损数
    'deficiency': 0,
    # 上一根K线的时间
    'lastTime': -1,
    # 当前下单的时间
    'currentTime': 0,
    # 当前价格
    'currentPrice': 0
}
# 类型
symbol = GOLD
# 手数
volume = 0.01
# 设置最小保护收益
min_protect_profit = 5.0  # 最小保护收益金额
protect_pips = 10  # 保护止损点数


mt5.initialize(login=login, server=server,password=password)
authorized=mt5.login(login=login, server=server,password=password)


if  (authorized == False):
    sys.exit('登录失败')

# 判断处于上升还是下降趋势
# def check_increasing_closes(df, n=2):
#     # 新增一个列来标记是否增加
#     df['Increasing_Close'] = False
#     for i in range(n, len(df)):
#         increasing = True
#         for j in range(1, n):
#             if df['close'].iloc[i - j] <= df['close'].iloc[i - j - 1]:
#                 increasing = False
#                 break
#         df['Increasing_Close'].iloc[i] = increasing
#     return df.iloc[-1].Increasing_Close and df.iloc[-2].Increasing_Close and df.iloc[-3].Increasing_Close

# def checkIsprofit():
#     from_date = datetime(2024, 7, 24, tzinfo=timezone.utc)
#     to_date = datetime(2024, 7, 25,tzinfo=timezone.utc)
#     deals=mt5.history_deals_get(from_date, to_date, group=symbol)
#     df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
#     df['time'] = pd.to_datetime(df['time'], unit='s')
#     # 根据时间排序
#     df.sort_values(by='time', ascending=False, inplace=True)
#     # 选择最后三笔交易
#     last_three_deals = df.head(10)
#     # 检查每笔交易的盈亏状态
#     for index, deal in last_three_deals.iterrows():
#         profit = deal['profit']
#         if profit < 0:
#             globalData['deficiency'] +=1

# 设置保护止损
def set_protective_stop(order):
    symbol = order['symbol']
    ticket = order['ticket']
    order_type = order['type']
    close_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': volume,
        'type': close_type,
        'position': ticket,
        'deviation': 20,
        'magic': 234000,
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
# 当前订单是否获得收益
def checkCurrentIsprofit():
    orders = mt5.positions_get()
    if orders is None:
        print(f"No open orders found: {mt5.last_error()}")
        return None
    orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
    for index, order in orders_df.iterrows():
        if order['profit'] > 0:
            set_protective_stop(order)
        else:
            print('当前订单无收益',order['ticket'])



def CalculateBollingerBands(): 
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 20)
    # 从所获得的数据创建DataFrame
    df = pd.DataFrame(rates)
    df['time']=pd.to_datetime(df['time'], unit='s')
    # 计算20日简单移动平均线（SMA）
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    # 计算布林带的标准差
    df['STD_20'] = df['close'].rolling(window=20).std()
    # 计算布林带上轨和下轨
    df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)
    last_row = df[['close','open','high','low','time']].iloc[-2]
    globalData['lastTime'] = last_row.time
    globalData['currentPrice'] = mt5.symbol_info_tick(symbol).bid
    # 上一根K线的最高价
    bollingData = df[['close', 'SMA_20', 'Upper_Band', 'Lower_Band','open']].iloc[-1]
    #上一根K线的最高价
    high = last_row.high
    #上一根K线的最低价
    low = last_row.low
    #上一根K线的收盘价
    close = last_row.close
    # 20日平均线
    SMA_20 = bollingData.SMA_20
    # 上轨线
    Upper_Band = bollingData.Upper_Band
    # 下轨线
    Lower_Band = bollingData.Lower_Band
    # 上一根K线的收盘价小于下轨下方 开多
    if (close < Lower_Band or globalData['currentPrice'] < SMA_20):
            return {
                'take_profit': SMA_20,
                'stop_loss': Lower_Band - 10, 
                'trend': 'Uptrend' 
            }
    # 上一根K线收盘价大于布林带上方做空
    if (close > Upper_Band or globalData['currentPrice'] > SMA_20):
            return {
                'take_profit': SMA_20,
                'stop_loss': Upper_Band + 10, 
                'trend': 'Downtrend' 
            }
    return None


def handleOrder():
    positions_total=mt5.positions_total()
    if positions_total >= 1:
        checkCurrentIsprofit()
        return
    if (globalData['deficiency'] >= 3):
        print('历史亏损订单量大于3，检查K线趋势是否处于单边')
    bandsRes = CalculateBollingerBands()
    if(bandsRes == None):
        print('无信号')
        return
    SellRequest = {
        "action": mt5.TRADE_ACTION_DEAL, # 交易请求类型
        "symbol": symbol,
        "volume": volume, # 请求的交易量（以手数表示）交易时的真实交易量
        "type": mt5.ORDER_TYPE_SELL, # 订单类型
        # "sl": bandsRes['stop_loss'], # 止损
        # "tp":  bandsRes['take_profit'], # 止盈
        "type_time": mt5.ORDER_TIME_GTC, # 订单到期类型
        "type_filling": mt5.ORDER_FILLING_IOC, #订单成交类型
    }
    BuyRequest = {
        "action": mt5.TRADE_ACTION_DEAL, # 交易请求类型
        "symbol": symbol,
        "volume": volume, # 请求的交易量（以手数表示）交易时的真实交易量
        "type": mt5.ORDER_TYPE_BUY, # 订单类型
        # "sl": bandsRes['stop_loss'], # 止损
        # "tp": bandsRes['take_profit'], # 止盈
        "type_time": mt5.ORDER_TIME_GTC, # 订单到期类型
        "type_filling": mt5.ORDER_FILLING_IOC, #订单成交类型
    }
    # 做多信号
    if bandsRes['trend'] == 'Uptrend':
        print('buy')
        result=mt5.order_send(BuyRequest)
        print(result)
        if result.retcode == 10009:
            print('success')
        else: print('fail',result)
    elif bandsRes['trend'] == 'Downtrend':
        print('sell')
        result=mt5.order_send(SellRequest)
        if result.retcode == 10009:
            print('success')
        else: print('fail',result)
    globalData['currentTime'] = globalData['lastTime']
    return

while True:
    handleOrder()
    time.sleep(1)


