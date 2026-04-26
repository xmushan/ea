//+------------------------------------------------------------------+
//| RSI + Bollinger Strategy                                         |
//+------------------------------------------------------------------+
#property strict

// 包含交易类库
#include <Trade/Trade.mqh>
// 创建交易对象
CTrade trade;

// 输入参数：布林带周期
input int    BB_Period = 20;
// 输入参数：布林带偏差
input double BB_Deviation = 2.0;
// 输入参数：RSI指标周期
input int    RSI_Period = 14;

// 输入参数：ATR指标周期
input int    ATR_Period = 14;
// 输入参数：ATR倍数（用于计算止损）
input double ATR_Multiplier = 2.0;

// 输入参数：魔术数字
input int    Magic = 123456;
// 输入参数：冷却期（交易后等待的K线数）
input int    CooldownBars = 3;
// 输入参数：交易量
input double Lot = 0.01;

// 布林带指标句柄
int bbHandle;
// RSI指标句柄
int rsiHandle;
// ATR指标句柄
int atrHandle;

// 上次交易的K线时间戳
 datetime lastTradeTime = 0;
// 上次交易的K线编号
int lastTradeBar = -100;
// 标记是否满足前置条件
bool preCondition = false;

//+------------------------------------------------------------------+
// 计算近N根K线的平均实体大小
//+------------------------------------------------------------------+
double CalculateAverageBodySize(int period)
{
   double totalBodySize = 0;
   int count = 0;
   
   for(int i = 0; i < period && i < Bars(_Symbol, _Period); i++)
   {
      double open = iOpen(_Symbol, _Period, i);
      double close = iClose(_Symbol, _Period, i);
      double bodySize = MathAbs(close - open);
      totalBodySize += bodySize;
      count++;
   }
   
   if(count > 0)
      return totalBodySize / count;
   else
      return 0;
}

