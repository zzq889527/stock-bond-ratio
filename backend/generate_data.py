
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import shutil

DATA_PATH = Path(__file__).parent / "data"
DATA_PATH.mkdir(exist_ok=True)

INDEX_CONFIGS = [
    {"id": "hs300", "name": "沪深300", "multiplier": 1.0},
    {"id": "hs300_eq", "name": "沪深300等权", "multiplier": 1.1},
    {"id": "zz500", "name": "中证500", "multiplier": 1.15},
    {"id": "zz500_eq", "name": "中证500等权", "multiplier": 1.25},
    {"id": "zzall", "name": "中证全指", "multiplier": 1.05},
    {"id": "zzall_eq", "name": "中证全指等权", "multiplier": 1.15}
]

def calculate_erp(pe, bond_yield):
    if pd.isna(pe) or pe == 0:
        return np.nan
    return (1.0 / pe) * 100 - bond_yield

def generate_index_data_from_base(base_data, config):
    np.random.seed(42)
    multiplier = config["multiplier"]
    
    df = pd.DataFrame(base_data).copy()
    df['index_value'] = df['hs300'] * multiplier
    
    adjustment = np.random.normal(0, 0.05, len(df))
    df['pe_ttm'] = (df['pe_ttm'] * (1 + adjustment * (multiplier - 1))).clip(5, 150).round(2)
    
    df['erp'] = df.apply(lambda row: calculate_erp(row['pe_ttm'], row['bond_10y']), axis=1)
    
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
    
    df['total_return'] = (df['total_return'] * multiplier).round(1)
    df['tr_p'] = (100 / df['pe_ttm']).round(2)
    
    return df

def main():
    print("加载沪深300基础数据...")
    with open(DATA_PATH / "erp_data.json", 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    
    print(f"基础数据：{len(base_data)} 条")
    
    for config in INDEX_CONFIGS:
        if config['id'] == 'hs300':
            print(f"\n处理 {config['name']}...")
            records = base_data
            with open(DATA_PATH / f"{config['id']}_erp_data.json", 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"   ✓ 保存 {config['name']}")
            continue
        
        print(f"\n生成 {config['name']} 数据...")
        df = generate_index_data_from_base(base_data, config)
        
        records = df.to_dict('records')
        with open(DATA_PATH / f"{config['id']}_erp_data.json", 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ 保存 {config['name']}")
    
    print(f"\n复制数据到 dist 目录...")
    dist_path = Path(__file__).parent.parent / "dist"
    for config in INDEX_CONFIGS:
        src_file = DATA_PATH / f"{config['id']}_erp_data.json"
        dst_file = dist_path / f"{config['id']}_erp_data.json"
        if src_file.exists():
            shutil.copy(src_file, dst_file)
            print(f"   ✓ 复制 {config['name']}")
    
    print("\n所有数据生成完成！")

if __name__ == "__main__":
    main()
