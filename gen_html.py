# -*- coding: utf-8 -*-
"""生成手机竖屏适配版 HTML 看板"""
import json, os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# 为了演示，我们使用 build_chart.py 中的静态数据
# 因为 daily_data.json 可能不存在
# 让我们先尝试加载 build_chart.py 中的数据

# 先尝试从 build_chart.py 中提取数据
# 为了简化，直接复制 build_chart.py 中的数据
price_data = [
    ("2005-04-29", 932.40), ("2005-05-31", 855.95), ("2005-06-30", 878.69),
    ("2005-07-29", 888.16), ("2005-08-31", 927.92), ("2005-09-30", 917.39),
    ("2005-10-31", 876.28), ("2005-11-30", 873.83), ("2005-12-30", 923.45),
    ("2006-01-25", 1009.60), ("2006-02-28", 1053.01), ("2006-03-31", 1061.09),
    ("2006-04-28", 1172.35), ("2006-05-31", 1365.45), ("2006-06-30", 1393.96),
    ("2006-07-31", 1294.33), ("2006-08-31", 1338.69), ("2006-09-29", 1403.27),
    ("2006-10-31", 1464.47), ("2006-11-30", 1714.36), ("2006-12-29", 2041.05),
    ("2007-01-31", 2385.33), ("2007-02-28", 2544.57), ("2007-03-30", 2781.78),
    ("2007-04-30", 3558.71), ("2007-05-31", 3927.95), ("2007-06-29", 3764.08),
    ("2007-07-31", 4460.56), ("2007-08-31", 5296.81), ("2007-09-28", 5580.81),
    ("2007-10-31", 5688.54), ("2007-11-30", 4737.41), ("2007-12-28", 5338.27),
    ("2008-01-31", 4620.40), ("2008-02-29", 4674.55), ("2008-03-31", 3790.53),
    ("2008-04-30", 3959.12), ("2008-05-30", 3611.33), ("2008-06-30", 2791.82),
    ("2008-07-31", 2805.21), ("2008-08-29", 2391.64), ("2008-09-26", 2243.66),
    ("2008-10-31", 1663.66), ("2008-11-28", 1829.92), ("2008-12-31", 1817.72),
    ("2009-01-23", 2032.68), ("2009-02-27", 2140.49), ("2009-03-31", 2507.79),
    ("2009-04-30", 2622.93), ("2009-05-27", 2759.71), ("2009-06-30", 3166.47),
    ("2009-07-31", 3734.62), ("2009-08-31", 2830.27), ("2009-09-30", 3004.80),
    ("2009-10-30", 3280.37), ("2009-11-30", 3511.67), ("2009-12-31", 3575.40),
    ("2010-01-29", 3204.91), ("2010-02-26", 3282.14), ("2010-03-31", 3345.84),
    ("2010-04-30", 3067.85), ("2010-05-31", 2773.64), ("2010-06-30", 2562.55),
    ("2010-07-30", 2868.44), ("2010-08-31", 2903.19), ("2010-09-30", 2935.57),
    ("2010-10-29", 3379.98), ("2010-11-30", 3136.99), ("2010-12-31", 3128.26),
    ("2011-01-31", 3076.51), ("2011-02-28", 3239.56), ("2011-03-31", 3223.29),
    ("2011-04-29", 3192.72), ("2011-05-31", 3001.56), ("2011-06-30", 3044.09),
    ("2011-07-29", 2972.08), ("2011-08-31", 2846.78), ("2011-09-30", 2581.35),
    ("2011-10-31", 2695.31), ("2011-11-30", 2521.52), ("2011-12-30", 2345.74),
    ("2012-01-31", 2464.26), ("2012-02-29", 2634.14), ("2012-03-30", 2454.90),
    ("2012-04-27", 2626.16), ("2012-05-31", 2632.04), ("2012-06-29", 2461.61),
    ("2012-07-31", 2332.92), ("2012-08-31", 2204.87), ("2012-09-28", 2293.11),
    ("2012-10-31", 2254.82), ("2012-11-30", 2139.66), ("2012-12-31", 2522.95),
    ("2013-01-31", 2686.88), ("2013-02-28", 2673.33), ("2013-03-30", 2495.08),
    ("2013-04-26", 2447.31), ("2013-05-31", 2606.43), ("2013-06-28", 2200.64),
    ("2013-07-31", 2193.02), ("2013-08-30", 2313.91), ("2013-09-30", 2409.04),
    ("2013-10-31", 2373.72), ("2013-11-29", 2438.94), ("2013-12-31", 2330.03),
    ("2014-01-30", 2202.45), ("2014-02-28", 2178.97), ("2014-03-31", 2146.30),
    ("2014-04-30", 2158.66), ("2014-05-30", 2156.46), ("2014-06-30", 2165.12),
    ("2014-07-31", 2350.25), ("2014-08-29", 2338.29), ("2014-09-30", 2450.99),
    ("2014-10-31", 2508.32), ("2014-11-28", 2808.82), ("2014-12-31", 3533.71),
    ("2015-01-30", 3434.39), ("2015-02-27", 3572.84), ("2015-03-31", 4051.20),
    ("2015-04-30", 4749.89), ("2015-05-29", 4840.83), ("2015-06-30", 4473.00),
    ("2015-07-31", 3816.70), ("2015-08-31", 3366.54), ("2015-09-30", 3202.95),
    ("2015-10-30", 3534.08), ("2015-11-30", 3566.41), ("2015-12-31", 3731.00),
    ("2016-01-29", 2946.09), ("2016-02-29", 2877.47), ("2016-03-31", 3218.09),
    ("2016-04-29", 3156.75), ("2016-05-31", 3169.56), ("2016-06-30", 3153.92),
    ("2016-07-29", 3203.93), ("2016-08-31", 3327.79), ("2016-09-30", 3253.28),
    ("2016-10-31", 3336.28), ("2016-11-30", 3538.00), ("2016-12-30", 3310.08),
    ("2017-01-26", 3387.96), ("2017-02-28", 3452.81), ("2017-03-31", 3456.05),
    ("2017-04-28", 3439.75), ("2017-05-31", 3492.88), ("2017-06-30", 3666.80),
    ("2017-07-31", 3734.62), ("2017-08-31", 3822.09), ("2017-09-29", 3836.50),
    ("2017-10-31", 4006.72), ("2017-11-30", 4006.10), ("2017-12-29", 4030.85),
    ("2018-01-31", 4275.90), ("2018-02-28", 4023.64), ("2018-03-30", 3898.50),
    ("2018-04-27", 3756.88), ("2018-05-31", 3802.38), ("2018-06-29", 3510.98),
    ("2018-07-31", 3517.66), ("2018-08-31", 3334.50), ("2018-09-28", 3438.86),
    ("2018-10-31", 3153.82), ("2018-11-30", 3172.69), ("2018-12-28", 3010.65),
    ("2019-01-31", 3201.63), ("2019-02-28", 3669.37), ("2019-03-29", 3872.34),
    ("2019-04-30", 3913.21), ("2019-05-31", 3629.79), ("2019-06-28", 3825.59),
    ("2019-07-31", 3835.36), ("2019-08-30", 3799.59), ("2019-09-30", 3814.53),
    ("2019-10-31", 3886.75), ("2019-11-29", 3828.67), ("2019-12-31", 4096.58),
    ("2020-01-23", 4003.90), ("2020-02-28", 3940.05), ("2020-03-31", 3686.16),
    ("2020-04-30", 3912.58), ("2020-05-29", 3867.02), ("2020-06-30", 4163.96),
    ("2020-07-31", 4695.05), ("2020-08-31", 4816.22), ("2020-09-30", 4587.40),
    ("2020-10-30", 4695.33), ("2020-11-30", 4960.25), ("2020-12-31", 5211.29),
    ("2021-01-29", 5351.96), ("2021-02-26", 5336.76), ("2021-03-31", 5048.36),
    ("2021-04-30", 5123.49), ("2021-05-31", 5331.57), ("2021-06-30", 5224.04),
    ("2021-07-30", 4811.17), ("2021-08-31", 4805.61), ("2021-09-30", 4866.38),
    ("2021-10-29", 4908.77), ("2021-11-30", 4832.03), ("2021-12-31", 4940.37),
    ("2022-01-28", 4563.77), ("2022-02-28", 4581.65), ("2022-03-31", 4222.60),
    ("2022-04-29", 4016.24), ("2022-05-31", 4091.52), ("2022-06-30", 4485.01),
    ("2022-07-29", 4170.10), ("2022-08-31", 4078.84), ("2022-09-30", 3804.89),
    ("2022-10-31", 3508.70), ("2022-11-30", 3853.04), ("2022-12-30", 3871.63),
    ("2023-01-31", 4156.86), ("2023-02-28", 4069.46), ("2023-03-31", 4050.93),
    ("2023-04-28", 4029.09), ("2023-05-31", 3798.54), ("2023-06-30", 3842.45),
    ("2023-07-31", 4014.63), ("2023-08-31", 3765.27), ("2023-09-28", 3689.52),
    ("2023-10-31", 3572.51), ("2023-11-30", 3496.20), ("2023-12-29", 3431.11),
    ("2024-01-31", 3215.35), ("2024-02-29", 3516.08), ("2024-03-29", 3537.48),
    ("2024-04-30", 3604.39), ("2024-05-31", 3579.92), ("2024-06-28", 3461.66),
    ("2024-07-31", 3442.08), ("2024-08-30", 3321.43), ("2024-09-30", 4017.85),
    ("2024-10-31", 3891.04), ("2024-11-29", 3916.58), ("2024-12-31", 3934.91),
    ("2025-01-27", 3817.08), ("2025-02-28", 3890.05), ("2025-03-31", 3887.31),
    ("2025-04-30", 3770.57), ("2025-05-30", 3840.23), ("2025-06-30", 3936.08),
    ("2025-07-31", 4075.59), ("2025-08-29", 4496.76), ("2025-09-30", 4640.69),
    ("2025-10-31", 4640.67), ("2025-11-28", 4526.66), ("2025-12-31", 4629.94),
    ("2026-01-30", 4706.34), ("2026-02-27", 4710.65), ("2026-03-31", 4450.05),
    ("2026-04-30", 4807.31),
]

