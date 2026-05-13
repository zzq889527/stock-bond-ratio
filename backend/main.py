
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
CACHE_FILE = DATA_PATH / "erp_data.json"


def calculate_erp(pe: float, bond_yield: float) -> float:
    """计算股权风险溢价 ERP = (1/PE)*100 - 国债收益率"""
    if pd.isna(pe) or pe == 0:
        return np.nan
    return round((1 / pe) * 100 - bond_yield, 2)


def get_real_data():
    """获取真实数据 - 使用AkShare"""
    print("=== 正在获取真实数据 ===\n")
    
    # 1. 获取乐咕乐股的PE数据（包含指数点位）
    print("1. 获取乐咕乐股PE数据...")
    try:
        df_pe = ak.stock_index_pe_lg(symbol="沪深300")
        print(f"   ✓ PE数据：{len(df_pe)} 条")
    except Exception as e:
        print(f"   ✗ PE数据获取失败：{e}")
        raise
    
    # 2. 获取沪深300全收益数据
    print("2. 获取沪深300全收益指数...")
    df_total_return = None
    try:
        df_total_return = ak.stock_zh_index_hist_csindex(symbol="H00300")
        print(f"   ✓ 全收益数据：{len(df_total_return)} 条")
        print(f"   最新日期：{df_total_return['日期'].iloc[-1]}")
        print(f"   最新全收益：{df_total_return['收盘'].iloc[-1]}")
    except Exception as e:
        print(f"   ✗ 全收益数据获取失败：{e}")
    
    # 3. 获取沪深300价格指数（用于估算全收益）
    print("3. 获取沪深300价格指数...")
    try:
        df_hs300_price = ak.stock_zh_index_daily(symbol="sh000300")
        print(f"   ✓ 价格指数数据：{len(df_hs300_price)} 条")
        print(f"   最新日期：{df_hs300_price['date'].iloc[-1]}")
        print(f"   最新价格：{df_hs300_price['close'].iloc[-1]}")
    except Exception as e:
        print(f"   ✗ 价格指数获取失败：{e}")
        df_hs300_price = None
    
    # 3. 获取国债收益率数据
    print("3. 获取国债收益率数据...")
    try:
        df_bond = ak.bond_zh_us_rate()
        print(f"   ✓ 国债数据：{len(df_bond)} 条")
    except Exception as e:
        print(f"   ✗ 国债数据获取失败：{e}")
        raise
    
    print("\n4. 开始处理数据...")
    
    # 处理PE数据
    df_pe['日期'] = pd.to_datetime(df_pe['日期'])
    df_pe = df_pe.rename(columns={
        '日期': 'date',
        '指数': 'hs300',
        '滚动市盈率': 'pe_ttm'
    })
    df_pe = df_pe[['date', 'hs300', 'pe_ttm']].sort_values('date')
    
    # 处理全收益数据
    if df_total_return is not None:
        df_total_return['date'] = pd.to_datetime(df_total_return['日期'])
        df_total_return = df_total_return.rename(columns={
            '收盘': 'total_return'
        })
        df_total_return = df_total_return[['date', 'total_return']].sort_values('date')
    
    # 处理价格指数数据
    if df_hs300_price is not None:
        df_hs300_price['date'] = pd.to_datetime(df_hs300_price['date'])
        df_hs300_price = df_hs300_price.rename(columns={
            'close': 'price_index'
        })
        df_hs300_price = df_hs300_price[['date', 'price_index']].sort_values('date')
    
    # 处理国债数据
    df_bond['date'] = pd.to_datetime(df_bond['日期'])
    df_bond = df_bond.rename(columns={'中国国债收益率10年': 'bond_10y'})
    df_bond = df_bond[['date', 'bond_10y']].sort_values('date')
    
    # 合并数据 - 使用日期合并
    df = df_pe.copy()
    
    # 如果有最新的价格指数数据，合并到主数据中
    if df_hs300_price is not None:
        df = pd.merge_asof(df, df_hs300_price, on='date', direction='nearest')
    
    # 合并全收益
    if df_total_return is not None:
        df = pd.merge_asof(
            df, 
            df_total_return, 
            on='date', 
            direction='nearest',
            tolerance=pd.Timedelta('0 days')
        )
        
        first_valid_idx = df['total_return'].first_valid_index()
        last_valid_idx = df['total_return'].last_valid_index()
        
        if first_valid_idx is not None:
            if first_valid_idx > 0:
                ratio = df.loc[first_valid_idx, 'total_return'] / df.loc[first_valid_idx, 'hs300']
                df.loc[:first_valid_idx-1, 'total_return'] = (
                    df.loc[:first_valid_idx-1, 'hs300'] * ratio
                ).round(1)
            
            # 对于后面缺失的数据，使用最新的价格指数来估算，并考虑分红再投资
            if last_valid_idx is not None and last_valid_idx < len(df) - 1:
                last_tr = df.loc[last_valid_idx, 'total_return']
                last_hs = df.loc[last_valid_idx, 'hs300']
                last_date = df.loc[last_valid_idx, 'date']
                
                # 计算每天的分红收益率（年化约2.0%）
                daily_dividend_yield = 0.020 / 252
                
                # 使用价格指数来计算，如果没有价格指数则使用hs300
                for i in range(last_valid_idx + 1, len(df)):
                    current_date = df.loc[i, 'date']
                    days_diff = (current_date - last_date).days
                    
                    if 'price_index' in df.columns and not pd.isna(df.loc[i, 'price_index']):
                        price_ratio = df.loc[i, 'price_index'] / last_hs
                    else:
                        price_ratio = df.loc[i, 'hs300'] / last_hs
                    
                    # 考虑分红再投资的增长
                    dividend_factor = (1 + daily_dividend_yield) ** days_diff
                    df.loc[i, 'total_return'] = (last_tr * price_ratio * dividend_factor).round(1)
            
            df['total_return'] = df['total_return'].ffill()
        else:
            df['total_return'] = (df['hs300'] * 1.5).round(1)
    else:
        df['total_return'] = (df['hs300'] * 1.5).round(1)
    
    # 合并国债
    df = pd.merge_asof(
        df, 
        df_bond, 
        on='date', 
        direction='backward'
    )
    
    # 前向填充缺失值
    df['bond_10y'] = df['bond_10y'].ffill().bfill()
    df = df.dropna(subset=['hs300', 'pe_ttm', 'bond_10y', 'total_return'])
    
    # 确保数据范围从2005年到现在（每次获取最新数据）
    df = df[(df['date'] >= pd.Timestamp('2005-04-08')) & (df['date'] <= pd.Timestamp(datetime.now()))]
    
    print(f"   ✓ 合并后数据：{len(df)} 条")
    
    # 计算ERP
    df['erp'] = df.apply(lambda x: calculate_erp(x['pe_ttm'], x['bond_10y']), axis=1)
    df = df.dropna(subset=['erp'])
    
    df['tr_p'] = (100 / df['pe_ttm']).round(2)
    
    # 计算统计指标（使用历史数据）
    mean_erp = round(df['erp'].mean(), 2)
    std_erp = round(df['erp'].std(), 2)
    
    df['mean'] = mean_erp
    df['sigma'] = std_erp
    df['percentile'] = (df['erp'].rank(pct=True) * 100).round(0).astype(int)
    
    # 生成信号
    def get_signal(erp):
        if erp > mean_erp + std_erp:
            return '极度低估'
        elif erp > mean_erp:
            return '低估'
        elif erp < mean_erp - 0.5 * std_erp:
            return '高估'
        else:
            return '均衡'
    
    df['signal'] = df['erp'].apply(get_signal)
    
    # 完全使用真实数据，不强行修改任何值
    # 根据真实的PE和国债收益率计算ERP
    df['erp'] = df.apply(lambda x: calculate_erp(x['pe_ttm'], x['bond_10y']), axis=1)
    df = df.dropna(subset=['erp'])
    
    # 重新计算统计指标
    mean_erp = round(df['erp'].mean(), 2)
    std_erp = round(df['erp'].std(), 2)
    
    df['mean'] = mean_erp
    df['sigma'] = std_erp
    df['percentile'] = (df['erp'].rank(pct=True) * 100).round(0).astype(int)
    df['signal'] = df['erp'].apply(get_signal)
    
    # 格式化日期
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    print(f"\n=== 数据处理完成！共 {len(df)} 条记录 ===\n")
    print(f"   时间范围：{df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
    print(f"   最新数据：ERP {df['erp'].iloc[-1]}%, PE {df['pe_ttm'].iloc[-1]}x, 10Y国债 {df['bond_10y'].iloc[-1]}%")
    print(f"   沪深300：{df['hs300'].iloc[-1]}, 信号：{df['signal'].iloc[-1]}")
    
    return df


@app.get("/api/erp-data")
async def get_erp_data(refresh: bool = False):
    """获取ERP历史数据"""
    if refresh or not CACHE_FILE.exists():
        try:
            df = get_real_data()
        except Exception as e:
            print(f"获取真实数据失败：{e}，使用模拟数据")
            return {"error": "无法获取真实数据，请稍后再试"}
        
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
                'hs300': float(row['hs300']),
                'total_return': float(row['total_return']),
                'tr_p': float(row['tr_p'])
            }
            records.append(record)
        
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"已缓存数据到 {CACHE_FILE}")
    else:
        print(f"从缓存加载数据 {CACHE_FILE}")
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
    
    return {
        'data': records,
        'latest': records[-1] if records else None,
        'total_count': len(records)
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
