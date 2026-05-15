import json

with open('backend/data/sp500_erp_data.json', 'r') as f:
    data = json.load(f)

print('=== PB数据验证（插值后） ===')
pb_vals = [(d['date'], d['pb']) for d in data if d['pb'] != 0]
print(f'  PB非0的数据: {len(pb_vals)}条')
if pb_vals:
    print(f'  范围: {pb_vals[0][0]} ~ {pb_vals[-1][0]}')

print()
print('关键年份的PB值:')
check_years = ['1999-12', '2000-06', '2000-12', '2001-06', '2001-12',
               '2005-06', '2008-06', '2008-12', '2009-06', '2009-12',
               '2020-01', '2020-06', '2020-12', '2025-01', '2025-06', '2025-12', '2026-05']
for d in data:
    if any(d['date'].startswith(y) for y in check_years):
        print(f"  {d['date']}: PB={d['pb']:.2f}")

print()
print('=== 验证PB是否平滑过渡 ===')
for i, d in enumerate(data):
    if d['date'] >= '2000-01' and d['date'] <= '2001-12':
        if i > 0 and i < len(data)-1:
            prev = data[i-1]
            next_ = data[i+1]
            # Check if PB changes gradually (not step function)
            if abs(d['pb'] - prev['pb']) > 0.3:
                print(f"  大跳变: {prev['date']}: {prev['pb']:.2f} -> {d['date']}: {d['pb']:.2f}")