# -*- coding: utf-8 -*-
"""
直接用 AKShare pandas 获取所有指数K线并保存
"""
import json
import os
import time
import akshare as ak

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def save_kline(symbol, name):
    """获取并保存指数K线"""
    outpath = os.path.join(OUT_DIR, f'kline_{symbol}.json')
    if os.path.exists(outpath):
        with open(outpath, 'r') as f:
            data = json.load(f)
        print(f'{name} ({symbol}): {len(data)} 条 (缓存)', flush=True)
        return data
    
    print(f'{name} ({symbol})...', end=' ', flush=True)
    for attempt in range(5):
        try:
            df = ak.index_zh_a_hist(symbol=symbol, period='daily', start_date='20050101', end_date='20260501')
            data = []
            for _, row in df.iterrows():
                try:
                    data.append({
                        'date': str(row['日期'])[:10],
                        'close': round(float(row['收盘']), 2),
                    })
                except: continue
            if data:
                with open(outpath, 'w') as f:
                    json.dump(data, f)
                print(f'{len(data)} 条 (已缓存)', flush=True)
                return data
        except Exception as e:
            print(f'attempt {attempt+1}({e}) ', end='', flush=True)
            time.sleep(5 + attempt * 5)
    print('失败', flush=True)
    return []

# 获取中证全指和国证A指
zzall = save_kline('000985', '中证全指')
time.sleep(2)
gza = save_kline('399310', '国证A指')

# 更新 daily_data.json
dd_path = os.path.join(OUT_DIR, 'daily_data.json')
with open(dd_path, 'r', encoding='utf-8') as f:
    dd = json.load(f)

dd['zzall'] = zzall
dd['gza'] = gza
dd['meta']['zzall'] = len(zzall)
dd['meta']['gza'] = len(gza)

with open(dd_path, 'w', encoding='utf-8') as f:
    json.dump(dd, f, ensure_ascii=False)

print(f'\n更新完成: 中证全指={len(zzall)}, 国证A指={len(gza)}')
print(f'文件大小: {os.path.getsize(dd_path)/1024:.0f}KB')
