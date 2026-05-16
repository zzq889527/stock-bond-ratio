import sys
import io
import time
import os

if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.platform == 'win32' and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
import pandas_datareader.data as web

DATA_PATH = Path(__file__).parent / "data"
DATA_PATH.mkdir(exist_ok=True)

INDEX_CONFIGS = [
    {
        "id": "hs300",
        "name": "沪深300",
        "pe_symbol": "沪深300",
        "price_symbol": "sh000300",
        "total_return_symbol": "H00300",
        "index_code": "000300"
    },
    {
        "id": "zz500",
        "name": "中证500",
        "pe_symbol": "中证500",
        "price_symbol": "sh000905",
        "total_return_symbol": "H00905",
        "index_code": "000905"
    },
    {
        "id": "zzall",
        "name": "中证全指",
        "pe_symbol": "中证800",
        "price_symbol": "sh000985",
        "total_return_symbol": "H00985",
        "index_code": "000985"
    }
]

def calculate_erp(pe, bond_yield):
    if pd.isna(pe) or pe == 0:
        return np.nan
    return (1.0 / pe) * 100 - bond_yield

PAYOUT_RATIOS = {}

def get_payout_ratio(index_code, index_name):
    try:
        df = ak.stock_zh_index_value_csindex(symbol=index_code)
        df['日期'] = pd.to_datetime(df['日期'])
        latest = df.iloc[-1]
        pe1 = float(latest['市盈率1'])
        dy1 = float(latest['股息率1'])
        if pe1 > 0:
            payout_ratio = dy1 * pe1 / 100
            print(f"  {index_name}({index_code}) 最新PE={pe1:.2f}, 股息率={dy1:.2f}%, payout_ratio={payout_ratio:.4f}")
            return payout_ratio
    except Exception as e:
        print(f"获取{index_name}({index_code})估值数据失败: {e}")
    return 0.38

def compute_dividend_yield(pe_series, index_code, index_name):
    if index_code not in PAYOUT_RATIOS:
        PAYOUT_RATIOS[index_code] = get_payout_ratio(index_code, index_name)
    ratio = PAYOUT_RATIOS[index_code]
    return (ratio / pe_series * 100).round(3)

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
    
    df_pb = None
    try:
        df_pb = ak.stock_index_pb_lg(symbol=index_config["pe_symbol"])
        df_pb['日期'] = pd.to_datetime(df_pb['日期'])
        df_pb = df_pb.rename(columns={'日期': 'date', '市净率': 'pb'})
        df_pb = df_pb[['date', 'pb']].sort_values('date')
        print(f"   ✓ PB数据：{len(df_pb)} 条")
    except Exception as e:
        print(f"   ✗ PB数据获取失败：{e}")
    
    df_dividend = compute_dividend_yield(df_pe['滚动市盈率'], index_config["index_code"], index_name)
    
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
    
    if df_pb is not None:
        df = pd.merge_asof(df, df_pb, on='date', direction='nearest')
    else:
        df['pb'] = 0
    
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
    
    if df_dividend is not None:
        df['dividend_yield'] = df_dividend.values
        df['dividend_yield'] = df['dividend_yield'].ffill().bfill()
    else:
        df['dividend_yield'] = 2.0
    
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

