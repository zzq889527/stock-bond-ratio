
export interface ERPDataItem {
  date: string;
  erp: number;
  mean: number;
  sigma: number;
  percentile: number;
  signal: string;
  pe_ttm: number;
  bond_10y: number;
  index_value?: number;
  hs300?: number;
  total_return: number;
  tr_p: number;
}

const API_BASE = 'http://localhost:8000';

async function fetchERPData(refresh = false): Promise<ERPDataItem[]> {
  try {
    const response = await fetch(`./erp_data.json`);
    if (response.ok) {
      const data = await response.json();
      return data;
    }
  } catch (e) {
    console.warn('Failed to fetch from file:', e);
  }

  try {
    const url = `${API_BASE}/api/erp-data${refresh ? '?refresh=true' : ''}`;
    const response = await fetch(url);
    if (response.ok) {
      const result = await response.json();
      return result.data;
    }
  } catch (e) {
    console.warn('Failed to fetch from API:', e);
  }

  throw new Error('无法加载数据');
}

export async function getERPData(refresh = false): Promise<ERPDataItem[]> {
  return await fetchERPData(refresh);
}

export function getLatestData(data: ERPDataItem[]): ERPDataItem {
  return data[data.length - 1];
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
  return data.map(item => item.index_value || item.hs300 || 0);
}

export function getTotalReturnValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.total_return);
}
