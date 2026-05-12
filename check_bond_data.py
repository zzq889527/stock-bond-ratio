# -*- coding: utf-8 -*-
"""检查 bond_zh_us_rate 中中国10年国债收益率的覆盖范围"""
import akshare as ak
from datetime import date

df = ak.bond_zh_us_rate()
cn10 = df[df['中国国债收益率10年'].notna()]

print(f'最早: {cn10.iloc[0]["日期"]}  {cn10.iloc[0]["中国国债收益率10年"]}')
print(f'最晚: {cn10.iloc[-1]["日期"]}  {cn10.iloc[-1]["中国国债收益率10年"]}')
print(f'总数: {len(cn10)}')

# 逐年统计
for y in range(2002, 2027):
    cnt = len(df[(df['日期'] >= date(y,1,1)) & (df['日期'] <= date(y,12,31)) & (df['中国国债收益率10年'].notna())])
    if cnt > 0:
        sub = df[(df['日期'] >= date(y,1,1)) & (df['日期'] <= date(y,12,31)) & (df['中国国债收益率10年'].notna())]
        first = sub.iloc[0]
        last = sub.iloc[-1]
        print(f'{y}: {cnt}条  {first["日期"]}~{last["日期"]} 首{first["中国国债收益率10年"]} 尾{last["中国国债收益率10年"]}')
    else:
        print(f'{y}: 无数据')
