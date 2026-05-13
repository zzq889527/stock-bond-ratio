
import { useState, useEffect } from 'react';
import { MetricCard, SignalCard } from '../components/MetricCard';
import { ERPChart } from '../components/ERPChart';
import { getERPData, ERPDataItem } from '../data/erpData';

export default function Home() {
  const [data, setData] = useState<ERPDataItem[]>([]);
  const [latest, setLatest] = useState<ERPDataItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');
  const [isLandscape, setIsLandscape] = useState(false);

  const toggleLandscape = () => {
    setIsLandscape(!isLandscape);
  };

  async function loadData() {
    setLoading(true);
    try {
      const erpData = await getERPData(false);
      setData(erpData);
      setLatest(erpData[erpData.length - 1]);
      setLastUpdate(new Date().toLocaleString('zh-CN'));
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const displayData = latest;

  const PortraitView = () => (
    <>
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

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          <MetricCard label="均值" value={displayData?.mean.toFixed(2) || '--'} color="#10b981" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 12h4l3 9 6-18 3 9h4" /></svg>} />
          <MetricCard label="标准差" value={displayData?.sigma.toFixed(2) || '--'} color="#f59e0b" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2" /></svg>} />
          <MetricCard label="PE(TTM)" value={displayData?.pe_ttm.toFixed(1) || '--'} color="#06b6d4" suffix="x" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} />
          <MetricCard label="10Y国债" value={displayData?.bond_10y.toFixed(2) || '--'} color="#8b5cf6" suffix="%" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6l9-3 9 3v12l-9 3-9-3V6z" /></svg>} />
          <MetricCard label="沪深300" value={displayData?.hs300.toLocaleString() || '--'} color="#ec4899" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg>} />
          <MetricCard label="全收益" value={displayData?.total_return.toFixed(1) || '--'} color="#f97316" icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>} />
        </div>
      </div>

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
            <ERPChart data={data} />
          </div>
        )}
      </div>

      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-4 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 bg-gradient-to-r from-emerald-400 to-red-400 rounded-full" />
          <span className="text-sm font-semibold text-slate-200">底部柱状图说明</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-8 bg-gradient-to-t from-emerald-600 to-emerald-400 rounded opacity-80" />
            <div>
              <p className="text-sm font-medium text-emerald-400">🟢 ERP 高于均值</p>
              <p className="text-xs text-slate-400">股票相对便宜，考虑配置股票</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-8 bg-gradient-to-t from-red-600 to-red-400 rounded opacity-80" />
            <div>
              <p className="text-sm font-medium text-red-400">🔴 ERP 低于均值</p>
              <p className="text-xs text-slate-400">股票相对较贵，考虑配置债券</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
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
              <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 rounded">低估</span>
              <span className="text-slate-500">&gt; 均值</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">均衡</span>
              <span className="text-slate-500">≈ 均值</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded">高估</span>
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
    </>
  );

  const LandscapeView = () => (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between bg-gradient-to-r from-slate-800/80 to-slate-900/80 backdrop-blur-sm rounded-xl border border-slate-700/30 p-2">
        <div className="flex items-center gap-3">
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                {displayData?.erp.toFixed(2)}%
              </span>
              {displayData && <SignalCard signal={displayData.signal} />}
            </div>
            <p className="text-slate-400 text-xs">ERP</p>
          </div>
          <div className="h-6 w-px bg-slate-700/50" />
          <div className="flex gap-3 text-xs">
            <div>
              <span className="text-slate-500">均值</span>
              <p className="font-semibold text-emerald-400">{displayData?.mean.toFixed(2)}%</p>
            </div>
            <div>
              <span className="text-slate-500">标准差</span>
              <p className="font-semibold text-amber-400">{displayData?.sigma.toFixed(2)}%</p>
            </div>
            <div>
              <span className="text-slate-500">PE</span>
              <p className="font-semibold text-cyan-400">{displayData?.pe_ttm.toFixed(1)}x</p>
            </div>
            <div>
              <span className="text-slate-500">国债</span>
              <p className="font-semibold text-violet-400">{displayData?.bond_10y.toFixed(2)}%</p>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-slate-200">{displayData?.percentile}分位</div>
          <p className="text-xs text-slate-400">历史百分位</p>
        </div>
      </div>

      <div className="flex-1 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 overflow-hidden shadow-xl shadow-black/20">
        {loading ? (
          <div className="h-[500px] flex items-center justify-center">
            <div className="text-center">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full blur-xl opacity-50 animate-pulse" />
                <div className="relative w-12 h-12 border-4 border-slate-700 border-t-cyan-400 rounded-full animate-spin mx-auto mb-3" />
              </div>
              <p className="text-slate-400 text-sm">加载中...</p>
            </div>
          </div>
        ) : (
          <div className="h-[500px]">
            <ERPChart data={data} isLandscape={true} />
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1.5 h-1.5 bg-gradient-to-r from-emerald-400 to-red-400 rounded-full" />
            <span className="text-xs font-semibold text-slate-200">柱状图说明</span>
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="w-4 h-3 bg-gradient-to-t from-emerald-600 to-emerald-400 rounded opacity-80" />
              <div>
                <p className="text-[10px] font-medium text-emerald-400">高于均值</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-3 bg-gradient-to-t from-red-600 to-red-400 rounded opacity-80" />
              <div>
                <p className="text-[10px] font-medium text-red-400">低于均值</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1.5 h-1.5 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full" />
            <span className="text-xs font-semibold text-slate-200">信号规则</span>
          </div>
          <div className="grid grid-cols-2 gap-1">
            <span className="px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded text-[10px]">极度低估</span>
            <span className="px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded text-[10px]">低估</span>
            <span className="px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded text-[10px]">均衡</span>
            <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px]">高估</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/30 p-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1.5 h-1.5 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full" />
            <span className="text-xs font-semibold text-slate-200">数据来源</span>
          </div>
          <p className="text-[10px] text-slate-400">📊 PE: 乐咕乐股</p>
          <p className="text-[10px] text-slate-400">📈 国债: 中债登</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white relative overflow-hidden min-h-screen">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      {isLandscape ? (
        <>
          <header className="relative backdrop-blur-sm bg-slate-900/50 border-b border-slate-700/30">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-xl blur opacity-75" />
                    <div className="relative w-10 h-10 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg">
                      <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M3 3v18h18M7 16l4-4 4 4 6-8" />
                      </svg>
                    </div>
                  </div>
                  <div>
                    <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">股债收益比 · 日频</h1>
                    <p className="text-xs text-slate-400">ERP = 1/PE - 10Y国债 · 2005~2026</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={toggleLandscape} className="p-2 rounded-full bg-slate-800/80 hover:bg-slate-700/80 transition-all duration-300 shadow-lg backdrop-blur-sm" title="退出横屏">
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <span className="text-xs text-slate-400">{loading ? '获取中...' : lastUpdate}</span>
                </div>
              </div>
            </div>
          </header>
          <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <LandscapeView />
          </main>
        </>
      ) : (
        <>
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
                    <p className="text-xs sm:text-sm text-slate-400">ERP = 1/PE - 10Y国债 · 2005~2026</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={toggleLandscape} className="p-2 rounded-full bg-slate-800/80 hover:bg-slate-700/80 transition-all duration-300 shadow-lg backdrop-blur-sm" title="横屏模式">
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <span className="text-xs sm:text-sm text-slate-400 hidden sm:block">{loading ? '获取中...' : lastUpdate}</span>
                </div>
              </div>
            </div>
          </header>
          <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <PortraitView />
          </main>
          <footer className="relative text-center py-6 text-xs text-slate-500">
            <p>数据每日自动更新 · 基于真实历史数据</p>
          </footer>
        </>
      )}
    </div>
  );
}
