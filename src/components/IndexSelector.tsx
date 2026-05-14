import { INDEX_CONFIGS, getIndexConfig, IndexConfig } from '../data/indexConfig';

interface IndexSelectorProps {
  selectedIndexId: string;
  onIndexChange: (indexId: string) => void;
}

export function IndexSelector({ selectedIndexId, onIndexChange }: IndexSelectorProps) {
  return (
    <div className="w-full">
      <div className="text-xs text-slate-400 mb-2">选择指数</div>
      <div className="grid grid-cols-3 gap-2">
        {INDEX_CONFIGS.map((config) => (
          <button
            key={config.id}
            onClick={() => onIndexChange(config.id)}
            className={`
              relative overflow-hidden rounded-lg px-3 py-2 text-sm font-medium
              transition-all duration-200 border
              ${selectedIndexId === config.id
                ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-cyan-500/50 text-white shadow-lg shadow-cyan-500/20'
                : 'bg-slate-800/50 border-slate-700/40 text-slate-300 hover:bg-slate-700/50 hover:border-slate-600/50'
              }
            `}
          >
            {selectedIndexId === config.id && (
              <div
                className="absolute left-0 top-0 bottom-0 w-1"
                style={{ backgroundColor: config.color }}
              />
            )}
            <div className="flex flex-col items-center">
              <span className="text-xs sm:text-sm font-medium">{config.name}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
