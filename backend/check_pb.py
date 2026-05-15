import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Check PB data from multpl.com
resp = requests.get('https://www.multpl.com/s-p-500-price-to-book/table/by-month', headers=headers, timeout=15)
soup = BeautifulSoup(resp.content, 'html.parser')
table = soup.find('table')
rows = table.find_all('tr')
data = []
for row in rows[1:]:
    cols = row.find_all('td')
    if len(cols) >= 2:
        date_str = cols[0].get_text(strip=True)
        val_str = cols[1].get_text(strip=True)
        val_str = re.sub(r'[†‡%]', '', val_str)
        try:
            val = float(val_str)
            data.append((date_str, val))
        except:
            pass

pb_multpl = pd.DataFrame(data, columns=['date_str', 'pb'])
pb_multpl['date'] = pd.to_datetime(pb_multpl['date_str'], format='mixed')
pb_multpl = pb_multpl.sort_values('date').reset_index(drop=True)

print('=== multpl.com PB数据 ===')
print(f'  总行数: {len(pb_multpl)}')
print(f'  日期范围: {pb_multpl["date"].min().date()} ~ {pb_multpl["date"].max().date()}')
print()
print('样本数据:')
for _, row in pb_multpl.iterrows():
    print(f'  {row["date"].date()} -> PB={row["pb"]}')

print()

# Check our generated data
with open('backend/data/sp500_erp_data.json', 'r') as f:
    sp500_data = json.load(f)

print('=== 我们数据中的PB ===')
pb_vals = [(d['date'], d['pb']) for d in sp500_data if d['pb'] != 0]
print(f'  PB非0的数据: {len(pb_vals)}条')
if pb_vals:
    print(f'  范围: {pb_vals[0][0]} ~ {pb_vals[-1][0]}')
    for date, pb in pb_vals[:5]:
        print(f'  {date} -> PB={pb}')
    print('  ...')
    for date, pb in pb_vals[-5:]:
        print(f'  {date} -> PB={pb}')

print()
print('=== 对比最新PB值 ===')
latest_multpl = pb_multpl.iloc[-1]
print(f'  multpl.com最新: {latest_multpl["date"].date()} -> PB={latest_multpl["pb"]}')
latest_ours = sp500_data[-1]
print(f'  我们数据最新: {latest_ours["date"]} -> PB={latest_ours["pb"]}')