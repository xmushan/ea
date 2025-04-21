import MetaTrader5 as mt5
import pandas as pd
import ta
from ta.trend import CCIIndicator
from utils.utils import get_historical_data,get_current_price,calculate_rsi,calculate_cci,get_current_kline_time,open_order,CalculateBollingerBands,checkCurrentIsprofit,get_sma

# symbol = "XAUUSDc"  # 交易符号
symbol = "XAUUSDm"  # 交易符号
timeframe = mt5.TIMEFRAME_H1  # 时间框架
retracement = -20
last_kline_time = None  # 用于存储上一次K线时间戳

def callBack(order):
    order_type = order['type']
    bid, ask = get_current_price(symbol)
    type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'type': mt5.ORDER_TYPE_BUY,
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


def analyze_sentiment_from_txt(filename='gold_analysis.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 关键词判断
        if "多" in content:
            return "多"
        elif "空" in content:
            return "空"
        elif "中性" in content:
            return "等"
        else:
            return "❓ 无明确信号，分析内容不包含常见关键词"

    except FileNotFoundError:
        return "🚫 文件未找到，请检查文件路径或名称是否正确"

def load_and_prepare_data():
    get_historical_data(symbol, timeframe)
    df = pd.read_csv('gold_h1.csv')
    df = df.rename(columns={
        '时间': 'time',
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量': 'tick_volume',
        '点差': 'spread',
        '实际成交量': 'real_volume'
    })
    return df

def compute_indicators():
    df = load_and_prepare_data()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd_diff()
    df['sma_fast'] = ta.trend.SMAIndicator(df['close'], window=5).sma_indicator()
    df['sma_slow'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
    df['cci'] = CCIIndicator(df['high'], df['low'], df['close'], window=20).cci()
    return df.iloc[-1]


def vibrate1(indicatorData, symbol, timeframe):
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
    tend = analyze_sentiment_from_txt()
    if (last_kline_time == current_kline_time):
        checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
        print('当前K线下过单')
        return
    # 当前订单被止损之后，继续追加下单
    checkCurrentIsprofit(symbol=symbol,retracement=retracement,onCallBack=callBack)

    print(tend)
    # 多
    if (tend == '多'):
        if ((28 <= rsi <= 30) and (-150 <= cci <=  -145)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
            last_kline_time = current_kline_time
        if ((22 <= rsi <= 25) and (-200 <= cci <=  -195)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, bid, timeframe)
            last_kline_time = current_kline_time
        if ((15 <= rsi <= 20) and (-280 <= cci <=  -260)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.04, mt5.ORDER_TYPE_BUY, bid, timeframe)
            last_kline_time = current_kline_time
        else:
            print("gold无明确趋势",rsi,cci)    
    # 空
    elif (tend == '空'):
        if ((70 <= rsi <= 72) and (200 <= cci <= 220)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.02, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        if ((80 <= rsi <= 82) and (250 <= cci <= 260)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.03, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        if ((85 <= rsi) and (280 <= cci)):
            checkCurrentIsprofit(symbol = symbol,retracement=retracement)
            open_order(symbol, 0.04, mt5.ORDER_TYPE_SELL, bid, timeframe)
            last_kline_time = current_kline_time
        else:
            checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
            print("gold无明确趋势",rsi,cci)  
    else:
        print("gold无明确趋势",rsi,cci)    



    # signals = []
    # latest_row = compute_indicators()
    # bid, ask = get_current_price(symbol)
    # global last_kline_time
    # current_kline_time = get_current_kline_time(symbol, timeframe)
    
    # if (last_kline_time == current_kline_time):
    #     checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
    #     print('当前K线下过单')
    #     return
    # if (analyze_sentiment_from_txt() == '多'):
    #     signals.append("🤖 AI 分析倾向于利多")
    # if latest_row['sma_fast'] > latest_row['sma_slow']:
    #     signals.append("📈 均线向上突破（短期趋势看涨）")
    # if latest_row['macd'] > 0:
    #     signals.append("⚡ MACD 动能为正（动能支持上涨）")

    # # 逢低做多条件
    # if  ( -150 <= latest_row['cci'] <=  -145):
    #     checkCurrentIsprofit(symbol=symbol, retracement=retracement)
    #     open_order(symbol, 0.03, mt5.ORDER_TYPE_BUY, ask, timeframe)
    #     last_kline_time = current_kline_time
    # print(latest_row['cci'],signals)
    # return

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
    vibrate1(indicatorData,symbol,timeframe)
