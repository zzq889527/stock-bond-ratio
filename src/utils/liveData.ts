const EASTMONEY_SECIDS: Record<string, string> = {
  hs300: '1.000300',
  zz500: '1.000905',
  zzall: '1.000985',
};

interface LivePriceResult {
  price: number;
  date: string;
}

async function fetchEastMoneyPrice(secid: string): Promise<LivePriceResult | null> {
  try {
    const url = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=f43,f58,f124&_=${Date.now()}`;
    const resp = await fetch(url);
    if (!resp.ok) return null;
    const json = await resp.json();
    if (!json?.data?.f43) return null;
    const price = json.data.f43 / 100;
    const ts = json.data.f124 ? new Date(json.data.f124) : new Date();
    const date = ts.toISOString().split('T')[0];
    return { price, date };
  } catch {
    return null;
  }
}

async function fetchYahooPrice(): Promise<LivePriceResult | null> {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=3d`;
    const resp = await fetch(url);
    if (!resp.ok) return null;
    const json = await resp.json();
    const result = json?.chart?.result?.[0];
    if (!result) return null;
    const timestamps = result.timestamp || [];
    const quotes = result.indicators?.quote?.[0];
    if (!quotes?.close || timestamps.length === 0) return null;
    let lastIdx = timestamps.length - 1;
    while (lastIdx >= 0 && quotes.close[lastIdx] === null) lastIdx--;
    if (lastIdx < 0) return null;
    const price = quotes.close[lastIdx];
    const date = new Date(timestamps[lastIdx] * 1000).toISOString().split('T')[0];
    return { price, date };
  } catch {
    return null;
  }
}

export async function getLatestPrice(indexId: string): Promise<LivePriceResult | null> {
  if (indexId === 'sp500') {
    return fetchYahooPrice();
  }
  const secid = EASTMONEY_SECIDS[indexId];
  if (secid) {
    return fetchEastMoneyPrice(secid);
  }
  return null;
}