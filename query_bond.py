import requests
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

TOKEN_FILE = Path.home() / ".workbuddy" / ".neodata_token"
token = TOKEN_FILE.read_text().strip()

url = "https://copilot.tencent.com/agenttool/v1/neodata"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
}

# Try to get historical PE and bond yield data
queries = [
    "上证指数历史PE市盈率年度数据",
    "沪深300历史市盈率PE年度数据",
    "中国10年期国债收益率年度历史数据2000年以来",
    "股债收益比ERP历史数据",
]

for q in queries:
    payload = {
        "query": q,
        "channel": "neodata",
        "sub_channel": "workbuddy",
        "data_type": "api"
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    result = resp.json()
    data = result.get("data", {})
    api_data = data.get("apiData", {})
    api_recall = api_data.get("apiRecall", [])
    entity = api_data.get("entity", [])
    print(f"\n=== Query: {q} ===")
    print(f"  Entity: {entity}")
    print(f"  apiRecall count: {len(api_recall)}")
    for item in api_recall:
        print(f"  type: {item.get('type')}, desc: {item.get('desc')}")
        content = item.get("content", "")
        if isinstance(content, str):
            print(f"  content preview: {content[:500]}")
