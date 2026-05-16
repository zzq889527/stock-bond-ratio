import { INDEX_CONFIGS, IndexConfig } from './indexConfig';
import { getLatestPrice } from '../utils/liveData';

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

async function mergeLiveData(indexId: string, data: ERPDataItem[]): Promise<ERPDataItem[]> {
  if (data.length === 0) return data;

  try {
    const liveResult = await getLatestPrice(indexId);
    if (!liveResult) return data;

    const lastItem = data[data.length - 1];

    if (liveResult.date > lastItem.date) {
      const priceRatio = liveResult.price / lastItem.index_value;
      const newItem: ERPDataItem = {
        ...lastItem,
        date: liveResult.date,
        index_value: Number(liveResult.price.toFixed(2)),
        total_return: Number((lastItem.total_return * priceRatio).toFixed(2)),
      };
      return [...data, newItem];
    }
  } catch {
  }

  return data;
}

export async function getAllIndexData(refresh = false): Promise<IndexDataMap> {
  if (cachedData && !refresh) {
    return cachedData;
  }
  
  const dataMap: IndexDataMap = {};
  
  const loadPromises = INDEX_CONFIGS.map(async (config) => {
    try {
      let data = await loadIndexData(config.id);
      data = await mergeLiveData(config.id, data);
      dataMap[config.id] = data;
    } catch (e) {
      console.error(`加载 ${config.name} 数据失败:`, e);
    }
  });

  await Promise.all(loadPromises);
  
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