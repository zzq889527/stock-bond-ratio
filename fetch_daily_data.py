# -*- coding: utf-8 -*-
"""
数据获取脚本 v4 - 最终版
AKShare获取 PE-TTM (2005~2026) + 国债收益率 (2010~2026)
AKShare备用获取 指数K线
"""
import json
import os
import time
import akshare as ak

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_pe_ttm():
    print('[1/3] PE-TTM...', end=' ', flush=True)
    try:
        df = ak.stock_index_pe_lg(symbol='沪深300')
        data = []
        for _, row in df.iterrows():
            try:
                data.append({
                    'date': str(row['日期'])[:10],
                    'pe_ttm': round(float(row['滚动市盈率']), 2),
                    'close': round(float(row['指数']), 2),
                })
            except: continue
        data.sort(key=lambda x: x['date'])
        print(f'{len(data)} 条', flush=True)
        return data
    except Exception as e:
        print(f'失败: {e}', flush=True)
        return []

def get_bond_yield():
    print('[2/3] 10Y国债收益率...', flush=True)
    all_data = []
    years = list(range(2010, 2027))
    
    for y in years:
        try:
            df = ak.bond_china_yield(start_date=f'{y}0101', end_date=f'{y}1231')
            mask = df['曲线名称'].str.contains('国债', na=False)
            for _, row in df[mask].iterrows():
                try:
                    yld = float(row['10年'])
                    if yld > 0:
                        all_data.append({'date': str(row['日期'])[:10], 'yield': round(yld, 4)})
                except: continue
            time.sleep(0.2)
        except: pass
    
    # 去重排序
    seen = set()
    unique = [d for d in sorted(all_data, key=lambda x: x['date']) if not (d['date'] in seen or seen.add(d['date']))]
    print(f'  合计: {len(unique)} 条', flush=True)
    return unique

def get_kline(symbol, name):
    """用 AKShare 获取指数日K线，带重试"""
    print(f'  {name} ({symbol})...', end=' ', flush=True)
    for attempt in range(3):
        try:
            df = ak.index_zh_a_hist(symbol=symbol, period='daily', start_date='20050101', end_date='20260501')
            data = []
            for _, row in df.iterrows():
                try:
                    data.append({
                        'date': str(row['日期'])[:10],
                        'close': round(float(row['收盘']), 2),
                    })
                except: continue
            if data:
                print(f'{len(data)} 条', flush=True)
                return data
        except Exception as e:
            print(f'attempt {attempt+1}: {e}', end=' ', flush=True)
            time.sleep(3)
    print('失败', flush=True)
    return []

def get_index_klines():
    print('[3/3] 指数日K线 (AKShare)...', flush=True)
    hs300 = get_kline('000300', '沪深300')
    time.sleep(1)
    zzall = get_kline('000985', '中证全指')
    time.sleep(1)
    gza = get_kline('399310', '国证A指')
    return hs300, zzall, gza

def main():
    t0 = time.time()
    print('=' * 60)
    
    pe = get_pe_ttm()
    bond = get_bond_yield()
    hs300, zzall, gza = get_index_klines()
    
    # 合并ERP
    bond_map = {d['date']: d['yield'] for d in bond}
    for item in hs300:
        item['bond_yield'] = bond_map.get(item['date'])
        if item.get('pe_ttm') and item.get('bond_yield'):
            item['erp'] = round(100.0 / item['pe_ttm'] - item['bond_yield'], 4)
        else:
            item['erp'] = None
    
    valid_erp = sum(1 for x in hs300 if x.get('erp') is not None)
    
    output = {
        'hs300': hs300, 'zzall': zzall, 'gza': gza,
        'pe_ttm': pe, 'bond_yields': bond,
        'meta': {
            'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'hs300': len(hs300), 'zzall': len(zzall), 'gza': len(gza),
            'pe': len(pe), 'bond': len(bond), 'erp': valid_erp,
        }
    }
    
    outpath = os.path.join(OUT_DIR, 'daily_data.json')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    elapsed = time.time() - t0
    print(f'\n{"=" * 60}')
    print(f'完成！{elapsed:.1f}s | {os.path.getsize(outpath)/1024:.0f}KB')
    print(f'沪深300:{len(hs300)} 中证全指:{len(zzall)} 国证A指:{len(gza)}')
    print(f'PE:{len(pe)} 国债:{len(bond)} ERP:{valid_erp}')

if __name__ == '__main__':
    main()
