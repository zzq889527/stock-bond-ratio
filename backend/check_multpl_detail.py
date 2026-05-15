import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Check multpl nominal price data for 2008
resp = requests.get('https://www.multpl.com/s-p-500-historical-prices/table/by-month', headers=headers, timeout=15)
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

df = pd.DataFrame(data, columns=['date_str', 'price'])
df['date'] = pd.to_datetime(df['date_str'], format='mixed')
df = df.sort_values('date').reset_index(drop=True)

print('=== 2007-2009 multpl名义价格数据 ===')
for _, row in df.iterrows():
    if row['date'].year >= 2007 and row['date'].year <= 2009:
        print('  ' + str(row['date'].date()) + ' -> ' + str(row['price']))

print()
print('=== 1997-1999 multpl名义价格数据 ===')
for _, row in df.iterrows():
    if row['date'].year >= 1997 and row['date'].year <= 1999:
        print('  ' + str(row['date'].date()) + ' -> ' + str(row['price']))

print()
print('=== 2002-2004 multpl名义价格数据 ===')
for _, row in df.iterrows():
    if row['date'].year >= 2002 and row['date'].year <= 2004:
        print('  ' + str(row['date'].date()) + ' -> ' + str(row['price']))

print()
print('=== 2015-2016 multpl名义价格数据 ===')
for _, row in df.iterrows():
    if row['date'].year >= 2015 and row['date'].year <= 2016:
        print('  ' + str(row['date'].date()) + ' -> ' + str(row['price']))