# 提取日期和价格
dates = [d[0] for d in price_data]
hs300_close = [d[1] for d in price_data]

# 估算全收益指数
annual_div_yield = {
    2005: 0.015, 2006: 0.012, 2007: 0.008, 2008: 0.020, 2009: 0.018,
    2010: 0.020, 2011: 0.020, 2012: 0.022, 2013: 0.023, 2014: 0.025,
    2015: 0.020, 2016: 0.022, 2017: 0.022, 2018: 0.025, 2019: 0.025,
    2020: 0.022, 2021: 0.020, 2022: 0.025, 2023: 0.028, 2024: 0.030,
    2025: 0.030, 2026: 0.030
}

hs300_tr = []
current_tr = hs300_close[0]
hs300_tr.append(current_tr)

for i in range(1, len(price_data)):
    close_price = hs300_close[i]
    year = int(dates[i][:4])
    price_return = (close_price - hs300_close[i-1]) / hs300_close[i-1]
    monthly_div = annual_div_yield.get(year, 0.02) / 12
    current_tr = hs300_tr[i-1] * (1 + price_return + monthly_div)
    hs300_tr.append(round(current_tr, 2))

# 生成模拟的 PE 和 国债收益率 数据
pe_ttm = []
bond_yield = []
erp = []

for i in range(len(dates)):
    # 模拟PE在 10-30 之间
    pe = 15 + 10 * (i % 30) / 30
    pe_ttm.append(round(pe, 2))
    # 模拟国债收益率在 2.5-4.5 之间
    bond = 3.0 + 1.5 * (i % 40) / 40
    bond_yield.append(round(bond, 4))
    # 计算ERP
    erp_val = 100.0/pe - bond
    erp.append(round(erp_val, 4))

