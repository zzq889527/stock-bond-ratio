import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { ERPDataItem, getDates, getPEValues, getPBValues, getDividendYieldValues } from '../data/erpData';

interface ValuationChartProps {
  data: ERPDataItem[];
}

export function ValuationChart({ data }: ValuationChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    const dates = getDates(data);
    const peValues = getPEValues(data);
    const pbValues = getPBValues(data);
    const dividendValues = getDividendYieldValues(data);

    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 1500,
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: '#334155',
        borderWidth: 1,
        textStyle: {
          color: '#e2e8f0'
        },
        axisPointer: {
          type: 'cross',
          crossStyle: {
            color: '#64748b'
          }
        },
        formatter: (params: any) => {
          let result = `<div style="font-weight: bold; margin-bottom: 8px; color: #f1f5f9">${params[0].axisValue}</div>`;
          params.forEach((param: any) => {
            const unit = param.seriesName === '股息率' ? '%' : 'x';
            result += `<div style="display: flex; align-items: center; margin: 4px 0;">
              <span style="display: inline-block; width: 10px; height: 10px; border-radius: ${param.seriesName === '股息率' ? '50%' : '2px'}; background: ${param.color}; margin-right: 8px;"></span>
              <span style="color: #94a3b8">${param.seriesName}:</span>
              <span style="color: #fff; margin-left: 4px; font-weight: 600;">${param.value.toFixed(param.seriesName === '股息率' ? 2 : 1)}${unit}</span>
            </div>`;
          });
          return result;
        }
      },
      legend: {
        textStyle: {
          color: '#94a3b8',
          fontSize: 11
        },
        top: 5,
        left: 15,
        itemWidth: 12,
        itemHeight: 6,
        itemGap: 20,
        data: [
          { name: 'PE(TTM)', icon: 'rect' },
          { name: 'PB', icon: 'rect' },
          { name: '股息率', icon: 'circle' }
        ]
      },
      grid: {
        left: 60,
        right: 40,
        top: 40,
        bottom: 30,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: {
          lineStyle: {
            color: '#334155'
          }
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 10,
          interval: 'auto',
          rotate: 0
        }
      },
      yAxis: [
        {
          type: 'value',
          name: 'PE/PB',
          nameTextStyle: {
            color: '#64748b',
            fontSize: 10,
            padding: [0, 0, 0, 40]
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: '#334155'
            }
          },
          axisLabel: {
            color: '#64748b',
            fontSize: 10,
            formatter: '{value}x'
          },
          splitLine: {
            lineStyle: {
              color: '#1e293b',
              type: 'dashed'
            }
          }
        },
        {
          type: 'value',
          name: '股息率',
          nameTextStyle: {
            color: '#64748b',
            fontSize: 10,
            padding: [0, 40, 0, 0]
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: '#334155'
            }
          },
          axisLabel: {
            color: '#64748b',
            fontSize: 10,
            formatter: '{value}%'
          },
          splitLine: {
            show: false
          }
        }
      ],
      series: [
        {
          name: 'PE(TTM)',
          type: 'line',
          data: peValues,
          smooth: 0.3,
          symbol: 'none',
          lineStyle: {
            color: '#06b6d4',
            width: 2
          },
          animationDuration: 0
        },
        {
          name: 'PB',
          type: 'line',
          data: pbValues,
          smooth: 0.3,
          symbol: 'none',
          lineStyle: {
            color: '#f59e0b',
            width: 2
          },
          animationDuration: 0
        },
        {
          name: '股息率',
          type: 'line',
          yAxisIndex: 1,
          data: dividendValues,
          smooth: 0.3,
          symbol: 'none',
          lineStyle: {
            color: '#10b981',
            width: 2
          },
          animationDuration: 0
        }
      ]
    };

    chartInstance.current.setOption(option);

    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data]);

  return <div ref={chartRef} className="w-full h-full" />;
}