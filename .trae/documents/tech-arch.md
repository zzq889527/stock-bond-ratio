## 1. Architecture Design
```mermaid
graph TD
    A[用户浏览器] --> B[React前端]
    B --> C[ECharts图表]
    B --> D[Mock数据服务]
    D --> E[数据文件]
```

## 2. Technology Description
- Frontend: React@18 + tailwindcss@3 + vite
- Initialization Tool: vite-init
- Backend: None (使用Mock数据)
- Chart Library: ECharts@5
- Database: 静态JSON数据文件

## 3. Route Definitions
| Route | Purpose |
|-------|---------|
| / | 首页，展示股债收益比数据和图表 |

## 4. API Definitions
- 后端：使用Mock数据，无需API
- 数据格式：JSON数组，包含日期、ERP、PE、国债收益率、沪深300、全收益等字段

## 5. Server Architecture Diagram
```mermaid
graph LR
    A[静态文件服务器] --> B[HTML/CSS/JS]
    B --> C[Mock数据]
```

## 6. Data Model
### 6.1 Data Model Definition
```mermaid
classDiagram
    class ERPData {
        +string date
        +number erp
        +number mean
        +number sigma
        +number percentile
        +string signal
        +number pe_ttm
        +number bond_10y
        +number hs300
        +number total_return
        +number tr_p
    }
```

### 6.2 Data Definition Language
```json
{
  "data": [
    {
      "date": "2005-04-08",
      "erp": 4.5,
      "mean": 4.46,
      "sigma": 2.34,
      "percentile": 50,
      "signal": "均衡",
      "pe_ttm": 15.2,
      "bond_10y": 3.2,
      "hs300": 980,
      "total_return": 120,
      "tr_p": 0.08
    }
  ]
}
```
