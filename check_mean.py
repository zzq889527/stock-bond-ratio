import json

for fname, name in [
    ('erp_data.json', '沪深300'),
    ('hs300_eq_erp_data.json', '沪深300等权'),
    ('zz500_erp_data.json', '中证500'),
    ('zz500_eq_erp_data.json', '中证500等权'),
]:
    d = json.load(open(f'e:/Trae Project/public/{fname}'))
    erps = [x['erp'] for x in d]
    mean = d[-1]['mean']
    latest = d[-1]['erp']
    print(f'{name}:')
    print(f'  Mean={mean:.2f}%, Latest ERP={latest:.2f}%')
    print(f'  ERP range: min={min(erps):.2f}%, max={max(erps):.2f}%')
    print()
