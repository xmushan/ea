import MetaTrader5 as mt5
from rsi import checkCurrentIsprofit,open_order

symbol = "XAUUSDm"  # 交易符号
lot_size = 0.03  # 每次交易的手数

# 震荡
def vibrate(indicatorData):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    middle = indicatorData['middle']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    if ((rsi <= 35 or cci <= -180) and ask < lower):
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask)
    elif 45 <= rsi <= 55 and cci <= -120 and ask < middle:
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_BUY, ask)
    elif ((rsi >= 75 and cci >= 155 and bid > upper) or (cci >= 280 and bid > upper)):
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid)
    elif 55 <= rsi <= 70 and cci >= 100 and bid >= upper:
        checkCurrentIsprofit()
        open_order(symbol, lot_size, mt5.ORDER_TYPE_SELL, bid)
    else:
        checkCurrentIsprofit()

# 趋势
def tend(indicatorData):
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
        if ((rsi <= 35 or cci <= -150) and ask < lower):
            checkCurrentIsprofit()
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask)
        elif 45 <= rsi <= 55 and cci <= -50 and ask < middle:
            checkCurrentIsprofit()
            open_order(symbol, 0.01, mt5.ORDER_TYPE_BUY, ask)
        else:
            print('无信号')
            print(rsi,cci)
            print(upper,lower) 
            print(bid,ask)
            print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
            checkCurrentIsprofit(True,True)
    # 大趋势为下
    if (is_downtrend):
        if ((rsi >= 75 or cci >= 180) and bid > upper):
            checkCurrentIsprofit()
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid)
        elif 55 <= rsi <= 70 and cci >= 100 and bid >= upper:
            checkCurrentIsprofit()
            open_order(symbol, 0.01, mt5.ORDER_TYPE_SELL, bid)
        else:
            print('无信号')
            print(rsi,cci)
            print(upper,lower)
            print(bid,ask)
            print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
            checkCurrentIsprofit(True,True)
    if (rsi >= 40 and rsi <= 65):
        checkCurrentIsprofit(True,True)
        print(f'is_downtrend:{is_downtrend},is_uptrend:{is_uptrend}')
        print('rsi指标在40 和65之间，检查收益')