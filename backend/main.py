import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path

app = FastAPI(title="股债收益比数据API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).parent / "data"
DATA_PATH.mkdir(exist_ok=True)

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
    if pd.isna(pe) or pe == 0:
        return np.nan
    return (1.0 / pe) * 100 - bond_yield

def get_real_data_for_index(index_config):
    index_id = index_config["id"]
    index_name = index_config["name"]
    print(f"\n=== 获取 {index_name} 数据 ===")
    
    try:
        df_pe = ak.stock_index_pe_lg(symbol=index_config["pe_symbol"])
        print(f"   ✓ PE数据：{len(df_pe)} 条")
    except Exception as e:
        print(f"   ✗ PE数据获取失败：{e}")
        raise
    
    df_tr = None
    try:
        df_tr = ak.stock_zh_index_hist_csindex(symbol=index_config["total_return_symbol"])
        print(f"   ✓ 全收益数据：{len(df_tr)} 条")
    except Exception as e:
        print(f"   ✗ 全收益数据获取失败：{e}")
    
    df_price = None
    try:
        df_price = ak.stock_zh_index_daily(symbol=index_config["price_symbol"])
        print(f"   ✓ 价格指数数据：{len(df_price)} 条")
    except Exception as e:
        print(f"   ✗ 价格指数获取失败：{e}")
    
    try:
        df_bond = ak.bond_zh_us_rate()
        print(f"   ✓ 国债数据：{len(df_bond)} 条")
    except Exception as e:
        print(f"   ✗ 国债数据获取失败：{e}")
        raise
    
    print(f"   开始处理 {index_name} 数据...")
    
    df_pe['日期'] = pd.to_datetime(df_pe['日期'])
    df_pe = df_pe.rename(columns={
        '日期': 'date',
        '指数': 'index_value',
        '滚动市盈率': 'pe_ttm'
    })
    df_pe = df_pe[['date', 'index_value', 'pe_ttm']].sort_values('date')
    
    if df_tr is not None:
        df_tr['日期'] = pd.to_datetime(df_tr['日期'])
        df_tr = df_tr.rename(columns={
            '日期': 'date',
            '收盘': 'total_return'
        })
        df_tr = df_tr[['date', 'total_return']].sort_values('date')
    
    if df_price is not None:
        df_price['date'] = pd.to_datetime(df_price['date'])
        df_price = df_price.rename(columns={
            'close': 'price_close'
        })
        df_price = df_price[['date', 'price_close']].sort_values('date')
    
    df_bond['日期'] = pd.to_datetime(df_bond['日期'])
    df_bond = df_bond.rename(columns={'日期': 'date', '中国国债收益率10年': 'bond_10y'})
    df_bond = df_bond[['date', 'bond_10y']].sort_values('date')
    
    df = df_pe.copy()
    
    if df_price is not None:
        df = pd.merge_asof(df, df_price, on='date', direction='nearest')
    
    if df_tr is not None:
        tr_max_date = df_tr['date'].max()
        
        df = pd.merge_asof(df, df_tr, on='date', direction='nearest')
        
        first_valid_idx = df['total_return'].first_valid_index()
        if first_valid_idx is not None and first_valid_idx > 0:
            ratio = df.loc[first_valid_idx, 'total_return'] / df.loc[first_valid_idx, 'index_value']
            df.loc[:first_valid_idx-1, 'total_return'] = (
                df.loc[:first_valid_idx-1, 'index_value'] * ratio
            ).round(1)
        
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
        df['total_return'] = (df['index_value'] * 1.5).round(1)
    
    df = pd.merge_asof(df, df_bond, on='date', direction='backward')
    
    df['bond_10y'] = df['bond_10y'].ffill().bfill()
    df = df.dropna(subset=['index_value', 'pe_ttm', 'bond_10y', 'total_return'])
    
    df = df[(df['date'] >= pd.Timestamp('2005-04-08')) & (df['date'] <= pd.Timestamp(datetime.now()))]
    
    df['erp'] = df.apply(lambda row: calculate_erp(row['pe_ttm'], row['bond_10y']), axis=1)
    df = df.dropna(subset=['erp'])
    
    df['tr_p'] = (100 / df['pe_ttm']).round(2)
    
    mean_erp = round(df['erp'].mean(), 2)
    std_erp = round(df['erp'].std(), 2)
    
    df['mean'] = mean_erp
    df['sigma'] = std_erp
    df['percentile'] = (df['erp'].rank(pct=True) * 100).round(0).astype(int)
    
    def get_signal(erp):
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
    
    df['signal'] = df['erp'].apply(get_signal)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    print(f"   ✓ {index_name} 数据完成：{len(df)} 条")
    return df

def generate_all_index_data(refresh=False):
    all_data = {}
    
    for config in INDEX_CONFIGS:
        cache_file = DATA_PATH / f"{config['id']}_erp_data.json"
        
        if not refresh and cache_file.exists():
            print(f"\n加载缓存：{config['name']}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                all_data[config['id']] = json.load(f)
            continue
        
        try:
            df = get_real_data_for_index(config)
            
            records = []
            for _, row in df.iterrows():
                record = {
                    'date': str(row['date']),
                    'erp': float(row['erp']),
                    'mean': float(row['mean']),
                    'sigma': float(row['sigma']),
                    'percentile': int(row['percentile']),
                    'signal': str(row['signal']),
                    'pe_ttm': float(row['pe_ttm']),
                    'bond_10y': float(row['bond_10y']),
                    'index_value': float(row['index_value']),
                    'total_return': float(row['total_return']),
                    'tr_p': float(row['tr_p'])
                }
                records.append(record)
            
            all_data[config['id']] = records
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            print(f"   ✓ 保存缓存：{config['name']}")
            
        except Exception as e:
            print(f"   ✗ {config['name']} 失败：{e}")
            import traceback
            traceback.print_exc()
    
    return all_data

@app.get("/api/all-data")
async def get_all_data_endpoint(refresh=False):
    try:
        all_data = generate_all_index_data(refresh=refresh)
        return {
            'data': all_data,
            'total_indices': len(all_data),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error: {e}")
        return {'error': str(e)}

@app.get("/api/health")
async def health_check():
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}

if __name__ == "__main__":
    print("开始生成所有指数数据...")
    all_data = generate_all_index_data(refresh=True)
    
    import shutil
    dist_path = Path(__file__).parent.parent / "dist"
    for config in INDEX_CONFIGS:
        src_file = DATA_PATH / f"{config['id']}_erp_data.json"
        dst_file = dist_path / f"{config['id']}_erp_data.json"
        if src_file.exists():
            shutil.copy(src_file, dst_file)
            print(f"复制 {config['name']} 数据到 dist")
    
    print("\n数据生成完成！")