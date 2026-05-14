import urllib.request
import json
import re

# Check page
url = 'https://zzq889527.github.io/stock-bond-ratio/'
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
html = resp.read().decode('utf-8')
match = re.search(r'src="/stock-bond-ratio/assets/(index-[^"]+\.js)"', html)
if match:
    print(f'JS file: {match.group(1)}')
else:
    print('Could not find JS file')
print()

# Check data
files = [
    ('erp_data.json', '沪深300'),
    ('hs300_eq_erp_data.json', '沪深300等权'),
    ('zz500_erp_data.json', '中证500'),
    ('zz500_eq_erp_data.json', '中证500等权'),
    ('zzall_erp_data.json', '中证全指'),
    ('zzall_eq_erp_data.json', '中证全指等权'),
]

for fname, name in files:
    url = f'https://zzq889527.github.io/stock-bond-ratio/{fname}'
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    latest = data[-1]
    print(f'{name}: date={latest["date"]}, ERP={latest["erp"]}%, mean={latest["mean"]}%, signal={latest["signal"]}')
