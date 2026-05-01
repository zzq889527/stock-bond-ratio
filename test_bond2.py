# -*- coding: utf-8 -*-
"""调试: 测试 bond_china_yield 的日期范围"""
import akshare as ak

# 测试不同日期范围
tests = [
    ('20260101', '20260430', '2026 Q1'),
    ('20250101', '20251231', '2025'),
    ('20200101', '20201231', '2020'),
    ('20150101', '20151231', '2015'),
    ('20100101', '20101231', '2010'),
    ('20050101', '20091231', '2005-2009'),
]

for start, end, label in tests:
    try:
        df = ak.bond_china_yield(start_date=start, end_date=end)
        mask = df['曲线名称'].str.contains('国债', na=False)
        count = len(df[mask])
        total = len(df)
        print(f'{label}: total={total}, 国债={count}')
        if count > 0:
            print(f'  日期范围: {df[mask]["日期"].iloc[0]} ~ {df[mask]["日期"].iloc[-1]}')
            print(f'  10年样本: {df[mask]["10年"].iloc[0]}')
    except Exception as e:
        print(f'{label}: 错误 {e}')