def get_sp500_data():
    print("  获取标普500数据...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def parse_multpl(url, name):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.content, 'html.parser')
            table = soup.find('table')
            if not table:
                print(f"    找不到{name}表格")
                return None
            rows = table.find_all('tr')
            data = []
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    date_str = cols[0].get_text(strip=True)
                    val_str = cols[1].get_text(strip=True)
                    val_str = re.sub(r'[†‡%]', '', val_str)
                    try:
                        val = float(val_str)
                        data.append((date_str, val))
                    except:
                        pass
            df = pd.DataFrame(data, columns=['date_str', name])
            df['date'] = pd.to_datetime(df['date_str'], format='mixed')
            df = df.sort_values('date').reset_index(drop=True)
            print("    " + name + ": " + str(len(df)) + "行, " + str(df['date'].min().date()) + " ~ " + str(df['date'].max().date()))
            return df
        except Exception as e:
            print(f"    获取{name}失败: {e}")
            return None
    
    pe_df = parse_multpl('https://www.multpl.com/s-p-500-pe-ratio/table/by-month', 'pe_ttm')
    div_df = parse_multpl('https://www.multpl.com/s-p-500-dividend-yield/table/by-month', 'dividend_yield')
    pb_df = parse_multpl('https://www.multpl.com/s-p-500-price-to-book/table/by-month', 'pb')
    adj_price_df = parse_multpl('https://www.multpl.com/inflation-adjusted-s-p-500/table/by-month', 'adj_price')
    nominal_price_df = parse_multpl('https://www.multpl.com/s-p-500-historical-prices/table/by-month', 'nominal_price')
    
    if pe_df is None:
        print("  ✗ PE数据是必需的，无法继续")
        return None
    
    start = datetime(1871, 1, 1)
    end = datetime.now()
    
    print("  获取CPI数据...")
    try:
        cpi = web.DataReader('CPIAUCNS', 'fred', start, end)
        cpi = cpi.reset_index()
        cpi.columns = ['date', 'cpi']
        cpi['date'] = pd.to_datetime(cpi['date'])
        cpi = cpi.sort_values('date').reset_index(drop=True)
        latest_cpi = cpi['cpi'].iloc[-1]
        print("    CPI: " + str(len(cpi)) + "行, 最新=" + str(latest_cpi))
    except Exception as e:
        print(f"    获取CPI失败: {e}")
        return None
    
    print("  获取FRED SP500...")
    try:
        sp_fred = web.DataReader('SP500', 'fred', start, end)
        sp_fred = sp_fred.reset_index()
        sp_fred.columns = ['date', 'fred_price']
        sp_fred['date'] = pd.to_datetime(sp_fred['date'])
        sp_fred = sp_fred.sort_values('date').reset_index(drop=True)
        sp_fred = sp_fred.dropna()
        print("    FRED SP500: " + str(len(sp_fred)) + "行, " + str(sp_fred['date'].min().date()) + " ~ " + str(sp_fred['date'].max().date()))
    except Exception as e:
        print(f"    获取FRED SP500失败: {e}")
        sp_fred = None
    
    print("  获取美债10Y收益率...")
    try:
        dgs10 = web.DataReader('DGS10', 'fred', start, end)
        dgs10 = dgs10.reset_index()
        dgs10.columns = ['date', 'bond_10y']
        dgs10['date'] = pd.to_datetime(dgs10['date'])
        dgs10 = dgs10.sort_values('date').reset_index(drop=True)
        dgs10 = dgs10.dropna()
        print("    DGS10: " + str(len(dgs10)) + "行, " + str(dgs10['date'].min().date()) + " ~ " + str(dgs10['date'].max().date()))
    except Exception as e:
        print(f"    获取DGS10失败: {e}")
        return None
    
    print("  构建价格数据...")
    
    yahoo_price = None
    try:
        yahoo_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        period1 = 536457600
        period2 = int(time.time())
        yahoo_url = f'https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?period1={period1}&period2={period2}&interval=1mo'
        yahoo_resp = requests.get(yahoo_url, headers=yahoo_headers, timeout=15)
        if yahoo_resp.status_code == 200:
            yahoo_data = yahoo_resp.json()
            yahoo_result = yahoo_data['chart']['result'][0]
            timestamps = yahoo_result['timestamp']
            quotes = yahoo_result['indicators']['quote'][0]
            closes = quotes['close']
            yahoo_rows = []
            for ts, close in zip(timestamps, closes):
                if close is not None:
                    dt = datetime.fromtimestamp(ts)
                    yahoo_rows.append({'date': dt, 'price': close})
            yahoo_price = pd.DataFrame(yahoo_rows)
            yahoo_price['date'] = pd.to_datetime(yahoo_price['date']).dt.floor('D')
            yahoo_price = yahoo_price.sort_values('date').reset_index(drop=True)
            print("    Yahoo SP500: " + str(len(yahoo_price)) + "行, " + str(yahoo_price['date'].min().date()) + " ~ " + str(yahoo_price['date'].max().date()))
    except Exception as e:
        print(f"    获取Yahoo SP500失败: {e}")
    
    adj_nominal = adj_price_df.copy()
    if adj_nominal is not None:
        adj_nominal = pd.merge_asof(adj_nominal, cpi[['date', 'cpi']], on='date')
        adj_nominal['price'] = adj_nominal['adj_price'] * (adj_nominal['cpi'] / latest_cpi)
        adj_nominal = adj_nominal[['date', 'price']].dropna()
    
    multpl_nominal = nominal_price_df[['date', 'nominal_price']].copy() if nominal_price_df is not None else None
    if multpl_nominal is not None:
        multpl_nominal = multpl_nominal.rename(columns={'nominal_price': 'price'})
    
    fred_price = sp_fred[['date', 'fred_price']].copy() if sp_fred is not None else None
    if fred_price is not None:
        fred_price = fred_price.rename(columns={'fred_price': 'price'})
    
    price_sources = []
    if yahoo_price is not None:
        price_sources.append(yahoo_price)
    if multpl_nominal is not None:
        price_sources.append(multpl_nominal)
    if adj_nominal is not None:
        price_sources.append(adj_nominal)
    if fred_price is not None:
        price_sources.append(fred_price)
    
    if price_sources:
        price_merged = pd.concat(price_sources).sort_values('date').reset_index(drop=True)
        price_merged = price_merged.drop_duplicates(subset='date', keep='first')
        price_merged = price_merged.dropna(subset=['price'])
    else:
        price_merged = None
    
    df = pe_df[['date', 'pe_ttm']].copy()
    if price_merged is not None:
        df = pd.merge(df, price_merged, on='date', how='left')
        df['eps'] = df['price'] / df['pe_ttm']
        df['eps'] = df['eps'].interpolate(method='linear')
        df['price'] = df['price'].fillna(df['eps'] * df['pe_ttm'])
        df = df.dropna(subset=['price'])
    else:
        df['price'] = df['pe_ttm'] * 100
    
    df = df.rename(columns={'price': 'index_value'})
    
    if div_df is not None:
        df = pd.merge_asof(df, div_df[['date', 'dividend_yield']], on='date')
    else:
        df['dividend_yield'] = 0.0
    
    if pb_df is not None:
        pb_interp = pb_df[['date', 'pb']].copy()
        pb_interp['date'] = pb_interp['date'].dt.to_period('M').dt.to_timestamp()
        pb_interp = pb_interp.drop_duplicates(subset='date')
        pb_min = min(pb_interp['date'].min(), df['date'].min())
        pb_max = max(pb_interp['date'].max(), df['date'].max())
        date_range = pd.date_range(start=pb_min, end=pb_max, freq='MS')
        pb_smooth = pd.DataFrame({'date': date_range})
        pb_smooth = pd.merge(pb_smooth, pb_interp, on='date', how='left')
        pb_smooth['pb'] = pb_smooth['pb'].interpolate(method='linear')
        pb_smooth['pb'] = pb_smooth['pb'].bfill().ffill()
        df = pd.merge(df, pb_smooth, on='date', how='left')
        df['pb'] = df['pb'].ffill()
    else:
        df['pb'] = 0.0
    
    df = pd.merge_asof(df, dgs10[['date', 'bond_10y']], on='date')
    df['bond_10y'] = df['bond_10y'].ffill().bfill()
    
    df = df.dropna(subset=['index_value', 'pe_ttm', 'bond_10y'])
    df = df[df['date'] >= pd.Timestamp('1962-01-01')]
    df = df[df['date'] <= pd.Timestamp(datetime.now())]
    
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
    
    print("  ✓ 标普500完成: " + str(len(df)) + "条, " + str(df['date'].iloc[0]) + " ~ " + str(df['date'].iloc[-1]))
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
                    'pb': float(row['pb']) if 'pb' in df.columns and pd.notna(row['pb']) else 0.0,
                    'dividend_yield': float(row['dividend_yield']) if 'dividend_yield' in df.columns and pd.notna(row['dividend_yield']) else 0.0,
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
    
    print("\n=== 标普500数据生成 ===")
    sp500_cache = DATA_PATH / "sp500_erp_data.json"
    if not refresh and sp500_cache.exists():
        print("\n加载缓存：标普500")
        with open(sp500_cache, 'r', encoding='utf-8') as f:
            all_data['sp500'] = json.load(f)
    else:
        try:
            df_sp500 = get_sp500_data()
            if df_sp500 is not None:
                records = []
                for _, row in df_sp500.iterrows():
                    record = {
                        'date': str(row['date']),
                        'erp': float(row['erp']),
                        'mean': float(row['mean']),
                        'sigma': float(row['sigma']),
                        'percentile': int(row['percentile']),
                        'signal': str(row['signal']),
                        'pe_ttm': float(row['pe_ttm']),
                        'pb': float(row['pb']) if 'pb' in df_sp500.columns and pd.notna(row['pb']) else 0.0,
                        'dividend_yield': float(row['dividend_yield']) if 'dividend_yield' in df_sp500.columns and pd.notna(row['dividend_yield']) else 0.0,
                        'bond_10y': float(row['bond_10y']),
                        'index_value': float(row['index_value']),
                        'total_return': float(row['index_value']),
                        'tr_p': float(row['tr_p'])
                    }
                    records.append(record)
                
                all_data['sp500'] = records
                
                with open(sp500_cache, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                print(f"   ✓ 保存缓存：标普500")
        except Exception as e:
            print(f"   ✗ 标普500 失败：{e}")
            import traceback
            traceback.print_exc()
    
    return all_data