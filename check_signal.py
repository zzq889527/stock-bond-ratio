import json

with open('e:/Trae Project/erp_data.json', 'r') as f:
    data = json.load(f)
latest = data[-1]
print('Latest data:')
print(json.dumps(latest, indent=2, ensure_ascii=False))
print()
print(f'ERP: {latest["erp"]}%')
print(f'Mean: {latest["mean"]}%')
print(f'Sigma: {latest["sigma"]}%')
print(f'Signal: {latest["signal"]}')
print()

mean = latest['mean']
sigma = latest['sigma']
erp = latest['erp']
threshold_low = mean + 0.5 * sigma
threshold_high = mean + sigma
print('Thresholds:')
print(f'  Extremely Undervalued: > {threshold_high:.2f}%')
print(f'  Undervalued: {threshold_low:.2f}% ~ {threshold_high:.2f}%')
print(f'  Balanced: {mean - 0.5*sigma:.2f}% ~ {threshold_low:.2f}%')
print(f'  Overvalued: {mean - sigma:.2f}% ~ {mean - 0.5*sigma:.2f}%')
print(f'  Extremely Overvalued: < {mean - sigma:.2f}%')
print()
print(f'Current ERP {erp}% is:')
if erp > threshold_high:
    print('  -> Extremely Undervalued')
elif erp > threshold_low:
    print('  -> Undervalued')
elif erp < mean - sigma:
    print('  -> Extremely Overvalued')
elif erp < mean - 0.5 * sigma:
    print('  -> Overvalued')
else:
    print('  -> Balanced')

print()
print('=== Check other index data ===')
for fname in ['hs300_eq_erp_data.json', 'zz500_erp_data.json', 'zz500_eq_erp_data.json', 'zzall_erp_data.json', 'zzall_eq_erp_data.json']:
    try:
        with open(f'e:/Trae Project/{fname}', 'r') as f:
            d = json.load(f)
        l = d[-1]
        print(f'{fname}: date={l["date"]}, erp={l["erp"]:.2f}%, mean={l["mean"]:.2f}%, signal={l["signal"]}')
    except Exception as e:
        print(f'{fname}: ERROR - {e}')
