import MetaTrader5 as mt5
from utils import open_order,checkCurrentIsprofit
from log import saveLog

# 买价(Bid) – 卖价(Ask)
 # 单边测试
def vibrateTest (indicatorData, symbol, lot_size, timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    middle = indicatorData['middle']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    sma_short = indicatorData['sma_short']
    sma_long_ma = indicatorData['sma_long_ma']
    is_uptrend = sma_short > sma_long_ma
    is_downtrend = sma_short < sma_long_ma

    sma_diff = abs(sma_short - sma_long_ma)
    if (sma_diff <= 2 ):
        print('无信号')
        return

    if ( 3 <= sma_diff <= 8 ):
        # 单边上涨
        if (is_uptrend and middle <= ask <= upper and 50 <= rsi <= 70):
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
        # 单边下跌
        if (is_downtrend and middle >= bid >= lower and 50 >= rsi >= 30):
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
    if (bid > upper):
        if (rsi >= 65):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.01, mt5.ORDER_TYPE_SELL, bid, timeframe)
        if (rsi >= 70):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
        if (rsi >= 80):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)

    
    elif (ask < lower):
        if (rsi <= 35):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.01, mt5.ORDER_TYPE_BUY, bid, timeframe)
        if (rsi <= 30):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
        if (rsi <= 20):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, bid, timeframe)
    else:
        print('无信号')
        


    


def vibrate(indicatorData, symbol, lot_size, timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    middle = indicatorData['middle']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    sma_short = indicatorData['sma_short']
    sma_long_ma = indicatorData['sma_long_ma']
    is_uptrend = sma_short > sma_long_ma
    is_downtrend = sma_short < sma_long_ma
    sma_diff = abs(sma_short - sma_long_ma)
    if (sma_diff <= 3 ):
        print('无信号')
        return
    # 判断趋势并进行顺势交易
    if (rsi >= 75 and cci >= 250) and bid > upper:
        checkCurrentIsprofit(symbol)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)
    elif (rsi <= 30 and cci <= -100 and ask < lower):
        checkCurrentIsprofit(symbol)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
    elif (rsi <= 25 and cci <= -250) and ask < lower:
        checkCurrentIsprofit(symbol)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask, timeframe)
    elif (rsi >= 65 and cci >= 230) and bid > upper:
        checkCurrentIsprofit(symbol)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
    elif (50 <= rsi <= 55):
        checkCurrentIsprofit(symbol)
        print("检查收益")
    else:
        print("无明确趋势")
