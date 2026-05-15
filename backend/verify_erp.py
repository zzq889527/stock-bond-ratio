import json

with open('backend/data/sp500_erp_data.json', 'r') as f:
    data = json.load(f)

print("=== ERP计算公式验证 ===")
print("公式: ERP = (1/PE) * 100 - 美债10Y收益率")
print()

# Check a few data points
check_dates = ['2000-01-01', '2005-01-01', '2008-01-01', '2009-03-01', '2013-01-01', '2020-01-01', '2023-01-01', '2026-01-01']
for d in data:
    if d['date'] in check_dates:
        pe = d['pe_ttm']
        bond = d['bond_10y']
        earnings_yield = (1.0 / pe) * 100
        erp_calc = round(earnings_yield - bond, 2)
        erp_data = round(d['erp'], 2)
        match = "✓" if abs(erp_calc - erp_data) < 0.01 else "✗"
        print(f"[{d['date']}]")
        print(f"  PE={pe}, 1/PE*100={earnings_yield:.2f}%, 美债10Y={bond}%")
        print(f"  ERP计算值: {erp_calc}%  数据中值: {erp_data}%  {match}")
        print()

print("=== 最新数据点 ===")
latest = data[-1]
pe = latest['pe_ttm']
bond = latest['bond_10y']
earnings_yield = (1.0 / pe) * 100
erp_calc = round(earnings_yield - bond, 2)
print(f"  日期: {latest['date']}")
print(f"  PE={pe}, 1/PE*100={earnings_yield:.2f}%, 美债10Y={bond}%")
print(f"  ERP计算值: {erp_calc}%  数据中值: {round(latest['erp'], 2)}%")
print()

print("=== 全量数据ERP范围 ===")
erps = [d['erp'] for d in data]
print(f"  最小值: {min(erps):.2f}%")
print(f"  最大值: {max(erps):.2f}%")
print(f"  均值: {sum(erps)/len(erps):.2f}%")
print()

print("=== 检查ERP与PE/利率的关系 ===")
# ERP should be high when PE is low (cheap) or bond yield is low
# ERP should be low when PE is high (expensive) or bond yield is high
for d in data[-10:]:
    pe = d['pe_ttm']
    bond = d['bond_10y']
    ey = (1.0/pe)*100
    erp = d['erp']
    print(f"  {d['date']}: PE={pe:.1f}, 盈利收益率={ey:.2f}%, 美债={bond}%, ERP={erp:.2f}%")

print()
print("=== 检查tr_p (total_return) ===")
for d in data[-5:]:
    tr_p = d['tr_p']
    ey = round((1.0/d['pe_ttm'])*100, 2)
    match = "✓" if abs(tr_p - ey) < 0.01 else "✗"
    print(f"  {d['date']}: tr_p={tr_p}, 1/PE*100={ey}  {match}")