# -*- coding: utf-8 -*-
"""
Created on Sun Dec 31 01:23:34 2023

@author: user
"""

# 載入必要模組
#import os
#os.chdir(r'D:\Bachelor\112-1\000 Graduate Project\111-2')
import numpy as np
import indicator_f_Lo2_short,datetime, indicator_forKBar_short
import pandas as pd
import streamlit as st 
import streamlit.components.v1 as stc 
from talib.abstract import SMA,EMA, WMA

html_temp = """
		<div style="background-color:#3872fb;padding:10px;border-radius:10px">
		<h1 style="color:white;text-align:center;">金融資料視覺化呈現 (金融看板) </h1>
		<h2 style="color:white;text-align:center;">Financial Dashboard </h2>
		</div>
		"""
stc.html(html_temp)
df_original = pd.read_pickle("kbars_2330_2022-01-01-2022-11-18.pkl")
df_original = df_original.drop('Unnamed: 0',axis=1)



st.subheader("選擇開始與結束的日期, 區間:2022-01-03 至 2022-11-18")
start_date = st.text_input('選擇開始日期 (日期格式: 2022-01-03)', '2022-01-03')
end_date = st.text_input('選擇結束日期 (日期格式: 2022-11-18)', '2022-11-18')
start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
# 使用条件筛选选择时间区间的数据
df = df_original[(df_original['time'] >= start_date) & (df_original['time'] <= end_date)]


### 轉化為字典:
KBar_dic = df.to_dict()

KBar_open_list = list(KBar_dic['open'].values())
KBar_dic['open']=np.array(KBar_open_list)

KBar_dic['product'] = np.repeat('tsmc', KBar_dic['open'].size)

KBar_time_list = list(KBar_dic['time'].values())
KBar_time_list = [i.to_pydatetime() for i in KBar_time_list] ## Timestamp to datetime
KBar_dic['time']=np.array(KBar_time_list)

KBar_low_list = list(KBar_dic['low'].values())
KBar_dic['low']=np.array(KBar_low_list)

KBar_high_list = list(KBar_dic['high'].values())
KBar_dic['high']=np.array(KBar_high_list)

KBar_close_list = list(KBar_dic['close'].values())
KBar_dic['close']=np.array(KBar_close_list)

KBar_volume_list = list(KBar_dic['volume'].values())
KBar_dic['volume']=np.array(KBar_volume_list)

KBar_amount_list = list(KBar_dic['amount'].values())
KBar_dic['amount']=np.array(KBar_amount_list)


######  改變 KBar 時間長度 (以下)  ########

Date = start_date.strftime("%Y-%m-%d")

st.subheader("設定一根 K 棒的時間長度(分鐘)")
cycle_duration = st.number_input('輸入一根 K 棒的時間長度(單位:分鐘, 一日=1440分鐘)', key="KBar_duration")
cycle_duration = int(cycle_duration)
KBar = indicator_forKBar_short.KBar(Date,cycle_duration)    ## 設定cycle_duration可以改成你想要的 KBar 週期

for i in range(KBar_dic['time'].size):
    

    time = KBar_dic['time'][i]
    open_price= KBar_dic['open'][i]
    close_price= KBar_dic['close'][i]
    low_price= KBar_dic['low'][i]
    high_price= KBar_dic['high'][i]
    qty =  KBar_dic['volume'][i]
    amount = KBar_dic['amount'][i]
    tag=KBar.AddPrice(time, open_price, close_price, low_price, high_price, qty)
    
KBar_dic = {}

## 形成 KBar 字典:
KBar_dic['time'] =  KBar.TAKBar['time']   
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['time'].size)
KBar_dic['open'] = KBar.TAKBar['open']
KBar_dic['high'] =  KBar.TAKBar['high']
KBar_dic['low'] =  KBar.TAKBar['low']
KBar_dic['close'] =  KBar.TAKBar['close']
KBar_dic['volume'] =  KBar.TAKBar['volume']


######  (一) 移動平均線策略   #########

st.subheader("設定計算長移動平均線(MA)的 K 棒數目(整數, 例如 10)")

LongMAPeriod=st.slider('選擇一個整數', 0, 100, 10)

st.subheader("設定計算短移動平均線(MA)的 K 棒數目(整數, 例如 2)")

ShortMAPeriod=st.slider('選擇一個整數', 0, 100, 2)

                
st.subheader("設定計算長RSI的 K 棒數目(整數, 例如 15)")
LongRSIPeriod=st.slider('選擇一個整數', 0, 1000, 15)


