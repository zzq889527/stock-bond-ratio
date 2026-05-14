import json

print("=== 检查 public/ 目录的数据 ===\n")

files = [
    ('public/erp_data.json', '沪深300'),
    ('public/hs300_eq_erp_data.json', '沪深300等权'),
    ('public/zz500_erp_data.json', '中证500'),
    ('public/zz500_eq_erp_data.json', '中证500等权'),
    ('public/zzall_erp_data.json', '中证全指'),
    ('public/zzall_eq_erp_data.json', '中证全指等权'),
]

for fname, name in files:
    try:
        with open(f'e:/Trae Project/{fname}', 'r') as f:
            data = json.load(f)
        latest = data[-1]
        print(f"{name}:")
        print(f"  日期: {latest['date']}")
        print(f"  ERP: {latest['erp']}%")
        print(f"  均值: {latest['mean']}%")
        print(f"  标准差: {latest['sigma']}%")
        print(f"  信号: {latest['signal']}")
        print(f"  PE: {latest['pe_ttm']}x")
        print(f"  国债: {latest['bond_10y']}%")
        print(f"  指数点位: {latest['index_value']}")
        print(f"  全收益: {latest['total_return']}")
        print()

        # 计算信号
        mean = latest['mean']
        sigma = latest['sigma']
        erp = latest['erp']
        if erp > mean + sigma:
            calc_signal = '极度低估'
        elif erp > mean + 0.5 * sigma:
            calc_signal = '低估'
        elif erp >= mean - 0.5 * sigma:
            calc_signal = '均衡'
        elif erp >= mean - sigma:
            calc_signal = '高估'
        else:
            calc_signal = '极度高估'
        print(f"  计算信号: {calc_signal}")
        if calc_signal != latest['signal']:
            print(f"  ⚠️ 信号不匹配！")
        print()

    except Exception as e:
        print(f"{name}: ERROR - {e}\n")