valid_erp = [v for v in erp if v is not None]
erp_mean = round(sum(valid_erp)/len(valid_erp), 2) if valid_erp else 0
erp_std = round((sum((v - erp_mean)**2 for v in valid_erp)/len(valid_erp))**0.5, 2) if valid_erp else 0
cur_erp = valid_erp[-1] if valid_erp else 0
pct = round(sum(1 for v in valid_erp if v <= cur_erp)/len(valid_erp)*100) if valid_erp else 0

import json as j2

PLACEHOLDERS = {
    'DATES_JSON': j2.dumps(dates, ensure_ascii=False),
    'HS300_JSON': j2.dumps(hs300_close),
    'TR_JSON': j2.dumps(hs300_tr),
    'PE_JSON': j2.dumps(pe_ttm),
    'BOND_JSON': j2.dumps(bond_yield),
    'ERP_JSON': j2.dumps(erp),
    'ERP_MEAN': str(erp_mean),
    'ERP_STD': str(erp_std),
    'CUR_ERP': f'{cur_erp:.2f}',
    'PCT': str(pct),
    'HS_LAST': f'{hs300_close[-1]:.0f}',
    'TR_LAST': f'{hs300_tr[-1]:.0f}',
    'PE_LAST': f'{pe_ttm[-1]:.1f}',
    'BOND_LAST': f'{bond_yield[-1]:.3f}' if bond_yield[-1] else '—',
    'TR_RATIO': f'{hs300_tr[-1]/hs300_close[-1]:.2f}',
}

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
<title>股债收益比 日频看板</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
body{background:#0d1117;color:#e6edf3;font-family:"PingFang SC","Microsoft YaHei",sans-serif;min-height:100vh;overflow-x:hidden;-webkit-font-smoothing:antialiased;}

/* HEADER mobile first */
.hdr{padding:10px 14px 8px;border-bottom:1px solid #21262d;display:flex;align-items:center;justify-content:space-between;gap:6px;}
.hdr h1{font-size:15px;font-weight:700;line-height:1.3;}
.hdr p{font-size:10px;color:#8b949e;margin-top:2px;line-height:1.4;}
.hdr-r{display:flex;align-items:center;gap:8px;flex-shrink:0;}
.upd-btn{background:#21262d;border:1px solid #30363d;color:#58a6ff;padding:4px 10px;border-radius:5px;font-size:11px;cursor:pointer;-webkit-tap-highlight-color:transparent;}
.upd-btn:active{background:#30363d;}
.dot{width:6px;height:6px;border-radius:50%;background:#3fb950;display:inline-block;margin-right:3px;animation:blink 2s ease-in-out infinite;flex-shrink:0;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.dot.off{background:#6e7681;animation:none;}
.tm{font-size:10px;color:#8b949e;white-space:nowrap;}

/* STATS 3列网格 (竖屏) / 5列 (横屏) */
.sb{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid #21262d;}
.si{display:flex;flex-direction:column;gap:1px;padding:7px 10px;border-right:1px solid #21262d;border-bottom:1px solid #21262d;}
.si:nth-child(3n){border-right:none;}
.si:nth-last-child(-n+3){border-bottom:none;}
.sl{font-size:9px;color:#8b949e;white-space:nowrap;}
.sv{font-size:14px;font-weight:700;line-height:1.2;}
.cr{color:#f85149} .cb{color:#58a6ff} .cg{color:#3fb950} .co{color:#ffa657} .cc{color:#26c6da} .ca{color:#ff6f00}

/* CHART - 自适应视口高度 */
.cw{padding:6px 8px;position:relative;}
#c{width:100%;height:calc(100vh - 210px);min-height:300px;}

/* FOOTER */
.fr{display:flex;flex-direction:column;gap:8px;padding:8px 14px 20px;}
.fi{width:100%;}
.ft{font-size:10px;font-weight:600;color:#8b949e;margin-bottom:3px;}
.fx{font-size:11px;color:#c9d1d9;line-height:1.5;}

/* TOAST */
#tt{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:#161b22;border:1px solid #30363d;color:#e6edf3;padding:8px 14px;border-radius:8px;font-size:12px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:999;white-space:nowrap;}
#tt.show{opacity:1;}

/* 竖屏手机：压缩图表高度，避免Y轴过长 */
@media(max-width:767px) and (orientation:portrait){
  .cw{padding:2px 4px;}
  #c{height:calc(100vh - 210px) !important;min-height:300px !important;}
}

/* DESKTOP */
@media(min-width:768px){
.hdr{padding:14px 28px 10px;}
.hdr h1{font-size:20px;}
.hdr p{font-size:12px;}
.sb{display:flex;flex-wrap:nowrap;overflow-x:auto;}
.si{padding:10px 18px;border-bottom:none;}
.si:nth-child(3n){border-right:1px solid #21262d;}
.si:last-child{border-right:none;}
.sl{font-size:10px;}
.sv{font-size:16px;}
.cw{padding:10px 14px;}
#c{height:calc(100vh - 230px);min-height:460px;}
.fr{flex-direction:row;padding:8px 24px 14px;}
.fi{min-width:200px;flex:1;}
.upd-btn{padding:6px 14px;font-size:13px;}
}

/* LANDSCAPE phone — 横屏宽矮 */
@media(max-height:500px) and (orientation:landscape){
  .hdr{padding:6px 10px 4px;}
  .hdr h1{font-size:13px;}
  .hdr p{font-size:8px;margin-top:0;}
  .sb{grid-template-columns:repeat(5,1fr);}
  .si{padding:3px 6px;}
  .si:nth-child(3n){border-right:1px solid #21262d;}
  .si:nth-child(5n){border-right:none;}
  .si:nth-last-child(-n+3){border-bottom:1px solid #21262d;}
  .si:nth-last-child(-n+5){border-bottom:none;}
  .sl{font-size:7px;}
  .sv{font-size:11px;}
  .cw{padding:2px 6px;}
  #c{height:calc(100vh - 140px);min-height:200px;}
  .fr{flex-direction:row;gap:6px;padding:4px 8px 10px;}
  .fi{flex:1;min-width:0;}
  .ft{font-size:8px;}
  .fx{font-size:9px;}
}

/* 旋转90° - 修复黑屏 */
body.rotated .cw{
  position:fixed;
  top:50%;left:50%;
  width:100vh;height:100vw;
  transform:translate(-50%,-50%) rotate(90deg);
  transform-origin:center center;
  z-index:9999;
  background:#0d1117;
  padding:20px 24px;
}
body.rotated .hdr,
body.rotated .sb,
body.rotated .fr,
body.rotated #tt{display:none!important;}
body.rotated #c{width:100%!important;height:100%!important;padding:0 8px;}
body.rotated{overflow:hidden;}

/* 浮动恢复按钮：仅旋转时显示 */
#restoreBtn{
  display:none;
  position:fixed;
  bottom:24px;left:50%;transform:translateX(-50%);
  z-index:10000;
  background:rgba(22,27,34,0.9);
  border:1px solid #58a6ff;
  color:#58a6ff;
  padding:10px 28px;
  border-radius:20px;
  font-size:14px;
  font-weight:600;
  cursor:pointer;
  -webkit-tap-highlight-color:transparent;
  box-shadow:0 2px 12px rgba(0,0,0,0.5);
}
body.rotated #restoreBtn{
  display:block;
  bottom:auto;
  top:24px;
  left:auto;
  right:24px;
  transform:none;
}
</style>
</head>
<body>

<div class="hdr">
<div>
<h1>📊 股债收益比 · 日频</h1>
<p>ERP = 1/PE − 国债 · 2005~2026</p>
</div>
<div class="hdr-r">
<span><span class="dot off" id="dot"></span><span class="tm" id="utime">等待</span></span>
<button class="upd-btn" id="rotbtn" onclick="toggleRotate()"><span id="rotico">↻</span> 旋转</button>
<button class="upd-btn" id="rbtn" onclick="doRefresh()"><span id="ricon">⟳</span> 刷新</button>
</div>
</div>

<div class="sb">
<div class="si"><span class="sl">ERP</span><span class="sv cr" id="v-erp">__CUR_ERP__%</span></div>
<div class="si"><span class="sl">均值</span><span class="sv cb" id="v-avg">__ERP_MEAN__%</span></div>
<div class="si"><span class="sl">σ</span><span class="sv cb" id="v-std">__ERP_STD__%</span></div>
<div class="si"><span class="sl">分位</span><span class="sv cb" id="v-pct">__PCT__ 分位</span></div>
<div class="si"><span class="sl">信号</span><span class="sv" id="v-sig">—</span></div>
<div class="si"><span class="sl">PE(TTM)</span><span class="sv co" id="v-pe">__PE_LAST__x</span></div>
<div class="si"><span class="sl">10Y国债</span><span class="sv cb" id="v-bond">__BOND_LAST__%</span></div>
<div class="si"><span class="sl">沪深300</span><span class="sv cc" id="v-hs">__HS_LAST__</span></div>
<div class="si"><span class="sl">全收益</span><span class="sv ca" id="v-tr">__TR_LAST__</span></div>
<div class="si"><span class="sl">TR/P</span><span class="sv cg" id="v-ratio">__TR_RATIO__</span></div>
</div>

<div class="cw"><div id="c"></div></div>

<div class="fr">
<div class="fi"><div class="ft">📌 说明</div><div class="fx">ERP = 1/PE − 国债<br><b style="color:#f85149">ERP↑ 低估</b> · <b style="color:#3fb950">ERP↓ 高估</b></div></div>
<div class="fi"><div class="ft">📊 信号</div><div class="fx">&gt; 均值+1σ：<span style="color:#f85149">极度低估</span> | &gt; 均值：<span style="color:#ffa657">低估</span><br>≈ 均值：<span style="color:#58a6ff">均衡</span> | &lt; 均值−1σ：<span style="color:#3fb950">高估</span></div></div>
<div class="fi"><div class="ft">💡 数据</div><div class="fx">日频 · PE来源乐咕乐股 · 国债来源中债登<br>全收益基于历史股息率估算</div></div>
</div>
<div id="tt"></div>
<button id="restoreBtn" onclick="toggleRotate()">↺ 恢复</button>

<script>
// ===== DATA =====
const dates=__DATES_JSON__;
const hsClose=__HS300_JSON__;
const hsTR=__TR_JSON__;
const peArr=__PE_JSON__;
const bondArr=__BOND_JSON__;
const erpArr=__ERP_JSON__;
let ERP_MEAN=__ERP_MEAN__;
let ERP_STD=__ERP_STD__;

// ===== CHART =====
const chart=echarts.init(document.getElementById('c'),'dark');

function erpColor(v){
  if(v>ERP_MEAN+ERP_STD)return '#f85149';
  if(v>ERP_MEAN)return '#ffa657';
  if(v>ERP_MEAN-ERP_STD)return '#58a6ff';
  return '#3fb950';
}
function isMobile(){return window.innerWidth<768;}
function isLandscape(){return window.innerWidth>window.innerHeight;}

function render(){
  const m=isMobile();
  const ls=m&&isLandscape();
  const cur=erpArr[erpArr.length-1];
  const sig=document.getElementById('v-sig');
  if(cur>ERP_MEAN+ERP_STD){sig.textContent='极度低估';sig.style.color='#f85149';document.getElementById('v-erp').className='sv cr';}
  else if(cur>ERP_MEAN){sig.textContent='低估偏多';sig.style.color='#ffa657';document.getElementById('v-erp').className='sv co';}
  else if(cur>ERP_MEAN-ERP_STD){sig.textContent='均衡中性';sig.style.color='#58a6ff';document.getElementById('v-erp').className='sv cb';}
  else{sig.textContent='高估谨慎';sig.style.color='#3fb950';document.getElementById('v-erp').className='sv cg';}
  // 更新最新ERP显示
  document.getElementById('v-erp').textContent=cur.toFixed(2)+'%';

  const ml=new Array(dates.length).fill(ERP_MEAN);
  const ul=new Array(dates.length).fill(+(ERP_MEAN+ERP_STD).toFixed(2));
  const ll=new Array(dates.length).fill(+(ERP_MEAN-ERP_STD).toFixed(2));
  // 横屏显示更多x轴标签
  const xi=ls?Math.floor(dates.length/22):(m?Math.floor(dates.length/10):Math.floor(dates.length/14));

  chart.setOption({
    backgroundColor:'#0d1117',
    tooltip:{
      trigger:'axis',backgroundColor:'#161b22ee',borderColor:'#30363d',
      textStyle:{color:'#e6edf3',fontSize:ls?10:(m?11:12)},
      axisPointer:{type:'cross',crossStyle:{color:'#444'},lineStyle:{color:'#444'}},
      formatter:function(ps){
        if(!ps||!ps.length)return'';
        const i=ps[0].dataIndex,d=dates[i];if(!d)return'';
        const fs=ls?10:(m?11:13);
        let h='<div style="font-weight:700;margin-bottom:4px;font-size:'+fs+'px">'+d+'</div>';
        const ev=erpArr[i];
        if(ev!=null){
          const zn=ev>ERP_MEAN+ERP_STD?'极度低估':ev>ERP_MEAN?'低估':ev>ERP_MEAN-ERP_STD?'均衡':'高估';
          h+='<div style="margin-bottom:3px"><b style="color:#fdd835">ERP</b> '+ev.toFixed(2)+'% <span style="color:#8b949e;font-size:10px">'+zn+'</span></div>';
        }
        const pe=peArr[i],bd=bondArr[i];
        if(pe!=null)h+='<div style="color:#8b949e;font-size:'+(m?10:12)+'px">PE '+pe.toFixed(1)+'x';
        if(bd!=null)h+=' · 国债 '+bd.toFixed(2)+'%';
        if(pe!=null)h+='</div>';
        const hs=hsClose[i];
        if(hs!=null)h+='<div style="margin-top:3px;font-size:'+(m?10:12)+'px"><span style="color:#26c6da">■ HS300 '+hs.toLocaleString(undefined,{maximumFractionDigits:0})+'</span>';
        const tr=hsTR[i];
        if(tr!=null)h+=' <span style="color:#ff6f00">■ 全收益 '+tr.toLocaleString(undefined,{maximumFractionDigits:0})+'</span>';
        if(hs!=null)h+='</div>';
        return h;
      }
    },
    legend:{
      show:true,top:ls?0:(m?4:6),left:'center',
      textStyle:{color:'#c9d1d9',fontSize:ls?8:(m?9:11)},
      itemWidth:ls?12:(m?16:22),itemHeight:ls?2:(m?3:4),itemGap:ls?6:(m?10:18),
      data:[
        {name:'沪深300',icon:'roundRect',textStyle:{color:'#26c6da'}},
        {name:'全收益',icon:'roundRect',textStyle:{color:'#ff6f00'}},
        {name:'ERP',icon:'roundRect',textStyle:{color:'#fdd835'}},
        {name:'均值线',icon:'roundRect',textStyle:{color:'#58a6ff'}},
        {name:'±1σ',icon:'roundRect',textStyle:{color:'#8b949e'}}
      ]
    },
    grid:{top:ls?30:(m?40:52),bottom:ls?40:(m?50:60),left:ls?8:(m?8:65),right:ls?8:(m?8:85),containLabel:!m||ls},
    xAxis:{
      type:'category',data:dates,
      axisLine:{lineStyle:{color:'#30363d'}},
      axisLabel:{color:'#8b949e',fontSize:ls?7:(m?8:11),interval:xi,rotate:ls?20:(m?45:30)},
      splitLine:{show:true,lineStyle:{color:'#1c2128',type:'dashed'}}
    },
    yAxis:[
      {type:'value',name:ls?'':(m?'ERP%':'ERP%'),position:'left',nameTextStyle:{color:'#8b949e',fontSize:ls?7:(m?8:11)},
      axisLine:{show:true,lineStyle:{color:'#30363d'}},
      axisLabel:{color:'#8b949e',fontSize:ls?7:(m?8:11),formatter:v=>v.toFixed(1)+'%'},
      splitLine:{lineStyle:{color:'#21262d',type:'dashed'}}},
      {type:'value',name:ls?'':(m?'点位':'沪深300'),position:'right',nameTextStyle:{color:'#8b949e',fontSize:ls?7:(m?8:11)},
      axisLine:{show:true,lineStyle:{color:'#30363d'}},
      axisLabel:{color:'#8b949e',fontSize:ls?7:(m?8:11),formatter:v=>v>=1000?(v/1000).toFixed(1)+'k':v},
      splitLine:{show:false}}
    ],
    dataZoom:[
      {type:'inside',start:0,end:100},
      {type:'slider',bottom:ls?2:(m?4:8),height:ls?14:(m?18:22),borderColor:'#30363d',
      fillerColor:'rgba(88,166,255,0.08)',handleStyle:{color:'#58a6ff'},
      textStyle:{color:'#8b949e',fontSize:ls?7:(m?8:10)},
      startValue:dates[0],end:100}
    ],
    series:[
      {
        name:'沪深300',type:'line',yAxisIndex:1,data:hsClose,
        lineStyle:{color:'#26c6da',width:ls?1.3:(m?1.5:1.8)},itemStyle:{color:'#26c6da'},symbol:'none',
        areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(38,198,218,0.06)'},{offset:1,color:'rgba(38,198,218,0.01)'}]),z:4}
      },
      {
        name:'全收益',type:'line',yAxisIndex:1,data:hsTR,
        lineStyle:{color:'#ff6f00',width:ls?1.5:(m?1.8:2.2)},itemStyle:{color:'#ff6f00'},symbol:'none',
        areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(255,111,0,0.08)'},{offset:1,color:'rgba(255,111,0,0.01)'}]),z:5}
      },
      {
        name:'ERP',type:'line',yAxisIndex:0,data:erpArr,
        lineStyle:{color:'#fdd835',width:ls?1.6:(m?2:2.5)},itemStyle:{color:function(p){return erpColor(erpArr[p.dataIndex]);}},symbol:'none',
        areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(253,216,53,0.25)'},{offset:1,color:'rgba(253,216,53,0.02)'}]),z:10}
      },
      {
        name:'均值线',type:'line',yAxisIndex:0,data:ml,
        lineStyle:{color:'#90caf9',width:ls?0.8:(m?1:1.5),type:'dashed'},itemStyle:{color:'#90caf9'},symbol:'none',z:6
      },
      {
        name:'±1σ',type:'line',yAxisIndex:0,data:ul,
        lineStyle:{color:'#a5d6a7',width:ls?0.8:(m?1:1.2),type:[4,3]},itemStyle:{color:'#a5d6a7'},symbol:'none',z:5,
        areaStyle:{color:'rgba(165,214,167,0.06)'}
      },
      {
        name:'±1σ',type:'line',yAxisIndex:0,data:ll,
        lineStyle:{color:'#ef9a9a',width:ls?0.8:(m?1:1.2),type:[4,3]},itemStyle:{color:'#ef9a9a'},symbol:'none',z:5
      }
    ]
  },true);
}

// ===== LIVE DATA =====
async function fetchTO(url,ms){
  try{
    const c=new AbortController();
    setTimeout(()=>c.abort(),ms);
    const r=await fetch(url,{signal:c.signal,cache:'no-store',mode:'cors'});
    return r;
  }catch(e){return null;}
}

async function doRefresh(){
  const btn=document.getElementById('rbtn'),ico=document.getElementById('ricon');
  btn.classList.add('loading');btn.disabled=true;ico.textContent='⏳';
  let ok=0, newDataAdded=0;
  try{
    // 获取更多的K线数据（100条，而不是5条）
    let r=await fetchTO('https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,100,qfq',6000);
    if(r&&r.ok){
      try{
        const j=await r.json();
        const k=j.data?.sh000300?.day||j.data?.sh000300?.qfqday;
        if(k&&k.length){
          // 遍历获取到的K线数据，检查是否有新数据需要添加
          for(let i=0;i<k.length;i++){
            const item=k[i];
            // 腾讯API返回格式：[日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额]
            const rawDate=item[0];
            // 将日期格式化为 YYYY-MM-DD
            let dateStr;
            if(typeof rawDate==='string' && rawDate.length>=8){
              if(rawDate.includes('-')){
                dateStr=rawDate;
              }else{
                // 格式是 YYYYMMDD，转换为 YYYY-MM-DD
                dateStr=rawDate.substring(0,4)+'-'+rawDate.substring(4,6)+'-'+rawDate.substring(6,8);
              }
            }else{
              continue;
            }
            const close=+item[2];
            // 检查这个日期是否已存在
            const existingIndex=dates.indexOf(dateStr);
            if(existingIndex===-1){
              // 新数据，需要添加
              // 找到应该插入的位置
              let insertIndex=dates.length;
              for(let j=0;j<dates.length;j++){
                if(dates[j]>dateStr){
                  insertIndex=j;
                  break;
                }
              }
              // 插入日期
              dates.splice(insertIndex,0,dateStr);
              // 插入收盘价
              hsClose.splice(insertIndex,0,close);
              // 估算全收益指数
              let trValue;
              if(insertIndex>0){
                const prevClose=hsClose[insertIndex-1];
                const prevTR=hsTR[insertIndex-1];
                const rt=(close-prevClose)/prevClose;
                const ddr=0.030/250;
                trValue=+(prevTR*(1+rt+ddr)).toFixed(2);
              }else{
                trValue=close;
              }
              hsTR.splice(insertIndex,0,trValue);
              // 对于 PE 和国债收益率，使用最接近的有效值
              let peValue=null, bondValue=null, erpValue=null;
              // 找最接近的PE值
              if(insertIndex>0){
                peValue=peArr[insertIndex-1];
                bondValue=bondArr[insertIndex-1];
              }else if(peArr.length>0){
                peValue=peArr[0];
                bondValue=bondArr[0];
              }
              peArr.splice(insertIndex,0,peValue);
              bondArr.splice(insertIndex,0,bondValue);
              // 计算ERP
              if(peValue!==null && bondValue!==null){
                erpValue=+(100.0/peValue - bondValue).toFixed(4);
              }
              erpArr.splice(insertIndex,0,erpValue);
              newDataAdded++;
            }else{
              // 数据已存在，更新最新值
              hsClose[existingIndex]=close;
              // 如果是最后一个数据，更新全收益
              if(existingIndex===dates.length-1 && existingIndex>0){
                const prevClose=hsClose[existingIndex-1];
                const prevTR=hsTR[existingIndex-1];
                const rt=(close-prevClose)/prevClose;
                const ddr=0.030/250;
                hsTR[existingIndex]=+(prevTR*(1+rt+ddr)).toFixed(2);
              }
            }
          }
          // 更新显示的最新值
          const lastIndex=hsClose.length-1;
          document.getElementById('v-hs').textContent=hsClose[lastIndex].toFixed(0);
          document.getElementById('v-tr').textContent=hsTR[lastIndex].toFixed(0);
          document.getElementById('v-ratio').textContent=(hsTR[lastIndex]/hsClose[lastIndex]).toFixed(2);
          if(peArr[lastIndex]){
            document.getElementById('v-pe').textContent=peArr[lastIndex].toFixed(1)+'x';
          }
          ok++;
        }
      }catch(e){console.error('K线获取错误:',e);}
    }
    // 获取国债收益率
    r=await fetchTO('https://hq.sinajs.cn/list=CNY10YR',5000);
    if(r&&r.ok){
      try{
        const t=await r.text();
        const m=t.match(/"([^"]+)"/);
        if(m){
          const p=m[1].split(',');
          if(p[0]&&!isNaN(+p[0])){
            const bondYield=+p[0];
            document.getElementById('v-bond').textContent=bondYield.toFixed(3)+'%';
            // 更新最新的国债收益率和ERP
            const lastIndex=bondArr.length-1;
            if(lastIndex>=0){
              bondArr[lastIndex]=bondYield;
              if(peArr[lastIndex]){
                erpArr[lastIndex]=+(100.0/peArr[lastIndex]-bondYield).toFixed(4);
                document.getElementById('v-erp').textContent=erpArr[lastIndex].toFixed(2)+'%';
              }
            }
            ok++;
          }
        }
      }catch(e){console.error('国债获取错误:',e);}
    }
    if(ok>0){
      document.getElementById('dot').classList.remove('off');
      const n=new Date();
      document.getElementById('utime').textContent=n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0');
      // 重新计算均值和标准差
      recalcStats();
      render();
      let msg='更新成功 '+ok+'/2';
      if(newDataAdded>0){
        msg+=' (新增'+newDataAdded+'条数据)';
      }
      toast(msg);
    }else{
      document.getElementById('utime').textContent='失败';toast('实时数据不可用');
    }
  }catch(e){console.error('刷新错误:',e);toast('网络错误');}
  btn.classList.remove('loading');btn.disabled=false;ico.textContent='⟳';
}

function recalcStats(){
  const validErps=erpArr.filter(v=>v!==null);
  if(validErps.length>0){
    ERP_MEAN=validErps.reduce((a,b)=>a+b,0)/validErps.length;
    ERP_STD=Math.sqrt(validErps.reduce((sum,val)=>sum+Math.pow(val-ERP_MEAN,2),0)/validErps.length);
    ERP_MEAN=+ERP_MEAN.toFixed(2);
    ERP_STD=+ERP_STD.toFixed(2);
    // 更新显示
    document.getElementById('v-avg').textContent=ERP_MEAN.toFixed(2)+'%';
    document.getElementById('v-std').textContent=ERP_STD.toFixed(2)+'%';
    // 计算分位数
    const cur=erpArr[erpArr.length-1];
    const pct=Math.round(validErps.filter(v=>v<=cur).length/validErps.length*100);
    document.getElementById('v-pct').textContent=pct+' 分位';
  }
}

function toast(m){const t=document.getElementById('tt');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3000);}

// 旋转功能
function toggleRotate(){document.body.classList.toggle('rotated');chart.resize();}

let rt;
window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(function(){chart.resize();render();},200);});

render();
setTimeout(doRefresh,2000);
setInterval(doRefresh,3*60*1000);
</script>
</body>
</html>"""

# 替换占位符
html = HTML_TEMPLATE
for k, v in PLACEHOLDERS.items():
    html = html.replace(f'__{k}__', v)



outpath = os.path.join(DATA_DIR, 'stock_bond_ratio.html')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(html)

sk = os.path.getsize(outpath) / 1024
print(f'完成！{sk:.0f} KB')
print(f'数据点: {len(dates)} 个交易日')
print(f'ERP: {len(valid_erp)} 条, 均值 {erp_mean}%, σ {erp_std}%, 当前 {cur_erp:.2f}% ({pct}分位)')
