import akshare as ak
import pandas as pd

# 获取PE数据
df_pe = ak.stock_index_pe_lg(symbol="沪深300")
print("=== 沪深300 PE数据 ===")
print(df_pe[['日期', '指数', '等权滚动市盈率', '滚动市盈率']].head(20))

print("\n=== 最新数据 ===")
print(df_pe[['日期', '指数', '等权滚动市盈率', '滚动市盈率']].tail(5))

# 对比
latest = df_pe.iloc[-1]
print(f"\n最新日期: {latest['日期']}")
print(f"指数点位: {latest['指数']}")
print(f"等权PE: {latest['等权滚动市盈率']}")
print(f"市值加权PE: {latest['滚动市盈率']}")
print(f"等权ERP: {(1/latest['等权滚动市盈率'])*100:.2f}%")
print(f"市值加权ERP: {(1/latest['滚动市盈率'])*100:.2f}%")
