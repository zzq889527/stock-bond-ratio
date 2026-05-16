import sys
import io
import time

if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.platform == 'win32' and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path

from .data_engine import (
    INDEX_CONFIGS,
    DATA_PATH,
    generate_all_index_data
)

app = FastAPI(title="股债收益比数据API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/all-data")
async def get_all_data_endpoint(refresh=False):
    try:
        all_data = generate_all_index_data(refresh=refresh)
        return {
            'data': all_data,
            'total_indices': len(all_data),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error: {e}")
        return {'error': str(e)}

@app.get("/api/health")
async def health_check():
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}

if __name__ == "__main__":
    print("开始生成所有指数数据...")
    all_data = generate_all_index_data(refresh=True)
    
    import shutil
    dist_path = Path(__file__).parent.parent / "dist"
    for config in INDEX_CONFIGS:
        src_file = DATA_PATH / f"{config['id']}_erp_data.json"
        dst_file = dist_path / f"{config['id']}_erp_data.json"
        if src_file.exists():
            shutil.copy(src_file, dst_file)
            print(f"复制 {config['name']} 数据到 dist")
    
    sp500_src = DATA_PATH / "sp500_erp_data.json"
    sp500_dst = dist_path / "sp500_erp_data.json"
    if sp500_src.exists():
        shutil.copy(sp500_src, sp500_dst)
        print("复制 标普500 数据到 dist")
    
    print("\n数据生成完成！")