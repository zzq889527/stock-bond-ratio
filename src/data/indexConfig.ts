export interface IndexConfig {
  id: string;
  name: string;
  displayName: string;
  totalReturnName: string;
  peSymbol: string;
  priceSymbol: string;
  totalReturnSymbol: string;
  color: string;
  description?: string;
}

export const INDEX_CONFIGS: IndexConfig[] = [
  {
    id: 'hs300',
    name: '沪深300',
    displayName: '沪深300',
    totalReturnName: '沪深300全收益',
    peSymbol: '沪深300',
    priceSymbol: 'sh000300',
    totalReturnSymbol: 'H00300',
    color: '#00d4ff'
  },
  {
    id: 'zz500',
    name: '中证500',
    displayName: '中证500',
    totalReturnName: '中证500全收益',
    peSymbol: '中证500',
    priceSymbol: 'sh000905',
    totalReturnSymbol: 'H00905',
    color: '#10b981'
  },
  {
    id: 'zzall',
    name: '中证全指',
    displayName: '中证全指',
    totalReturnName: '中证全指全收益',
    peSymbol: '中证全指',
    priceSymbol: 'sh000985',
    totalReturnSymbol: 'H00985',
    color: '#8b5cf6'
  }
];

export function getIndexConfig(id: string): IndexConfig {
  return INDEX_CONFIGS.find(config => config.id === id) || INDEX_CONFIGS[0];
}

export function getIndexNames(): string[] {
  return INDEX_CONFIGS.map(config => config.name);
}
