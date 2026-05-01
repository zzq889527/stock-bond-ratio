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

queries = [
    "沪深300全收益指数历史行情数据",
    "H00300沪深300全收益指数",
    "沪深300全收益指数",
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
        t = item.get('type')
        d = item.get('desc')
        content = item.get("content", "")
        if isinstance(content, str):
            print(f"  type: {t}, desc: {d}")
            print(f"  preview: {content[:500]}")
        else:
            print(f"  type: {t}, desc: {d}, content type: {type(content)}")
