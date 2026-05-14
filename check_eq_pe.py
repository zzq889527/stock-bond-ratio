import akshare as ak
import pandas as pd

# 检查等权PE列是否存在
for name in ['沪深300', '中证500', '中证800']:
    df = ak.stock_index_pe_lg(symbol=name)
    has_eq = '等权滚动市盈率' in df.columns
    cols = df.columns.tolist()
    daterange = f"{df['日期'].min()} ~ {df['日期'].max()}"
    print(f"{name}:")
    print(f"  列名: {cols}")
    print(f"  日期范围: {daterange}")
    print(f"  是否有等权PE: {has_eq}")
    if has_eq:
        valid_eq = df['等权滚动市盈率'].notna().sum()
        valid_reg = df['滚动市盈率'].notna().sum()
        print(f"  等权PE有效值: {valid_eq} 条")
        print(f"  市值PE有效值: {valid_reg} 条")
        latest_eq = df['等权滚动市盈率'].iloc[-1]
        latest_reg = df['滚动市盈率'].iloc[-1]
        print(f"  最新等权PE: {latest_eq}")
        print(f"  最新市值PE: {latest_reg}")
        print(f"  最新ERP(等权): {(1/latest_eq)*100:.2f}%")
        print(f"  最新ERP(市值): {(1/latest_reg)*100:.2f}%")
    print()