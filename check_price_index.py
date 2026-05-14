import akshare as ak
import pandas as pd

# 检查中证500价格指数
print("=== 中证500价格指数 (sh000905) ===")
try:
    df = ak.stock_zh_index_daily(symbol="sh000905")
    print(df.tail(10))
except Exception as e:
    print(f"Error: {e}")

print("\n=== 沪深300价格指数 (sh000300) ===")
try:
    df = ak.stock_zh_index_daily(symbol="sh000300")
    print(df.tail(10))
except Exception as e:
    print(f"Error: {e}")

# 对比乐咕乐股的"指数"列和真实价格指数
print("\n=== 对比 ===")
pe_df = ak.stock_index_pe_lg(symbol="中证500")
price_df = ak.stock_zh_index_daily(symbol="sh000905")
print("乐咕乐股 指数列:")
print(pe_df[['日期', '指数']].tail())
print("\n价格指数:")
print(price_df[['date', 'close']].tail())
