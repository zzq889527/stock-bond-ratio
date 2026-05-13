# -*- coding: utf-8 -*-
"""
合并已有数据：
- PE-TTM 中已有沪深300收盘价
- 国债收益率已获取
- 中证全指和国证A指用之前缓存的 westock-data + 东方财富数据
"""
import json
import os
import subprocess
import time

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 读取已有的 daily_data.json
with open(os.path.join(OUT_DIR, 'daily_data.json'), 'r', encoding='utf-8') as f:
    cached = json.load(f)

pe = cached['pe_ttm']  # 5117条，含 index_val
bond = cached['bond_yields']  # 4080条
gza_cached = cached['gza']  # 100条

print(f'缓存数据: PE={len(pe)}, 国债={len(bond)}, 国证A指={len(gza_cached)}')

# 从 PE 数据中提取沪深300收盘价
hs300 = []
for item in pe:
    hs300.append({
        'date': item['date'],
        'close': item['close'],
        'pe_ttm': item['pe_ttm'],
    })

# 构建 ERP
bond_map = {d['date']: d['yield'] for d in bond}
for item in hs300:
    item['bond_yield'] = bond_map.get(item['date'])
    if item.get('pe_ttm') and item.get('bond_yield'):
        item['erp'] = round(100.0 / item['pe_ttm'] - item['bond_yield'], 4)
    else:
        item['erp'] = None

valid_erp = sum(1 for x in hs300 if x.get('erp') is not None)
print(f'沪深300: {len(hs300)} 条, 有效ERP: {valid_erp}')

# 尝试获取中证全指 - 用 westock-data (每次100条，分多段)
print('\n尝试获取中证全指...')
zzall = []
# 用 npx 批量获取
try:
    result = subprocess.run(
        'npx --yes westock-data-skillhub@latest kline sh000985 day 5000',
        shell=True, capture_output=True, text=True, encoding='utf-8', timeout=120
    )
    output = result.stdout
    lines = output.strip().split('\n')
    started = False
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith('| ---'): started = True; continue
        if started and line.startswith('|'):
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]
            if len(cells) >= 3:
                try:
                    zzall.append({'date': cells[0], 'close': round(float(cells[2]), 2)})
                except: continue
    zzall.reverse()
    print(f'  中证全指: {len(zzall)} 条')
except Exception as e:
    print(f'  失败: {e}')

# 尝试获取更多中证全指历史 - 用 AKShare 重试一次
if len(zzall) < 100:
    print('  AKShare 备用...')
    try:
        import akshare as ak
        df = ak.index_zh_a_hist(symbol='000985', period='daily', start_date='20050101', end_date='20260501')
        for _, row in df.iterrows():
            try:
                zzall.append({'date': str(row['日期'])[:10], 'close': round(float(row['收盘']), 2)})
            except: continue
        # 去重排序
        seen = set()
        unique = [d for d in sorted(zzall, key=lambda x: x['date']) if not (d['date'] in seen or seen.add(d['date']))]
        zzall = unique
        print(f'  中证全指(合并): {len(zzall)} 条')
    except Exception as e:
        print(f'  AK也失败: {e}')

# 合并输出
output = {
    'hs300': hs300,
    'zzall': zzall,
    'gza': gza_cached,
    'pe_ttm': pe,
    'bond_yields': bond,
    'meta': {
        'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'hs300': len(hs300), 'zzall': len(zzall), 'gza': len(gza_cached),
        'pe': len(pe), 'bond': len(bond), 'erp': valid_erp,
    }
}

outpath = os.path.join(OUT_DIR, 'daily_data.json')
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False)

print(f'\n最终: daily_data.json ({os.path.getsize(outpath)/1024:.0f}KB)')
print(f'沪深300:{len(hs300)} 中证全指:{len(zzall)} 国证A指:{len(gza_cached)} ERP:{valid_erp}')
