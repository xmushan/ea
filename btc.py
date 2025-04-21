import MetaTrader5 as mt5
from utils.utils import is_within_business_hours,get_sma,get_historical_data,get_current_price,calculate_rsi,calculate_cci,get_current_kline_time,open_order,CalculateBollingerBands,checkCurrentIsprofit

# symbol = "BTCUSDc"  # 交易符号
symbol = "BTCUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
retracement = -15
last_kline_time = None  # 用于存储上一次K线时间戳

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


def vibrate1(indicatorData, symbol, timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    sma_short = indicatorData['sma_short']
    sma_long_ma = indicatorData['sma_long_ma']
    daysRsi = indicatorData['daysRsi']
    sma_diff = abs(sma_short - sma_long_ma)
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
    
    if (last_kline_time == current_kline_time):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
        print('当前K线下过单')
        return
    # 当前订单被止损之后，继续追加下单
    checkCurrentIsprofit(symbol=symbol,retracement=retracement,onCallBack=callBack)

    # 多
    if (bid <= lower):
        if ((28 <= rsi <= 30) or (-150 <= cci <=  -145)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
            last_kline_time = current_kline_time
        if ((22 <= rsi <= 25) or (-200 <= cci <=  -195)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, bid, timeframe)
            last_kline_time = current_kline_time
        if ((15 <= rsi <= 20) or (-280 <= cci <=  -260)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.04, mt5.ORDER_TYPE_BUY, bid, timeframe)
            last_kline_time = current_kline_time
    else:
        print("btc无明确趋势",rsi,cci)

    # 空
    if (ask >= upper):
        if ((70 <= rsi <= 72) or (200 <= cci <= 220)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        if ((80 <= rsi <= 82) or (250 <= cci <= 260)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        if ((85 <= rsi) or (280 <= cci)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.04, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
    else:
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
        print("btc无明确趋势",rsi,cci)


def vibrate2(indicatorData, symbol, timeframe):
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    upper = indicatorData['upper']
    lower = indicatorData['lower']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    sma_short = indicatorData['sma_short']
    sma_long_ma = indicatorData['sma_long_ma']
    daysRsi = indicatorData['daysRsi']
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
    
    if last_kline_time == current_kline_time:
        checkCurrentIsprofit(symbol=symbol, retracement=retracement, profit=10)
        print('当前K线下过单')
        return

    # 当前订单被止损之后，继续追加下单
    checkCurrentIsprofit(symbol=symbol, retracement=retracement, onCallBack=callBack)

    # 逢低做多条件
    if ask < lower and (rsi <= 30 or cci <= -200) and daysRsi < 45:
        checkCurrentIsprofit(symbol=symbol, retracement=retracement)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask, timeframe)
        last_kline_time = current_kline_time
        print(f"逢低做多: ask={ask}, rsi={rsi}, cci={cci}")

    # 增强逢低做多条件
    elif ask < lower and (40 <= rsi <= 50 and cci <= -150) and daysRsi < 45:
        checkCurrentIsprofit(symbol=symbol, retracement=retracement)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
        last_kline_time = current_kline_time
        print(f"增强逢低做多: ask={ask}, rsi={rsi}, cci={cci}")

    # 逢高做空条件
    if bid > upper and (rsi >= 75 or cci >= 200) and daysRsi > 65:
        checkCurrentIsprofit(symbol=symbol, retracement=retracement)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)
        last_kline_time = current_kline_time
        print(f"逢低做多: ask={ask}, rsi={rsi}, cci={cci}")

    # 增强逢高做空条件
    elif bid > upper and (65 <= rsi <= 70 and cci >= 150) and daysRsi > 65:
        checkCurrentIsprofit(symbol=symbol, retracement=retracement)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
        last_kline_time = current_kline_time
        print(f"增强逢低做多: ask={ask}, rsi={rsi}, cci={cci}")


    else:
        checkCurrentIsprofit(symbol=symbol, retracement=retracement, profit=10)
        print("btc无明确做多信号", rsi, cci)


def main(indicatorData):
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
    rsi = indicatorData['rsi']
    cci = indicatorData['cci']
    ask = indicatorData['ask']
    bid = indicatorData['bid']
    # 多单
    if (cci <= -150):
        open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
    print(rsi,cci)




def btcStrategy():
    data = get_historical_data(symbol, timeframe)
    # 获取一天的数据
    daysData = get_historical_data(symbol,mt5.TIMEFRAME_D1 )
    upper,lower,middle = CalculateBollingerBands(data)
    rsi = calculate_rsi(data,12)
    daysRsi = calculate_rsi(daysData,20)
    cci = calculate_cci(data,12)
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
        'daysRsi': daysRsi
    }
    main(indicatorData)
    # if (daysRsi >= 65 or daysRsi <= 40):
    #     vibrate2(indicatorData,symbol,timeframe)
    # else:
    # vibrate1(indicatorData,symbol,timeframe)
    

