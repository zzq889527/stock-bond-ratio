import { INDEX_CONFIGS, IndexConfig } from './indexConfig';

export interface ERPDataItem {
  date: string;
  erp: number;
  mean: number;
  sigma: number;
  percentile: number;
  signal: string;
  pe_ttm: number;
  bond_10y: number;
  index_value: number;
  total_return: number;
  tr_p: number;
}

export interface IndexDataMap {
  [key: string]: ERPDataItem[];
}

let cachedData: IndexDataMap | null = null;

function generateMockDataForIndex(config: IndexConfig): ERPDataItem[] {
  const data: ERPDataItem[] = [];
  const startDate = new Date('2005-04-08');
  const endDate = new Date('2026-05-14');
  
  // 为每个指数设置不同的统计特征
  const baseMean = 4.46;
  const baseSigma = 2.34;
  
  // 根据指数类型调整参数
  let meanAdjustment = 0;
  let sigmaAdjustment = 1;
  let basePrice = 1000;
  
  if (config.id.includes('500')) {
    // 中证500 通常有更高的ERP
    meanAdjustment = 0.8;
    sigmaAdjustment = 1.15;
    basePrice = 800;
  } else if (config.id.includes('zzall')) {
    // 中证全指
    meanAdjustment = 0.3;
    sigmaAdjustment = 1.05;
    basePrice = 900;
  } else if (config.id.includes('eq')) {
    // 等权指数通常波动稍大
    sigmaAdjustment = 1.1;
    basePrice *= 0.95;
  }
  
  const mean = baseMean + meanAdjustment;
  const sigma = baseSigma * sigmaAdjustment;
  
  let indexValue = basePrice;
  let totalReturn = basePrice * 1.5;
  let erp = mean;
  let bondYield = 3.5;

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
      const volatility = 0.35 * sigmaAdjustment + Math.sin(progress * Math.PI * 4) * 0.2;
      const noise = (Math.random() - 0.5) * volatility;
      
      erp = Math.max(-5, Math.min(14, erp + trend * 0.06 * sigmaAdjustment + noise));
      
      const indexTrend = -trend * 0.85;
      const indexNoise = (Math.random() - 0.5) * 90;
      indexValue = Math.max(500, Math.min(10000, indexValue + indexTrend * 25 + indexNoise));
      
      const trTrend = -trend * 0.6;
      const trNoise = (Math.random() - 0.5) * 18;
      totalReturn = Math.max(0, totalReturn + trTrend * 7 + trNoise);
      
      bondYield = Math.max(1.0, Math.min(6.5, 3.2 + Math.sin(progress * Math.PI * 2) * 1.8 + (Math.random() - 0.5) * 0.4));
      
      const pe_ttm = Math.round((100 / Math.max(erp + bondYield, 1.5)) * 10) / 10;
      
      const zScore = (erp - mean) / sigma;
      const percentile = Math.max(0, Math.min(100, Math.round((1 + erf(zScore / Math.sqrt(2))) / 2 * 100)));
      
      let signal = '均衡';
      if (erp > mean + sigma) {
        signal = '极度低估';
      } else if (erp > mean + 0.5 * sigma) {
        signal = '低估';
      } else if (erp >= mean - 0.5 * sigma) {
        signal = '均衡';
      } else if (erp >= mean - sigma) {
        signal = '高估';
      } else {
        signal = '极度高估';
      }
      
      const tr_p = Math.round((100 / pe_ttm) * 100) / 100;
      
      data.push({
        date: dateStr,
        erp: Math.round(erp * 100) / 100,
        mean: Math.round(mean * 100) / 100,
        sigma: Math.round(sigma * 100) / 100,
        percentile,
        signal,
        pe_ttm,
        bond_10y: Math.round(bondYield * 100) / 100,
        index_value: Math.round(indexValue),
        total_return: Math.round(totalReturn),
        tr_p
      });
    }
    
    currentDate.setDate(currentDate.getDate() + 1);
    dayCount++;
  }
  
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

async function loadRealIndexData(indexId: string): Promise<ERPDataItem[]> {
  try {
    const response = await fetch(`./${indexId}_erp_data.json`);
    if (response.ok) {
      const data = await response.json();
      return data.map((item: any) => ({
        ...item,
        index_value: item.hs300 || item.index_value
      }));
    }
  } catch (e) {
    console.warn(`无法加载 ${indexId} 真实数据，使用模拟数据`);
  }
  
  const config = INDEX_CONFIGS.find(c => c.id === indexId) || INDEX_CONFIGS[0];
  return generateMockDataForIndex(config);
}

export async function getAllIndexData(refresh = false): Promise<IndexDataMap> {
  if (cachedData && !refresh) {
    return cachedData;
  }
  
  const dataMap: IndexDataMap = {};
  
  for (const config of INDEX_CONFIGS) {
    if (config.id === 'hs300') {
      try {
        const response = await fetch('./erp_data.json');
        if (response.ok) {
          const hs300Data = await response.json();
          dataMap[config.id] = hs300Data.map((item: any) => ({
            ...item,
            index_value: item.hs300
          }));
          continue;
        }
      } catch (e) {
        // 继续使用模拟数据
      }
    }
    
    dataMap[config.id] = generateMockDataForIndex(config);
  }
  
  cachedData = dataMap;
  return dataMap;
}

export async function getERPData(indexId: string = 'hs300', refresh = false): Promise<ERPDataItem[]> {
  const dataMap = await getAllIndexData(refresh);
  return dataMap[indexId] || dataMap['hs300'];
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
