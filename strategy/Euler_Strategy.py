#!/usr/bin/env python3
import pandas as pd

def load_data(input_file):
    """
    讀取 CSV 檔案，並返回包含日期和收盤價的 DataFrame。
    自動處理時間列，支持 'date' 或 'ts'。
    :param input_file: CSV 檔案名稱
    :return: 包含日期和收盤價的 DataFrame
    """
    df = pd.read_csv(input_file)

    # 自動檢測是 'ts' 還是 'date' 作為時間列
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    elif 'date' in df.columns:
        df['ts'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    else:
        raise ValueError("CSV 檔案中沒有找到 'ts' 或 'date' 列。")

    return df

def euler_predict(timestamps, prices):
    """
    使用歐拉法進行股價預測，考慮實際的時間間隔。
    :param timestamps: 包含時間戳的列表
    :param prices: 包含股價的列表
    :return: 預測的股價列表
    """

    predicted_prices = prices[:2].copy()  # 複製前兩個元素作為初始值
    for i in range(0, len(prices) - 3):  # 最後一個不用預測
        # 計算時間間隔（以分鐘為單位）
        # i+1 代表現在，i 代表前一個，i+2 代表未來
        time_diff = (timestamps[i + 1] - timestamps[i]).total_seconds() / 60.0
        rate_of_change = (prices[i + 1] - prices[i]) / time_diff  # 計算每分鐘的價格變化率
        # 計算到目標時間點的時間間隔（分鐘）
        target_diff = (timestamps[i + 2] - timestamps[i + 1]).total_seconds() / 60.0
        
        # 根據時間間隔預測目標時間點的價格
        next_price = prices[i + 1] + rate_of_change * target_diff
        predicted_prices.append(next_price)

    return predicted_prices

def process_data(df):
    """
    處理 DataFrame，提取收盤價和時間戳。
    :param df: 包含收盤價和日期的 DataFrame
    :return: 收盤價列表和時間戳列表
    """
    timestamps = df['ts'].tolist()  # 提取時間戳列
    prices_open = df['open'].tolist()  # 提取開盤價列
    prices = df['close'].tolist()  # 提取收盤價列
    return timestamps, prices_open, prices

def generate_signals(timestamps, prices, open_prices, profit_per_point, transaction_tax_rate, transaction_fee):
    """
    根據預測結果生成買賣信號，並計算總交易費用和獲利。
    :param df: 包含收盤價和日期的DataFrame
    :param profit_per_point: 每點獲利金額（元）
    :param transaction_tax_rate: 交易稅率
    :param transaction_fee: 每次交易的手續費（元）
    :return: 包含買賣信號、總獲利金額、總手續費、總交易稅和總交易次數的tuple
    """
    signals = []
    total_profit_in_money = 0.0  # 總獲利金額
    total_transaction_fee = 0.0
    total_transaction_tax = 0.0
    
    if len(prices) < 3:
        return signals, total_profit_in_money, total_transaction_fee, total_transaction_tax, 0

    predicted_prices = euler_predict(timestamps, prices)
    
    in_position = False  # 是否持有倉位
    buy_price = 0.0  # 買入價格
    buy_net_cost = 0.0  # 買入時的淨收付
    total_trades = 0  # 總交易次數

    for i in range(2, len(predicted_prices) - 1):
        if not in_position:
            # 買入信號
            if prices[i] > prices[i - 1] and prices[i] > predicted_prices[i]:
            #if prices[i] > predicted_prices[i]:
                buy_price = open_prices[i + 1]  # 使用下一分鐘的開盤價買入
                buy_total = buy_price * profit_per_point
                transaction_tax = buy_total * transaction_tax_rate  # 計算買入時的交易稅
                buy_net_cost = - (buy_total + transaction_fee + transaction_tax)  # 買入的淨收付為負值
                signals.append(f"買入於 {timestamps[i + 1].strftime('%Y-%m-%d %H:%M:%S')}: 成交點數 = {buy_price:.2f}, 成交價金 = {buy_total:.2f}, 手續費 = {transaction_fee:.2f}, 交易稅 = {transaction_tax:.2f}, 淨收付 = {buy_net_cost:.2f}")
                total_transaction_fee += transaction_fee
                total_transaction_tax += transaction_tax  # 累計買入時的交易稅
                in_position = True
                total_trades += 1
        else:
            # 賣出信號
            if prices[i] < prices[i - 1] and prices[i] < predicted_prices[i]:
            #if prices[i] < predicted_prices[i]:
                sell_price = open_prices[i + 1]  # 使用下一分鐘的開盤價賣出
                sell_total = sell_price * profit_per_point
                transaction_tax = sell_total * transaction_tax_rate  # 計算賣出時的交易稅
                sell_net_revenue = sell_total - (transaction_fee + transaction_tax)  # 賣出的淨收付為正值
                net_profit = sell_net_revenue + buy_net_cost  # 修正為賣出淨收付減去買入淨收付
                signals.append(f"賣出於 {timestamps[i + 1].strftime('%Y-%m-%d %H:%M:%S')}: 成交點數 = {sell_price:.2f}, 成交價金 = {sell_total:.2f}, 手續費 = {transaction_fee:.2f}, 交易稅 = {transaction_tax:.2f}, 淨收付 = {sell_net_revenue:.2f}, 淨獲利 = {net_profit:.2f}")
                total_profit_in_money += sell_total - buy_total
                total_transaction_fee += transaction_fee
                total_transaction_tax += transaction_tax  # 累計賣出時的交易稅
                in_position = False
                total_trades += 1
    
    return signals, total_profit_in_money, total_transaction_fee, total_transaction_tax, total_trades

def save_output_to_file(file_name, signals, total_profit_in_money, total_transaction_fee, total_transaction_tax, total_trades, profit_per_point):
    """
    將買賣信號和總獲利金額保存到檔案。
    :param file_name: 輸出的檔案名稱
    :param signals: 買賣信號列表
    :param total_profit_in_money: 總獲利金額
    :param total_transaction_fee: 總手續費
    :param total_transaction_tax: 總交易稅
    :param total_trades: 總交易次數
    :param profit_per_point: 每點獲利金額
    """
    total_cost = total_transaction_fee + total_transaction_tax
    actual_profit = total_profit_in_money - total_cost
    
    with open(file_name, 'w') as f:
        f.write("=== 買賣信號 ===\n")
        for signal in signals:
            f.write(signal + '\n')
        
        f.write("\n=== 總結 ===\n")
        f.write(f"總獲利金額: {total_profit_in_money:.2f} 元\n")  # 顯示總獲利金額
        f.write(f"總手續費: {total_transaction_fee:.2f} 元\n")
        f.write(f"總交易稅: {total_transaction_tax:.2f} 元\n")
        f.write(f"總交易次數: {total_trades}\n")
        f.write(f"每點獲利金額: {profit_per_point:.2f} 元\n")
        f.write(f"實際盈利: {actual_profit:.2f} 元\n")

def main(input_file, output_file, profit_per_point, transaction_fee, transaction_tax_rate):
    """
    主函數，執行完整的流程，包括數據加載、信號生成和結果保存。
    :param input_file: 加權指數的CSV檔案路徑
    :param output_file: 輸出結果的檔案名稱
    :param profit_per_point: 每點獲利金額
    :param transaction_fee: 每次交易的手續費
    :param transaction_tax_rate: 每元的交易稅率
    """
    # 讀取數據
    df = load_data(input_file)
    
    # 處理數據
    timestamps, open_prices, prices = process_data(df)
    
    signals, total_profit_in_money, total_transaction_fee, total_transaction_tax, total_trades = generate_signals(timestamps, prices, open_prices, profit_per_point, transaction_tax_rate, transaction_fee)
    
    print("\n=== 買賣信號 ===")
    for signal in signals:
        print(signal)
    
    print("\n=== 總結 ===")
    print(f"總獲利金額: {total_profit_in_money:.2f} 元")
    print(f"總手續費: {total_transaction_fee:.2f} 元")
    print(f"總交易稅: {total_transaction_tax:.2f} 元")
    print(f"總交易次數: {total_trades}")
    print(f"實際盈利: {total_profit_in_money - total_transaction_fee - total_transaction_tax:.2f} 元")
    
    save_output_to_file(output_file, signals, total_profit_in_money, total_transaction_fee, total_transaction_tax, total_trades, profit_per_point)

# 自訂CSV檔案名稱和參數
input_file = 'daily_report.csv'
output_file = 'signals_output.txt'  # 輸出的結果檔案
profit_per_point = 10  # 每點的獲利金額
transaction_fee = 18  # 每次交易的手續費
transaction_tax_rate = 0.00002  # 每元的交易稅率

if __name__ == "__main__":
    main(input_file, output_file, profit_per_point, transaction_fee, transaction_tax_rate)
