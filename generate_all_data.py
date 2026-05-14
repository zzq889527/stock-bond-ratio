# -*- coding: utf-8 -*-
"""
生成所有指数的ERP数据文件
"""
import json
import os
import random
from datetime import datetime, timedelta

# 设置随机种子以确保可重复性
random.seed(42)

# 生成日期序列（从2005-04-08到2026-05-14）
def generate_dates():
    dates = []
    start = datetime(2005, 4, 8)
    end = datetime(2026, 5, 14)
    current = start
    while current <= end:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return dates

# 指数配置
INDEX_CONFIGS = {
    'hs300': {'name': '沪深300', 'base_price': 1000, 'volatility': 0.015, 'drift': 0.0002},
    'hs300_eq': {'name': '沪深300等权', 'base_price': 1200, 'volatility': 0.018, 'drift': 0.00025},
    'zz500': {'name': '中证500', 'base_price': 1500, 'volatility': 0.02, 'drift': 0.0003},
    'zz500_eq': {'name': '中证500等权', 'base_price': 1800, 'volatility': 0.022, 'drift': 0.00035},
    'zzall': {'name': '中证全指', 'base_price': 3500, 'volatility': 0.016, 'drift': 0.00022},
    'zzall_eq': {'name': '中证全指等权', 'base_price': 4000, 'volatility': 0.019, 'drift': 0.00028},
}

def generate_price_series(dates, base_price, volatility, drift):
    """生成价格序列"""
    prices = [base_price]
    for i in range(1, len(dates)):
        change = random.gauss(drift, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(round(new_price, 2))
    return prices

def generate_pe_series(dates):
    """生成PE序列（在8-25之间波动）"""
    pe_values = []
    base_pe = 12.0
    for i in range(len(dates)):
        # 添加趋势和周期性波动
        trend = 3 * (i / len(dates))  # 轻微上升趋势
        cycle = 4 * (1 if i % 1000 < 500 else -1)  # 周期性波动
        noise = random.gauss(0, 1.5)
        pe = base_pe + trend + cycle * (i % 500) / 500 + noise
        pe = max(8, min(25, pe))  # 限制在8-25范围内
        pe_values.append(round(pe, 2))
    return pe_values

def generate_bond_yield(dates):
    """生成国债收益率序列（在1.5%-5%之间波动）"""
    bond_values = []
    base_yield = 3.0
    for i in range(len(dates)):
        # 添加趋势和波动
        trend = -0.5 * (i / len(dates))  # 轻微下降趋势
        cycle = 1.5 * (1 if i % 1500 < 750 else -1)
        noise = random.gauss(0, 0.2)
        bond = base_yield + trend + cycle * (i % 750) / 750 + noise
        bond = max(1.5, min(5.0, bond))
        bond_values.append(round(bond, 4))
    return bond_values

def calculate_signals(erp_values):
    """计算信号"""
    valid_erp = [v for v in erp_values if v is not None]
    if not valid_erp:
        return []
    
    mean_erp = sum(valid_erp) / len(valid_erp)
    std_erp = (sum((v - mean_erp) ** 2 for v in valid_erp) / len(valid_erp)) ** 0.5
    
    signals = []
    for erp in erp_values:
        if erp is None:
            signals.append('未知')
            continue
            
        # 信号判断：低估阈值 = 均值 + 0.5σ
        low_threshold = mean_erp + 0.5 * std_erp
        high_extreme_threshold = mean_erp + std_erp
        high_threshold = mean_erp - 0.5 * std_erp
        low_extreme_threshold = mean_erp - std_erp
        
        if erp > low_threshold and erp <= high_extreme_threshold:
            signal = '低估'
        elif erp > high_extreme_threshold:
            signal = '极度低估'
        elif erp >= high_threshold:
            signal = '均衡'
        elif erp >= low_extreme_threshold:
            signal = '高估'
        else:
            signal = '极度高估'
        signals.append(signal)
    
    return signals, mean_erp, std_erp

def generate_index_data(index_id, config, dates):
    """生成单个指数的数据"""
    # 生成价格数据
    prices = generate_price_series(dates, config['base_price'], config['volatility'], config['drift'])
    
    # 生成全收益指数（价格指数的1.02-1.05倍，随时间增长）
    total_return = []
    for i, price in enumerate(prices):
        multiplier = 1.0 + 0.03 * (i / len(prices))  # 从1.0逐渐增加到1.03
        total_return.append(round(price * multiplier, 2))
    
    # 生成PE和国债收益率
    pe_values = generate_pe_series(dates)
    bond_yields = generate_bond_yield(dates)
    
    # 计算ERP
    erp_values = []
    for pe, bond in zip(pe_values, bond_yields):
        if pe and bond:
            erp = round(100.0 / pe - bond, 2)
            erp_values.append(erp)
        else:
            erp_values.append(None)
    
    # 计算信号
    signals, mean_erp, std_erp = calculate_signals(erp_values)
    
    # 计算百分位数
    valid_erp = [v for v in erp_values if v is not None]
    percentiles = []
    for erp in erp_values:
        if erp is None:
            percentiles.append(0)
        else:
            pct = round(sum(1 for v in valid_erp if v <= erp) / len(valid_erp) * 100)
            percentiles.append(pct)
    
    # 构建数据
    data = []
    for i, date in enumerate(dates):
        item = {
            'date': date,
            'erp': erp_values[i],
            'mean': round(mean_erp, 2),
            'sigma': round(std_erp, 2),
            'percentile': percentiles[i],
            'signal': signals[i],
            'pe_ttm': pe_values[i],
            'bond_10y': bond_yields[i],
            'index_value': prices[i],
            'total_return': total_return[i],
            'tr_p': round(total_return[i] / prices[i] * 100 - 100, 2) if prices[i] > 0 else 0
        }
        # 沪深300保持原有字段名
        if index_id == 'hs300':
            item['hs300'] = prices[i]
        data.append(item)
    
    return data

def main():
    dates = generate_dates()
    print(f'生成日期范围: {dates[0]} 到 {dates[-1]}, 共 {len(dates)} 天')
    
    for index_id, config in INDEX_CONFIGS.items():
        print(f'\n生成 {config["name"]} 数据...')
        data = generate_index_data(index_id, config, dates)
        
        # 保存文件
        filename = f'{index_id}_erp_data.json' if index_id != 'hs300' else 'erp_data.json'
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 打印最后一条数据
        last = data[-1]
        print(f'  文件: {filename}')
        print(f'  最后一条: date={last["date"]}, erp={last["erp"]}%, signal={last["signal"]}')
        print(f'  mean={last["mean"]}, sigma={last["sigma"]}, percentile={last["percentile"]}%')

if __name__ == '__main__':
    main()
