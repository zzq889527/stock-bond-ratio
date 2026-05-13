import { ReactNode } from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  color: string;
  suffix?: string;
  icon?: ReactNode;
}

export function MetricCard({ label, value, color, suffix = '', icon }: MetricCardProps) {
  return (
    <div className="group relative bg-slate-800/30 hover:bg-slate-700/40 rounded-xl p-3 transition-all duration-300 border border-slate-700/20 hover:border-slate-600/40 hover:shadow-lg hover:shadow-black/20">
      <div className="flex items-center gap-2 mb-1.5">
        {icon && (
          <div className="opacity-60 group-hover:opacity-100 transition-opacity" style={{ color }}>
            {icon}
          </div>
        )}
        <span className="text-xs text-slate-400 font-medium">{label}</span>
      </div>
      <span 
        className="text-lg sm:text-xl font-bold tabular-nums tracking-tight"
        style={{ color }}
      >
        {value}{suffix}
      </span>
    </div>
  );
}

interface SignalCardProps {
  signal: string;
}

export function SignalCard({ signal }: SignalCardProps) {
  const getConfig = () => {
    switch (signal) {
      case '极度低估':
        return {
          bg: 'bg-gradient-to-r from-green-500 to-emerald-400',
          text: 'text-slate-900',
          shadow: 'shadow-green-500/30'
        };
      case '低估':
        return {
          bg: 'bg-gradient-to-r from-cyan-500 to-cyan-400',
          text: 'text-slate-900',
          shadow: 'shadow-cyan-500/30'
        };
      case '均衡':
        return {
          bg: 'bg-gradient-to-r from-yellow-500 to-amber-400',
          text: 'text-slate-900',
          shadow: 'shadow-yellow-500/30'
        };
      case '高估':
        return {
          bg: 'bg-gradient-to-r from-orange-500 to-orange-400',
          text: 'text-white',
          shadow: 'shadow-orange-500/30'
        };
      case '极度高估':
        return {
          bg: 'bg-gradient-to-r from-red-600 to-red-500',
          text: 'text-white',
          shadow: 'shadow-red-600/30'
        };
      default:
        return {
          bg: 'bg-slate-600',
          text: 'text-white',
          shadow: 'shadow-slate-500/20'
        };
    }
  };

  const config = getConfig();

  return (
    <span 
      className={`px-4 py-1.5 rounded-lg text-sm font-bold shadow-lg ${config.bg} ${config.text} ${config.shadow}`}
    >
      {signal}
    </span>
  );
}
