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
        print('AI 分析结果: ${content}')
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


# 获取最近20根K线的阻力位（最高价）和支撑位（最低价）
def get_resistance_support(window=20):
    df = pd.read_csv('gold_h1.csv')
    resistance = df['high'][-window:].max()  # 阻力位
    support = df['low'][-window:].min()  # 支撑位
    return resistance, support


def goldStrategy():
    latest = compute_indicators()
    resistance, support = get_resistance_support()
    bid, ask = get_current_price(symbol)
    # 判断AI分析的情绪
    if analyze_sentiment_from_txt() != '多':
        print("🔍 当前宏观趋势非多，策略取消。")
        return

    print(f"📊 当前收盘价：{latest['close']:.2f}，阻力位：{resistance:.2f}，支撑位：{support:.2f}")
    global last_kline_time
    current_kline_time = get_current_kline_time(symbol, timeframe)
    signals = []
    if latest['close'] > resistance:
        signals.append("💥 突破阻力位")
    if latest['macd'] > 0:
        signals.append("📈 MACD 动能支持上涨")
    if latest['sma_fast'] > latest['sma_slow']:
        signals.append("✅ 均线金叉")

    # 满足条件进行下单
    if len(signals) >= 2:
        print("📈 满足做多条件：\n" + "\n".join(signals))
        if (last_kline_time == current_kline_time):
            # checkCurrentIsprofit(symbol = symbol,retracement = retracement,profit=5)
            print('当前K线下过单')
            return
        # 突破策略：当前价格突破阻力位
        if bid > resistance:
            print(f"🔔 当前价格突破阻力位，准备下单做多！")
            last_kline_time = current_kline_time
            open_order(symbol, 0.04, mt5.ORDER_TYPE_BUY, bid, timeframe)
        # 回调策略：当前价格接近支撑位
        elif support < bid and bid < (support + 3):
            print(f"🔔 当前价格接近支撑位，准备低吸！")
            last_kline_time = current_kline_time
            open_order(symbol, 0.1, mt5.ORDER_TYPE_BUY, bid, timeframe)
        elif latest['rsi'] < 30:
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
        # 判断 CCI 是否适合做多
        elif latest['cci'] < 100:
            open_order(symbol, 0.02, mt5.ORDER_TYPE_BUY, bid, timeframe)
        else:
            print(bid,resistance,support)
    else:
        print("⏳ 信号不够明确，暂不进场。\n" + "\n".join(signals),support+3)

