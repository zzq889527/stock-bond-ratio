import subprocess
import json
import sys
import os

os.chdir(r"C:\Users\zzqo\.workbuddy\plugins\marketplaces\cb_teams_marketplace\plugins\finance-data\skills\neodata-financial-search")

# Read the query script to understand how to call the API directly
with open("scripts/query.py", "r", encoding="utf-8") as f:
    content = f.read()
print(content)
