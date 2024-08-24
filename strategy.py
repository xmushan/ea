import MetaTrader5 as mt5
from utils import open_order,checkCurrentIsprofit
from log import saveLog


# 震荡
def vibrate(indicatorData,symbol,lot_size,timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    middle = indicatorData['middle']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    # 买入条件：RSI和CCI处于超卖区，且价格低于下轨
    if (rsi <= 30 and cci <= -200 and ask < lower):
        checkCurrentIsprofit(symbol)
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask,timeframe)
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---做多")
    # 中轨买入条件：RSI和CCI处于中性区间，但价格仍低于中轨
    elif (40 <= rsi <= 50 and cci <= -100 and ask < middle):
        checkCurrentIsprofit(symbol)
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask,timeframe)
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---中轨做多")
    # 卖出条件：RSI和CCI处于超买区，且价格高于上轨
    elif (rsi >= 70 or cci >= 230 and bid > upper):
        checkCurrentIsprofit(symbol)
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid,timeframe)
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---做空")
     # 中轨卖出条件：RSI和CCI处于中性偏高区间，且价格高于上轨
    elif (50 <= rsi <= 60 and cci >= 100 and bid >= upper):
        checkCurrentIsprofit(symbol)
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid,timeframe)
        saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---中轨做空")
    else:
        checkCurrentIsprofit(symbol)
        print('无信号，检查收益')

# 趋势
def tend(indicatorData,symbol,timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    middle = indicatorData['middle']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    shortMa = indicatorData['shortMa']
    longMa = indicatorData['longMa']
    is_uptrend = shortMa > longMa
    is_downtrend = shortMa < longMa

    # 大趋势为上
    if (is_uptrend):
        if rsi <= 35 and cci <= -150 and ask < lower:
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask,timeframe)
        elif 45 <= rsi <= 55 and cci <= -50 and ask < middle:
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.01, mt5.ORDER_TYPE_BUY, ask,timeframe)
        else:
            print('无信号')
            print(rsi,cci)
            print(upper,lower) 
            print(bid,ask)
            print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
            checkCurrentIsprofit(symbol)
    # 大趋势为下
    if (is_downtrend):
        if ((rsi >= 75 or cci >= 180) and bid > upper):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid,timeframe)
        elif 55 <= rsi <= 70 and cci >= 100 and bid >= upper:
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.01, mt5.ORDER_TYPE_SELL, bid,timeframe)
        else:
            print('无信号')
            print(rsi,cci)
            print(upper,lower)
            print(bid,ask)
            print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
            checkCurrentIsprofit(symbol)
    if (rsi >= 40 and rsi <= 65):
        checkCurrentIsprofit(symbol)
        print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
        print('rsi指标在40 和65之间，检查收益')