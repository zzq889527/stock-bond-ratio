# -*- coding: utf-8 -*-
"""用 AKShare 获取10Y国债收益率和沪深300 PE-TTM"""
import akshare as ak
import json
import os

out = {}

# 1. 10年期国债收益率
print('[1] 获取10年期国债到期收益率...')
try:
    df = ak.bond_china_yield(start_date='20050101', end_date='20260501', symbol='中国国债收益率曲线')
    print(f'  列: {list(df.columns)}')
    print(f'  行数: {len(df)}')
    print(df.head(3))
    print('...')
    print(df.tail(3))
    
    bond = []
    for _, row in df.iterrows():
        try:
            # 尝试找到10Y列
            for col in df.columns:
                if '10' in str(col) and '年' in str(col):
                    date = str(row.iloc[0])[:10]
                    yld = float(row[col])
                    if yld > 0:
                        bond.append({'date': date, 'yield': yld})
                    break
        except:
            continue
    out['bond'] = bond
    print(f'  解析: {len(bond)} 条')
except Exception as e:
    print(f'  失败: {e}')

# 2. 沪深300 PE-TTM
print('\n[2] 获取沪深300 PE-TTM...')
try:
    df = ak.index_value_hist_funddb(symbol='沪深300')
    print(f'  列: {list(df.columns)}')
    print(f'  行数: {len(df)}')
    print(df.head(3))
except Exception as e:
    print(f'  funddb失败: {e}')
    try:
        # 备选
        df = ak.stock_a_lg_indicator('000300')
        print(f'  lg 列: {list(df.columns)}')
        print(f'  行数: {len(df)}')
        print(df.head(3))
    except Exception as e2:
        print(f'  lg也失败: {e2}')
