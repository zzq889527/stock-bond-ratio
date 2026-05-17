import { useState, useEffect } from 'react';
import * as echarts from 'echarts';
import { MetricCard, SignalCard } from '../components/MetricCard';
import { ERPChart } from '../components/ERPChart';
import { PEChart } from '../components/PEChart';
import { PBChart } from '../components/PBChart';
import { DividendYieldChart } from '../components/DividendYieldChart';
import { IndexSelector } from '../components/IndexSelector';
import { getERPData, ERPDataItem, getLiveDateInfo } from '../data/erpData';
import { getIndexConfig } from '../data/indexConfig';

export default function Home() {
  const [data, setData] = useState<ERPDataItem[]>([]);
  const [selectedIndexId, setSelectedIndexId] = useState<string>('hs300');
  const [latest, setLatest] = useState<ERPDataItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [liveDateInfo, setLiveDateInfo] = useState('');
  const [isLandscape, setIsLandscape] = useState(false);

  const toggleLandscape = () => {
    setIsLandscape(!isLandscape);
  };

  async function loadData(indexId: string = 'hs300') {
    setLoading(true);
    try {
      const erpData = await getERPData(indexId, false);
      setData(erpData);
      setLatest(erpData[erpData.length - 1]);
      setLiveDateInfo(getLiveDateInfo(indexId));
      setLastUpdate(new Date().toLocaleString('zh-CN'));
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData(selectedIndexId);
  }, [selectedIndexId]);

  useEffect(() => {
    echarts.connect('valuationGroup');
  }, []);

  useEffect(() => {
    const mql = window.matchMedia('(orientation: landscape)');
    const handler = (e: MediaQueryListEvent | MediaQueryList) => {
      if (e.matches && window.innerWidth < 768) {
        setIsLandscape(true);
      } else if (!e.matches && window.innerWidth < 768) {
        setIsLandscape(false);
      }
    };
    handler(mql);
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, []);

  const handleIndexChange = (indexId: string) => {
    setSelectedIndexId(indexId);
  };

  const displayData = latest;
  const config = getIndexConfig(selectedIndexId);

  return (
    <div className={`bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white relative min-h-screen ${isLandscape ? 'landscape-mode' : ''}`}>
      {isLandscape && (
        <div className="landscape-overlay">
          <header className="landscape-header">
            <div className="flex items-center gap-2">
              <button onClick={toggleLandscape} className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 transition-all" title="退出横屏">
                <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <span className="text-xs font-medium text-slate-300 bg-slate-800/60 px-2 py-1 rounded border border-slate-700/40">
                {config.name}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-cyan-400 font-medium">ERP <span className="text-white">{displayData?.erp.toFixed(2)}%</span></span>
              <span className="text-slate-600">|</span>
              <span className="text-cyan-400">PE <span className="text-white">{displayData?.pe_ttm.toFixed(1)}x</span></span>
              <span className="text-slate-600">|</span>
              <span className="text-amber-400">PB <span className="text-white">{displayData?.pb.toFixed(2)}x</span></span>
              <span className="text-slate-600">|</span>
              <span className="text-emerald-400">DY <span className="text-white">{displayData?.dividend_yield.toFixed(2)}%</span></span>
            </div>
          </header>
          <main className="landscape-grid">
            <div className="chart-cell">
              {loading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-slate-700 border-t-cyan-400 rounded-full animate-spin" />
                </div>
              ) : (
                <ERPChart data={data} indexId={selectedIndexId} isLandscape={true} />
              )}
            </div>
            <div className="chart-cell">
              {loading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-slate-700 border-t-cyan-400 rounded-full animate-spin" />
                </div>
              ) : (
                <PEChart data={data} indexId={selectedIndexId} isLandscape={true} />
              )}
            </div>
            <div className="chart-cell">
              {loading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-slate-700 border-t-amber-400 rounded-full animate-spin" />
                </div>
              ) : (
                <PBChart data={data} indexId={selectedIndexId} isLandscape={true} />
              )}
            </div>
            <div className="chart-cell">
              {loading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="w-6 h-6 border-2 border-slate-700 border-t-emerald-400 rounded-full animate-spin" />
                </div>
              ) : (
                <DividendYieldChart data={data} indexId={selectedIndexId} isLandscape={true} />
              )}
            </div>
          </main>
        </div>
      )}

      {!isLandscape && (
        <>
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
          </div>
          <header className="relative backdrop-blur-sm bg-slate-900/50 border-b border-slate-700/30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-xl blur opacity-75" />
                    <div className="relative w-12 h-12 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M3 3v18h18M7 16l4-4 4 4 6-8" />
                      </svg>
                    </div>
                  </div>
                  <div>
                    <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">股债收益比 · 日频</h1>
                    <p className="text-xs sm:text-sm text-slate-400">ERP = 1/PE - 10Y国债 · 2005-2026</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={toggleLandscape} className="p-2 rounded-full bg-slate-800/80 hover:bg-slate-700/80 transition-all duration-300 shadow-lg backdrop-blur-sm" title="横屏模式">
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <button
                    onClick={() => loadData(selectedIndexId)}
                    className="p-2 rounded-full bg-slate-800/80 hover:bg-slate-700/80 transition-all duration-300 shadow-lg backdrop-blur-sm"
                    title="刷新数据"
                  >
                    <svg className={`w-4 h-4 text-slate-400 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357Fit" />
                    </svg>
                  </button>
                  <div className="text-right hidden sm:block">
                    <div className="text-xs text-slate-400">{loading ? '获取中...' : liveDateInfo}</div>
                    <div className="text-[10px] text-slate-500">{loading ? '' : `共 ${data.length.toLocaleString()} 个数据点`}</div>
                  </div>
                </div>
              </div>
            </div>
          </header>
          <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* 指数选择器 */}
            <div className="mb-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 p-4 sm:p-6 shadow-xl shadow-black/20">
              <IndexSelector 
                selectedIndexId={selectedIndexId} 
                onIndexChange={handleIndexChange} 
              />
            </div>

            {/* 主要指标卡片 */}
            <div className="mb-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 p-4 sm:p-6 shadow-xl shadow-black/20">
              {displayData && (
                <div className="mb-6">
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-baseline gap-3">
                        <span className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                          {displayData.erp.toFixed(2)}%
                        </span>
                        <SignalCard signal={displayData.signal} />
                      </div>
                      <p className="text-slate-400 mt-1 text-sm">股权风险溢价 ERP</p>
                    </div>
                    <div className="text-right hidden sm:block">
                      <div className="text-2xl font-semibold text-slate-200">{displayData.percentile}分位</div>
                      <p className="text-xs text-slate-400">历史百分位</p>
                    </div>
                  </div>
                </div>
              )}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 sm:gap-4">
                <MetricCard label="均值" value={displayData?.mean.toFixed(2) || '--'} color="#10b981" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 12h4l3 9 6-18 3 9h4" /></svg>} />
                <MetricCard label="标准差" value={displayData?.sigma.toFixed(2) || '--'} color="#f59e0b" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>} />
                <MetricCard label="PE(TTM)" value={displayData?.pe_ttm.toFixed(1) || '--'} color="#06b6d4" suffix="x" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} />
                <MetricCard label="PB" value={displayData?.pb.toFixed(2) || '--'} color="#f59e0b" suffix="x" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} />
                <MetricCard label="股息率" value={displayData?.dividend_yield.toFixed(2) || '--'} color="#10b981" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} />
                <MetricCard label="10Y国债" value={displayData?.bond_10y.toFixed(2) || '--'} color="#8b5cf6" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6l9-3 9 3v12l-9 3-9-3V6z" /></svg>} />
                <MetricCard label={config.displayName} value={displayData?.index_value.toLocaleString() || '--'} color={config.color} icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg>} />
              </div>
            </div>

            {/* 图表区域 */}
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 overflow-hidden shadow-xl shadow-black/20 mb-4">
              {loading ? (
                <div className="h-[400px] sm:h-[500px] flex items-center justify-center">
                  <div className="text-center">
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full blur-xl opacity-50 animate-pulse" />
                      <div className="relative w-16 h-16 border-4 border-slate-700 border-t-cyan-400 rounded-full animate-spin mx-auto mb-4" />
                    </div>
                    <p className="text-slate-400">正在加载市场数据...</p>
                  </div>
                </div>
              ) : (
                <div className="h-[400px] sm:h-[500px]">
                  <ERPChart data={data} indexId={selectedIndexId} />
                </div>
              )}
            </div>

            {/* 估值指标图表区域 */}
            <div className="space-y-4">
              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 overflow-hidden shadow-xl shadow-black/20">
                <div className="px-4 pt-3 pb-0 flex items-center gap-2 border-b border-slate-700/20">
                  <div className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span className="text-xs font-semibold text-slate-300">市盈率 PE(TTM)</span>
                </div>
                {loading ? (
                  <div className="h-[220px] flex items-center justify-center">
                    <div className="w-8 h-8 border-3 border-slate-700 border-t-cyan-400 rounded-full animate-spin" />
                  </div>
                ) : (
                  <div className="h-[220px]">
                    <PEChart data={data} indexId={selectedIndexId} />
                  </div>
                )}
              </div>

              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 overflow-hidden shadow-xl shadow-black/20">
                <div className="px-4 pt-3 pb-0 flex items-center gap-2 border-b border-slate-700/20">
                  <div className="w-2 h-2 rounded-full bg-amber-400" />
                  <span className="text-xs font-semibold text-slate-300">市净率 PB</span>
                </div>
                {loading ? (
                  <div className="h-[220px] flex items-center justify-center">
                    <div className="w-8 h-8 border-3 border-slate-700 border-t-amber-400 rounded-full animate-spin" />
                  </div>
                ) : (
                  <div className="h-[220px]">
                    <PBChart data={data} indexId={selectedIndexId} />
                  </div>
                )}
              </div>

              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 overflow-hidden shadow-xl shadow-black/20">
                <div className="px-4 pt-3 pb-0 flex items-center gap-2 border-b border-slate-700/20">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="text-xs font-semibold text-slate-300">股息率 Dividend Yield</span>
                </div>
                {loading ? (
                  <div className="h-[220px] flex items-center justify-center">
                    <div className="w-8 h-8 border-3 border-slate-700 border-t-emerald-400 rounded-full animate-spin" />
                  </div>
                ) : (
                  <div className="h-[220px]">
                    <DividendYieldChart data={data} indexId={selectedIndexId} />
                  </div>
                )}
              </div>
            </div>

            {/* 信号规则说明 */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full animate-pulse" />
                  <span className="text-sm font-semibold text-slate-200">指标说明</span>
                </div>
                <p className="text-sm text-slate-400 mb-2">
                  <span className="text-cyan-400 font-medium">ERP↑</span> = 股票相对债券更便宜
                </p>
                <p className="text-sm text-slate-400">
                  <span className="text-pink-400 font-medium">ERP↓</span> = 股票相对债券更昂贵
                </p>
              </div>
              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full" />
                  <span className="text-sm font-semibold text-slate-200">信号规则</span>
                </div>
                <div className="space-y-1.5 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded">极度低估</span>
                    <span className="text-slate-500">&gt; 均值+1σ</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded">低估</span>
                    <span className="text-slate-500">均值+0.5σ ~ 均值+1σ</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">均衡</span>
                    <span className="text-slate-500">均值±0.5σ</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-orange-500/20 text-orange-400 rounded">高估</span>
                    <span className="text-slate-500">均值-0.5σ ~ 均值-1σ</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 bg-red-600/30 text-red-300 rounded">极度高估</span>
                    <span className="text-slate-500">&lt; 均值-1σ</span>
                  </div>
                </div>
              </div>
              <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-5">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2 h-2 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full" />
                  <span className="text-sm font-semibold text-slate-200">数据来源</span>
                </div>
                <p className="text-xs text-slate-400 mb-1">📊 PE数据: 乐咕乐股</p>
                <p className="text-xs text-slate-400 mb-1">📈 国债数据: 中债登</p>
                <p className="text-xs text-slate-500 mt-2">共 {data.length.toLocaleString()} 个数据点</p>
              </div>
            </div>
          </main>
          <footer className="relative text-center py-6 text-xs text-slate-500">
            <p>数据每日自动更新 · 基于真实历史数据</p>
          </footer>
        </>
      )}
      
      <style>{`
        .landscape-mode {
          position: fixed;
          inset: 0;
          z-index: 9999;
          background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e1b4b 100%);
        }
        
        .landscape-overlay {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        
        .landscape-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 6px 12px;
          background: rgba(15, 23, 42, 0.95);
          border-bottom: 1px solid rgba(100, 116, 139, 0.3);
          flex-shrink: 0;
          gap: 8px;
          min-height: 40px;
        }
        
        .landscape-grid {
          flex: 1;
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: 1fr 1fr;
          gap: 3px;
          padding: 3px;
          overflow: hidden;
        }
        
        .chart-cell {
          background: rgba(30, 41, 59, 0.4);
          border-radius: 8px;
          border: 1px solid rgba(100, 116, 139, 0.2);
          overflow: hidden;
          min-height: 0;
        }
      `}</style>
    </div>
  );
}
