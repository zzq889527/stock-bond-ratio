# -*- coding: utf-8 -*-
"""
[已废弃 2026-10-01] 请改用 update_dashboard.py
原因：乐咕乐股免费接口已改为仅返回月频PE（freq=day 需 VIP），
      本脚本会得到月频PE导致序列错位；且全收益为估算值。
新方案见 update_dashboard.py：中证指数官网(000300/H00300 日频) + 中债登10Y。
"""
import json
import os
import sys
import time
from datetime import datetime
import akshare as ak

# 调试日志
DEBUG_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fetch_debug.log')
def log(msg):
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    print(msg, flush=True)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_pe_ttm():
    log('[1/3] PE-TTM...')
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
        log(f'PE-TTM 成功: {len(data)} 条')
        print(f'[1/3] PE-TTM... {len(data)} 条', flush=True)
        return data
    except Exception as e:
        log(f'PE-TTM 失败: {e}')
        print(f'失败: {e}', flush=True)
        return []

def get_bond_yield():
    log('[2/3] 10Y国债收益率...')
    all_data = []
    current_year = datetime.now().year
    today_str = datetime.now().strftime('%Y%m%d')
    years = list(range(2010, current_year + 1))
    log(f'年份范围: 2010~{current_year}, 今天:{today_str}')
    
    for y in years:
        try:
            log(f'正在获取 {y} 年数据...')
            # 当前年份：结束日期用今天；历史年份：用12月31日
            end_date = today_str if y == current_year else f'{y}1231'
            df = ak.bond_china_yield(start_date=f'{y}0101', end_date=end_date)
            log(f'{y} 年: 获取到 {len(df)} 条原始数据')
            if df.empty:
                if y >= 2024:  # 近年无数据也提示
                    log(f'{y} 年数据为空')
                continue
            mask = df['曲线名称'].str.contains('国债', na=False)
            for _, row in df[mask].iterrows():
                try:
                    yld = float(row['10年'])
                    if yld > 0:
                        all_data.append({'date': str(row['日期'])[:10], 'yield': round(yld, 4)})
                except: continue
            time.sleep(0.2)
            if y % 5 == 0 or y >= 2023:
                log(f'{y} 年处理完成')
        except Exception as e:
            if y >= 2020:  # 只打印近年的错误
                log(f'年份{y} 错误: {str(e)[:50]}')
    
    # 去重排序
    seen = set()
    unique = [d for d in sorted(all_data, key=lambda x: x['date']) if not (d['date'] in seen or seen.add(d['date']))]
    log(f'去重后合计: {len(unique)} 条')
    print(f'  合计: {len(unique)} 条', flush=True)
    return unique

def get_kline(symbol, name):
    """用 AKShare 获取指数日K线，带重试"""
    print(f'  {name} ({symbol})...', end=' ', flush=True)
    today = datetime.now().strftime('%Y%m%d')
    for attempt in range(3):
        try:
            df = ak.index_zh_a_hist(symbol=symbol, period='daily', start_date='20050101', end_date=today)
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
    log('[3/3] 指数日K线 (AKShare)...')
    hs300 = get_kline('000300', '沪深300')
    if not hs300:
        log('沪深300获取失败，跳过')
    time.sleep(2)
    zzall = get_kline('000985', '中证全指')
    if not zzall:
        log('中证全指获取失败，跳过')
    time.sleep(2)
    gza = get_kline('399310', '国证A指')
    if not gza:
        log('国证A指获取失败，跳过')
    log(f'指数K线获取完成: hs300={len(hs300)}, zzall={len(zzall)}, gza={len(gza)}')
    return hs300, zzall, gza

def main():
    t0 = time.time()
    log('开始执行 main()')
    print('=' * 60)
    
    log('正在获取 PE-TTM...')
    pe = get_pe_ttm()
    log(f'PE-TTM 完成: {len(pe)} 条')
    
    log('正在获取国债收益率...')
    bond = get_bond_yield()
    log(f'国债收益率 完成: {len(bond)} 条')
    
    log('正在获取指数K线...')
    hs300, zzall, gza = get_index_klines()
    log(f'指数K线 完成: hs300={len(hs300)}, zzall={len(zzall)}, gza={len(gza)}')
    
    # 合并ERP
    log('正在合并ERP数据...')
    bond_map = {d['date']: d['yield'] for d in bond}
    for item in hs300:
        item['bond_yield'] = bond_map.get(item['date'])
        if item.get('pe_ttm') and item.get('bond_yield'):
            item['erp'] = round(100.0 / item['pe_ttm'] - item['bond_yield'], 4)
        else:
            item['erp'] = None
    
    valid_erp = sum(1 for x in hs300 if x.get('erp') is not None)
    log(f'ERP合并完成: valid_erp={valid_erp}')
    
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
    log(f'正在写入文件: {outpath}')
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    log(f'文件写入成功: {os.path.getsize(outpath)/1024:.0f}KB')
    
    elapsed = time.time() - t0
    print(f'\n{"=" * 60}')
    print(f'完成！{elapsed:.1f}s | {os.path.getsize(outpath)/1024:.0f}KB')
    print(f'沪深300:{len(hs300)} 中证全指:{len(zzall)} 国证A指:{len(gza)}')
    print(f'PE:{len(pe)} 国债:{len(bond)} ERP:{valid_erp}')
    log(f'脚本完成！用时{elapsed:.1f}秒')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        print('脚本异常退出:', flush=True)
        traceback.print_exc()
        raise
