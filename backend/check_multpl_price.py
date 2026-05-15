import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

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
print('名义价格数据: ' + str(len(df)) + '行')
print('日期范围: ' + str(df['date'].min().date()) + ' ~ ' + str(df['date'].max().date()))

df['year'] = df['date'].dt.year
years = sorted(df['year'].unique())
all_years = list(range(min(years), max(years)+1))
missing = [y for y in all_years if y not in years]
print('年份范围: ' + str(min(years)) + ' ~ ' + str(max(years)))
print('缺失年份: ' + str(missing))

print('\n样本数据:')
for _, row in df.iloc[:5].iterrows():
    print('  ' + str(row['date'].date()) + ' -> ' + str(row['price']))
print('...')
for _, row in df.iloc[-5:].iterrows():
    print('  ' + str(row['date'].date()) + ' -> ' + str(row['price']))