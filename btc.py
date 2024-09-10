import MetaTrader5 as mt5
from utils.utils import get_sma,get_historical_data,get_current_price,calculate_rsi,calculate_cci,get_current_kline_time,open_order,CalculateBollingerBands,checkCurrentIsprofit

# symbol = "BTCUSDc"  # 交易符号
symbol = "BTCUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_M15  # 时间框架
retracement = -12

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
    if (rsi >= 75 and cci >= 250) and bid > upper:
        checkCurrentIsprofit(symbol,retracement)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)
    elif (rsi <= 30 and cci <= -150 and ask < lower):
        checkCurrentIsprofit(symbol,retracement)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, ask, timeframe)
    elif (rsi <= 25 and cci <= -250) and ask < lower:
        checkCurrentIsprofit(symbol,retracement)
        open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask, timeframe)
    elif (rsi >= 70 and cci >= 200) and bid > upper:
        checkCurrentIsprofit(symbol,retracement)
        open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
        print(rsi,cci)
    elif (35 < rsi < 45):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,order_type='sell')
        print("btc检查空单收益")
    elif (60 < rsi < 70):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,order_type='buy')
        print("btc检查多单收益")
    else:
        print("btc无明确趋势",rsi,cci)

def btcStrategy():
    # positions_total=mt5.positions_total()
    # if positions_total >= 5:
    #     checkCurrentIsprofit(symbol,retracement)
    #     print('已达当前最大订单量')
    #     return
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