//+------------------------------------------------------------------+
// 初始化函数
//+------------------------------------------------------------------+
int OnInit()
{
   // 创建布林带指标
   bbHandle = iBands(_Symbol, _Period, BB_Period, 0, BB_Deviation, PRICE_CLOSE);
   // 创建RSI指标
   rsiHandle = iRSI(_Symbol, _Period, RSI_Period, PRICE_CLOSE);
   // 创建ATR指标
   atrHandle = iATR(_Symbol, _Period, ATR_Period);

   // 检查指标创建是否成功
   if(bbHandle == INVALID_HANDLE || rsiHandle == INVALID_HANDLE || atrHandle == INVALID_HANDLE)
      return INIT_FAILED;

   // 初始化成功
   return INIT_SUCCEEDED;
}
//+------------------------------------------------------------------+
// 反初始化函数
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // 释放布林带指标
   IndicatorRelease(bbHandle);
   // 释放RSI指标
   IndicatorRelease(rsiHandle);
   // 释放ATR指标
   IndicatorRelease(atrHandle);
}
//+------------------------------------------------------------------+
// 每tick执行的函数
//+------------------------------------------------------------------+
void OnTick()
{
   // 获取当前K线数量
   int currentBar = Bars(_Symbol, _Period);

   // 检查是否在冷却期内
   if(currentBar - lastTradeBar < CooldownBars)
      return;

   // 获取当前K线时间戳
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   // 检查是否在同一根K线上
   if(currentBarTime == lastTradeTime)
      return;

   // 定义数组用于存储指标数据
   double upper[], lower[], middle[], cci[], rsi[];

   // 获取布林带中轨数据 (缓冲区索引 0)
   if(CopyBuffer(bbHandle, 0, 0, 1, middle) <= 0) return;
   // 获取布林带上轨数据 (缓冲区索引 1)
   if(CopyBuffer(bbHandle, 1, 0, 1, upper) <= 0) return;
   // 获取布林带下轨数据 (缓冲区索引 2)
   if(CopyBuffer(bbHandle, 2, 0, 1, lower) <= 0) return;
   // 获取RSI数据
   if(CopyBuffer(rsiHandle, 0, 0, 1, rsi) <= 0) return;

   // 获取当前价格
   double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   // 标记是否已交易
   bool traded = false;

   // 打印指标数据
   Print("指标数据: 价格=", price, " 上轨=", upper[0], " 中轨=", middle[0], " 下轨=", lower[0], " RSI=", rsi[0]);

   // 获取当前K线数据
   double open0 = iOpen(_Symbol, _Period, 0);
   double close0 = iClose(_Symbol, _Period, 0);
   double high0 = iHigh(_Symbol, _Period, 0);
   double low0 = iLow(_Symbol, _Period, 0);

   // 获取上一根K线数据
   double open1 = iOpen(_Symbol, _Period, 1);
   double close1 = iClose(_Symbol, _Period, 1);
   double high1 = iHigh(_Symbol, _Period, 1);
   double low1 = iLow(_Symbol, _Period, 1);

   // 计算近20根K线平均实体大小
   double avgBodySize = CalculateAverageBodySize(20);

   // 前置条件判断（基于当前K线）
   if(rsi[0] >= 70)
   {
      double prevBodySize = close1 - open1;
      Print(prevBodySize,"currentBodySize",avgBodySize * 0.5,close0,open0);
      if(prevBodySize < avgBodySize * 0.5)
      {
         preCondition = true;
         Print("前置条件满足: 阳线实体很小，RSI超买");
      }
   }

   // ===== 做空条件 =====
   if(preCondition && price > upper[0])
   {
      Print("做空条件满足: 上一根是大阴线，当前价格突破上轨");
      if (rsi[0] > 75) {
        traded = tradeSell(0.02);
      } else if (rsi[0] > 70) {
        traded = tradeSell(0.01);
      }
   }

   // ===== 做多条件 =====
   if(!traded && !preCondition && price < lower[0] && rsi[0] < 30)
   {
      Print("做多条件满足: 价格<", lower[0], " RSI<", rsi[0]);
      traded = tradeBuy(0.01);
   }

   // 如果已交易，更新交易时间和K线编号
   if(traded)
   {
      lastTradeTime = currentBarTime;
      lastTradeBar = currentBar;
   }
}
//+------------------------------------------------------------------+
// 开多单
//+------------------------------------------------------------------+
bool tradeBuy(double lotSize)
{
   // 定义ATR数组
   double atr[];
   // 获取ATR数据
   if(CopyBuffer(atrHandle, 0, 0, 1, atr) <= 0)
      return false;

   // 获取当前买价
   double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   // 计算止损价格
   double sl = price - atr[0] * ATR_Multiplier;
   // 标准化止损价格
   sl = NormalizeDouble(sl, _Digits);

   // 计算止盈价格（1R）
   double tp = price + (price - sl); // 1R
   // 标准化止盈价格
   tp = NormalizeDouble(tp, _Digits);

   // 定义交易请求和结果对象
   MqlTradeRequest req;
   MqlTradeResult res;
   // 清空请求对象
   ZeroMemory(req);

   // 设置交易动作
   req.action = TRADE_ACTION_DEAL;
   // 设置交易品种
   req.symbol = _Symbol;
   // 设置交易量
   req.volume = lotSize;
   // 设置订单类型
   req.type = ORDER_TYPE_BUY;
   // 设置交易价格
   req.price = price;
   // 设置止损价格
   req.sl = sl;
   // 设置止盈价格
   req.tp = tp;
   // 设置魔术数字
   req.magic = Magic;
   // 设置价格偏差
   req.deviation = 10;
   // 设置订单填充类型
   req.type_filling = ORDER_FILLING_IOC;

   // 发送订单
   if(!OrderSend(req, res) || res.retcode != TRADE_RETCODE_DONE)
   {
      // 打印失败信息
      Print("BUY失败:", res.retcode);
      return false;
   }

   // 打印交易成功信息
   Print("做多成功: 价格=", price, " 止损=", sl, " 止盈=", tp, " 仓位=", lotSize);

   // 交易成功
   return true;
}
//+------------------------------------------------------------------+
// 开空单
//+------------------------------------------------------------------+
bool tradeSell(double lotSize)
{
   // 定义ATR数组
   double atr[];
   // 获取ATR数据
   if(CopyBuffer(atrHandle, 0, 0, 1, atr) <= 0)
      return false;

   // 获取当前卖价
   double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   // 计算止损价格
   double sl = price + atr[0] * ATR_Multiplier;
   // 标准化止损价格
   sl = NormalizeDouble(sl, _Digits);

   // 计算止盈价格（1R）
   double tp = price - (sl - price); // 1R
   // 标准化止盈价格
   tp = NormalizeDouble(tp, _Digits);

   // 定义交易请求和结果对象
   MqlTradeRequest req;
   MqlTradeResult res;
   // 清空请求对象
   ZeroMemory(req);

   // 设置交易动作
   req.action = TRADE_ACTION_DEAL;
   // 设置交易品种
   req.symbol = _Symbol;
   // 设置交易量
   req.volume = lotSize;
   // 设置订单类型
   req.type = ORDER_TYPE_SELL;
   // 设置交易价格
   req.price = price;
   // 设置止损价格
   req.sl = sl;
   // 设置止盈价格
   req.tp = tp;
   // 设置魔术数字
   req.magic = Magic;
   // 设置价格偏差
   req.deviation = 10;
   // 设置订单填充类型
   req.type_filling = ORDER_FILLING_IOC;

   // 发送订单
   if(!OrderSend(req, res) || res.retcode != TRADE_RETCODE_DONE)
   {
      // 打印失败信息
      Print("SELL失败:", res.retcode);
      return false;
   }

   // 打印交易成功信息
   Print("做空成功: 价格=", price, " 止损=", sl, " 止盈=", tp, " 仓位=", lotSize);

   // 交易成功
   return true;
}
