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
let liveDataDates: Record<string, string> = {};

function estimateLiveItem(lastItem: ERPDataItem, livePrice: number, liveDate: string): ERPDataItem {
  const oldPrice = lastItem.index_value;
  if (oldPrice <= 0) {
    return { ...lastItem, date: liveDate, index_value: Number(livePrice.toFixed(2)) };
  }

  const ratio = livePrice / oldPrice;
  const pe = lastItem.pe_ttm * ratio;
  const tr = lastItem.total_return * ratio;
  const newErp = lastItem.bond_10y > 0 ? (100 / pe) - lastItem.bond_10y : lastItem.erp;

  return {
    ...lastItem,
    date: liveDate,
    index_value: Number(livePrice.toFixed(2)),
    total_return: Number(tr.toFixed(1)),
    pe_ttm: Number(pe.toFixed(2)),
    pb: Number((lastItem.pb * ratio).toFixed(2)),
    dividend_yield: Number((lastItem.dividend_yield / ratio).toFixed(3)),
    tr_p: Number((100 / pe).toFixed(2)),
    erp: Number(newErp.toFixed(4)),
  };
}

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
        bond_10y: item.bond_10y || 0,
      }));
    }
  } catch (e) {
    console.warn(`\u65E0\u6CD5\u52A0\u8F7D ${indexId} \u6570\u636E`);
  }
  throw new Error(`\u65E0\u6CD5\u52A0\u8F7D ${indexId} \u6570\u636E`);
}

async function mergeLiveData(indexId: string, data: ERPDataItem[]): Promise<ERPDataItem[]> {
  if (data.length === 0) return data;

  try {
    const liveResult = await getLatestPrice(indexId);
    if (!liveResult) {
      liveDataDates[indexId] = `\u6570\u636E\u6587\u4EF6 ${data[data.length - 1]?.date || ''}`;
      return data;
    }

    const lastItem = data[data.length - 1];
    const liveDate = liveResult.date;

    if (liveDate > lastItem.date) {
      const newItem = estimateLiveItem(lastItem, liveResult.price, liveDate);
      liveDataDates[indexId] = `\u5B9E\u65F6 ${liveDate}`;
      return [...data, newItem];
    }

    const priceDiff = Math.abs(liveResult.price - lastItem.index_value) / lastItem.index_value;
    if (liveDate === lastItem.date && priceDiff > 0.001) {
      data[data.length - 1] = estimateLiveItem(lastItem, liveResult.price, liveDate);
      liveDataDates[indexId] = `\u5B9E\u65F6 ${liveDate}`;
    } else {
      liveDataDates[indexId] = `\u6570\u636E\u6587\u4EF6 ${lastItem.date}`;
    }
  } catch {
    liveDataDates[indexId] = `\u6570\u636E\u6587\u4EF6 ${data[data.length - 1]?.date || ''}`;
  }

  return data;
}

export function getLiveDateInfo(indexId: string): string {
  return liveDataDates[indexId] || '';
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
      console.error(`\u52A0\u8F7D ${config.name} \u6570\u636E\u5931\u8D25:`, e);
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