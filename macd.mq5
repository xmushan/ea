//+------------------------------------------------------------------+
//| MACD + RSI + MA + Bollinger Bands EA                             |
//| 综合使用 MACD、RSI、移动平均线和布林带指标的交易策略            |
//+------------------------------------------------------------------+
#property strict
#include <Trade/Trade.mqh>

// 交易参数
input double LotSize = 0.1;        // 交易手数
input int Magic = 8898;            // 魔术数字

// MACD 指标参数
input int MACD_Fast = 12;          // MACD 快线周期
input int MACD_Slow = 26;          // MACD 慢线周期
input int MACD_Signal = 9;         // MACD 信号周期

// RSI 指标参数
input int RSI_Period = 14;         // RSI 周期

// 移动平均线参数
input int MA_Period = 20;          // 移动平均线周期

// 布林带参数
input int BB_Period = 20;          // 布林带周期
input double BB_Dev = 2.0;         // 布林带标准差

// ATR 指标参数（用于动态止损止盈）
input int ATR_Period = 14;         // ATR 周期
input double StopLoss_Multiplier = 1.5;  // 止损乘数
input double TakeProfit_Multiplier = 3.0; // 止盈乘数

// 全局变量
int macdHandle, rsiHandle, maHandle, bbHandle, atrHandle;
CTrade trade;
datetime lastBarTime = 0;

//+------------------------------------------------------------------+
//| 初始化函数                                                       |
//+------------------------------------------------------------------+
int OnInit()
{
   // 创建 MACD 指标句柄
   macdHandle = iMACD(_Symbol, _Period, MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE);
   
   // 创建 RSI 指标句柄
   rsiHandle = iRSI(_Symbol, _Period, RSI_Period, PRICE_CLOSE);
   
   // 创建移动平均线指标句柄
   maHandle = iMA(_Symbol, _Period, MA_Period, 0, MODE_SMA, PRICE_CLOSE);
   
   // 创建布林带指标句柄
   bbHandle = iBands(_Symbol, _Period, BB_Period, 0, BB_Dev, PRICE_CLOSE);
   
   // 创建 ATR 指标句柄
   atrHandle = iATR(_Symbol, _Period, ATR_Period);
   
   // 设置交易对象的魔术数字
   trade.SetExpertMagicNumber(Magic);
   
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| 获取当前仓位函数                                                 |
//+------------------------------------------------------------------+
int GetPosition()
{
   // 遍历所有仓位
   for(int i=0; i<PositionsTotal(); i++)
   {
      // 获取仓位 ticket
      ulong ticket = PositionGetTicket(i);
      
      // 选择该仓位
      if(PositionSelectByTicket(ticket))
      {
         // 检查是否是本 EA 开的当前品种的仓位
         if(PositionGetInteger(POSITION_MAGIC) == Magic &&
            PositionGetString(POSITION_SYMBOL) == _Symbol)
         {
            // 返回仓位类型：0 为买入，1 为卖出
            return (int)PositionGetInteger(POSITION_TYPE);
         }
      }
   }
   
   // 没有找到匹配的仓位，返回 -1
   return -1;
}

//+------------------------------------------------------------------+
//| 主交易函数                                                       |
//+------------------------------------------------------------------+
void OnTick()
{
   // === 新 K 线限制 ===
   datetime barTime = iTime(_Symbol, _Period, 0);
   if(barTime == lastBarTime) return; // 如果是同一根 K 线，直接返回
   lastBarTime = barTime; // 更新最后处理的 K 线时间

   // === 指标数据 ===
   // MACD 数据
   double macdMain[], macdSignal[];
   ArraySetAsSeries(macdMain, true);
   ArraySetAsSeries(macdSignal, true);
   
   // RSI 数据
   double rsi[];
   ArraySetAsSeries(rsi, true);
   
   // 移动平均线数据
   double ma[];
   ArraySetAsSeries(ma, true);
   
   // 布林带数据
   double bbUpper[], bbMiddle[], bbLower[];
   ArraySetAsSeries(bbUpper, true);
   ArraySetAsSeries(bbMiddle, true);
   ArraySetAsSeries(bbLower, true);
   
   // ATR 数据
   double atr[];
   ArraySetAsSeries(atr, true);

   // 复制指标数据到数组（获取前一根 K 线的数据，索引为 1）
   CopyBuffer(macdHandle, 0, 1, 2, macdMain);     // MACD 主线
   CopyBuffer(macdHandle, 1, 2, 2, macdSignal);   // MACD 信号线
   CopyBuffer(rsiHandle, 0, 1, 1, rsi);           // RSI
   CopyBuffer(maHandle, 0, 1, 1, ma);             // 移动平均线
   CopyBuffer(bbHandle, 0, 1, 1, bbMiddle);       // 布林带中轨
   CopyBuffer(bbHandle, 1, 1, 1, bbUpper);        // 布林带上轨
   CopyBuffer(bbHandle, 2, 1, 1, bbLower);        // 布林带下轨
   CopyBuffer(atrHandle, 0, 1, 1, atr);           // ATR

   // === 市场数据 ===
   double close = iClose(_Symbol, _Period, 1);     // 前一根 K 线收盘价
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK); // 当前买价
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID); // 当前卖价

   // === 计算止损止盈 ===
   double stopLoss = atr[0] * StopLoss_Multiplier;   // 止损
   double takeProfit = atr[0] * TakeProfit_Multiplier; // 止盈

   // === 获取当前仓位 ===
   int pos = GetPosition();

   // === 指标信号判断 ===
   // MACD 金叉：主线从下往上穿过信号线
   bool macdGoldenCross = macdMain[1] < macdSignal[1] && macdMain[0] > macdSignal[0];
   
   // MACD 死叉：主线从上往下穿过信号线
   bool macdDeathCross = macdMain[1] > macdSignal[1] && macdMain[0] < macdSignal[0];
   
   // RSI 在 30-70 之间（避免超买超卖）
   bool rsiNeutral = rsi[0] > 30 && rsi[0] < 70;
   
   // 价格在移动平均线上方（多头趋势）
   bool priceAboveMA = close > ma[0];
   
   // 价格在移动平均线下方（空头趋势）
   bool priceBelowMA = close < ma[0];
   
   // 价格突破布林带中轨向上
   bool priceBreakAboveBB = close > bbMiddle[0];
   
   // 价格突破布林带中轨向下
   bool priceBreakBelowBB = close < bbMiddle[0];

   // === 交易信号 ===
   // 买入信号
   bool buySignal = macdGoldenCross && rsiNeutral && priceAboveMA && priceBreakAboveBB;
   
   // 卖出信号
   bool sellSignal = macdDeathCross && rsiNeutral && priceBelowMA && priceBreakBelowBB;

   // === 执行交易 ===
   // 如果没有持仓且有买入信号，执行买入
   if(pos == -1 && buySignal)
   {
      trade.Buy(LotSize, _Symbol, ask, ask - stopLoss, ask + takeProfit);
   }
   
   // 如果没有持仓且有卖出信号，执行卖出
   if(pos == -1 && sellSignal)
   {
      trade.Sell(LotSize, _Symbol, bid, bid + stopLoss, bid - takeProfit);
   }
}