st.subheader("設定計算短RSI的 K 棒數目(整數, 例如 8)")
ShortRSIPeriod=st.slider('選擇一個整數', 0, 1000, 8)

st.subheader("設定計算布林通道的 K 棒數目(整數, 例如 20)")

bollinger_bandsPeriod=st.slider('選擇一個整數', 0, 100, 20)

st.subheader("設定計算布林通道的標準差倍數數(整數, 通常為 2)")

num_std_dev=st.slider('選擇一個整數', 0, 10, 2)

st.subheader("設定計算短期指數移動平均線週期天數(整數, 通常為 12)")

EMA_shortPeriod=st.slider('選擇一個整數', 0, 100, 12)

st.subheader("設定計算長期指數移動平均線週期天數(整數, 通常為 26)")

EMA_longPeriod=st.slider('選擇一個整數', 0, 100, 26)

st.subheader("設定計算信號線週期天數(整數, 通常為 9)")

Signal_LinePeriod=st.slider('選擇一個整數', 0, 100, 9)






# 將K線 Dictionary 轉換成 Dataframe
KBar_df = pd.DataFrame(KBar_dic)

KBar_df['MA_long'] = KBar_df['close'].rolling(window=LongMAPeriod).mean()
KBar_df['MA_short'] = KBar_df['close'].rolling(window=ShortMAPeriod).mean()

#RSI計算函式
def calculate_rsi(df, period):
    # 計算每日價格變動
    delta = np.diff(df['close'])

    # 計算正價格變動的平均值（gain）
    gain = np.where(delta > 0, delta, 0)
    gain = np.convolve(gain, np.ones((period,))/period, mode='valid')

    # 計算負價格變動的平均值（loss）
    loss = np.where(delta < 0, -delta, 0)
    loss = np.convolve(loss, np.ones((period,))/period, mode='valid')


    # 計算相對強弱指數（RS）
    rs = gain / loss

    # 計算RSI
    rsi = 100 - (100 / (1 + rs))
    
    rsi_nan = np.array([np.nan]*period)
    
    rsi = np.hstack((rsi_nan, rsi))

    return rsi
# # 計算 RSI指標長短線
KBar_df['RSI_long'] = calculate_rsi(KBar_dic,LongRSIPeriod)
KBar_df['RSI_short'] = calculate_rsi(KBar_dic,ShortRSIPeriod)











def calculate_bollinger_bands(KBar_dic, period, num_std_dev):
    close_prices = KBar_dic['close']
    sma = np.convolve(close_prices, np.ones((period,))/period, mode='valid')
    std_dev = np.std(np.lib.stride_tricks.sliding_window_view(close_prices, (period,)), axis=1, ddof=0)

    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)

    df = np.column_stack((sma, upper_band, lower_band))
    
    arr_nan = np.full((period-1, 3), np.nan)
    
    df = np.concatenate((arr_nan,df), axis=0)

    return df

bollinger_bands = calculate_bollinger_bands(KBar_dic,bollinger_bandsPeriod,num_std_dev)
KBar_df[['SMA', 'upper_band', 'lower_band']] = bollinger_bands[:, :3]









close_prices = KBar_dic['close']

close_prices = KBar_dic['close']

# 计算短期（12天）和长期（26天）的指数移动平均值
EMA_short = np.convolve(close_prices, np.ones(EMA_shortPeriod)/EMA_shortPeriod, mode='valid')
EMA_long = np.convolve(close_prices, np.ones(EMA_longPeriod)/EMA_longPeriod, mode='valid')
EMA_long = np.concatenate((np.full(EMA_longPeriod-EMA_shortPeriod, np.nan), EMA_long))
# 计算差异值（MACD线）
macd_line = EMA_short - EMA_long
macd_line = np.concatenate((np.full(EMA_shortPeriod-1, np.nan), macd_line))

# 计算信号线（9天的指数移动平均值）
signal_line = np.convolve(macd_line, np.ones(Signal_LinePeriod)/Signal_LinePeriod, mode='valid')
signal_line = np.concatenate((np.full(Signal_LinePeriod-1, np.nan), signal_line))

# 计算差异值和信号线的差异（MACD Histogram）
macd_histogram = macd_line[-len(signal_line):] - signal_line

KBar_df['macd_line'] = macd_line










## 尋找最後 NAN值的位置
last_nan_index_MA = KBar_df['MA_long'][::-1].index[KBar_df['MA_long'][::-1].apply(pd.isna)][0]
last_nan_index_RSI = KBar_df['RSI_long'][::-1].index[KBar_df['RSI_long'][::-1].apply(pd.isna)][0]
last_nan_index_bollinger_bands = KBar_df['SMA'][::-1].index[KBar_df['SMA'][::-1].apply(pd.isna)][0]
last_nan_MACD = KBar_df['macd_line'][::-1].index[KBar_df['macd_line'][::-1].apply(pd.isna)][0]



