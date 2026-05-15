import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

# Try to get S&P 500 data from alternative sources
start = datetime(1990, 1, 1)
end = datetime(2026, 5, 15)

# Try stooq
try:
    sp = web.DataReader('^SPX', 'stooq', start, end)
    print('stooq ^SPX: ' + str(len(sp)) + ' rows')
    sp = sp.sort_index()
    print('  Range: ' + str(sp.index[0].date()) + ' ~ ' + str(sp.index[-1].date()))
    print('  2008-01: ' + str(sp.loc['2008-01'].iloc[0]['Close']))
except Exception as e:
    print('stooq ^SPX failed: ' + str(e))

# Try with different symbol
try:
    sp2 = web.DataReader('SPX', 'stooq', start, end)
    print('stooq SPX: ' + str(len(sp2)) + ' rows')
except Exception as e:
    print('stooq SPX failed: ' + str(e))

# Try alphavantage
try:
    sp3 = web.DataReader('SPY', 'av-daily', start, end, api_key='demo')
    print('av-daily SPY: ' + str(len(sp3)) + ' rows')
except Exception as e:
    print('av-daily SPY failed: ' + str(e))

# Try to get from FRED with different series
try:
    sp500_fred = web.DataReader('SP500', 'fred', datetime(1950, 1, 1), end)
    print('FRED SP500: ' + str(len(sp500_fred)) + ' rows')
    print('  Range: ' + str(sp500_fred.index[0].date()) + ' ~ ' + str(sp500_fred.index[-1].date()))
except Exception as e:
    print('FRED SP500 failed: ' + str(e))