#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path

def main():
    print("=== 开始更新股债收益比数据 ===")
    sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))
    
    try:
        from data_engine import generate_all_index_data
    except Exception as e:
        print(f"! 导入数据引擎失败: {e}")
        print("OK 使用现有数据，退出")
        return 0
    
    try:
        all_data = generate_all_index_data(refresh=True)
    except Exception as e:
        print(f"! 数据生成失败: {e}")
        print("OK 使用现有数据，退出")
        return 0
    
    try:
        public_path = Path(__file__).parent.parent / 'public'
        public_path.mkdir(exist_ok=True)
        
        written = 0
        for index_id, records in all_data.items():
            if not records:
                continue
            
            if index_id == 'hs300':
                output_path = public_path / 'erp_data.json'
            else:
                output_path = public_path / f'{index_id}_erp_data.json'
            
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                written += 1
            except Exception:
                continue
        
        print(f"OK 完成！写入 {written} 个文件")
        return 0
        
    except Exception as e:
        print(f"! 写入失败: {e}")
        return 0

if __name__ == '__main__':
    sys.exit(main())