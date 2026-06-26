# 股债收益比 · 日频数据可视化平台

基于真实金融数据的 ERP（股权风险溢价）分析工具，支持多指数切换与实时数据更新。

> 🌐 在线访问：https://zzq889527.github.io/stock-bond-ratio/

## 支持指数

| 指数 | 数据范围 | 记录数 |
|------|---------|-------|
| 标普500 | 1962-01-01 ~ 最新 | 775条 |
| 沪深300 | 2005-04-08 ~ 最新 | 5153条 |
| 中证500 | 2007-01-15 ~ 最新 | 4724条 |
| 中证全指 | 2007-01-15 ~ 最新 | 4724条 |
<!-- DATA_STATS -->
> 📊 数据最后更新：2026-06-26
<!-- /DATA_STATS -->

## 功能特性

- 📊 **多指数覆盖**: 标普500、沪深300、中证500、中证全指
- 📈 **自动更新**: GitHub Actions 每日3次自动拉取最新数据
- 📉 **四维图表**: ERP、PE、PB、股息率 四大指标可视化
- 🎯 **信号提示**: 基于均值和标准差的投资信号（极度低估/低估/均衡/高估/极度高估）
- 📱 **响应式设计**: 支持手机横屏模式，2×2 图表网格布局
- 🔄 **实时数据**: 客户端通过东方财富 + Yahoo Finance API 获取最新交易日数据

## 数据来源

### A股指数
- PE/PB 数据：乐咕乐股（通过 AkShare）
- 指数价格：东方财富（通过 AkShare）
- 全收益指数：中证指数公司（通过 AkShare）
- 10年期国债收益率：中国债券信息网（通过 AkShare）

### 标普500
- PE/PB/股息率/价格：multpl.com（1871年至今）
- 10年期国债收益率：FRED（DGS10，1962年至今）
- CPI：FRED（CPIAUCNS）
- 实时价格：Yahoo Finance

## 快速开始

### 方式一：使用启动脚本（推荐）

Windows 用户直接双击 `start.bat`

### 方式二：手动启动

#### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 生成数据

```bash
python scripts/update_data.py
```

#### 3. 安装前端依赖并启动

```bash
npm install
npm run dev
```

访问 http://localhost:5173 查看页面

## 项目结构

```
.
├── backend/
│   ├── data_engine.py        # 数据引擎（AkShare + multpl + FRED）
│   └── data/                 # 数据缓存目录
├── scripts/
│   ├── update_data.py        # 数据更新脚本
│   └── sync-data.js          # 构建前数据同步
├── src/
│   ├── components/
│   │   ├── ERPChart.tsx      # ERP 图表
│   │   ├── PEChart.tsx       # PE 图表
│   │   ├── PBChart.tsx       # PB 图表
│   │   ├── DividendYieldChart.tsx  # 股息率图表
│   │   ├── IndexSelector.tsx # 指数选择器
│   │   └── MetricCard.tsx    # 指标卡片
│   ├── data/
│   │   ├── erpData.ts        # 数据加载
│   │   └── indexConfig.ts    # 指数配置
│   ├── utils/
│   │   └── liveData.ts       # 实时数据拉取
│   └── pages/
│       └── Home.tsx          # 主页
├── public/                   # 静态数据文件
├── .github/workflows/
│   ├── update-data.yml       # 数据自动更新工作流
│   └── deploy.yml            # GitHub Pages 部署工作流
└── start.bat                 # 一键启动脚本
```

## 技术栈

- **前端**: React 18 + TypeScript + Tailwind CSS + ECharts
- **数据引擎**: Python + AkShare + yfinance + pandas-datareader
- **部署**: GitHub Actions + GitHub Pages
- **数据格式**: JSON 静态文件 + 客户端实时 API

## 指标说明

| 指标 | 说明 |
|------|------|
| ERP | 股权风险溢价 = 1/PE - 10年期国债收益率 |
| 均值 | 历史 ERP 均值 |
| σ | 历史 ERP 标准差 |
| 分位 | 当前 ERP 的历史百分位 |
| PE(TTM) | 滚动市盈率 |
| PB | 市净率 |
| 股息率 | 指数股息率 |
| 10Y国债 | 10年期国债收益率 |

## 信号规则

- 🟢 **极度低估**: ERP > 均值 + 1σ
- 🟦 **低估**: ERP > 均值 + 0.5σ
- 🟡 **均衡**: ERP ≈ 均值
- 🟠 **高估**: ERP < 均值 - 0.5σ
- 🔴 **极度高估**: ERP < 均值 - 1σ

## 自动更新

数据通过 GitHub Actions 自动更新：
- 调度频率：每天 3 次（09:00 / 15:00 / 21:00 北京时间）
- 触发方式：手动可通过仓库 Actions 页面的 "Update Data" 工作流触发
- 部署流程：数据更新 → README 同步 → 自动部署到 GitHub Pages

## License

MIT