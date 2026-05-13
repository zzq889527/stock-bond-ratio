#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

import main as backend

def main():
    print("=== 开始更新股债收益比数据 ===")
    
    try:
        # Get real data
        df = backend.get_real_data()
        
        # Convert to records
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
        
        # Save to public folder
        output_path = Path(__file__).parent.parent / 'public' / 'erp_data.json'
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 数据已更新！共 {len(records)} 条记录")
        print(f"✓ 最新日期: {records[-1]['date']}")
        print(f"✓ 最新ERP: {records[-1]['erp']}%")
        print(f"✓ 保存到: {output_path}")
        return 0
        
    except Exception as e:
        print(f"✗ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
