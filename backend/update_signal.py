import json
import numpy as np

with open('data/erp_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

erps = [d['erp'] for d in data]
mean_erp = round(np.mean(erps), 2)
std_erp = round(np.std(erps), 2)

def get_signal(erp):
    if erp > mean_erp + std_erp:
        return '极度低估'
    elif erp > mean_erp + 0.5 * std_erp:
        return '低估'
    elif erp >= mean_erp - 0.5 * std_erp:
        return '均衡'
    elif erp >= mean_erp - std_erp:
        return '高估'
    else:
        return '极度高估'

for d in data:
    d['signal'] = get_signal(d['erp'])

with open('data/erp_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

latest = data[-1]
print('均值:', mean_erp)
print('标准差:', std_erp)
print('低估阈值:', mean_erp + 0.5 * std_erp)
print('最新日期:', latest['date'])
print('最新ERP:', latest['erp'])
print('最新信号:', latest['signal'])
