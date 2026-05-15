import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

start = datetime(1990, 1, 1)
end = datetime(2026, 5, 15)

# Try to get S&P 500 from investing.com via pandas-datareader
# Try different FRED series for S&P 500
fred_series = ['SP500', 'NASDAQCOM', 'DJIA']
for series in fred_series:
    try:
        df = web.DataReader(series, 'fred', start, end)
        df = df.dropna()
        print(f'FRED {series}: {len(df)} rows, {df.index[0].date()} ~ {df.index[-1].date()}')
    except Exception as e:
        print(f'FRED {series} failed: {e}')

# Try to get from Nasdaq website directly
import requests
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
try:
    url = 'https://api.nasdaq.com/api/quote/SPY/historical?assetclass=etf&fromdate=2000-01-01&todate=2026-05-15&limit=9999'
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'Nasdaq API: status={resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'  Response keys: {list(data.keys())}')
except Exception as e:
    print(f'Nasdaq API failed: {e}')

# Try macrotrends
try:
    url = 'https://www.macrotrends.net/assets/php/stock_price_history.php?t=SPY'
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'Macrotrends: status={resp.status_code}')
except Exception as e:
    print(f'Macrotrends failed: {e}')