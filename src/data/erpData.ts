import { INDEX_CONFIGS, IndexConfig } from './indexConfig';

export interface ERPDataItem {
  date: string;
  erp: number;
  mean: number;
  sigma: number;
  percentile: number;
  signal: string;
  pe_ttm: number;
  pb: number;
  dividend_yield: number;
  bond_10y: number;
  index_value: number;
  total_return: number;
  tr_p: number;
}

export interface IndexDataMap {
  [key: string]: ERPDataItem[];
}

let cachedData: IndexDataMap | null = null;

async function loadIndexData(indexId: string): Promise<ERPDataItem[]> {
  try {
    const url = indexId === 'hs300' ? './erp_data.json' : `./${indexId}_erp_data.json`;
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      return data.map((item: any) => ({
        ...item,
        index_value: item.hs300 || item.index_value,
        pb: item.pb || 0,
        dividend_yield: item.dividend_yield || 0
      }));
    }
  } catch (e) {
    console.warn(`无法加载 ${indexId} 数据`);
  }
  throw new Error(`无法加载 ${indexId} 数据`);
}

export async function getAllIndexData(refresh = false): Promise<IndexDataMap> {
  if (cachedData && !refresh) {
    return cachedData;
  }
  
  const dataMap: IndexDataMap = {};
  
  for (const config of INDEX_CONFIGS) {
    try {
      const data = await loadIndexData(config.id);
      dataMap[config.id] = data;
    } catch (e) {
      console.error(`加载 ${config.name} 数据失败:`, e);
    }
  }
  
  cachedData = dataMap;
  return dataMap;
}

export async function getERPData(indexId: string = 'hs300', refresh = false): Promise<ERPDataItem[]> {
  const dataMap = await getAllIndexData(refresh);
  return dataMap[indexId] || [];
}

export function getDates(data: ERPDataItem[]): string[] {
  return data.map(item => item.date);
}

export function getERPValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.erp);
}

export function getMeanValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.mean);
}

export function getSigmaUpper(data: ERPDataItem[]): number[] {
  return data.map(item => item.mean + item.sigma);
}

export function getSigmaLower(data: ERPDataItem[]): number[] {
  return data.map(item => item.mean - item.sigma);
}

export function getIndexValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.index_value);
}

export function getTotalReturnValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.total_return);
}

export function getPEValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.pe_ttm);
}

export function getPBValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.pb);
}

export function getDividendYieldValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.dividend_yield);
}