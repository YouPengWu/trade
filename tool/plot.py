#!/usr/bin/env python3

import plotly.graph_objects as go
import pandas as pd

# 從 CSV 文件讀取數據
csv_file = 'daily_report.csv'  # 替換為你的 CSV 檔案名稱
data = pd.read_csv(csv_file)

# 確保 'ts' 列是日期時間格式
data['ts'] = pd.to_datetime(data['ts'])

# 計算移動平均線 (例如 5 日、20 日移動平均線)
data['MA_5'] = data['close'].rolling(window=5).mean()   # 5 日移動平均
data['MA_20'] = data['close'].rolling(window=20).mean()  # 20 日移動平均

# 將日期設為字符串，用於忽略日期跳躍的問題
data['ts_str'] = data['ts'].dt.strftime('%Y-%m-%d %H:%M:%S')

# 繪製 K 線圖 (Candle chart)
fig = go.Figure(data=[go.Candlestick(
    x=data['ts_str'],
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    name="K Line",
    increasing_line_color='limegreen',  # 陽線顏色
    decreasing_line_color='red'         # 陰線顏色
)])

# 添加 5 日移動平均線
fig.add_trace(go.Scatter(
    x=data['ts_str'],
    y=data['MA_5'],
    mode='lines',
    line=dict(color='yellow', width=2),
    name='5 Day MA'
))

# 添加 20 日移動平均線
fig.add_trace(go.Scatter(
    x=data['ts_str'],
    y=data['MA_20'],
    mode='lines',
    line=dict(color='cyan', width=2),
    name='20 Day MA'
))

# 添加交易量
fig.add_trace(go.Bar(
    x=data['ts_str'],
    y=data['volume'],
    marker_color='dodgerblue',
    name='Volume',
    yaxis='y2'
))

# 設定圖表布局，包含滑鼠十字準線 (crosshair)
fig.update_layout(
    title='Stock Price with Moving Averages',
    xaxis_title='Date',
    yaxis_title='Price',
    yaxis2=dict(
        title='Volume',
        overlaying='y',
        side='right',
        showgrid=False
    ),
    xaxis_rangeslider_visible=False,
    width=900,
    height=600,
    hovermode='x unified',  # 啟用十字準線
    legend=dict(x=0, y=1),
    
    # 深色模式設置
    plot_bgcolor='#1e1e1e',  # 深色背景
    paper_bgcolor='#1e1e1e',  # 深色背景
    font_color='white',  # 字體顏色
    xaxis=dict(
        showgrid=False,
        color='white'  # x 軸標籤顏色
    ),
    yaxis=dict(
        showgrid=False,
        color='white'  # y 軸標籤顏色
    )
)

# 顯示圖表
fig.show(renderer='browser')