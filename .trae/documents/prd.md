## 1. Product Overview
股债收益比（ERP）数据可视化平台，展示沪深300指数、全收益、ERP等金融指标的日频数据，帮助投资者分析市场估值水平。
- 核心功能：实时展示ERP指标、PE(TTM)、10Y国债收益率等关键数据
- 目标用户：金融投资者、分析师、市场研究人员

## 2. Core Features

### 2.1 User Roles
| Role | Registration Method | Core Permissions |
|------|---------------------|------------------|
| Visitor | No registration required | View all public data and charts |

### 2.2 Feature Module
1. **首页**: ERP指标卡片、时间序列图表、数据说明
2. **数据更新**: 自动获取最新交易日数据

### 2.3 Page Details
| Page Name | Module Name | Feature description |
|-----------|-------------|---------------------|
| 首页 | 指标卡片 | 展示ERP、均值、σ、分位、信号、PE(TTM)、10Y国债、沪深300、全收益、TR/P |
| 首页 | 图表区域 | 显示沪深300、全收益、ERP、均值线、±1σ的时间序列图表 |
| 首页 | 说明区域 | ERP公式说明、信号说明、数据来源说明 |

## 3. Core Process
用户打开网站 → 自动加载最新交易日数据 → 展示指标卡片 → 渲染时间序列图表 → 用户可查看数据说明

## 4. User Interface Design
### 4.1 Design Style
- 主色调：深色主题（#0a0e17）
- 强调色：青色（#00d4ff）、红色（#ff4757）、绿色（#2ed573）、橙色（#ffa502）、蓝色（#3742fa）
- 按钮风格：圆角矩形，hover效果
- 字体：等宽字体（Roboto Mono）
- 布局：顶部指标卡片，中间图表区域，底部说明区域

### 4.2 Page Design Overview
| Page Name | Module Name | UI Elements |
|-----------|-------------|-------------|
| 首页 | 头部 | 标题"股债收益比·日频"、刷新按钮、等待状态 |
| 首页 | 指标卡片 | 横向排列的指标卡片，显示数值和标签 |
| 首页 | 图表区域 | ECharts时间序列图表，支持缩放、拖拽 |
| 首页 | 底部说明 | ERP公式、信号规则、数据来源 |

### 4.3 Responsiveness
- 桌面优先设计
- 响应式布局，适配不同屏幕尺寸
- 移动端图表支持触摸操作

### 4.4 3D Scene Guidance
- 无3D场景需求
