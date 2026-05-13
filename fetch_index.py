# -*- coding: utf-8 -*-
"""获取中证全指和国证A指，更新到 daily_data.json"""
import json, os, subprocess

dd_path = r'C:\Users\zzqo\WorkBuddy\20260501084217\daily_data.json'
with open(dd_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

def parse_westock(code):
    result = subprocess.run(
        f'npx --yes westock-data-skillhub@latest kline {code} day 120',
        shell=True, capture_output=True, text=True, encoding='utf-8', timeout=60
    )
    rows = []
    started = False
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('| ---'): started = True; continue
        if started and line.startswith('|'):
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) >= 3:
                try: rows.append({'date': cells[0], 'close': round(float(cells[2]), 2)})
                except: pass
    rows.reverse()
    return rows

print('获取中证全指...')
d['zzall'] = parse_westock('sh000985')
print(f'  {len(d["zzall"])} 条')

import time; time.sleep(1)

print('获取国证A指...')
d['gza'] = parse_westock('sz399310')
print(f'  {len(d["gza"])} 条')

d['meta']['zzall'] = len(d['zzall'])
d['meta']['gza'] = len(d['gza'])

with open(dd_path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False)

print(f'已更新 daily_data.json ({os.path.getsize(dd_path)/1024:.0f}KB)')
