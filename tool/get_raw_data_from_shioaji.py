#!/usr/bin/env python3

import shioaji as sj
import pandas as pd
import configparser
from datetime import datetime


def load_config(file_path: str, key_name: str) -> dict:
    """從配置文件加載API密鑰."""
    config = configparser.ConfigParser()
    config.read(file_path)
    return config[key_name]


def login_to_shioaji(api_key: str, secret_key: str) -> sj.Shioaji:
    """登錄Shioaji API."""
    api = sj.Shioaji()
    api.login(api_key=api_key, secret_key=secret_key,
              contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."))
    return api

def fetch_kbars(api: sj.Shioaji, contract, start_date: str, end_date: str) -> pd.DataFrame:
    """獲取指定合約的歷史數據，並轉換為Pandas DataFrame."""
    kbars = api.kbars(contract, start=start_date, end=end_date)
    df = pd.DataFrame({
        "ts": pd.to_datetime(kbars.ts),
        "open": kbars.Open,
        "high": kbars.High,
        "low": kbars.Low,
        "close": kbars.Close,
        "volume": kbars.Volume,
    })
    return df


def save_to_csv(df: pd.DataFrame, file_path: str):
    """將DataFrame保存為CSV文件."""
    df.to_csv(file_path, index=False)
    print(f"數據已保存到 {file_path}")


def logout(api: sj.Shioaji):
    """登出Shioaji API."""
    api.logout()
    print("已登出Shioaji API")


def main():
    config_file = 'shioaji_api_config.ini'
    key_name = 'key'
    
    # 加載配置
    credentials = load_config(config_file, key_name)
    
    # 登錄API
    api = login_to_shioaji(credentials['api_key'], credentials['secret_key'])
    
    # 檢查API使用情況
    usage = api.usage()
    print(usage)
    
    # 獲取合約
    contract = api.Contracts.Futures.TXF.TXFR2
    print(contract)
    
    # 設定開始和結束日期
    start_date = "2020-03-02"
    end_date = "2024-09-17"
    
    # 獲取歷史數據
    df = fetch_kbars(api, contract, start_date, end_date)
    
    # 保存為CSV
    csv_file = "TXFR2_yearly_report.csv"
    save_to_csv(df, csv_file)
    
    # 登出API
    logout(api)


if __name__ == "__main__":
    main()
