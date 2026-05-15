import json
import sys

with open('backend/data/sp500_erp_data.json', 'r') as f:
    data = json.load(f)

print('=== 价格数据异常检查（月环比>30%） ===')
for i, d in enumerate(data):
    if i > 0:
        prev = data[i-1]
        if prev['index_value'] > 0:
            ratio = d['index_value'] / prev['index_value']
            if ratio > 1.3 or ratio < 0.7:
                print(f"  [{d['date']}] price={d['index_value']:.2f}  prev={prev['index_value']:.2f}  ratio={ratio:.4f}  PE={d['pe_ttm']}")

print()
print('=== ERP异常检查（>15或<-10） ===')
for d in data:
    if d['erp'] > 15 or d['erp'] < -10:
        print(f"  [{d['date']}] ERP={d['erp']:.2f}  PE={d['pe_ttm']}  bond={d['bond_10y']}  price={d['index_value']:.2f}")

print()
print('=== PE异常检查（>100或<5） ===')
for d in data:
    if d['pe_ttm'] > 100 or d['pe_ttm'] < 5:
        print(f"  [{d['date']}] PE={d['pe_ttm']}  price={d['index_value']:.2f}  bond={d['bond_10y']}")

print()
print('=== 数据概览 ===')
print(f"  总条数: {len(data)}")
print(f"  日期范围: {data[0]['date']} ~ {data[-1]['date']}")
prices = [d['index_value'] for d in data]
print(f"  价格范围: {min(prices):.2f} ~ {max(prices):.2f}")
pes = [d['pe_ttm'] for d in data]
print(f"  PE范围: {min(pes):.2f} ~ {max(pes):.2f}")
erps = [d['erp'] for d in data]
print(f"  ERP范围: {min(erps):.2f} ~ {max(erps):.2f}")

print()
print('=== 价格分段检查 ===')
for d in data:
    if d['date'] in ['1970-01-01', '1980-01-01', '1990-01-01', '2000-01-01', '2010-01-01', '2020-01-01', '2026-01-01']:
        print(f"  [{d['date']}] price={d['index_value']:.2f}  PE={d['pe_ttm']}  div={d['dividend_yield']}  bond={d['bond_10y']}  ERP={d['erp']:.2f}")

print()
print('=== 检查PB=0的数据点 ===')
pb_zero = [d for d in data if d['pb'] == 0]
print(f"  PB=0的数据: {len(pb_zero)}条")
if pb_zero:
    print(f"  最早: {pb_zero[0]['date']}  最晚: {pb_zero[-1]['date']}")

print()
print('=== 检查股息率异常 ===')
for d in data:
    if d['dividend_yield'] > 10 or d['dividend_yield'] < 0.5:
        print(f"  [{d['date']}] dividend_yield={d['dividend_yield']:.2f}  PE={d['pe_ttm']}")