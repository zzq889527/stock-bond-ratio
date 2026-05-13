# -*- coding: utf-8 -*-
"""测试 AKShare 关键函数"""
import akshare as ak
import traceback

# 1. bond_china_yield - 国债收益率
print('=== bond_china_yield ===')
try:
    # 查看函数签名
    import inspect
    sig = inspect.signature(ak.bond_china_yield)
    print(f'signature: {sig}')
    
    # 不带参数调用看看
    df = ak.bond_china_yield()
    print(f'columns: {list(df.columns)}')
    print(f'rows: {len(df)}')
    print(df.head(3))
    print('...')
    print(df.tail(3))
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()

# 2. stock_index_pe_lg - PE
print('\n=== stock_index_pe_lg ===')
try:
    sig = inspect.signature(ak.stock_index_pe_lg)
    print(f'signature: {sig}')
    df = ak.stock_index_pe_lg(symbol='沪深300')
    print(f'columns: {list(df.columns)}')
    print(f'rows: {len(df)}')
    print(df.head(3))
    print('...')
    print(df.tail(3))
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()

# 3. stock_zh_index_value_csindex - 中证估值
print('\n=== stock_zh_index_value_csindex ===')
try:
    sig = inspect.signature(ak.stock_zh_index_value_csindex)
    print(f'signature: {sig}')
except Exception as e:
    print(f'Error: {e}')