# 將 Dataframe 欄位名稱轉換
KBar_df.columns = [ i[0].upper()+i[1:] for i in KBar_df.columns ]


st.subheader("畫圖")
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.offline as pyoff

with st.expander("K線圖與移動平均線"):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # include candlestick with rangeselector
    fig.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=True)   ## secondary_y=True 表示此圖形的y軸scale是在右邊而不是在左邊
    
    #include a go.Bar trace for volumes
    fig.add_trace(go.Bar(x=KBar_df['Time'], y=KBar_df['Volume'], name='成交量', marker=dict(color='black')),secondary_y=False)  ## secondary_y=False 表示此圖形的y軸scale是在左邊而不是在右邊
    fig.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA+1:], y=KBar_df['MA_long'][last_nan_index_MA+1:], mode='lines',line=dict(color='orange', width=2), name=f'{LongMAPeriod}-根 K棒 移動平均線'), 
                  secondary_y=True)
    fig.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_MA+1:], y=KBar_df['MA_short'][last_nan_index_MA+1:], mode='lines',line=dict(color='pink', width=2), name=f'{ShortMAPeriod}-根 K棒 移動平均線'), 
                  secondary_y=True)
    fig.layout.yaxis2.showgrid=True

    st.plotly_chart(fig, use_container_width=True)

with st.expander("K線圖, 長短 RSI"):
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    #### include candlestick with rangeselector
    fig2.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=True)   ## secondary_y=True 表示此圖形的y軸scale是在右邊而不是在左邊
    
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI+1:], y=KBar_df['RSI_long'][last_nan_index_RSI+1:], mode='lines',line=dict(color='red', width=2), name=f'{LongRSIPeriod}-根 K棒 移動 RSI'), 
                  secondary_y=False)
    fig2.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_RSI+1:], y=KBar_df['RSI_short'][last_nan_index_RSI+1:], mode='lines',line=dict(color='blue', width=2), name=f'{ShortRSIPeriod}-根 K棒 移動 RSI'), 
                  secondary_y=False)
    
    fig2.layout.yaxis2.showgrid=True
    st.plotly_chart(fig2, use_container_width=True)
    
    
with st.expander("K線圖, 布林通道"):

    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=False)    
    fig3.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_bollinger_bands+1:], y=bollinger_bands[:,0][last_nan_index_bollinger_bands+1:], mode='lines',line=dict(color='black', width=2), name='SMA'), 
                  secondary_y=True)
    fig3.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_bollinger_bands+1:], y=bollinger_bands[:,1][last_nan_index_bollinger_bands+1:], mode='lines',line=dict(color='red', width=2), name='upperband'), 
                  secondary_y=True)
    fig3.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_index_bollinger_bands+1:], y=bollinger_bands[:,2][last_nan_index_bollinger_bands+1:], mode='lines',line=dict(color='blue', width=2), name='lowerband'), 
                  secondary_y=True)
    
    fig3.layout.yaxis2.showgrid=True

    st.plotly_chart(fig3, use_container_width=True)
    
    
with st.expander("K線圖, MACD"):

    fig4 = make_subplots(specs=[[{"secondary_y": True}]])

    fig4.add_trace(go.Candlestick(x=KBar_df['Time'],
                    open=KBar_df['Open'], high=KBar_df['High'],
                    low=KBar_df['Low'], close=KBar_df['Close'], name='K線'),
                   secondary_y=False)

    fig4.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_MACD+1:], y=macd_line[last_nan_MACD+1:], mode='lines',line=dict(color='orange', width=2), name='MACD'), 
                  secondary_y=True)
    fig4.add_trace(go.Scatter(x=KBar_df['Time'][last_nan_MACD+1:], y=signal_line[last_nan_MACD+1:], mode='lines',line=dict(color='green', width=2), name='Signal Line'), 
                  secondary_y=True)
    fig4.add_trace(go.Bar(x=KBar_df['Time'][last_nan_MACD+1:], y=macd_histogram[last_nan_MACD+1:], marker=dict(color='gray'), name='MACD Histogram'), 
                  secondary_y=True)
    
    fig4.layout.yaxis2.showgrid=True

    st.plotly_chart(fig4, use_container_width=True)    
    
    
    
    
    
##画图2

