import requests
import pandas as pd
import json
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Try Yahoo Finance API directly
url = 'https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?period1=536457600&period2=1747267200&interval=1mo'
try:
    resp = requests.get(url, headers=headers, timeout=15)
    print(f'Yahoo Finance API: status={resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        closes = quotes['close']
        
        rows = []
        for ts, close in zip(timestamps, closes):
            if close is not None:
                dt = datetime.fromtimestamp(ts)
                rows.append({'date': dt.strftime('%Y-%m-%d'), 'price': round(close, 2)})
        
        df = pd.DataFrame(rows)
        print(f'Yahoo data: {len(df)} rows')
        print(f'  Range: {df["date"].iloc[0]} ~ {df["date"].iloc[-1]}')
        
        # Check 2008-2009
        for _, row in df.iterrows():
            if row['date'] >= '2008-01' and row['date'] <= '2009-12':
                print(f'  {row["date"]}: {row["price"]}')
    else:
        print(f'  Response: {resp.text[:500]}')
except Exception as e:
    print(f'Yahoo Finance API failed: {e}')

# Try alternative Yahoo endpoint
url2 = 'https://query2.finance.yahoo.com/v8/finance/chart/%5EGSPC?period1=536457600&period2=1747267200&interval=1mo'
try:
    resp2 = requests.get(url2, headers=headers, timeout=15)
    print(f'\nYahoo Finance API (query2): status={resp2.status_code}')
except Exception as e:
    print(f'Yahoo Finance API (query2) failed: {e}')