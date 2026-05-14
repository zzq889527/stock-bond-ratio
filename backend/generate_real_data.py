#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data"
PUBLIC_PATH = Path(__file__).parent.parent / "public"
DIST_PATH = Path(__file__).parent.parent / "dist"

DATA_PATH.mkdir(exist_ok=True)
PUBLIC_PATH.mkdir(exist_ok=True)
DIST_PATH.mkdir(exist_ok=True)

INDEX_CONFIGS = [
    {"id": "hs300", "name": "沪深300", "pe_symbol": "沪深300", "price_symbol": "sh000300", "total_return_symbol": "H00300"},
    {"id": "zz500", "name": "中证500", "pe_symbol": "中证500", "price_symbol": "sh000905", "total_return_symbol": "H00905"},
    {"id": "zzall", "name": "中证全指", "pe_symbol": "中证800", "price_symbol": "sh000985", "total_return_symbol": "H00985"}
]

def calculate_erp(pe, bond_yield):
    if pd.isna(pe) or pe == 0:
        return np.nan
    return (1.0 / pe) * 100 - bond_yield

def get_pe_data(symbol):
    try:
        df = ak.stock_index_pe_lg(symbol=symbol)
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.rename(columns={
            '日期': 'date',
            '指数': 'index_value',
            '滚动市盈率': 'pe_ttm'
        })
        return df[['date', 'index_value', 'pe_ttm']]
    except Exception as e:
        print(f"获取{symbol} PE数据失败: {e}")
        return None

def get_pb_data(symbol):
    try:
        df = ak.stock_index_pb_lg(symbol=symbol)
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.rename(columns={
            '日期': 'date',
            '市净率': 'pb'
        })
        return df[['date', 'pb']]
    except Exception as e:
        print(f"获取{symbol} PB数据失败: {e}")
        return None

def get_dividend_yield(symbol):
    try:
        df = ak.stock_history_dividend(symbol=symbol)
        df['date'] = pd.to_datetime(df['date'])
        df = df.rename(columns={'dividend': 'dividend_yield'})
        return df[['date', 'dividend_yield']]
    except Exception as e:
        print(f"获取{symbol}股息率数据失败: {e}")
        return None

def get_total_return(symbol):
    try:
        df = ak.stock_zh_index_hist_csindex(symbol=symbol)
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.rename(columns={'日期': 'date', '收盘': 'total_return'})
        return df[['date', 'total_return']]
    except Exception as e:
        print(f"获取{symbol}全收益数据失败: {e}")
        return None

def get_price_data(symbol):
    try:
        df = ak.stock_zh_index_daily(symbol=symbol)
        df['date'] = pd.to_datetime(df['date'])
        df = df.rename(columns={'close': 'price_close'})
        return df[['date', 'price_close']]
    except Exception as e:
        print(f"获取{symbol}价格指数失败: {e}")
        return None

def get_bond_data():
    try:
        df = ak.bond_zh_us_rate()
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.rename(columns={'日期': 'date', '中国国债收益率10年': 'bond_10y'})
        return df[['date', 'bond_10y']]
    except Exception as e:
        print(f"获取国债数据失败: {e}")
        return None

