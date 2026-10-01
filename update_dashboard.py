# -*- coding: utf-8 -*-
"""
股债收益比看板 · 数据更新与重建脚本
==================================================
数据源（全部免鉴权）：
  1) 沪深300 日频收盘 + 滚动市盈率  → 中证指数官网 (akshare stock_zh_index_hist_csindex)
     - 官网滚动市盈率自 2011-06-28 起提供；2005~2011 段沿用乐咕乐股日频PE(已内嵌)，
       2011 之后仍用乐咕口径做"口径对齐"（用乐咕周频序列做比值插值）
  2) 沪深300全收益指数 H00300 日频收盘 → 中证指数官网（真实全收益，非估算）
  3) 10年期国债收益率   → 中债登 bond_china_yield（2010起）/ bond_zh_us_rate（2005起，两者口径一致）
  4) 乐咕乐股 周频 PE   → 用于 PE 口径对齐（免费版无日频）

用法：
  python update_dashboard.py            # 拉取最新数据并重建 HTML
  python update_dashboard.py --offline  # 只用本地缓存重建（不联网）
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

import akshare as ak

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, 'stock_bond_ratio.html')
DATA_JSON = os.path.join(BASE, 'dashboard_data.json')
CACHE = os.path.join(BASE, 'cache')
os.makedirs(CACHE, exist_ok=True)

DIV_YIELD_ANNUAL = 0.030          # 全收益指数日均股息率近似（仅用于前端实时尾部外推）
CSV_LEGACY_START = '2005-04-08'   # 看板历史起点


def log(msg):
    print(msg, flush=True)


# ----------------------------------------------------------------------------
# 1. 抓数据（带本地缓存）
# ----------------------------------------------------------------------------
def _cache_path(name):
    return os.path.join(CACHE, name + '.json')


def _load_cache(name):
    p = _cache_path(name)
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return None


def _save_cache(name, obj):
    with open(_cache_path(name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)


def _cache_fresh(name):
    """缓存是否今天生成的"""
    p = _cache_path(name)
    if not os.path.exists(p):
        return False
    return datetime.fromtimestamp(os.path.getmtime(p)).date() == datetime.now().date()


def fetch_csi(symbol, offline=False):
    """中证指数官网日频数据 -> {date: {'close':..,'pe':..}}"""
    name = 'csi_' + symbol
    if offline or _cache_fresh(name):
        c = _load_cache(name)
        if c:
            log(f'  [缓存] {symbol}: {len(c)} 条')
            return c
    df = ak.stock_zh_index_hist_csindex(
        symbol=symbol, start_date='20050101',
        end_date=datetime.now().strftime('%Y%m%d'))
    out = {}
    for _, r in df.iterrows():
        d = str(r['日期'])[:10]
        try:
            close = float(r['收盘'])
        except Exception:
            continue
        if close != close:  # NaN
            continue
        pe = r.get('滚动市盈率')
        try:
            pe = float(pe)
            if pe != pe:
                pe = None
        except Exception:
            pe = None
        out[d] = {'close': round(close, 2), 'pe': (round(pe, 4) if pe else None)}
    _save_cache(name, out)
    log(f'  [抓取] {symbol}: {len(out)} 条 ({min(out)} ~ {max(out)})')
    return out


def fetch_y10(offline=False):
    """10年期国债收益率 -> {date: yield}"""
    name = 'y10'
    if offline or _cache_fresh(name):
        c = _load_cache(name)
        if c:
            log(f'  [缓存] 10Y国债: {len(c)} 条')
            return c
    df = ak.bond_zh_us_rate(start_date='20050101')
    col = '中国国债收益率10年'
    out = {}
    for _, r in df.iterrows():
        try:
            v = float(r[col])
        except Exception:
            continue
        if v != v or v <= 0:
            continue
        out[str(r['日期'])[:10]] = round(v, 4)
    _save_cache(name, out)
    log(f'  [抓取] 10Y国债: {len(out)} 条 ({min(out)} ~ {max(out)})')
    return out


def fetch_legulegu_week(offline=False):
    """乐咕乐股 周频 PE -> {date: 滚动市盈率}（用于口径对齐）"""
    name = 'lg_week'
    if offline or _cache_fresh(name):
        c = _load_cache(name)
        if c:
            log(f'  [缓存] 乐咕周频PE: {len(c)} 条')
            return c
    import requests
    import py_mini_racer
    import akshare.stock_feature.stock_a_pe_and_pb as mod
    js = py_mini_racer.MiniRacer()
    js.eval(mod.hash_code)
    token = js.call('hex', datetime.now().date().isoformat()).lower()
    url = 'https://legulegu.com/api/stockdata/index-basic-pe'
    kw = mod.get_cookie_csrf(url='https://legulegu.com/stockdata/sz50-ttm-lyr')
    r = requests.get(url, params={'token': token, 'indexCode': '000300.SH',
                                  'freq': 'week'}, timeout=30, **kw)
    data = r.json().get('data') or []
    out = {}
    for it in data:
        pe = it.get('addTtmPe')
        if pe:
            out[str(it['date'])[:10]] = round(float(pe), 4)
    _save_cache(name, out)
    log(f'  [抓取] 乐咕周频PE: {len(out)} 条 ({min(out)} ~ {max(out)})')
    return out


# ----------------------------------------------------------------------------
# 2. 读取现有 HTML 内嵌数组
# ----------------------------------------------------------------------------
def read_embedded(html):
    def grab(name, is_str=False):
        m = re.search(r'const\s+' + name + r'\s*=\s*\[(.*?)\]\s*;', html, re.DOTALL)
        if not m:
            raise SystemExit(f'!! HTML 中找不到 const {name}')
        raw = m.group(1)
        if is_str:
            return re.findall(r'"([^"]+)"', raw)
        return [float(x) for x in re.split(r'[,\s]+', raw.strip()) if x]
    return {
        'dates': grab('dates', True),
        'hsClose': grab('hsClose'),
        'peArr': grab('peArr'),
    }


def read_legacy_json():
    """daily_data.json 里有完整的日频 PE（乐咕口径），用于补内嵌数组缺失的尾部"""
    if not os.path.exists(DATA_JSON.replace('dashboard_data', 'daily_data')):
        return {}, {}
    with open(DATA_JSON.replace('dashboard_data', 'daily_data'), encoding='utf-8') as f:
        j = json.load(f)
    pe_by_date, close_by_date = {}, {}
    for it in j.get('pe_ttm', []):
        pe_by_date[it['date']] = it.get('pe_ttm')
        close_by_date[it['date']] = it.get('close')
    return pe_by_date, close_by_date


# ----------------------------------------------------------------------------
# 3. 构建统一对齐序列
# ----------------------------------------------------------------------------
def build_series(embedded, csi300, csiTR, y10, lg_week, legacy_pe):
    hist_dates = embedded['dates']
    hist_close = embedded['hsClose']
    emb_pe = embedded['peArr']
    n_hist = len(hist_dates)
    if len(hist_close) < n_hist:
        raise SystemExit('!! hsClose 比 dates 短，数据已损坏')

    # --- 3.1 校验：中证收盘 vs 内嵌收盘 ---
    diff = []
    for i, d in enumerate(hist_dates):
        if d in csi300:
            diff.append(abs(csi300[d]['close'] - hist_close[i]))
    if diff:
        log(f'  校验: 中证收盘 vs 内嵌收盘 最大偏差 {max(diff):.2f} 点（{len(diff)} 个共同交易日）')

    last_hist = hist_dates[-1]
    # --- 3.2 PE 口径对齐系数（乐咕/中证），按周插值 ---
    ratio_pts = []
    for d, pe in lg_week.items():
        if d in csi300 and csi300[d]['pe']:
            ratio_pts.append((d, pe / csi300[d]['pe']))
    ratio_pts.sort()
    if not ratio_pts:
        raise SystemExit('!! 无法计算 PE 口径对齐系数')

    def ratio_at(date):
        prev = None
        for d, r in ratio_pts:
            if d <= date:
                prev = (d, r)
            else:
                if prev is None:
                    return r
                (d0, r0) = prev
                span = (datetime.strptime(d, '%Y-%m-%d') - datetime.strptime(d0, '%Y-%m-%d')).days
                if span <= 0:
                    return r
                w = (datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(d0, '%Y-%m-%d')).days / span
                return r0 + (r - r0) * w
        return prev[1] if prev else 1.0

    win = [(d, r) for d, r in ratio_pts if d >= '2026-05-01']
    if win:
        log('  PE口径系数(乐咕/中证) 近月锚点: ' +
            ', '.join(f'{d[-5:]}:{r:.3f}' for d, r in win[:10]))
    if len(ratio_pts) > 3:
        old_r = [r for d, r in ratio_pts if d < '2015-01-01']
        mid_r = [r for d, r in ratio_pts if '2015-01-01' <= d < '2022-01-01']
        new_r = [r for d, r in ratio_pts if d >= '2022-01-01']
        for tag, v in (('2005-2014', old_r), ('2015-2021', mid_r), ('2022-2026', new_r)):
            if v:
                log(f'    系数区间 {tag}: {min(v):.4f}~{max(v):.4f} 均值 {sum(v)/len(v):.4f}')

    # --- 3.3 内嵌 PE 对齐到 dates（补齐尾部缺的几条）---
    hist_pe = []
    filled = 0
    for i, d in enumerate(hist_dates):
        v = emb_pe[i] if i < len(emb_pe) else None
        if v is None and d in legacy_pe and legacy_pe[d]:
            v = float(legacy_pe[d])
            filled += 1
        hist_pe.append(round(v, 2) if v is not None else None)
    if filled:
        log(f'  内嵌 PE 尾部补齐 {filled} 条（取自 daily_data.json）')

    # --- 3.4 扩展段 ---
    new_dates = sorted(d for d in csi300 if d > last_hist)
    log(f'  历史 {n_hist} 条（至 {last_hist}），新增 {len(new_dates)} 条交易日')

    dates = list(hist_dates)
    close = list(hist_close)
    pe = list(hist_pe)
    for d in new_dates:
        c = csi300[d]
        p = c['pe'] * ratio_at(d) if c['pe'] else None
        dates.append(d)
        close.append(c['close'])
        pe.append(round(p, 2) if p else None)

    # --- 3.4 全收益指数（真实 H00300，全历史覆盖）---
    tr = []
    last_tr = None
    for i, d in enumerate(dates):
        if i >= n_hist:
            # 新增段：优先用 H00300 实际值，缺失用价格推算
            if d in csiTR:
                last_tr = csiTR[d]['close']
            elif last_tr is not None:
                last_tr = round(last_tr * (close[i] / close[i - 1]) * (1 + DIV_YIELD_ANNUAL / 250), 2)
        elif d in csiTR:
            last_tr = csiTR[d]['close']
        tr.append(round(last_tr, 2) if last_tr else None)
    # 头部若缺失，用价格/1000*基准回填
    if tr[0] is None:
        base = close[0]
        tr = [round(c / base * 1003.45, 2) if t is None else t for c, t in zip(close, tr)]

    # --- 3.5 10Y 国债（对齐 dates，缺失沿用前一交易日）---
    bond = []
    last_y = None
    for d in dates:
        if d in y10:
            last_y = y10[d]
        bond.append(last_y)

    # --- 3.6 ERP ---
    erp = []
    for i in range(len(dates)):
        if pe[i] is None or bond[i] is None:
            erp.append(None)
        else:
            erp.append(round(100.0 / pe[i] - bond[i], 4))

    return dates, close, tr, pe, bond, erp


# ----------------------------------------------------------------------------
# 4. 写回 HTML
# ----------------------------------------------------------------------------
def js_num(v):
    if v is None:
        return 'null'
    if isinstance(v, float):
        s = f'{v:.4f}'.rstrip('0').rstrip('.')
        return s if s else '0'
    return str(v)


def js_float(v, nd=2):
    return 'null' if v is None else f'{v:.{nd}f}'


def build_data_block(dates, close, tr, pe, bond, erp, mean, std):
    parts = ['// ===== DATA =====',
             '// 沪深300价格/PE：2005~2011 乐咕乐股口径；2011-06-28 起中证指数官网滚动市盈率(按乐咕口径对齐)',
             '// 全收益：中证指数官网 沪深300全收益指数 H00300（真实全收益，非估算）',
             '// 10Y国债：中债登（2005 起，与中债国债收益率曲线10年期一致）',
             'const dates = [' + ', '.join(f'"{d}"' for d in dates) + '];',
             'const hsClose = [' + ', '.join(js_num(v) for v in close) + '];',
             'const hsTR = [' + ', '.join(js_num(v) for v in tr) + '];',
             'const peArr = [' + ', '.join(js_num(v) for v in pe) + '];',
             'const bondArr = [' + ', '.join(js_num(v) for v in bond) + '];',
             'const erpArr = [' + ', '.join(js_num(v) for v in erp) + '];',
             f'const ERP_MEAN={mean};',
             f'const ERP_STD={std};',
             f'const UPDATE_DATE="{dates[-1]}";',
             '']
    return '\n'.join(parts)


ECHARTS_URLS = [
    'https://unpkg.com/echarts@5.4.3/dist/echarts.min.js',
    'https://registry.npmmirror.com/echarts/5.4.3/files/dist/echarts.min.js',
    'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js',
]
CDN_TAG = '<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'


def ensure_echarts():
    """确保本地有 echarts.min.js（内嵌进 HTML，使看板离线可用）"""
    p = os.path.join(CACHE, 'echarts.min.js')
    if os.path.exists(p) and os.path.getsize(p) > 500000:
        return p
    import urllib.request
    for u in ECHARTS_URLS:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) > 500000:
                with open(p, 'wb') as f:
                    f.write(data)
                log(f'  [抓取] echarts.min.js {len(data) // 1024}KB')
                return p
        except Exception as e:
            log(f'  echarts 下载失败 {u}: {e}')
    return None


def patch_html(html, block, st, note):
    # 4.1 DATA 段整体替换
    a = html.index('// ===== DATA =====')
    b = html.index('// ===== ROTATE =====')
    html = html[:a] + block + '\n' + html[b:]

    # 4.2 顶部指标条
    def setstat(idname, text):
        nonlocal html
        if f'id="{idname}"' not in html:
            log(f'  ⚠ 未找到指标 {idname}')
            return
        html = re.sub(r'(id="' + idname + r'">)[^<]*(</span>)',
                      lambda m: m.group(1) + text + m.group(2), html, count=1)

    setstat('v-erp', f'{st["erp"]:.2f}%')
    setstat('v-avg', f'{st["mean"]:.2f}%')
    setstat('v-std', f'{st["std"]:.2f}%')
    setstat('v-pct', f'{st["pct"]} 分位')
    setstat('v-sig', '—')
    setstat('v-pe', f'{st["pe"]:.1f}x')
    setstat('v-bond', f'{st["bond"]:.3f}%')
    setstat('v-hs', f'{st["hs"]:.0f}')
    setstat('v-tr', f'{st["tr"]:.0f}')
    setstat('v-ratio', f'{st["ratio"]:.2f}')

    # 4.3 页脚数据说明
    html = re.sub(r'(<div class="ft">💡 数据</div><div class="fx">).*?(</div>)',
                  lambda m: m.group(1) + note + m.group(2), html, count=1, flags=re.DOTALL)

    # 4.4 副标题年份
    html = re.sub(r'(ERP = 1/PE − 国债 · )\d{4}~\d{4}', lambda m: m.group(1) + f'{st["first_year"]}~{st["last_year"]}', html, count=1)

    # 4.5 ERP 折线着色对 null 容错
    html = html.replace("itemStyle:{color:function(p){return erpColor(erpArr[p.dataIndex]);}}",
                        "itemStyle:{color:function(p){var v=erpArr[p.dataIndex];return v==null?'#6e7681':erpColor(v);}}")
    # 4.6 内嵌 echarts（去 CDN 依赖，离线可用）
    if CDN_TAG in html:
        ep = ensure_echarts()
        if ep:
            with open(ep, encoding='utf-8') as f:
                ejs = f.read()
            if '</script' not in ejs:
                html = html.replace(CDN_TAG, '<script>\n' + ejs + '\n</script>', 1)
                log('  echarts 已内嵌，看板完全离线可用')
            else:
                log('  ⚠ echarts 源码含 </script>，跳过内嵌')
    return html


LIVE_JS = r'''// ===== LIVE DATA =====
async function fetchTO(url,ms){
  try{
    const c=new AbortController();
    setTimeout(()=>c.abort(),ms);
    const r=await fetch(url,{signal:c.signal,cache:'no-store',mode:'cors'});
    return r;
  }catch(e){return null;}
}

// 把内嵌序列补齐到最新收盘（浏览器能联网时自动生效）
function extendToLatest(kline){
  if(!kline||!kline.length)return 0;
  const embLast=dates[dates.length-1];
  const prevBond=bondArr[bondArr.length-1];
  const ddr=0.030/250;
  let added=0;
  // 1) 同一交易日：刷新收盘价
  const same=kline.filter(k=>k.date===embLast);
  if(same.length){
    const c=+same[0].close;
    if(isFinite(c)&&c>0&&Math.abs(c-hsClose[hsClose.length-1])>0.005){
      hsClose[hsClose.length-1]=c;
    }
  }
  // 2) 新交易日：追加
  const news=kline.filter(k=>k.date>embLast);
  for(const k of news){
    const c=+k.close; if(!isFinite(c)||c<=0)continue;
    const pc=hsClose[hsClose.length-1], pt=hsTR[hsTR.length-1];
    let pp=null; for(let i=peArr.length-1;i>=0;i--){if(peArr[i]!=null){pp=peArr[i];break;}}
    const r=c/pc-1;
    const tr=pt*(1+r+ddr);
    const pe=pp!=null?pp*(c/pc):null;
    dates.push(k.date); hsClose.push(+c.toFixed(2)); hsTR.push(+tr.toFixed(2));
    peArr.push(pe!=null?+pe.toFixed(2):null);
    bondArr.push(prevBond);
    erpArr.push((pe!=null&&prevBond!=null)?+(100/pe-prevBond).toFixed(4):null);
    added++;
  }
  return added;
}

async function doRefresh(){
  const btn=document.getElementById('rbtn'),ico=document.getElementById('ricon');
  if(btn){btn.classList.add('loading');btn.disabled=true;}
  if(ico)ico.textContent='⏳';
  let ok=0,added=0;
  try{
    // 沪深300 近 120 交易日
    let r=await fetchTO('https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000300,day,,,120,qfq',8000);
    if(r&&r.ok){
      try{
        const j=await r.json();
        const k=(j.data&&j.data.sh000300&&(j.data.sh000300.day||j.data.sh000300.qfqday))||[];
        if(k.length){
          const kl=k.map(x=>({date:String(x[0]).slice(0,10),close:x[2]}));
          added=extendToLatest(kl);
          const lst=kl[kl.length-1];
          const ehs=document.getElementById('v-hs'); if(ehs)ehs.textContent=(+lst.close).toFixed(0);
          const etr=document.getElementById('v-tr');
          if(etr)etr.textContent=hsTR[hsTR.length-1].toFixed(0);
          const er=document.getElementById('v-ratio');
          if(er)er.textContent=(hsTR[hsTR.length-1]/hsClose[hsClose.length-1]).toFixed(2);
          const ee=document.getElementById('v-erp');
          const cur=erpArr[erpArr.length-1];
          if(ee&&cur!=null)ee.textContent=cur.toFixed(2)+'%';
          ok++;
        }
      }catch(e){}
    }
    // 10Y 国债（新浪）
    r=await fetchTO('https://hq.sinajs.cn/list=CNY10YR',5000);
    if(r&&r.ok){
      try{
        const t=await r.text();
        const m=t.match(/"([^"]+)"/);
        if(m){
          const p=m[1].split(',');
          if(p[0]&&!isNaN(+p[0])){
            const y=+p[0];
            const eb=document.getElementById('v-bond');
            if(eb)eb.textContent=y.toFixed(3)+'%';
            bondArr[bondArr.length-1]=+y.toFixed(4);
            const lastPe=peArr[peArr.length-1];
            if(lastPe!=null)erpArr[erpArr.length-1]=+(100/lastPe-y).toFixed(4);
            ok++;
          }
        }
      }catch(e){}
    }
    if(ok>0){
      const d=document.getElementById('dot'); if(d)d.classList.remove('off');
      const n=new Date();
      const u=document.getElementById('utime');
      if(u)u.textContent=n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0');
      render();chart.resize();
      toast('已更新至 '+dates[dates.length-1]+(added?'（新增'+added+'个交易日）':''));
    }else{
      const u=document.getElementById('utime'); if(u)u.textContent='离线';
      toast('实时接口不可用，显示内嵌数据（至 '+dates[dates.length-1]+'）');
    }
  }catch(e){toast('网络错误');}
  if(btn){btn.classList.remove('loading');btn.disabled=false;}
  if(ico)ico.textContent='⟳';
}

'''


def patch_live_js(html):
    a = html.index('// ===== LIVE DATA =====')
    b = html.index('function toast(m)')
    return html[:a] + LIVE_JS + html[b:]


# ----------------------------------------------------------------------------
# 5. main
# ----------------------------------------------------------------------------
def main():
    offline = '--offline' in sys.argv
    t0 = time.time()
    log('=' * 62)
    log(f'股债收益比看板 · 数据更新  {datetime.now():%Y-%m-%d %H:%M:%S}'
        + ('  [离线模式]' if offline else ''))

    with open(HTML, encoding='utf-8') as f:
        html = f.read()

    log('[1/5] 读取内嵌历史数据...')
    embedded = read_embedded(html)
    legacy_pe, _ = read_legacy_json()
    log(f'  dates={len(embedded["dates"])} hsClose={len(embedded["hsClose"])} pe={len(embedded["peArr"])}'
        f'  备用日频PE={len(legacy_pe)} 条')

    log('[2/5] 抓取数据源...')
    csi300 = fetch_csi('000300', offline)
    csiTR = fetch_csi('H00300', offline)
    y10 = fetch_y10(offline)
    lg_week = fetch_legulegu_week(offline)

    log('[3/5] 构建对齐序列...')
    dates, close, tr, pe, bond, erp = build_series(embedded, csi300, csiTR, y10, lg_week, legacy_pe)
    valid = [v for v in erp if v is not None]
    mean = round(sum(valid) / len(valid), 2)
    std = round((sum((v - mean) ** 2 for v in valid) / len(valid)) ** 0.5, 2)
    cur = valid[-1]
    pct = round(sum(1 for v in valid if v <= cur) / len(valid) * 100)
    st = {
        'erp': cur, 'mean': mean, 'std': std, 'pct': pct,
        'pe': pe[-1], 'bond': bond[-1], 'hs': close[-1], 'tr': tr[-1],
        'ratio': tr[-1] / close[-1],
        'first_year': dates[0][:4], 'last_year': dates[-1][:4],
    }
    log(f'  最终序列 {len(dates)} 条   {dates[0]} ~ {dates[-1]}')
    log(f'  沪深300 {close[-1]:.2f} | 全收益 {tr[-1]:.2f} (TR/P={st["ratio"]:.3f})')
    log(f'  PE(TTM) {pe[-1]:.2f}x | 10Y国债 {bond[-1]:.3f}% | ERP {cur:.2f}%')
    log(f'  ERP 均值 {mean}% σ {std}% 当前分位 {pct}')

    log('[4/5] 写回 HTML...')
    note = ('日频 · 沪深300 与 全收益指数：中证指数官网(000300 / H00300，全收益为指数真实值)<br>'
            'PE(TTM)：整体法滚动市盈率(乐咕乐股口径) · 10Y国债：中债登<br>'
            f'数据截至 <b>{dates[-1]}</b>')
    html = patch_html(html, build_data_block(dates, close, tr, pe, bond, erp, mean, std), st, note)
    html = patch_live_js(html)
    with open(HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    log('[5/5] 写 dashboard_data.json...')
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'series': [{'date': dates[i], 'close': close[i], 'tr': tr[i], 'pe': pe[i],
                        'bond': bond[i], 'erp': erp[i]} for i in range(len(dates))],
            'stats': st,
            'meta': {'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     'source': '中证指数官网 000300/H00300 + 中债登10Y + 乐咕乐股',
                     'n': len(dates)},
        }, f, ensure_ascii=False)

    log(f'完成，用时 {time.time() - t0:.1f}s  →  {HTML}')


if __name__ == '__main__':
    main()
