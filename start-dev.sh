#!/bin/bash

echo "========================================"
echo "股债收益比数据可视化平台"
echo "========================================"
echo ""

echo "[1/2] 启动后端服务..."
cd backend

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "后端API: http://localhost:8000"
echo ""

python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

echo "[2/2] 启动前端服务..."
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "服务已启动"
echo "前端: http://localhost:5173"
echo "后端: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "========================================"

trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
