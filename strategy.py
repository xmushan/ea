#  计算单均线系统
def calculate_moving_average(currentPrice,SMA20,Upper_Band,Lower_Band,last_row):
    lastRowOpen = last_row.open
    lastRowClose = last_row.close
    # 反转
    if (lastRowOpen > SMA20 and lastRowClose > SMA20):
        return 'Uptrend' # 上升趋势 
    elif (lastRowOpen < SMA20 and lastRowClose < SMA20):
        return 'Downtrend' # 下降趋势
    elif (currentPrice < SMA20 and currentPrice < Lower_Band):
        return 'noSignal'
    elif (currentPrice > SMA20 and currentPrice > Upper_Band):
        return 'noSignal'
    else:
        return 'Hold'
