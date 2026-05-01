# -*- coding: utf-8 -*-
"""
补充 2005-2009 年国债收益率数据到 daily_data.json
使用 AKShare bond_zh_us_rate (2002年起)
"""
import json
import os
import akshare as ak
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(DATA_DIR, 'daily_data.json')

# 1. 获取完整的中国10年国债收益率 (2002~2026)
print('[1/3] 获取 bond_zh_us_rate 数据...', end=' ', flush=True)
df = ak.bond_zh_us_rate()
bond_map = {}
for _, row in df.iterrows():
    v = row['中国国债收益率10年']
    d = row['日期']
    if v is not None and not pd.isna(v):
        # 日期转字符串 YYYY-MM-DD
        d_str = str(d)[:10] if not isinstance(d, str) else d[:10]
        bond_map[d_str] = round(float(v), 4)
print(f'{len(bond_map)} 条日期有数据')

# 2. 加载现有数据
print('[2/3] 加载 daily_data.json...', end=' ', flush=True)
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
hs300 = data['hs300']
print(f'{len(hs300)} 条 hs300 数据')

# 3. 补充 bond_yield 和重算 ERP
print('[3/3] 补充 bond_yield 和重算 ERP...', flush=True)
filled_2005_2009 = 0
filled_all = 0
for item in hs300:
    dt = item['date']
    new_yield = bond_map.get(dt)
    if new_yield is not None:
        old = item.get('bond_yield')
        if old is None or abs(old - new_yield) > 0.0001:
            item['bond_yield'] = new_yield
            filled_all += 1
            if '2005' <= dt <= '2009':
                filled_2005_2009 += 1
    
    # 重算 ERP
    if item.get('pe_ttm') and item.get('bond_yield'):
        item['erp'] = round(100.0 / item['pe_ttm'] - item['bond_yield'], 4)

# 统计
valid_erp = sum(1 for x in hs300 if x.get('erp') is not None)
erp_vals = [x['erp'] for x in hs300 if x.get('erp') is not None]
erp_mean = round(sum(erp_vals)/len(erp_vals), 2) if erp_vals else 0
erp_first = next(x for x in hs300 if x.get('erp') is not None)
erp_last = hs300[-1] if hs300[-1].get('erp') else next(x for x in reversed(hs300) if x.get('erp'))

print(f'  补充/更新 bond_yield: {filled_all} 条')
print(f'  其中 2005-2009 年: {filled_2005_2009} 条')
print(f'  有效 ERP: {valid_erp} 条')
print(f'  ERP 最早: {erp_first["date"]} = {erp_first["erp"]}%')
print(f'  ERP 最晚: {erp_last["date"]} = {erp_last["erp"]}%')
print(f'  ERP 均值: {erp_mean}%')

# 4. 保存
data['meta']['bond_source'] = 'bond_zh_us_rate (2002~2026)'
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print(f'\n✅ 保存完成')
