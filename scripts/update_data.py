#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

import main as backend

def main():
    print("=== 开始更新股债收益比数据 ===")
    
    try:
        all_data = backend.generate_all_index_data(refresh=True)
        
        public_path = Path(__file__).parent.parent / 'public'
        public_path.mkdir(exist_ok=True)
        
        for index_id, records in all_data.items():
            if index_id == 'hs300':
                output_path = public_path / 'erp_data.json'
            else:
                output_path = public_path / f'{index_id}_erp_data.json'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            print(f"✓ {index_id}: {len(records)} 条记录, 最新: {records[-1]['date']}")
        
        print("\n✓ 所有数据更新完成！")
        return 0
        
    except Exception as e:
        print(f"✗ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())