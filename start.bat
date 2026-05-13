@echo off
echo ========================================
echo 股债收益比数据可视化平台
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo Python环境: OK
echo.

echo [2/3] 安装Python依赖...
if not exist "backend\venv" (
    echo 创建虚拟环境...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
) else (
    echo 虚拟环境已存在
    cd backend
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
)
echo.

echo [3/3] 启动服务...
echo.
echo ========================================
echo 服务即将启动
echo.
echo 后端API: http://localhost:8000
echo 前端预览: 请在新终端运行 npm run dev
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

cd backend
call venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
