import MetaTrader5 as mt5
from utils.utils import get_sma,get_historical_data,get_current_price,calculate_rsi,calculate_cci,get_current_kline_time,open_order,CalculateBollingerBands,checkCurrentIsprofit

# symbol = "BTCUSDc"  # 交易符号
symbol = "BTCUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
retracement = -18


def callBack(order):
    order_type = order['type']
    bid, ask = get_current_price(symbol)
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'type': order_type,
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
    # if (sma_diff <= 3 ):
    #     print('无信号')
    #     return
    # 判断趋势并进行顺势交易
    checkCurrentIsprofit(symbol=symbol,retracement=retracement,onCallBack=callBack)
    if (rsi >= 75 and cci >= 250) and bid > upper:
        checkCurrentIsprofit(symbol = symbol,retracement=retracement)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)
    elif (rsi <= 30 and cci <= -150 and ask < lower):
        checkCurrentIsprofit(symbol=symbol,retracement=retracement)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
    elif (rsi <= 25 and cci <= -250) and ask < lower:
        checkCurrentIsprofit(symbol=symbol,retracement=retracement)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask, timeframe)
    elif (rsi >= 72 and cci >= 220) and bid > upper:
        checkCurrentIsprofit(symbol=symbol,retracement=retracement)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
        print(rsi,cci)
    elif (cci <= 0):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,order_type='sell')
        print("btc检查空单收益")
    elif (cci >= 50):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,order_type='buy')
        print("btc检查多单收益")
    else:
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
        print("btc无明确趋势",rsi,cci)

def btcStrategy():
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
