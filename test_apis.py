# -*- coding: utf-8 -*-
"""测试东方财富国债收益率和PE接口"""
import urllib.request, ssl, json, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def try_url(url, name):
    print(f'\n--- {name} ---')
    print(f'URL: {url[:100]}...')
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': UA,
            'Referer': 'https://data.eastmoney.com/'
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        text = resp.read().decode('utf-8')
        j = json.loads(text)
        code = j.get('code', 'N/A')
        msg = j.get('message', 'N/A')
        print(f'code: {code}, message: {msg}')
        
        # 尝试提取数据
        result = j.get('result', j.get('data', {}))
        if isinstance(result, dict):
            data = result.get('data', [])
            total = result.get('count', len(data))
            print(f'data count: {len(data)}, total: {total}')
            if data:
                print(f'first: {json.dumps(data[0], ensure_ascii=False)[:200]}')
                print(f'last: {json.dumps(data[-1], ensure_ascii=False)[:200]}')
        elif isinstance(result, list):
            print(f'data count: {len(result)}')
            if result:
                print(f'first: {json.dumps(result[0], ensure_ascii=False)[:200]}')
    except Exception as e:
        print(f'Error: {e}')

# 1. 国债收益率 - 尝试不同接口
# 中债国债收益率
try_url(
    'https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_BOND_CB_INDEX_DAILY&columns=ALL&pageSize=5&sortColumns=TRADE_DATE&sortTypes=-1',
    '中债国债收益率(取5条测试)'
)

# 2. 指数PE估值
try_url(
    'https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_LICO_FN_CPD&columns=ALL&pageSize=5&sortColumns=TRADE_DATE&sortTypes=-1&filter=(SECURITY_CODE="000300")',
    '沪深300 PE-TTM(取5条测试)'
)

# 3. 另一个PE接口
try_url(
    'https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_VALUEANAL_DET&columns=ALL&pageSize=5&sortColumns=TRADE_DATE&sortTypes=-1&filter=(SECURITY_CODE="000300")',
    '沪深300 估值分析(取5条测试)'
)

# 4. 指数估值数据 - 东方财富另一个接口
try_url(
    'https://push2.eastmoney.com/api/qt/stock/get?secid=1.000300&fields=f43,f44,f45,f46,f47,f48,f49,f50,f55,f57,f58,f59,f60,f71,f116,f117,f162,f167,f168,f169,f170,f171',
    '沪深300 实时估值'
)

# 5. 国债收益率 - 新浪接口
try_url(
    'https://hq.sinajs.cn/list=CNY10YR',
    '新浪10Y国债收益率(实时)'
)
