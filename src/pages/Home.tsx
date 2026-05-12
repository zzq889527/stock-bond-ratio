
import { useState, useEffect } from 'react';
import { MetricCard, SignalCard } from '../components/MetricCard';
import { ERPChart } from '../components/ERPChart';
import { getERPData, ERPDataItem } from '../data/erpData';

export default function Home() {
  const [data, setData] = useState<ERPDataItem[]>([]);
  const [latest, setLatest] = useState<ERPDataItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState('');

  async function loadData(refresh = false) {
    setLoading(true);
    try {
      const erpData = await getERPData(refresh);
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

  const handleRefresh = () => {
    loadData(true);
  };

  const displayData = latest;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white relative overflow-hidden">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      {/* Header */}
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
                <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                  股债收益比 · 日频
                </h1>
                <p className="text-xs sm:text-sm text-slate-400">ERP = 1/PE - 10Y国债 · 2005~2026</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs sm:text-sm text-slate-400 hidden sm:block">
                {loading ? '获取中...' : lastUpdate}
              </span>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="group relative px-4 py-2 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 rounded-xl text-sm font-medium transition-all border border-cyan-500/30 hover:border-cyan-400/50 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyan-500/10"
              >
                <span className="flex items-center gap-2">
                  <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span className="hidden sm:inline">刷新</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 指标卡片区 */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 p-4 sm:p-6 mb-6 shadow-xl shadow-black/20">
          {/* 主要指标 - ERP */}
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

          {/* 次要指标网格 */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
            <MetricCard 
              label="均值" 
              value={displayData?.mean.toFixed(2) || '--'} 
              color="#10b981" 
              suffix="%"
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M2 12h4l3 9 6-18 3 9h4" />
                </svg>
              }
            />
            <MetricCard 
              label="标准差" 
              value={displayData?.sigma.toFixed(2) || '--'} 
              color="#f59e0b" 
              suffix="%"
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              }
            />
            <MetricCard 
              label="PE(TTM)" 
              value={displayData?.pe_ttm.toFixed(1) || '--'} 
              color="#06b6d4" 
              suffix="x"
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
            <MetricCard 
              label="10Y国债" 
              value={displayData?.bond_10y.toFixed(2) || '--'} 
              color="#8b5cf6" 
              suffix="%"
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 6l9-3 9 3v12l-9 3-9-3V6z" />
                </svg>
              }
            />
            <MetricCard 
              label="沪深300" 
              value={displayData?.hs300.toLocaleString() || '--'} 
              color="#ec4899" 
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
              }
            />
            <MetricCard 
              label="全收益" 
              value={displayData?.total_return.toFixed(1) || '--'} 
              color="#f97316" 
              icon={
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              }
            />
          </div>
        </div>

        {/* 图表区域 */}
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-2xl border border-slate-700/30 overflow-hidden shadow-xl shadow-black/20">
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
            <ERPChart data={data} />
          )}
        </div>

        {/* 底部信息区 */}
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
            <p className="text-xs text-slate-500 mt-2">
              共 {data.length.toLocaleString()} 个数据点
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative text-center py-6 text-xs text-slate-500">
        <p>数据每日自动更新 · 基于真实历史数据</p>
      </footer>
    </div>
  );
}
