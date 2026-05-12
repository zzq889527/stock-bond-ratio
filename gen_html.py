# -*- coding: utf-8 -*-
"""生成手机竖屏适配版 HTML 看板"""
import json, os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DATA_DIR, 'daily_data.json'), 'r', encoding='utf-8') as f:
    d = json.load(f)

hs300 = d['hs300']
dates = [item['date'] for item in hs300]
hs300_close = [item['close'] for item in hs300]
pe_ttm = [item['pe_ttm'] for item in hs300]
bond_yield = [item['bond_yield'] for item in hs300]
erp = [item['erp'] for item in hs300]

# 估算全收益指数
div_yield = {2005:0.015,2006:0.012,2007:0.008,2008:0.020,2009:0.018,
             2010:0.020,2011:0.020,2012:0.022,2013:0.023,2014:0.025,
             2015:0.020,2016:0.022,2017:0.022,2018:0.025,2019:0.025,
             2020:0.022,2021:0.020,2022:0.025,2023:0.028,2024:0.030,
             2025:0.030,2026:0.030}
hs300_tr = [0.0]*len(hs300_close)
hs300_tr[0] = hs300_close[0]
for i in range(1,len(hs300_close)):
    y=int(dates[i][:4]); ddr=div_yield.get(y,0.02)/250.0
    r=(hs300_close[i]-hs300_close[i-1])/hs300_close[i-1]
    hs300_tr[i]=round(hs300_tr[i-1]*(1+r+ddr),2)

valid_erp=[v for v in erp if v is not None]
erp_mean=round(sum(valid_erp)/len(valid_erp),2) if valid_erp else 0
erp_std=round((sum((v-erp_mean)**2 for v in valid_erp)/len(valid_erp))**0.5,2) if valid_erp else 0
cur_erp=valid_erp[-1] if valid_erp else 0
pct=round(sum(1 for v in valid_erp if v<=cur_erp)/len(valid_erp)*100) if valid_erp else 0

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
    'BOND_LAST': f'{bond_yield[-1]:.3f}' if bond_yield[-1] else '\u2014',
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

<script>
// ===== DATA =====
const dates=__DATES_JSON__;
const hsClose=__HS300_JSON__;
const hsTR=__TR_JSON__;
const peArr=__PE_JSON__;
const bondArr=__BOND_JSON__;
const erpArr=__ERP_JSON__;
const ERP_MEAN=__ERP_MEAN__;
const ERP_STD=__ERP_STD__;

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
  if(cur>ERP_MEAN+ERP_STD){sig.textContent='极度低估';sig.style.color='#f85149';}
  else if(cur>ERP_MEAN){sig.textContent='低估偏多';sig.style.color='#ffa657';}
  else if(cur>ERP_MEAN-ERP_STD){sig.textContent='均衡中性';sig.style.color='#58a6ff';}
  else{sig.textContent='高估谨慎';sig.style.color='#3fb950';}

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
      {name:'沪深300',type:'line',yAxisIndex:1,data:hsClose,
       lineStyle:{color:'#26c6da',width:ls?1.3:(m?1.5:1.8)},itemStyle:{color:'#26c6da'},symbol:'none',
       areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(38,198,218,0.06)'},{offset:1,color:'rgba(38,198,218,0.01)'}])},z:4},
      {name:'全收益',type:'line',yAxisIndex:1,data:hsTR,
       lineStyle:{color:'#ff6f00',width:ls?1.5:(m?1.8:2.2)},itemStyle:{color:'#ff6f00'},symbol:'none',
       areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(255,111,0,0.08)'},{offset:1,color:'rgba(255,111,0,0.01)'}])},z:5},
      {name:'ERP',type:'line',yAxisIndex:0,data:erpArr,
       lineStyle:{color:'#fdd835',width:ls?1.6:(m?2:2.5)},itemStyle:{color:function(p){return erpColor(erpArr[p.dataIndex]);}},symbol:'none',
       areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(253,216,53,0.25)'},{offset:1,color:'rgba(253,216,53,0.02)'}])},z:10},
      {name:'均值线',type:'line',yAxisIndex:0,data:ml,
       lineStyle:{color:'#90caf9',width:ls?0.8:(m?1:1.5),type:'dashed'},itemStyle:{color:'#90caf9'},symbol:'none',z:6},
      {name:'±1σ',type:'line',yAxisIndex:0,data:ul,
       lineStyle:{color:'#a5d6a7',width:ls?0.8:(m?1:1.2),type:[4,3]},itemStyle:{color:'#a5d6a7'},symbol:'none',z:5,
       areaStyle:{color:'rgba(165,214,167,0.06)'}},
      {name:'±1σ',type:'line',yAxisIndex:0,data:ll,
       lineStyle:{color:'#ef9a9a',width:ls?0.8:(m?1:1.2),type:[4,3]},itemStyle:{color:'#ef9a9a'},symbol:'none',z:5}
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
  let ok=0;
  try{
    let r=await fetchTO('https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,5,qfq',6000);
    if(r&&r.ok){
      try{
        const j=await r.json();
        const k=j.data?.sh000300?.day||j.data?.sh000300?.qfqday;
        if(k&&k.length){
          const lst=k[k.length-1],prv=k.length>1?k[k.length-2]:null;
          document.getElementById('v-hs').textContent=(+lst[2]).toFixed(0);
          if(prv){
            const rt=(+lst[2]-+prv[2])/+prv[2];
            const ddr=0.030/250;
            hsClose[hsClose.length-1]=+lst[2];
            hsTR[hsTR.length-1]=+(hsTR[hsTR.length-2]*(1+rt+ddr)).toFixed(2);
            document.getElementById('v-tr').textContent=hsTR[hsTR.length-1].toFixed(0);
            document.getElementById('v-ratio').textContent=(hsTR[hsTR.length-1]/hsClose[hsClose.length-1]).toFixed(2);
          }
          ok++;
        }
      }catch(e){}
    }
    r=await fetchTO('https://hq.sinajs.cn/list=CNY10YR',5000);
    if(r&&r.ok){
      try{
        const t=await r.text();
        const m=t.match(/"([^"]+)"/);
        if(m){
          const p=m[1].split(',');
          if(p[0]&&!isNaN(+p[0])){
            document.getElementById('v-bond').textContent=(+p[0]).toFixed(3)+'%';
            ok++;
          }
        }
      }catch(e){}
    }
    if(ok>0){
      document.getElementById('dot').classList.remove('off');
      const n=new Date();
      document.getElementById('utime').textContent=n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0');
      render();toast('更新成功 '+ok+'/2');
    }else{
      document.getElementById('utime').textContent='失败';toast('实时数据不可用');
    }
  }catch(e){toast('网络错误');}
  btn.classList.remove('loading');btn.disabled=false;ico.textContent='⟳';
}

function toast(m){const t=document.getElementById('tt');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3000);}

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
