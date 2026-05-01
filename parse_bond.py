import json
import re

# Read the bond rate data
with open(r"C:\Users\zzqo\WorkBuddy\20260501084217\bond_rate.json", "r", encoding="utf-8") as f:
    data = json.load(f)

api_recall = data["data"]["apiData"]["apiRecall"]
content = api_recall[0]["content"]

# Parse the markdown table
lines = content.strip().split("\n")
data_rows = []
for line in lines:
    if line.startswith("|") and "中债国债到期收益率:10年" in line:
        parts = [p.strip() for p in line.split("|")]
        # parts: ['', query, name, date, pub_date, unit, value, '']
        if len(parts) >= 7:
            date_val = parts[3]  # 数据日期
            value = parts[6]  # 数据值
            try:
                data_rows.append((date_val, float(value)))
            except:
                pass

print(f"Total rows: {len(data_rows)}")
if data_rows:
    print(f"First: {data_rows[0]}")
    print(f"Last: {data_rows[-1]}")
    # Get date range
    dates = [r[0] for r in data_rows]
    dates.sort()
    print(f"Date range: {dates[0]} to {dates[-1]}")
