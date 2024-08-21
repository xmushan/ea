import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone,time
from config import login, server, password
from cci import judegeOrder
import time as timeSleep
from log import saveLog
import pytz

# 初始化MT5
mt5.initialize()
authorized = mt5.login(login=login, password=password, server=server)
print(authorized)
if not authorized:
    print(f"Failed to login to MT5: {mt5.last_error()}")
    mt5.shutdown()
    exit()
# symbol = "GOLD_"  # 交易符号
# symbol = "XAUUSDm"  # 交易符号
symbol = "XAUUSDc"  # 交易符号
# symbol = "BTCUSDc"  # 交易符号
# symbol = "XAUUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
lot_size = 0.03  # 每次交易的手数
bars = 100  # 获取最近100个柱数据
slippage = 5  # 允许的价格滑点
last_kline_time = None  # 用于存储上一次K线时间戳
profit = 10 # 单比订单盈利额
totalProfit = 30 # 总盈利额度
retracement = -200 # 最大回撤

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

# 计算布林带
def CalculateBollingerBands(data): 
    df = pd.DataFrame(data)
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['STD_20'] = df['close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Lower_Band'] = df['SMA_20'] - (df['STD_20'] * 2)
    bollingData = df[['close', 'SMA_20', 'Upper_Band', 'Lower_Band','open']].iloc[-1]
    return bollingData.Upper_Band,bollingData.Lower_Band,bollingData.SMA_20

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
    filtered_orders_df = orders_df.loc[orders_df['symbol'] == symbol]
    for index, order in filtered_orders_df.iterrows():
        total = total + order['profit']
    # 最大回撤金额
    if (total < retracement):
        for index, order in filtered_orders_df.iterrows():
            set_protective_stop(order)
        timeSleep.sleep(3600)
        return
    if (flag == False):
        for index, order in filtered_orders_df.iterrows():
            set_protective_stop(order)
        return
    if (isAll == True and total >= totalProfit):
        for index, order in filtered_orders_df.iterrows():
            set_protective_stop(order)
        return
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

# 获取当前K线时间戳
def get_current_kline_time(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    if rates is None or len(rates) == 0:
        print(f"Failed to get rates: {mt5.last_error()}")
        return None
    rates_frame = pd.DataFrame(rates)
    utc_time = datetime.fromtimestamp(rates_frame['time'].iloc[-1], tz=timezone.utc)
    return utc_time

def is_within_business_hours(timezone_str='Asia/Shanghai'):
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
        return True
    # 判断欧洲盘时间
    if EuropeStartTime <= current_time <= EuropeEndTime:
        timeframe = mt5.TIMEFRAME_H1
        return True
    # 判断美盘时间（跨午夜）
    if (current_time >= UsaStartTime) or (current_time <= UsaopeEndTime):
        timeframe = mt5.TIMEFRAME_H1
        return True


def main():
    positions_total=mt5.positions_total()
    isWorking = is_within_business_hours()
    if (isWorking == False):
        print('时间不符合')
        return
    if positions_total >= 5:
        checkCurrentIsprofit(True,True)
        print('已达当前最大订单量')
        return
    short_ma = calculate_ma(symbol, timeframe, 50)  # 50周期均线
    long_ma = calculate_ma(symbol, timeframe, 200)  # 200周期均线
    # 检查趋势方向
    is_uptrend = short_ma > long_ma
    is_downtrend = short_ma < long_ma
    data = get_historical_data(symbol, timeframe)
    upper,lower,middle = CalculateBollingerBands(data)
    rsi = calculate_rsi(data,25)
    cci = calculate_cci(data,20)
    bid, ask = get_current_price(symbol)
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
    if (last_kline_time == current_kline_time):
        checkCurrentIsprofit()
        print('当前K线下过单')
        return
    # rsi指标小于35，执行做多操作
    if ((rsi <= 40 or cci <= -100) and ask < lower ):
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask)
        last_kline_time = current_kline_time
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---lower:{lower}---rsi指标小于35，执行做多操作")
    # rsi指标在40到50之间，cci < -120，并且价格接近布林带中轨，执行做多操作
    elif 45 <= rsi <= 55 and cci <= -120 and ask < middle and is_uptrend:
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask)
        last_kline_time = current_kline_time
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---is_uptrend:{is_uptrend}---布林带中轨，执行做多操作")
    # rsi指标大于75，执行做空操作
    elif ((rsi >= 75 and cci >= 155 and bid > upper) or (cci >= 280 and bid > upper)):
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid)
        last_kline_time = current_kline_time
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---bid:{bid}---upper:{upper}---rsi指标大于75，执行做空操作")
    # 做空操作
    elif ( 50 <= rsi <= 70 ) and cci >= 215 and bid > upper:
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid)
        last_kline_time = current_kline_time
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---is_downtrend:{is_downtrend}---布林带中轨，执行做空操作")
    # rsi指标在40 和65之间，检查收益
    elif (rsi >= 40 and rsi <= 65):
        checkCurrentIsprofit(True,True)
        print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
        print('rsi指标在40 和65之间，检查收益')
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---bid:{bid}---upper:{upper}---lower:{lower}---检查收益")
    else:
        print('无信号')
        print(rsi,cci)
        print(upper,lower) 
        print(bid,ask)
        print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
        checkCurrentIsprofit(True,True)
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---bid:{bid}---upper:{upper}---lower:{lower}---无信号")

while True:
    main()
    timeSleep.sleep(1)