def process_index_data(index_config):
    index_id = index_config["id"]
    index_name = index_config["name"]
    print(f"\n=== 处理 {index_name} ===")
    
    df_pe = get_pe_data(index_config["pe_symbol"])
    if df_pe is None:
        print(f"✗ PE数据获取失败")
        return None
    
    df_pb = get_pb_data(index_config["pe_symbol"])
    df_tr = get_total_return(index_config["total_return_symbol"])
    df_price = get_price_data(index_config["price_symbol"])
    df_bond = get_bond_data()
    df_dividend = get_dividend_yield(index_config["price_symbol"])
    
    print(f"  PE数据: {len(df_pe)}条")
    if df_pb is not None:
        print(f"  PB数据: {len(df_pb)}条")
    if df_tr is not None:
        print(f"  全收益数据: {len(df_tr)}条")
    if df_price is not None:
        print(f"  价格指数: {len(df_price)}条")
    if df_bond is not None:
        print(f"  国债数据: {len(df_bond)}条")
    if df_dividend is not None:
        print(f"  股息率数据: {len(df_dividend)}条")
    
    df = df_pe.copy()
    
    if df_pb is not None:
        df = pd.merge_asof(df, df_pb, on='date', direction='nearest')
    else:
        df['pb'] = 0
    
    if df_price is not None:
        df = pd.merge_asof(df, df_price, on='date', direction='nearest')
    
    if df_tr is not None:
        tr_max_date = df_tr['date'].max()
        df = pd.merge_asof(df, df_tr, on='date', direction='nearest')
        
        first_valid_idx = df['total_return'].first_valid_index()
        if first_valid_idx is not None and first_valid_idx > 0:
            ratio = df.loc[first_valid_idx, 'total_return'] / df.loc[first_valid_idx, 'index_value']
            df.loc[:first_valid_idx-1, 'total_return'] = (df.loc[:first_valid_idx-1, 'index_value'] * ratio).round(1)
        
        mask_after_tr = df['date'] > tr_max_date
        if mask_after_tr.any():
            last_tr_row = df[df['date'] <= tr_max_date].iloc[-1]
            if df_price is not None and df_price['date'].max() > tr_max_date:
                last_ratio = last_tr_row['total_return'] / last_tr_row['price_close']
                df.loc[mask_after_tr, 'total_return'] = (df.loc[mask_after_tr, 'price_close'] * last_ratio).round(1)
            else:
                last_ratio = last_tr_row['total_return'] / last_tr_row['index_value']
                df.loc[mask_after_tr, 'total_return'] = (df.loc[mask_after_tr, 'index_value'] * last_ratio).round(1)
        
        df['total_return'] = df['total_return'].ffill().bfill()
    else:
        df['total_return'] = (df['index_value'] * 1.5).round(1)
    
    if df_dividend is not None:
        df = pd.merge_asof(df, df_dividend, on='date', direction='nearest')
        df['dividend_yield'] = df['dividend_yield'].ffill().bfill()
    else:
        df['dividend_yield'] = 2.0
    
    if df_bond is not None:
        df = pd.merge_asof(df, df_bond, on='date', direction='backward')
        df['bond_10y'] = df['bond_10y'].ffill().bfill()
    else:
        df['bond_10y'] = 2.5
    
    df = df.dropna(subset=['index_value', 'pe_ttm', 'bond_10y', 'total_return'])
    df = df[(df['date'] >= pd.Timestamp('2005-04-08')) & (df['date'] <= pd.Timestamp(datetime.now()))]
    
    df['erp'] = df.apply(lambda row: calculate_erp(row['pe_ttm'], row['bond_10y']), axis=1)
    df = df.dropna(subset=['erp'])
    
    df['tr_p'] = (100 / df['pe_ttm']).round(2)
    
    mean_erp = round(df['erp'].mean(), 2)
    std_erp = round(df['erp'].std(), 2)
    
    df['mean'] = mean_erp
    df['sigma'] = std_erp
    df['percentile'] = (df['erp'].rank(pct=True) * 100).round(0).astype(int)
    
    def get_signal(erp):
        if erp > mean_erp + std_erp:
            return '极度低估'
        elif erp > mean_erp + 0.5 * std_erp:
            return '低估'
        elif erp >= mean_erp - 0.5 * std_erp:
            return '均衡'
        elif erp >= mean_erp - std_erp:
            return '高估'
        else:
            return '极度高估'
    
    df['signal'] = df['erp'].apply(get_signal)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    print(f"  ✓ 完成: {len(df)}条")
    return df

def generate_all_data():
    print("=== 开始生成股债收益比数据 ===")
    
    for config in INDEX_CONFIGS:
        df = process_index_data(config)
        if df is None:
            continue
        
        records = []
        for _, row in df.iterrows():
            record = {
                'date': str(row['date']),
                'erp': float(row['erp']),
                'mean': float(row['mean']),
                'sigma': float(row['sigma']),
                'percentile': int(row['percentile']),
                'signal': str(row['signal']),
                'pe_ttm': float(row['pe_ttm']),
                'pb': float(row['pb']) if 'pb' in df.columns and pd.notna(row['pb']) else 0.0,
                'dividend_yield': float(row['dividend_yield']) if 'dividend_yield' in df.columns and pd.notna(row['dividend_yield']) else 0.0,
                'bond_10y': float(row['bond_10y']),
                'index_value': float(row['index_value']),
                'total_return': float(row['total_return']),
                'tr_p': float(row['tr_p'])
            }
            records.append(record)
        
        cache_file = DATA_PATH / f"{config['id']}_erp_data.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"  保存缓存: {cache_file}")
        
        if config['id'] == 'hs300':
            public_file = PUBLIC_PATH / 'erp_data.json'
        else:
            public_file = PUBLIC_PATH / f"{config['id']}_erp_data.json"
        with open(public_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"  保存到public: {public_file}")
        
        dist_file = DIST_PATH / f"{config['id']}_erp_data.json"
        with open(dist_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"  保存到dist: {dist_file}")
    
    print("\n=== 数据生成完成 ===")

if __name__ == "__main__":
    generate_all_data()