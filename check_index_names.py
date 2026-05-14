import akshare as ak
import pandas as pd

# 测试中证500的PE数据
print("=== 中证500 PE数据 ===")
try:
    df = ak.stock_index_pe_lg(symbol="中证500")
    print(df.columns.tolist())
    print(df.tail(10))
except Exception as e:
    print(f"Error: {e}")

print("\n=== 中证800 PE数据 ===")
try:
    df = ak.stock_index_pe_lg(symbol="中证800")
    print(df.columns.tolist())
    print(df.tail(10))
except Exception as e:
    print(f"Error: {e}")

print("\n=== 沪深300 PE数据 ===")
try:
    df = ak.stock_index_pe_lg(symbol="沪深300")
    print(df.columns.tolist())
    print(df.tail(10))
except Exception as e:
    print(f"Error: {e}")
