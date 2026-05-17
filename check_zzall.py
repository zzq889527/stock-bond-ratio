import json
from datetime import datetime, timedelta

with open(r'e:\Trae Project\backend\data\zzall_erp_data.json') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print(f"Range: {data[0]['date']} ~ {data[-1]['date']}")

# Monthly sampling
print("\n=== Monthly sampling (first of each month) ===")
for d in data:
    if d['date'].endswith('-01') or d['date'] == data[0]['date']:
        print(f"{d['date']} PE={d['pe_ttm']} Price={d['index_value']}")

# Large jumps
print("\n=== Large price jumps (>10% in a day) ===")
prev_price = None
for d in data:
    if prev_price:
        chg = (d['index_value'] - prev_price) / prev_price * 100
        if abs(chg) > 10:
            print(f"{d['date']} Price={d['index_value']:.2f} (prev={prev_price:.2f}) chg={chg:.1f}%")
    prev_price = d['index_value']

# Data gaps
print("\n=== Data gaps (>7 days) ===")
prev_date = None
for d in data:
    curr = datetime.strptime(d['date'], '%Y-%m-%d')
    if prev_date:
        gap = (curr - prev_date).days
        if gap > 7:
            print(f"  Gap: {prev_date.strftime('%Y-%m-%d')} -> {curr.strftime('%Y-%m-%d')} ({gap} days)")
    prev_date = curr