import MetaTrader5 as mt5
from utils import open_order,checkCurrentIsprofit
from log import saveLog


# 震荡
# def vibrate(indicatorData,symbol,lot_size,timeframe):
#     rsi = indicatorData['rsi']
#     cci = indicatorData['cci']
#     upper = indicatorData['upper']
#     lower = indicatorData['lower']
#     middle = indicatorData['middle']
#     ask = indicatorData['ask']
#     bid = indicatorData['bid']
#     sma_short = indicatorData['sma_short']
#     sma_long_ma = indicatorData['sma_long_ma']
#     is_uptrend = sma_short > sma_long_ma
#     is_downtrend = sma_short < sma_long_ma
#     # 买入条件：RSI和CCI处于超卖区，且价格低于下轨
#     if ((rsi <= 30 or cci <= -200) and ask < lower):
#         checkCurrentIsprofit(symbol)
#         open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask,timeframe)
#         saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---做多")
#     # 中轨买入条件：RSI和CCI处于中性区间，但价格仍低于中轨
#     elif (40 <= rsi <= 50 and cci <= -100 and ask < middle):
#         checkCurrentIsprofit(symbol)
#         open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask,timeframe)
#         saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---中轨做多")
#     # 卖出条件：RSI和CCI处于超买区，且价格高于上轨
#     elif (rsi >= 70 or cci >= 230 and bid > upper):
#         checkCurrentIsprofit(symbol)
#         open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid,timeframe)
#         saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---做空")
#      # 中轨卖出条件：RSI和CCI处于中性偏高区间，且价格高于上轨
#     elif (55 <= rsi <= 65 and cci >= 100 and bid >= upper):
#         checkCurrentIsprofit(symbol)
#         open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid,timeframe)
#         saveLog(f"rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}---中轨做空")
#     elif (rsi <= 15 and ask < lower):
#         checkCurrentIsprofit(symbol)
#         open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, bid,timeframe)
#     else:
#         checkCurrentIsprofit(symbol)
#         print('无信号，检查收益')

def vibrate1 (indicatorData, symbol, lot_size, timeframe):
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

    if (sma_diff <=1.5 ):
        checkCurrentIsprofit(symbol)
        print('无信号')
        return

    if ( 3 <= sma_diff <= 8 ):
        # 单边上涨
        if (is_uptrend and middle <= ask <= upper and 50 <= rsi <= 70):
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
    
        # 单边下跌
        if (is_downtrend and middle >= bid >= upper and 50 >= rsi >= 30):
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
    if (ask < lower):
        if (rsi <= 35):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.01, mt5.ORDER_TYPE_BUY, bid, timeframe)
        if (rsi <= 30):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
        if (rsi <= 20):
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, bid, timeframe)
    
            
        




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
    # 判断趋势并进行顺势交易
    if is_uptrend:
        if (rsi >= 75 or cci >= 250) and bid > upper:
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid, timeframe)
            saveLog(f"下降趋势，做空: rsi:{rsi}---cci:{cci}---bid:{bid}---upper:{upper}")
        elif (rsi <= 40 and cci <= -100 and ask < lower):
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask, timeframe)
            saveLog(f"上升趋势，中轨做多: rsi:{rsi}---cci:{cci}---ask:{ask}---middle:{middle}")
        elif 50 <= rsi <= 65 and cci >= 20 and ask < middle:
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask)
        elif (rsi <= 30 or cci <= -250) and ask < lower:
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask, timeframe)
            saveLog(f"强势上升趋势，做多: rsi:{rsi}---cci:{cci}---ask:{ask}---lower:{lower}")
        else:
            checkCurrentIsprofit(symbol)
            print("无明确趋势，保持观望")
    elif is_downtrend:
        if (rsi <= 30 or cci <= -250) and ask < lower:
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask, timeframe)
            saveLog(f"可能上升趋势，做多: rsi:{rsi}---cci:{cci}---ask:{ask}---lower:{lower}")
        elif rsi <= 50 and cci <= -50 and ask > middle:
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, ask)
        if (rsi >= 70 or cci >= 230) and bid > upper:
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid, timeframe)
            saveLog(f"下降趋势，做空: rsi:{rsi}---cci:{cci}---bid:{bid}---upper:{upper}")
        elif (55 <= rsi <= 65 and cci >= 100 and bid >= upper):
            checkCurrentIsprofit(symbol)
            open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid, timeframe)
            saveLog(f"下降趋势，中轨做空: rsi:{rsi}---cci:{cci}---bid:{bid}---upper:{upper}")
        else:
            checkCurrentIsprofit(symbol)
            print("无明确趋势，保持观望")
    else:
        # 如果不是明确的上升或下降趋势，则保持观望，或根据其他指标判断
        checkCurrentIsprofit(symbol)
        saveLog("无明确趋势，保持观望")


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
        elif 45 <= rsi <= 55 and cci <= -50 and ask < lower:
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask,timeframe)
        elif rsi >= 80 and cci >= 300 and bid > upper:
            checkCurrentIsprofit(symbol)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid,timeframe)
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
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid,timeframe)
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
