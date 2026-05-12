
import { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';
import {
  getDates,
  getERPValues,
  getMeanValues,
  getSigmaUpper,
  getSigmaLower,
  getHS300Values,
  getTotalReturnValues,
  ERPDataItem
} from '../data/erpData';

interface ERPChartProps {
  data: ERPDataItem[];
}

export function ERPChart({ data }: ERPChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    if (chartInstance.current) {
      chartInstance.current.dispose();
    }

    chartInstance.current = echarts.init(chartRef.current);

    const dates = getDates(data);
    const erpValues = getERPValues(data);
    const meanValues = getMeanValues(data);
    const sigmaUpper = getSigmaUpper(data);
    const sigmaLower = getSigmaLower(data);
    const hs300Values = getHS300Values(data);
    const totalReturnValues = getTotalReturnValues(data);

    const mean = data[0].mean;
    const minERP = Math.min(...erpValues);
    const maxERP = Math.max(...erpValues);
    const erpPadding = Math.max(Math.abs(maxERP - mean), Math.abs(minERP - mean)) * 0.2;

    const minHS300 = Math.min(...hs300Values);
    const maxHS300 = Math.max(...hs300Values);
    const hs300Padding = (maxHS300 - minHS300) * 0.1;

    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 1500,
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(100, 116, 139, 0.3)',
        borderWidth: 1,
        textStyle: {
          color: '#f1f5f9',
          fontSize: isMobile ? 12 : 13
        },
        axisPointer: {
          type: 'line',
          lineStyle: {
            color: 'rgba(148, 163, 184, 0.5)',
            type: 'dashed'
          }
        },
        formatter: function(params: any) {
          let result = `<div style="font-weight: 600; margin-bottom: 8px;">${params[0].axisValue}</div>`;
          params.forEach((param: any) => {
            if (param.seriesName !== 'ERP柱状') {
              const color = param.color;
              const value = typeof param.value === 'number' ? param.value.toLocaleString() : param.value;
              result += `<div style="display: flex; align-items: center; gap: 8px; margin: 4px 0;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${color};"></span>
                <span style="flex: 1;">${param.seriesName}</span>
                <span style="font-weight: 600; font-variant-numeric: tabular-nums;">${value}</span>
              </div>`;
            }
          });
          return result;
        }
      },
      legend: {
        data: ['沪深300', '全收益', 'ERP', '均值线', '±1σ'],
        textStyle: {
          color: '#94a3b8',
          fontSize: isMobile ? 10 : 12
        },
        top: isMobile ? 5 : 10,
        left: isMobile ? 5 : 20,
        icon: 'circle',
        itemWidth: isMobile ? 8 : 10,
        itemHeight: isMobile ? 8 : 10,
        itemGap: isMobile ? 10 : 15
      },
      grid: [
        {
          left: isMobile ? '3%' : '5%',
          right: isMobile ? '3%' : '5%',
          top: isMobile ? '15%' : '12%',
          height: isMobile ? '58%' : '65%',
          containLabel: true
        },
        {
          left: isMobile ? '3%' : '5%',
          right: isMobile ? '3%' : '5%',
          top: isMobile ? '75%' : '78%',
          height: isMobile ? '10%' : '12%',
          containLabel: true,
          show: false
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          axisLine: {
            lineStyle: {
              color: 'rgba(100, 116, 139, 0.4)'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#64748b',
            fontSize: isMobile ? 9 : 11,
            rotate: isMobile ? 45 : 0,
            interval: isMobile ? Math.floor(dates.length / 4) : Math.floor(dates.length / 10)
          },
          splitLine: {
            show: false
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          splitLine: { show: false }
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: 'ERP %',
          nameTextStyle: {
            color: '#64748b',
            fontSize: isMobile ? 10 : 12,
            padding: [0, 0, isMobile ? 0 : 8, 0]
          },
          min: -5,
          max: 12,
          axisLine: {
            show: true,
            lineStyle: {
              color: 'rgba(100, 116, 139, 0.4)'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#64748b',
            fontSize: isMobile ? 9 : 11,
            formatter: '{value}%'
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(100, 116, 139, 0.15)',
              type: 'dashed'
            }
          }
        },
        {
          type: 'value',
          name: '沪深300',
          nameTextStyle: {
            color: '#64748b',
            fontSize: isMobile ? 10 : 12,
            padding: [0, 0, isMobile ? 0 : 8, 0]
          },
          min: Math.floor((minHS300 - hs300Padding) / 500) * 500,
          max: Math.ceil((maxHS300 + hs300Padding) / 500) * 500,
          axisLine: {
            show: true,
            lineStyle: {
              color: 'rgba(100, 116, 139, 0.4)'
            }
          },
          axisTick: {
            show: false
          },
          axisLabel: {
            color: '#64748b',
            fontSize: isMobile ? 9 : 11
          },
          splitLine: { show: false }
        },
        {
          type: 'value',
          gridIndex: 1,
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { show: false },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true
        },
        {
          type: 'slider',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
          bottom: isMobile ? 5 : 10,
          height: isMobile ? 20 : 30,
          borderColor: 'rgba(100, 116, 139, 0.3)',
          backgroundColor: 'rgba(30, 41, 59, 0.5)',
          fillerColor: 'rgba(6, 182, 212, 0.2)',
          handleStyle: {
            color: '#06b6d4',
            borderColor: '#22d3ee'
          },
          moveHandleStyle: {
            color: '#06b6d4'
          },
          textStyle: {
            color: '#94a3b8',
            fontSize: isMobile ? 9 : 11
          },
          showDataShadow: false,
          showDetail: false,
          emphasis: {
            handleStyle: {
              color: '#22d3ee',
              borderColor: '#67e8f9'
            }
          }
        }
      ],
      series: [
        {
          name: '沪深300',
          type: 'line',
          yAxisIndex: 1,
          data: hs300Values,
          lineStyle: {
            color: '#00d4ff',
            width: 1.5,
            opacity: 0.9
          },
          showSymbol: false,
          smooth: false,
          animationDuration: 0
        },
        {
          name: '全收益',
          type: 'line',
          data: totalReturnValues,
          lineStyle: {
            color: '#ffa502',
            width: 2,
            opacity: 0.9
          },
          showSymbol: false,
          smooth: false,
          animationDuration: 0,
          yAxisIndex: 1
        },
        {
          name: 'ERP',
          type: 'line',
          data: erpValues,
          lineStyle: {
            color: '#5856d6',
            width: 2,
            opacity: 0.95
          },
          showSymbol: false,
          smooth: false,
          animationDuration: 0,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(88, 86, 214, 0.35)' },
              { offset: 1, color: 'rgba(88, 86, 214, 0.05)' }
            ])
          }
        },
        {
          name: '均值线',
          type: 'line',
          data: meanValues,
          lineStyle: {
            color: '#9ca3af',
            width: 1.5,
            type: 'dashed',
            opacity: 0.8
          },
          showSymbol: false,
          animationDuration: 1500
        },
        {
          name: '±1σ',
          type: 'line',
          data: sigmaUpper,
          lineStyle: {
            color: '#84cc16',
            width: 1.5,
            type: 'dashed',
            opacity: 0.7
          },
          showSymbol: false,
          animationDuration: 0
        },
        {
          name: '±1σ',
          type: 'line',
          data: sigmaLower,
          lineStyle: {
            color: '#84cc16',
            width: 1.5,
            type: 'dashed',
            opacity: 0.7
          },
          showSymbol: false,
          animationDuration: 0
        },
        {
          name: 'ERP柱状',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 2,
          data: erpValues.map((v) => ({
            value: v - mean,
            itemStyle: {
              color: v >= mean 
                ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#10b981' },
                    { offset: 1, color: '#059669' }
                  ])
                : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#ef4444' },
                    { offset: 1, color: '#dc2626' }
                  ]),
              opacity: 0.8
            }
          })),
          barWidth: '60%',
          animationDuration: 2000
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
      chartInstance.current?.dispose();
    };
  }, [data, isMobile]);

  return (
    <div
      ref={chartRef}
      className="w-full h-[400px] sm:h-[500px]"
    />
  );
}
