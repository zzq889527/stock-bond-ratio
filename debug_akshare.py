import akshare as ak
import pandas as pd

# Test PE data structure
print("=== Testing PE data ===")
try:
    df_pe = ak.stock_index_pe_lg(symbol="沪深300")
    print(f"Columns: {df_pe.columns.tolist()}")
    print(df_pe.head())
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing Bond data ===")
try:
    df_bond = ak.bond_zh_us_rate()
    print(f"Columns: {df_bond.columns.tolist()}")
    print(df_bond.head())
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing Total Return data ===")
try:
    df_tr = ak.stock_zh_index_hist_csindex(symbol="H00300")
    print(f"Columns: {df_tr.columns.tolist()}")
    print(df_tr.head())
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing Price Index data ===")
try:
    df_price = ak.stock_zh_index_daily(symbol="sh000300")
    print(f"Columns: {df_price.columns.tolist()}")
    print(df_price.head())
except Exception as e:
    print(f"Error: {e}")
