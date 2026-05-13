# -*- coding: utf-8 -*-
"""查找 AKShare 中可用的债券收益率和PE函数"""
import akshare as ak

# 查找债券相关函数
bond_funcs = [f for f in dir(ak) if 'bond' in f.lower() and 'yield' in f.lower()]
print('=== 债券收益率函数 ===')
for f in bond_funcs:
    print(f'  {f}')

# 查找PE相关函数
pe_funcs = [f for f in dir(ak) if ('pe' in f.lower() or 'value' in f.lower() or 'valuation' in f.lower()) and 'index' in f.lower()]
print('\n=== 指数估值函数 ===')
for f in pe_funcs:
    print(f'  {f}')

# 查找指数相关函数
idx_funcs = [f for f in dir(ak) if 'index' in f.lower() and ('hist' in f.lower() or 'daily' in f.lower())]
print('\n=== 指数历史函数 ===')
for f in idx_funcs:
    print(f'  {f}')

# 查找宏观函数
macro_funcs = [f for f in dir(ak) if 'macro' in f.lower() and ('bond' in f.lower() or 'yield' in f.lower() or 'rate' in f.lower())]
print('\n=== 宏观债券函数 ===')
for f in macro_funcs:
    print(f'  {f}')

# 查找所有含yield的函数
all_yield = [f for f in dir(ak) if 'yield' in f.lower()]
print('\n=== 所有含yield的函数 ===')
for f in all_yield:
    print(f'  {f}')
