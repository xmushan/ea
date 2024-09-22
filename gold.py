import MetaTrader5 as mt5
from utils.utils import get_historical_data,get_current_price,calculate_rsi,calculate_cci,get_current_kline_time,open_order,CalculateBollingerBands,checkCurrentIsprofit,get_sma

# symbol = "XAUUSDc"  # 交易符号
symbol = "XAUUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
retracement = -10
last_kline_time = None  # 用于存储上一次K线时间戳

def callBack(order):
    order_type = order['type']
    bid, ask = get_current_price(symbol)
    type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'type': type,
        'volume': 0.02,
        'price': bid,
        'magic': 234000,
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == 10009:
        print('success')
    else:
        print(result)

def vibrate(indicatorData, symbol, timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    sma_short = indicatorData['sma_short']
    sma_long_ma = indicatorData['sma_long_ma']
    sma_diff = abs(sma_short - sma_long_ma)
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
    if (last_kline_time == current_kline_time):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
        print('当前K线下过单')
        return
    checkCurrentIsprofit(symbol=symbol,retracement=retracement,onCallBack=callBack)
    if (bid < upper and ask > lower):
            # 判断趋势并进行顺势交易
        if ( 110 >= cci >= 100):
            checkCurrentIsprofit(symbol=symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        elif (125 >= cci >= 120):
            checkCurrentIsprofit(symbol=symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        elif (-100 <= cci <= -110):
            checkCurrentIsprofit(symbol=symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
            last_kline_time = current_kline_time
        elif ( 115 <= cci <= -120):
            checkCurrentIsprofit(symbol = symbol,retracement= retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
            last_kline_time = current_kline_time
    else:
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
        print("gold无明确趋势",rsi,cci)

def goldStrategy():
    data = get_historical_data(symbol, timeframe)
    upper,lower,middle = CalculateBollingerBands(data)
    rsi = calculate_rsi(data,20)
    cci = calculate_cci(data,20)
    bid, ask = get_current_price(symbol)
    sma_short = get_sma(data, 14)
    sma_long_ma = get_sma(data, 50)
    indicatorData = {
        'rsi': rsi,
        'cci': cci,
        'upper': upper,
        'lower': lower,
        'middle': middle,
        'sma_short': sma_short,
        'sma_long_ma': sma_long_ma,
        'ask': ask,
        'bid': bid,
    }
    vibrate(indicatorData,symbol,timeframe)
