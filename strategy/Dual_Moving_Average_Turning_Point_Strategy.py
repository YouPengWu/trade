#!/usr/bin/env python3
import pandas as pd

def load_data(file_name):
    """讀取CSV檔案，返回包含日期和收盤價的DataFrame"""
    df = pd.read_csv(file_name, parse_dates=['date'], dayfirst=True)
    df['date'] = pd.to_datetime(df['date'])  # 確保 'date' 列是 datetime64[ns] 類型
    return df

def calculate_moving_averages(df, short_window, long_window):
    """計算短期和長期移動平均線"""
    df['Short_MA'] = df['close'].rolling(window=short_window).mean()
    df['Long_MA'] = df['close'].rolling(window=long_window).mean()
    return df

def find_moving_average_signals(df, short_window, long_window):
    """檢測均線交叉點並返回買賣信號，顯示短期和長期均線的計算值"""
    signals = []
    holding = False
    buy_price = None
    profit_points = 0
    
    for i in range(1, len(df)):
        short_ma = df['Short_MA'].iloc[i]
        long_ma = df['Long_MA'].iloc[i]
        
        # 短期均線上穿長期均線 -> 買入信號
        if short_ma > long_ma and df['Short_MA'].iloc[i-1] <= df['Long_MA'].iloc[i-1]:
            if not holding:  # 如果沒有持倉
                holding = True
                buy_price = df['close'].iloc[i]
                buy_date = df['date'].iloc[i]
                signals.append(f"{buy_date}: 買入，價格= {buy_price:.2f} (短期均線= {short_ma:.2f}, 長期均線= {long_ma:.2f})")
        
        # 短期均線下穿長期均線 -> 賣出信號
        elif short_ma < long_ma and df['Short_MA'].iloc[i-1] >= df['Long_MA'].iloc[i-1]:
            if holding:  # 如果持倉
                holding = False
                sell_price = df['close'].iloc[i]
                sell_date = df['date'].iloc[i]
                profit = sell_price - buy_price
                profit_points += profit
                signals.append(f"{sell_date}: 賣出，價格= {sell_price:.2f}，獲利= {profit:.2f} (短期均線= {short_ma:.2f}, 長期均線= {long_ma:.2f})")
    
    return signals, profit_points

def save_output_to_file(file_name, signals, profit_points):
    """將買賣信號和總獲利點數保存到檔案"""
    with open(file_name, 'w') as f:
        f.write("=== 買賣信號 ===\n")
        for signal in signals:
            f.write(signal + '\n')
        
        f.write("\n=== 總結 ===\n")
        f.write(f"總獲利點數: {profit_points:.2f}\n")

def main(taiex_file, short_window, long_window, output_file):
    taiex_df = load_data(taiex_file)
    
    # 計算移動平均線
    taiex_df = calculate_moving_averages(taiex_df, short_window, long_window)
    
    # 找到均線交叉點信號
    signals, profit_points = find_moving_average_signals(taiex_df, short_window, long_window)
    
    # 輸出買賣信號到終端機
    print("\n=== 買賣信號 ===")
    for signal in signals:
        print(signal)
    
    # 輸出總獲利點數到終端機
    print("\n=== 總結 ===")
    print(f"總獲利點數: {profit_points:.2f}")
    
    # 保存結果到檔案
    save_output_to_file(output_file, signals, profit_points)

# 自訂CSV檔案名稱和參數
taiex_file = 'daily_report.csv'  # 加權指數的CSV檔案
short_window = 1  # 短期均線窗口 (可由使用者設定)
long_window = 3  # 長期均線窗口 (可由使用者設定)
output_file = 'signals_output.txt'  # 輸出的檔案名稱

# 執行程式
if __name__ == "__main__":
    main(taiex_file, short_window, long_window, output_file)
