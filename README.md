# 股债收益比 · 日频数据可视化平台

基于真实金融数据的ERP（股权风险溢价）分析工具。

> 支持多指数切换：沪深300、中证500、中证全指

## 功能特性

- 📊 真实数据: 通过AkShare获取A股市场真实数据
- 📈 实时更新: 自动获取最新交易日数据
- 📉 可视化展示: ECharts双Y轴图表
- 🎯 信号提示: 基于均值和标准差的投资信号
- 💾 数据缓存: 本地JSON缓存提升加载速度

## 数据来源

- 沪深300估值数据: 乐咕乐股（AkShare）
- 10年期国债收益率: 中债登（AkShare）
- 沪深300指数: 东方财富（AkShare）

## 快速开始

### 方式一: 使用启动脚本（推荐）

Windows用户直接双击 `start.bat`

### 方式二: 手动启动

#### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 启动前端服务

在新终端窗口：

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看页面

## API接口

### 获取ERP数据

```
GET /api/erp-data?refresh=true
```

响应示例：
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "erp": 3.62,
      "mean": 4.46,
      "sigma": 2.34,
      "percentile": 7,
      "signal": "均衡",
      "pe_ttm": 27.6,
      "bond_10y": 3.46,
      "hs300": 2415,
      "total_return": 193,
      "tr_p": 0.08
    }
  ],
  "latest": {...},
  "total_count": 5000
}
```

## 项目结构

```
.
├── backend/
│   ├── main.py              # FastAPI后端服务
│   ├── requirements.txt      # Python依赖
│   └── data/                # 数据缓存目录
├── src/
│   ├── components/
│   │   ├── MetricCard.tsx   # 指标卡片
│   │   └── ERPChart.tsx     # ECharts图表
│   ├── data/
│   │   └── erpData.ts       # 数据接口和处理
│   └── pages/
│       └── Home.tsx         # 主页
└── start.bat               # 一键启动脚本
```

## 技术栈

- **前端**: React 18 + TypeScript + Tailwind CSS + ECharts
- **后端**: FastAPI + AkShare + Pandas
- **数据**: 本地JSON缓存

## 指标说明

| 指标 | 说明 |
|------|------|
| ERP | 股权风险溢价 = 1/PE - 10年期国债收益率 |
| 均值 | 历史ERP均值 |
| σ | 历史ERP标准差 |
| 分位 | 当前ERP的历史分位数 |
| PE(TTM) | 沪深300市盈率 |
| 10Y国债 | 10年期国债收益率 |
| 沪深300 | 沪深300指数点位 |
| 全收益 | 假设的全收益指数 |

## 信号规则

- 🟢 **极度低估**: ERP > 均值 + 1σ
- 🟦 **低估**: ERP > 均值
- 🟡 **均衡**: ERP ≈ 均值
- 🔴 **高估**: ERP < 均值 - 1σ

## 注意事项

1. 首次启动时需要获取历史数据，可能需要几分钟
2. 数据会自动缓存到 `backend/data/erp_data.json`
3. 点击"刷新数据"按钮可以强制重新获取
4. 如遇API限流，会自动切换到模拟数据

## License

MIT
