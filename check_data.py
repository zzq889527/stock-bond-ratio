import json

with open('backend/data/erp_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"数据总条数: {len(data)}")
print("\n最后10条数据:")
for d in data[-10:]:
    print(f"{d['date']}: hs300={d['hs300']}, total_return={d['total_return']}, erp={d['erp']}")
