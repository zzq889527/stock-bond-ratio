import sys
import os
sys.path.insert(0, 'backend')

import pandas as pd
import akshare as ak

print("=== 调试全收益数据 ===\n")

# 获取数据
df_pe = ak.stock_index_pe_lg(symbol="沪深300")
df_total_return = ak.stock_zh_index_hist_csindex(symbol="H00300")

# 处理PE数据
df_pe['date'] = pd.to_datetime(df_pe['日期'])
df_pe = df_pe.rename(columns={
    '日期': 'date',
    '指数': 'hs300',
    '滚动市盈率': 'pe_ttm'
})
df_pe = df_pe[['date', 'hs300', 'pe_ttm']].sort_values('date')

# 处理全收益数据
df_total_return['date'] = pd.to_datetime(df_total_return['日期'])
df_total_return = df_total_return.rename(columns={
    '收盘': 'total_return'
})
df_total_return = df_total_return[['date', 'total_return']].sort_values('date')

print(f"PE数据: {len(df_pe)} 条, 范围: {df_pe['date'].iloc[0]} ~ {df_pe['date'].iloc[-1]}")
print(f"全收益数据: {len(df_total_return)} 条, 范围: {df_total_return['date'].iloc[0]} ~ {df_total_return['date'].iloc[-1]}")

# 合并数据
df = df_pe.copy()
df = pd.merge_asof(df, df_total_return, on='date', direction='backward')

print(f"\n合并后数据: {len(df)} 条")
print(f"\n前10条数据:")
print(df[['date', 'hs300', 'total_return']].head(10))
print(f"\n后10条数据:")
print(df[['date', 'hs300', 'total_return']].tail(10))

# 找到有效索引
first_valid_idx = df['total_return'].first_valid_index()
last_valid_idx = df['total_return'].last_valid_index()

print(f"\n第一个有效全收益索引: {first_valid_idx}")
print(f"最后一个有效全收益索引: {last_valid_idx}")

if last_valid_idx is not None:
    print(f"最后有效数据: date={df.loc[last_valid_idx, 'date']}, hs300={df.loc[last_valid_idx, 'hs300']}, tr={df.loc[last_valid_idx, 'total_return']}")

# 检查后面的数据
if last_valid_idx is not None:
    print(f"\n检查后面的数据 (从索引 {last_valid_idx+1} 开始):")
    check_df = df.loc[last_valid_idx:, ['date', 'hs300', 'total_return']]
    print(check_df.head(20))
