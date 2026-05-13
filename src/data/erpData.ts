
export interface ERPDataItem {
  date: string;
  erp: number;
  mean: number;
  sigma: number;
  percentile: number;
  signal: string;
  pe_ttm: number;
  bond_10y: number;
  hs300: number;
  total_return: number;
  tr_p: number;
}

let cachedData: ERPDataItem[] | null = null;
const API_BASE = 'http://localhost:8000';

async function fetchERPData(refresh = false): Promise<ERPDataItem[]> {
  if (cachedData && !refresh) {
    return cachedData;
  }

  try {
    const url = `${API_BASE}/api/erp-data${refresh ? '?refresh=true' : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    
    const result = await response.json();
    cachedData = result.data;
    return result.data;
  } catch (error) {
    console.warn('Using mock data:', error);
    return getMockData();
  }
}

function getMockData(): ERPDataItem[] {
  const data: ERPDataItem[] = [];
  const startDate = new Date('2005-04-08');
  const endDate = new Date('2026-03-09');
  
  const mean = 4.46;
  const sigma = 2.34;
  
  let hs300 = 980;
  let totalReturn = 120;
  let erp = 2.53;
  let bondYield = 2.5;

  const cycles = [
    { start: 0, end: 0.1, trend: 1 },
    { start: 0.1, end: 0.15, trend: -1 },
    { start: 0.15, end: 0.25, trend: 1 },
    { start: 0.25, end: 0.35, trend: -1 },
    { start: 0.35, end: 0.4, trend: 1 },
    { start: 0.4, end: 0.45, trend: -1 },
    { start: 0.45, end: 0.55, trend: 0.5 },
    { start: 0.55, end: 0.6, trend: -1 },
    { start: 0.6, end: 0.65, trend: 1 },
    { start: 0.65, end: 0.7, trend: -0.5 },
    { start: 0.7, end: 0.8, trend: 1 },
    { start: 0.8, end: 1, trend: -0.3 },
  ];

  let currentDate = new Date(startDate);
  let dayCount = 0;
  const totalDays = Math.floor((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

  while (currentDate <= endDate) {
    const dateStr = currentDate.toISOString().split('T')[0];
    const dayOfWeek = currentDate.getDay();
    
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      const progress = dayCount / totalDays;
      
      const cycle = cycles.find(c => progress >= c.start && progress < c.end) || cycles[cycles.length - 1];
      
      const trend = cycle.trend;
      const volatility = 0.3 + Math.sin(progress * Math.PI * 4) * 0.2;
      const noise = (Math.random() - 0.5) * volatility;
      
      erp = Math.max(-3, Math.min(12, erp + trend * 0.05 + noise));
      
      const hsTrend = -trend * 0.8;
      const hsNoise = (Math.random() - 0.5) * 80;
      hs300 = Math.max(800, Math.min(6500, hs300 + hsTrend * 20 + hsNoise));
      
      const trTrend = -trend * 0.5;
      const trNoise = (Math.random() - 0.5) * 15;
      totalReturn = Math.max(0, totalReturn + trTrend * 5 + trNoise);
      
      bondYield = Math.max(1.5, Math.min(6, 2.5 + Math.sin(progress * Math.PI * 2) * 1.5 + (Math.random() - 0.5) * 0.3));
      
      const pe_ttm = Math.round((100 / Math.max(erp + bondYield, 2)) * 10) / 10;
      
      const zScore = (erp - mean) / sigma;
      const percentile = Math.max(0, Math.min(100, Math.round((1 + erf(zScore / Math.sqrt(2))) / 2 * 100)));
      
      let signal = '均衡';
      if (erp > mean + sigma) {
        signal = '极度低估';
      } else if (erp > mean) {
        signal = '低估';
      } else if (erp < mean - sigma) {
        signal = '高估';
      }
      
      const tr_p = Math.round((totalReturn / hs300) * 100) / 100;
      
      data.push({
        date: dateStr,
        erp: Math.round(erp * 100) / 100,
        mean,
        sigma,
        percentile,
        signal,
        pe_ttm,
        bond_10y: Math.round(bondYield * 100) / 100,
        hs300: Math.round(hs300),
        total_return: Math.round(totalReturn),
        tr_p
      });
    }
    
    currentDate.setDate(currentDate.getDate() + 1);
    dayCount++;
  }
  
  const lastItem = data[data.length - 1];
  lastItem.erp = 3.62;
  lastItem.percentile = 7;
  lastItem.signal = '均衡';
  lastItem.pe_ttm = 27.6;
  lastItem.bond_10y = 3.46;
  lastItem.hs300 = 2415;
  lastItem.total_return = 193;
  lastItem.tr_p = 0.08;
  
  return data;
}

function erf(x: number): number {
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;

  const sign = x >= 0 ? 1 : -1;
  x = Math.abs(x);

  const t = 1.0 / (1.0 + p * x);
  const y = 1.0 - ((((a5 * t + a4) * t) + a3) * t + a2) * t * a1 * Math.exp(-x * x);

  return sign * y;
}

export async function getERPData(refresh = false): Promise<ERPDataItem[]> {
  return await fetchERPData(refresh);
}

export function getLatestData(): ERPDataItem {
  const data = cachedData || getMockData();
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

export function getHS300Values(data: ERPDataItem[]): number[] {
  return data.map(item => item.hs300);
}

export function getTotalReturnValues(data: ERPDataItem[]): number[] {
  return data.map(item => item.total_return);
}
