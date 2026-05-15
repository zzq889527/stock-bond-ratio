import json

with open('backend/data/sp500_erp_data.json', 'r') as f:
    data = json.load(f)

print('=== 2008-2009年价格和PE数据 ===')
for d in data:
    if d['date'] >= '2008-01-01' and d['date'] <= '2010-12-01':
        print(f"  {d['date']}  price={d['index_value']:.2f}  PE={d['pe_ttm']}  ERP={d['erp']:.2f}")

print()
print('=== 实际标普500价格参考（2008-2009） ===')
print('  2008-01: ~1380  2008-06: ~1280  2008-09: ~1166')
print('  2008-12: ~903   2009-03: ~757   2009-06: ~926')
print('  2009-09: ~1057  2009-12: ~1115')