class Record:
    def __init__(self):
        self.positions = []

    def Order(self, action, product, time, price, quantity):
        self.positions.append((action, product, time, price, quantity))

    def Cover(self, action, product, time, price, quantity):
        self.positions.append((action, product, time, price, quantity))

    def GetOpenInterest(self):
        if not self.positions:
            return 0
        last_position = self.positions[-1]
        if last_position[0] == 'Buy':
            return 1
        elif last_position[0] == 'Sell':
            return -1
        return 0

    def GetPositions(self):
        return self.positions

# 假设 KBar_dic 已经在之前的代码中被定义和填充了
# 这里是处理逻辑
OrderRecord = Record()
LongMAPeriod = 20
ShortMAPeriod = 10
MoveStopLoss = 30

# 假设 KBar_dic 是之前定义的字典，包含交易数据
KBar_dic['MA_long'] = SMA(KBar_dic, timeperiod=LongMAPeriod)
KBar_dic['MA_short'] = SMA(KBar_dic, timeperiod=ShortMAPeriod)

#
for n in range(1, len(KBar_dic['time'])):  # 从第二个数据点开始，因为我们需要比较当前和前一个数据点
    # 先判断长期移动平均线的上一个值是否为空值，再进行策略逻辑判断
    if not np.isnan(KBar_dic['MA_long'][n-1]):
        # 如果当前无开仓
        if OrderRecord.GetOpenInterest() == 0:
            # 多单进场条件：短期移动平均线上穿长期移动平均线（黄金交叉）
            if KBar_dic['MA_short'][n-1] <= KBar_dic['MA_long'][n-1] and KBar_dic['MA_short'][n] > KBar_dic['MA_long'][n]:
                OrderRecord.Order('Buy', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['open'][n], 1)
                OrderPrice = KBar_dic['open'][n]
                StopLossPoint = OrderPrice - MoveStopLoss  # 设置停损点
            # 空单进场条件：短期移动平均线下穿长期移动平均线（死亡交叉）
            elif KBar_dic['MA_short'][n-1] >= KBar_dic['MA_long'][n-1] and KBar_dic['MA_short'][n] < KBar_dic['MA_long'][n]:
                OrderRecord.Order('Sell', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['open'][n], 1)
                OrderPrice = KBar_dic['open'][n]
                StopLossPoint = OrderPrice + MoveStopLoss  # 设置停损点
        # 如果持有多单
        elif OrderRecord.GetOpenInterest() == 1:
            # 更新停损点
            if KBar_dic['close'][n] - MoveStopLoss > StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] - MoveStopLoss
            # 触发停损条件
            elif KBar_dic['close'][n] < StopLossPoint:
                OrderRecord.Cover('Sell', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['open'][n], 1)
        # 如果持有空单
        elif OrderRecord.GetOpenInterest() == -1:
            # 更新停损点
            if KBar_dic['close'][n] + MoveStopLoss < StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] + MoveStopLoss
            # 触发停损条件
            elif KBar_dic['close'][n] > StopLossPoint:
                OrderRecord.Cover('Buy', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['open'][n], 1)

                
# 繪製K線圖加上MA以及下單點位
from chart import ChartOrder_MA
ChartOrder_MA(KBar_dic,OrderRecord.GetTradeRecord())
KBar_dic.keys()
    
## 未平倉資訊:
OrderRecord.GetOpenInterest()   ## 1
OrderRecord.OpenInterest        ## [[1, 'tsmc', datetime.datetime(2022, 7, 5, 11, 27), 435.0]]

# 繪製K線圖以及MA
from chart import ChartKBar_MA
ChartKBar_MA(KBar_dic,longPeriod=20,shortPeriod=10)


## 計算績效:
OrderRecord.GetTradeRecord()          ## 交易紀錄清單
OrderRecord.GetProfit()               ## 利潤清單
OrderRecord.GetTotalProfit()          ## 取得交易總盈虧
OrderRecord.GetAverageProfit()        ## 取得交易 "平均" 盈虧(每次)
OrderRecord.GetAverageProfitRate()    ## 取得交易 "平均" 投資報酬率(每次)  
OrderRecord.GetAverEarn()             ## 平均獲利(只看獲利的) 
OrderRecord.GetAverLoss()             ## 平均虧損(只看虧損的)
OrderRecord.GetWinRate()              ## 勝率
OrderRecord.GetAccLoss()              ## 最大連續虧損
OrderRecord.GetMDD()                  ## 最大資金回落(MDD)
OrderRecord.GetCumulativeProfit()         ## 累計盈虧
OrderRecord.GetCumulativeProfit_rate()    ## 累計投資報酬率


## 畫累計盈虧圖:
OrderRecord.GeneratorProfitChart('MA')    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
