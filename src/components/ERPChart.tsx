
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
  isLandscape?: boolean;
}

export function ERPChart({ data, isLandscape = false }: ERPChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    if (chartInstance.current) {
      chartInstance.current.dispose();
    }

    chartInstance.current = echarts.init(chartRef.current, 'dark', {
      renderer: 'canvas',
      devicePixelRatio: window.devicePixelRatio || 2
    });

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

    const minHS300 = Math.min(...hs300Values);
    const maxHS300 = Math.max(...hs300Values);
    const hs300Padding = (maxHS300 - minHS300) * 0.1;

    // 横屏模式下的图表配置
    const landscapeGrid = [
      {
        left: '6%',
        right: '6%',
        top: '12%',
        bottom: '10%',
        containLabel: true
      },
      {
        left: '6%',
        right: '6%',
        top: '88%',
        height: '8%',
        containLabel: true,
        show: false
      }
    ];

    const portraitGrid = [
      {
        left: window.innerWidth < 768 ? '3%' : '5%',
        right: window.innerWidth < 768 ? '3%' : '5%',
        top: window.innerWidth < 768 ? '15%' : '12%',
        height: window.innerWidth < 768 ? '58%' : '65%',
        containLabel: true
      },
      {
        left: window.innerWidth < 768 ? '3%' : '5%',
        right: window.innerWidth < 768 ? '3%' : '5%',
        top: window.innerWidth < 768 ? '75%' : '78%',
        height: window.innerWidth < 768 ? '10%' : '12%',
        containLabel: true,
        show: false
      }
    ];

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
          fontSize: isLandscape ? 12 : (window.innerWidth < 768 ? 12 : 13)
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
          fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 9 : 12)
        },
        top: isLandscape ? 5 : (window.innerWidth < 768 ? 5 : 10),
        left: isLandscape ? 15 : (window.innerWidth < 768 ? 5 : 20),
        icon: 'circle',
        itemWidth: isLandscape ? 9 : (window.innerWidth < 768 ? 8 : 10),
        itemHeight: isLandscape ? 9 : (window.innerWidth < 768 ? 8 : 10),
        itemGap: isLandscape ? 12 : (window.innerWidth < 768 ? 8 : 15),
        selected: {
          '全收益': false
        }
      },
      grid: isLandscape ? landscapeGrid : portraitGrid,
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
            fontSize: isLandscape ? 10 : (window.innerWidth < 768 ? 9 : 11),
            rotate: isLandscape ? 0 : (window.innerWidth < 768 ? 45 : 0),
            interval: isLandscape ? Math.floor(dates.length / 10) : (window.innerWidth < 768 ? Math.floor(dates.length / 4) : Math.floor(dates.length / 10)),
            showMaxLabel: true
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
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12),
            padding: [0, 0, isLandscape ? 0 : (window.innerWidth < 768 ? 0 : 8), 0]
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
            fontSize: isLandscape ? 10 : (window.innerWidth < 768 ? 9 : 11),
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
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12),
            padding: [0, 0, isLandscape ? 0 : (window.innerWidth < 768 ? 0 : 8), 0]
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
            fontSize: isLandscape ? 10 : (window.innerWidth < 768 ? 9 : 11)
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
          bottom: isLandscape ? 5 : (window.innerWidth < 768 ? 5 : 10),
          height: isLandscape ? 14 : (window.innerWidth < 768 ? 20 : 30),
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
            fontSize: isLandscape ? 9 : (window.innerWidth < 768 ? 9 : 11)
          },
          showDataShadow: false,
          showDetail: false,
          emphasis: {
            handleStyle: {
              color: '#22d3ee',
              borderColor: '#67e8f9'
            },
            handleLabel: {
              show: false
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
            width: isLandscape ? 1.8 : 1.5,
            opacity: 0.9
          },
          showSymbol: false,
          smooth: 0.3,
          animationDuration: 0
        },
        {
          name: '全收益',
          type: 'line',
          data: totalReturnValues,
          lineStyle: {
            color: '#ef4444',
            width: isLandscape ? 2.2 : 2,
            opacity: 0.9
          },
          showSymbol: false,
          smooth: 0.3,
          animationDuration: 0,
          yAxisIndex: 1
        },
        {
          name: 'ERP',
          type: 'line',
          data: erpValues,
          lineStyle: {
            color: '#f59e0b',
            width: isLandscape ? 2.5 : 2.5,
            opacity: 1
          },
          showSymbol: false,
          smooth: 0.35,
          animationDuration: 0,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(245, 158, 11, 0.35)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }
            ])
          }
        },
        {
          name: '均值线',
          type: 'line',
          data: meanValues,
          lineStyle: {
            color: '#6b7280',
            width: isLandscape ? 1.2 : 1,
            type: 'dashed',
            opacity: 0.7
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
            width: isLandscape ? 1 : 1,
            type: 'dashed',
            opacity: 0.6
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
            width: isLandscape ? 1 : 1,
            type: 'dashed',
            opacity: 0.6
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
              opacity: isLandscape ? 0.7 : 0.8
            }
          })),
          barWidth: isLandscape ? '50%' : '60%',
          animationDuration: 2000
        },
        {
          name: '当前ERP',
          type: 'scatter',
          data: [[dates.length - 1, erpValues[erpValues.length - 1]]],
          symbol: 'circle',
          symbolSize: isLandscape ? 8 : 10,
          itemStyle: {
            color: '#f59e0b',
            borderColor: '#fff',
            borderWidth: 2,
            shadowColor: 'rgba(245, 158, 11, 0.6)',
            shadowBlur: 10
          },
          label: {
            show: true,
            position: 'right',
            offset: [isLandscape ? 10 : 5, 0],
            color: '#f59e0b',
            fontSize: isLandscape ? 11 : 12,
            fontWeight: 'bold',
            formatter: `${erpValues[erpValues.length - 1].toFixed(2)}%`
          },
          animationDuration: 1500,
          animationDelay: 1000
        },
        {
          name: '当前日期',
          type: 'scatter',
          data: [[dates.length - 1, -4.5]],
          symbol: 'rect',
          symbolSize: [isLandscape ? 60 : 50, 20],
          itemStyle: {
            color: 'rgba(6, 182, 212, 0.9)',
            borderColor: '#22d3ee',
            borderWidth: 1,
            borderRadius: 4
          },
          label: {
            show: true,
            position: 'bottom',
            color: '#fff',
            fontSize: isLandscape ? 9 : 10,
            fontWeight: 500,
            formatter: dates[dates.length - 1]
          },
          animationDuration: 1500,
          animationDelay: 1500,
          xAxisIndex: 1,
          yAxisIndex: 2
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
  }, [data, isLandscape]);

  return (
    <div className="w-full h-full">
      <div ref={chartRef} className="w-full h-full" />
    </div>
  );
}
