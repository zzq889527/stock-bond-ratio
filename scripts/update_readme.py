#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
README_PATH = ROOT / "README.md"

DATA_FILES = [
    ("public/sp500_erp_data.json", "标普500"),
    ("public/erp_data.json", "沪深300"),
    ("public/zz500_erp_data.json", "中证500"),
    ("public/zzall_erp_data.json", "中证全指"),
]

def get_data_stats():
    rows = []
    for f, name in DATA_FILES:
        path = ROOT / f
        if not path.exists():
            rows.append(f"| {name} | - | - |")
            continue
        try:
            d = json.load(open(path, encoding="utf-8"))
            rows.append(f"| {name} | {d[0]['date']} ~ 最新 | {len(d)}条 |")
        except Exception:
            rows.append(f"| {name} | - | - |")
    return "\n".join(rows)

def update_readme():
    try:
        stats = get_data_stats()
    except Exception:
        return False
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
    except Exception:
        return False
    
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False
    
    try:
        table_block = (
            "| 指数 | 数据范围 | 记录数 |\n"
            "|------|---------|-------|\n"
            + stats + "\n"
        )
        pattern = r"## 支持指数\n\n.*?\n<!-- DATA_STATS -->"
        replacement = "## 支持指数\n\n" + table_block + "<!-- DATA_STATS -->"
        content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    except Exception:
        pass
    
    try:
        content = re.sub(
            r"(<!-- DATA_STATS -->\n> 📊 数据最后更新：).*?(\n<!-- /DATA_STATS -->)",
            rf"\g<1>{today}\g<2>",
            content, count=1
        )
    except Exception:
        pass
    
    try:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"OK README: {today}")
        return True
    except Exception:
        return False

if __name__ == "__main__":
    try:
        update_readme()
    except Exception:
        pass