# -*- coding: utf-8 -*-
"""调试: 看看 bond_china_yield 返回了什么"""
import akshare as ak

# 获取一小段看看
df = ak.bond_china_yield(start_date='20260101', end_date='20260430')
print('columns:', list(df.columns))
print('rows:', len(df))
print()
print('曲线名称唯一值:')
for name in df['曲线名称'].unique():
    count = len(df[df['曲线名称'] == name])
    print(f'  {name}: {count}条')
print()
# 找国债
mask = df['曲线名称'].str.contains('国债', na=False)
print('含"国债"的行:', len(df[mask]))
if len(df[mask]) > 0:
    print(df[mask][['曲线名称', '日期', '10年']].head(5))
