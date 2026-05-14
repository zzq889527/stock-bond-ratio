#!/usr/bin/env python3
"""
生成所有指数的真实ERP数据
使用 akshare 获取真实数据
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path

# 指数配置
INDEX_CONFIGS = [
    {
        "id": "hs300",
        "name": "沪深300",
        "pe_symbol": "沪深300",
        "price_symbol": "sh000300",
        "total_return_symbol": "H00300"
    },
    {
        "id": "zz500",
        "name": "中证500",
        "pe_symbol": "中证500",
        "price_symbol": "sh000905",
        "total_return_symbol": "H00905"
    },
    {
        "id": "zzall",
        "name": "中证全指",
        "pe_symbol": "中证800",
        "price_symbol": "sh000985",
        "total_return_symbol": "H00985"
    }
]

def calculate_erp(pe, bond_yield):
    """计算ERP: 1/PE * 100 - 国债收益率"""
    if pd.isna(pe) or pe == 0:
        return np.nan
    return (1.0 / pe) * 100 - bond_yield

def get_signal(erp, mean_erp, std_erp):
    """判断信号"""
    if erp > mean_erp + std_erp:
        return '极度低估'
    elif erp > mean_erp + 0.5 * std_erp:
        return '低估'
    elif erp >= mean_erp - 0.5 * std_erp:
        return '均衡'
    elif erp >= mean_erp - std_erp:
        return '高估'
    else:
        return '极度高估'

def get_real_data_for_index(config):
    """获取单个指数的真实数据"""
    index_id = config["id"]
    index_name = config["name"]
    print(f"\n=== 获取 {index_name} 数据 ===")
    
    # 1. 获取PE数据
    try:
        df_pe = ak.stock_index_pe_lg(symbol=config["pe_symbol"])
        print(f"   ✓ PE数据：{len(df_pe)} 条")
    except Exception as e:
        print(f"   ✗ PE数据获取失败：{e}")
        raise
    
    # 2. 获取全收益数据
    df_tr = None
    try:
        df_tr = ak.stock_zh_index_hist_csindex(symbol=config["total_return_symbol"])
        print(f"   ✓ 全收益数据：{len(df_tr)} 条")
    except Exception as e:
        print(f"   ✗ 全收益数据获取失败：{e}")
    
    # 3. 获取价格指数数据
    df_price = None
    try:
        df_price = ak.stock_zh_index_daily(symbol=config["price_symbol"])
        print(f"   ✓ 价格指数数据：{len(df_price)} 条")
    except Exception as e:
        print(f"   ✗ 价格指数获取失败：{e}")
    
    # 4. 获取国债收益率数据
    try:
        df_bond = ak.bond_zh_us_rate()
        print(f"   ✓ 国债数据：{len(df_bond)} 条")
    except Exception as e:
        print(f"   ✗ 国债数据获取失败：{e}")
        raise
    
    print(f"   开始处理 {index_name} 数据...")
    
    # 处理PE数据
    df_pe['日期'] = pd.to_datetime(df_pe['日期'])
    
    # 使用滚动市盈率
    pe_col = '滚动市盈率'
    
    # 使用 '指数' 列作为指数点位
    df_pe = df_pe[['日期', '指数', pe_col]].copy()
    df_pe.columns = ['date', 'index_value', 'pe_ttm']
    df_pe = df_pe.sort_values('date').reset_index(drop=True)
    
    # 处理全收益数据
    if df_tr is not None:
        df_tr['日期'] = pd.to_datetime(df_tr['日期'])
        df_tr = df_tr[['日期', '收盘']].copy()
        df_tr.columns = ['date', 'total_return']
        df_tr = df_tr.sort_values('date').reset_index(drop=True)
    
    # 处理价格指数数据
    if df_price is not None:
        df_price['date'] = pd.to_datetime(df_price['date'])
        df_price = df_price[['date', 'close']].copy()
        df_price.columns = ['date', 'price_close']
        df_price = df_price.sort_values('date').reset_index(drop=True)
    
    # 处理国债数据
    df_bond['日期'] = pd.to_datetime(df_bond['日期'])
    df_bond = df_bond[['日期', '中国国债收益率10年']].copy()
    df_bond.columns = ['date', 'bond_10y']
    df_bond = df_bond.sort_values('date').reset_index(drop=True)
    
    # 合并数据
    df = df_pe.copy()
    
    # 使用价格指数数据（如果有）
    if df_price is not None:
        df = pd.merge_asof(df, df_price, on='date', direction='nearest')
    else:
        df['price_close'] = df['index_value']
    
    # 合并全收益数据
    if df_tr is not None:
        # 记录全收益数据的截止日期
        tr_max_date = df_tr['date'].max()
        
        df = pd.merge_asof(
            df,
            df_tr,
            on='date',
            direction='nearest'
        )
        
        # 填充缺失的全收益数据（前面的缺失）
        first_valid_idx = df['total_return'].first_valid_index()
        if first_valid_idx is not None and first_valid_idx > 0:
            ratio = df.loc[first_valid_idx, 'total_return'] / df.loc[first_valid_idx, 'index_value']
            df.loc[:first_valid_idx-1, 'total_return'] = (
                df.loc[:first_valid_idx-1, 'index_value'] * ratio
            ).round(1)
        
        # 全收益数据截止日期之后的数据，用价格指数推算
        mask_after_tr = df['date'] > tr_max_date
        if mask_after_tr.any():
            last_tr_row = df[df['date'] <= tr_max_date].iloc[-1]
            if df_price is not None and df_price['date'].max() > tr_max_date:
                last_ratio = last_tr_row['total_return'] / last_tr_row['price_close']
                df.loc[mask_after_tr, 'total_return'] = (
                    df.loc[mask_after_tr, 'price_close'] * last_ratio
                ).round(1)
            else:
                last_ratio = last_tr_row['total_return'] / last_tr_row['index_value']
                df.loc[mask_after_tr, 'total_return'] = (
                    df.loc[mask_after_tr, 'index_value'] * last_ratio
                ).round(1)
        
        df['total_return'] = df['total_return'].ffill().bfill()
    else:
        df['total_return'] = df['index_value']
    
    # 合并国债数据
    df = pd.merge_asof(df, df_bond, on='date', direction='backward')
    df['bond_10y'] = df['bond_10y'].ffill().bfill()
    
    # 删除无效数据
    df = df.dropna(subset=['index_value', 'pe_ttm', 'bond_10y', 'total_return'])
    
    # 过滤日期范围
    df = df[(df['date'] >= pd.Timestamp('2005-04-08')) & (df['date'] <= pd.Timestamp(datetime.now()))]
    
    # 计算ERP
    df['erp'] = df.apply(lambda row: calculate_erp(row['pe_ttm'], row['bond_10y']), axis=1)
    df = df.dropna(subset=['erp'])
    
    # 计算TR_P
    df['tr_p'] = (100 / df['pe_ttm']).round(2)
    
    # 计算统计指标
    mean_erp = round(df['erp'].mean(), 2)
    std_erp = round(df['erp'].std(), 2)
    
    df['mean'] = mean_erp
    df['sigma'] = std_erp
    df['percentile'] = (df['erp'].rank(pct=True) * 100).round(0).astype(int)
    
    # 判断信号
    df['signal'] = df['erp'].apply(lambda x: get_signal(x, mean_erp, std_erp))
    
    # 格式化日期
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    print(f"   ✓ {index_name} 数据完成：{len(df)} 条, ERP均值={mean_erp}%, 标准差={std_erp}%")
    return df

def generate_all_index_data(refresh=False):
    """生成所有指数数据"""
    all_data = {}
    
    for config in INDEX_CONFIGS:
        try:
            df = get_real_data_for_index(config)
            
            records = []
            for _, row in df.iterrows():
                record = {
                    'date': str(row['date']),
                    'erp': round(float(row['erp']), 2),
                    'mean': float(row['mean']),
                    'sigma': float(row['sigma']),
                    'percentile': int(row['percentile']),
                    'signal': str(row['signal']),
                    'pe_ttm': round(float(row['pe_ttm']), 2),
                    'bond_10y': round(float(row['bond_10y']), 4),
                    'index_value': round(float(row['index_value']), 2),
                    'total_return': round(float(row['total_return']), 1),
                    'tr_p': round(float(row['tr_p']), 2)
                }
                records.append(record)
            
            all_data[config['id']] = records
            
            # 打印最新数据
            latest = records[-1]
            print(f"   最新: {latest['date']}, ERP={latest['erp']}%, 均值={latest['mean']}%, 信号={latest['signal']}")
            
        except Exception as e:
            print(f"   ✗ {config['name']} 失败：{e}")
            import traceback
            traceback.print_exc()
    
    return all_data

def save_data(all_data, output_dir):
    """保存数据到指定目录"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存各指数数据
    for index_id, records in all_data.items():
        if index_id == 'hs300':
            filename = 'erp_data.json'
        else:
            filename = f'{index_id}_erp_data.json'
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 保存 {output_path}")
    
    print(f"\n共保存 {len(all_data)} 个指数的数据")

def main():
    print("=" * 60)
    print("开始生成所有指数的真实ERP数据")
    print("=" * 60)
    
    # 生成数据
    all_data = generate_all_index_data(refresh=True)
    
    # 保存到项目目录
    project_root = Path(__file__).parent.parent
    public_dir = project_root / 'public'
    dist_dir = project_root / 'dist'
    backend_data_dir = project_root / 'backend' / 'data'
    
    print("\n=== 保存数据 ===")
    save_data(all_data, public_dir)
    save_data(all_data, dist_dir)
    save_data(all_data, backend_data_dir)
    
    print("\n" + "=" * 60)
    print("数据生成完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
