
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import shutil

DATA_PATH = Path(__file__).parent / "data"
DATA_PATH.mkdir(exist_ok=True)

def generate_mock_data():
    data = []
    start_date = pd.Timestamp('2005-04-08')
    end_date = pd.Timestamp('2026-05-14')
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')
    
    np.random.seed(42)
    
    # 目标：最新ERP约5.35%，均值4.46%，标准差2.34%
    # 低估阈值 = 4.46 + 0.5*2.34 = 5.63%
    # 所以当前应该是"均衡"（5.35% < 5.63%）
    
    mean_erp = 4.46
    std_erp = 2.34
    
    # 生成接近真实分布的ERP序列
    erp_values = []
    current_erp = 4.5
    
    for i, date in enumerate(date_range):
        # 趋势和季节性
        trend = np.sin(i / 252 * np.pi * 2) * 0.8
        seasonal = np.sin(i / 63 * np.pi * 2) * 0.3
        noise = (np.random.rand() - 0.5) * std_erp * 0.5
        
        # 更新ERP
        current_erp = current_erp + trend * 0.02 + seasonal * 0.01 + noise * 0.1
        current_erp = max(-2, min(12, current_erp))
        
        # 逐渐接近目标值（5.35）
        if i > len(date_range) - 10:
            current_erp = current_erp * 0.3 + 5.35 * 0.7
        
        erp_values.append(current_erp)
    
    erp_values = np.array(erp_values)
    
    for i, date in enumerate(date_range):
        erp = round(erp_values[i], 2)
        pe_ttm = round((100 / (erp + np.random.uniform(3.0, 4.5))), 2)
        hs300 = round(3500 + np.cumsum(np.random.randn(len(date_range)) * 20)[i], 2)
        total_return = round(hs300 * (1.35 + np.random.rand() * 0.15), 1)
        bond_yield = round(3.2 + np.sin(i / 252 * np.pi * 2) * 1.5 + (np.random.rand() - 0.5) * 0.3, 4)
        
        # 信号判断
        low_threshold = mean_erp + 0.5 * std_erp  # 5.63
        high_threshold = mean_erp - 0.5 * std_erp  # 3.29
        
        if erp > mean_erp + std_erp:  # > 6.8
            signal = '极度低估'
        elif erp > low_threshold:  # > 5.63
            signal = '低估'
        elif erp >= high_threshold:  # >= 3.29
            signal = '均衡'
        elif erp >= mean_erp - std_erp:  # >= 2.12
            signal = '高估'
        else:  # < 2.12
            signal = '极度高估'
        
        z_score = (erp - mean_erp) / std_erp
        percentile = int(min(99, max(1, ((1 + erf(z_score / np.sqrt(2))) / 2) * 100)))
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'erp': erp,
            'mean': mean_erp,
            'sigma': std_erp,
            'percentile': percentile,
            'signal': signal,
            'pe_ttm': pe_ttm,
            'bond_10y': bond_yield,
            'hs300': hs300,
            'total_return': total_return,
            'tr_p': round(100 / pe_ttm, 2)
        })
    
    return data

def erf(x):
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    
    sign = 1 if x >= 0 else -1
    x = abs(x)
    
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - ((((a5 * t + a4) * t) + a3) * t + a2) * t * a1 * np.exp(-x * x)
    
    return sign * y

INDEX_CONFIGS = [
    {"id": "hs300", "name": "沪深300", "multiplier": 1.0, "mean_adj": 0.0, "sigma_adj": 1.0},
    {"id": "hs300_eq", "name": "沪深300等权", "multiplier": 0.98, "mean_adj": 0.15, "sigma_adj": 1.08},
    {"id": "zz500", "name": "中证500", "multiplier": 0.82, "mean_adj": 0.35, "sigma_adj": 1.12},
    {"id": "zz500_eq", "name": "中证500等权", "multiplier": 0.85, "mean_adj": 0.5, "sigma_adj": 1.18},
    {"id": "zzall", "name": "中证全指", "multiplier": 0.75, "mean_adj": 0.1, "sigma_adj": 1.05},
    {"id": "zzall_eq", "name": "中证全指等权", "multiplier": 0.78, "mean_adj": 0.25, "sigma_adj": 1.1}
]

def generate_index_data(base_data, config):
    np.random.seed(42)
    
    mean_erp = 4.46 + config["mean_adj"]
    std_erp = 2.34 * config["sigma_adj"]
    
    result = []
    for item in base_data:
        erp = item['erp'] * (1 + config["mean_adj"] * 0.05) + np.random.uniform(-0.3, 0.3)
        erp = max(-2, min(12, erp))
        
        # 信号判断
        low_threshold = mean_erp + 0.5 * std_erp
        high_threshold = mean_erp - 0.5 * std_erp
        
        if erp > mean_erp + std_erp:
            signal = '极度低估'
        elif erp > low_threshold:
            signal = '低估'
        elif erp >= high_threshold:
            signal = '均衡'
        elif erp >= mean_erp - std_erp:
            signal = '高估'
        else:
            signal = '极度高估'
        
        z_score = (erp - mean_erp) / std_erp
        percentile = int(min(99, max(1, ((1 + erf(z_score / np.sqrt(2))) / 2) * 100)))
        
        result.append({
            'date': item['date'],
            'erp': round(erp, 2),
            'mean': round(mean_erp, 2),
            'sigma': round(std_erp, 2),
            'percentile': percentile,
            'signal': signal,
            'pe_ttm': round(item['pe_ttm'] * (1 + config["mean_adj"] * 0.08), 2),
            'bond_10y': item['bond_10y'],
            'index_value': round(item['hs300'] * config["multiplier"], 2),
            'total_return': round(item['total_return'] * config["multiplier"], 1),
            'tr_p': round(100 / (item['pe_ttm'] * (1 + config["mean_adj"] * 0.08)), 2)
        })
    
    return result

def main():
    print("正在生成沪深300基础数据...")
    base_data = generate_mock_data()
    
    with open(DATA_PATH / "erp_data.json", 'w', encoding='utf-8') as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
    
    last = base_data[-1]
    print(f"✓ 沪深300数据已生成")
    print(f"  最新: {last['date']}, ERP={last['erp']}%, 信号={last['signal']}")
    print()
    
    dist_path = Path(__file__).parent.parent / "dist"
    
    for config in INDEX_CONFIGS:
        print(f"处理 {config['name']}...")
        
        if config['id'] == 'hs300':
            data = base_data
        else:
            data = generate_index_data(base_data, config)
        
        data_path_file = DATA_PATH / f"{config['id']}_erp_data.json"
        dist_path_file = dist_path / f"{config['id']}_erp_data.json"
        
        with open(data_path_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        shutil.copy(data_path_file, dist_path_file)
        
        last = data[-1]
        print(f"  ✓ 最新: {last['date']}, ERP={last['erp']}%, 均值={last['mean']}%, 信号={last['signal']}")
    
    print("\n所有数据生成完成！")

if __name__ == "__main__":
    main()
