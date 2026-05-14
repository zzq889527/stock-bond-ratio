import akshare as ak
import pandas as pd

# 测试是否有等权PE数据
print("=== 沪深300 PE数据（检查等权列） ===")
df = ak.stock_index_pe_lg(symbol="沪深300")
print(df.columns.tolist())
print(df[['日期', '指数', '等权滚动市盈率', '滚动市盈率']].tail(10))

print("\n=== 中证500 PE数据 ===")
df = ak.stock_index_pe_lg(symbol="中证500")
print(df.columns.tolist())
print(df[['日期', '指数', '等权滚动市盈率', '滚动市盈率']].tail(10))

# 测试聚宽
print("\n=== 尝试获取更多指数 ===")
try:
    df = ak.stock_index_pe_lg(symbol="中证1000")
    print("中证1000: 列 =", df.columns.tolist())
except Exception as e:
    print(f"中证1000: {e}")
