#!/usr/bin/env python3

import pandas as pd
from datetime import datetime, timedelta
import os

def read_csv(file_path):
    """讀取CSV檔案並返回DataFrame"""
    df = pd.read_csv(file_path)
    return df

def aggregate_data(df, close_time_str):
    """根據設定的收盤時間聚合數據"""
    close_time = datetime.strptime(close_time_str, "%H:%M").time()
    
    # 確保 'ts' 列是 datetime 格式
    df['ts'] = pd.to_datetime(df['ts'])
    
    # 分割日期和時間
    df['date'] = df['ts'].dt.date
    df['time'] = df['ts'].dt.time
    
    # 初始化結果 DataFrame
    result = []

    # 獲取所有日期
    all_dates = sorted(df['date'].unique())
    
    for i in range(1, len(all_dates)):
        current_date = all_dates[i]
        previous_date = all_dates[i - 1]

        # 查找前一天的收盤時間之後的所有數據
        prev_day_end_time = datetime.combine(previous_date, close_time)
        current_day_start_time = prev_day_end_time + timedelta(seconds=1)

        # 計算當前交易日的時間區間
        current_day_end_time = datetime.combine(current_date, close_time)

        # 篩選數據
        relevant_data = df[
            ((df['ts'] >= current_day_start_time) & (df['ts'] <= current_day_end_time))
        ]

        if relevant_data.empty:
            # 如果篩選的數據為空，則跳過此日期
            continue

        # 獲取當前交易日的開盤數據
        next_open_data = df[(df['date'] == previous_date) & (df['time'] > close_time)]
        if not next_open_data.empty:
            next_open = next_open_data.iloc[0]['open']
        else:
            # 如果前一天沒有數據，嘗試向前尋找
            for j in range(i - 1, -1, -1):
                fallback_date = all_dates[j]
                fallback_data = df[df['date'] == fallback_date]
                next_open_data = fallback_data[fallback_data['time'] > close_time]
                if not next_open_data.empty:
                    next_open = next_open_data.iloc[0]['open']
                    break
            else:
                # 如果都找不到數據，則跳過此日期
                continue

        # 計算當前交易日的 High, Low, Volume
        day_high = relevant_data['high'].max()
        day_low = relevant_data['low'].min()
        day_volume = relevant_data['volume'].sum()

        # 查找當天收盤時間的數據
        close_time_data = df[(df['date'] == current_date) & (df['time'] == close_time)]

        if not close_time_data.empty:
            current_day_close = close_time_data.iloc[0]['close']
        else:
            # 如果當天在指定時間點沒有數據，跳過此日期
            continue

        # 記錄結果
        result.append({
            'date': current_date,
            'open': next_open,
            'high': day_high,
            'low': day_low,
            'close': current_day_close,
            'volume': day_volume
        })

    df_resampled = pd.DataFrame(result)
    df_resampled['date'] = pd.to_datetime(df_resampled['date'])
    df_resampled.set_index('date', inplace=True)
    
    # 將 'date' 列移動到最前面
    df_resampled.reset_index(inplace=True)
    df_resampled = df_resampled[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    return df_resampled

def save_to_csv(df, output_file):
    """將聚合後的數據保存為CSV文件"""
    df.to_csv(output_file, index=False)
    print(f"總結已儲存至 {output_file}")

def main():
    # 設定檔案路徑
    input_file = 'TXFR2_yearly_report.csv'  # 輸入的原始數據 CSV 檔案
    
    # 創建輸出資料夾
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 自定義收盤時間
    close_time = "13:45"  # 設定的收盤時間
    
    # 讀取CSV檔案
    df = read_csv(input_file)
    
    # 聚合數據
    aggregated_data = aggregate_data(df, close_time)
    
    # 保存聚合後的數據
    save_to_csv(aggregated_data, os.path.join(output_dir, 'daily_report.csv'))

if __name__ == "__main__":
    main()
