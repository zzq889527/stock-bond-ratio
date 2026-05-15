import requests
import pandas as pd
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?period1=536457600&period2=1747267200&interval=1mo'
resp = requests.get(url, headers=headers, timeout=15)
data = resp.json()
result = data['chart']['result'][0]
timestamps = result['timestamp']
quotes = result['indicators']['quote'][0]
closes = quotes['close']

rows = []
for ts, close in zip(timestamps, closes):
    if close is not None:
        dt = datetime.fromtimestamp(ts)
        rows.append({'date': dt, 'price': close})

yahoo = pd.DataFrame(rows)
yahoo['date'] = pd.to_datetime(yahoo['date'])
yahoo = yahoo.sort_values('date').reset_index(drop=True)

print('Yahoo 2008-01:')
for _, row in yahoo.iterrows():
    if row['date'].year == 2008 and row['date'].month == 1:
        print(f"  date={row['date']}, price={row['price']}")

print()
print('Yahoo 2008-01 to 2008-09:')
for _, row in yahoo.iterrows():
    if row['date'] >= pd.Timestamp('2008-01-01') and row['date'] <= pd.Timestamp('2008-09-01'):
        print(f"  date={row['date']}, price={row['price']}")

print()
print('Yahoo date range:')
print(f"  {yahoo['date'].min()} ~ {yahoo['date'].max()}")
print(f"  Total rows: {len(yahoo)}")

# Check if 2008-01-01 exists
mask = yahoo['date'] == pd.Timestamp('2008-01-01')
print(f"  2008-01-01 exists: {mask.any()}")
if mask.any():
    print(f"  Value: {yahoo.loc[mask, 'price'].values[0]}")