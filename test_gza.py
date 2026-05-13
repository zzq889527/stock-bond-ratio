# -*- coding: utf-8 -*-
import urllib.request, ssl, json
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 测试国证A指
url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.399310&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20050101&end=20260501&lmt=6000'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
r = urllib.request.urlopen(req, timeout=30, context=ctx)
t = r.read().decode('utf-8')
j = json.loads(t)
d = j.get('data', {})
klines = d.get('klines', [])
print(f'name: {d.get("name")}, klines: {len(klines)}')
if klines:
    print(f'first: {klines[0]}')
    print(f'last: {klines[-1]}')
