import json

print("=== 检查数据 ===")
with open('data/erp_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

last = data[-1]
print(f"最新数据日期: {last['date']}")
print(f"ERP: {last['erp']}")
print(f"均值: {last['mean']}")
print(f"σ: {last['sigma']}")
print(f"低估阈值 (均值+0.5σ): {last['mean'] + 0.5 * last['sigma']}")
print(f"极度低估阈值 (均值+1σ): {last['mean'] + last['sigma']}")
print(f"信号: {last['signal']}")
print()

if last['erp'] > last['mean'] + 0.5 * last['sigma']:
    print(f"✓ ERP({last['erp']}) > 低估阈值({last['mean'] + 0.5 * last['sigma']:.2f})，应该是'低估'或'极度低估'")
    if last['erp'] > last['mean'] + last['sigma']:
        print(f"✓ ERP({last['erp']}) > 极度低估阈值({last['mean'] + last['sigma']:.2f})，应该是'极度低估'")
    else:
        print(f"✓ ERP({last['erp']}) <= 极度低估阈值({last['mean'] + last['sigma']:.2f})，应该是'低估'")
else:
    print(f"✗ ERP({last['erp']}) <= 低估阈值({last['mean'] + 0.5 * last['sigma']:.2f})，应该是'均衡'")
