import MetaTrader5 as mt5
from datetime import datetime,time
from config import login, server, password
from utils.utils import checkAllIsprofit
import time as timeSleep
import pytz
from gold import goldStrategy
from btc import btcStrategy

# 初始化MT5
mt5.initialize()
authorized = mt5.login(login=login, password=password, server=server)

print('登录成功')
if not authorized:
    print(f"Failed to login to MT5: {mt5.last_error()}")
    mt5.login(login=login, password=password, server=server)
    # mt5.shutdown()
    # exit()

def is_within_business_hours(timezone_str='Asia/Shanghai'):
    global timeframe
    # 获取指定时区的当前时间
    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone).time()
    # 亚洲盘时间
    asiaStartTime = time(7, 0, 0)
    asiaEndTime = time(15, 30, 0)
    # 欧洲盘时间
    EuropeStartTime = time(15, 30, 0)
    EuropeEndTime = time(19, 30, 0)
    # 美盘时间
    UsaStartTime = time(20, 30, 0)
    UsaopeEndTime = time(7, 0, 0)
    # 判断亚洲盘时间
    if asiaStartTime <= current_time <= asiaEndTime:
        goldStrategy()
        btcStrategy()
        return
    # # 判断欧洲盘时间
    if EuropeStartTime <= current_time <= EuropeEndTime:
        goldStrategy()
        btcStrategy()
        return
    # # 判断美盘时间（跨午夜）
    if (current_time >= UsaStartTime) or (current_time <= UsaopeEndTime):
        print('美盘时间，不做单')
        # goldStrategy()
        # btcStrategy()
        checkAllIsprofit()
        return


def main():
    is_within_business_hours()

while True:
    main()
    timeSleep.sleep(1)

