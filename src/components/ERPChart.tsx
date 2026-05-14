import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import {
  getDates,
  getERPValues,
  getMeanValues,
  getSigmaUpper,
  getSigmaLower,
  getIndexValues,
  getTotalReturnValues,
  ERPDataItem
} from '../data/erpData';
import { getIndexConfig } from '../data/indexConfig';

interface ERPChartProps {
  data: ERPDataItem[];
  indexId?: string;
  isLandscape?: boolean;
}

export function ERPChart({ data, indexId = 'hs300', isLandscape = false }: ERPChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  
  const config = getIndexConfig(indexId);

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
    const indexValues = getIndexValues(data);
    const totalReturnValues = getTotalReturnValues(data);

    // 计算自适应的ERP轴范围
    const minERP = Math.min(...erpValues);
    const maxERP = Math.max(...erpValues);
    const erpPadding = (maxERP - minERP) * 0.15;
    
    // 计算自适应的指数轴范围
    const minIndex = Math.min(...indexValues, ...totalReturnValues);
    const maxIndex = Math.max(...indexValues, ...totalReturnValues);
    const indexPadding = (maxIndex - minIndex) * 0.1;

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
        }
      },
      legend: {
        data: [
          { name: 'ERP', icon: 'circle' },
          { name: config.displayName, icon: 'circle' },
          { name: config.totalReturnName, icon: 'circle' },
          { name: '均值线', icon: 'path://M0,5 L30,5', iconKeepGlyph: true },
          { name: '+1σ', icon: 'path://M0,5 L30,5', iconKeepGlyph: true },
          { name: '-1σ', icon: 'path://M0,5 L30,5', iconKeepGlyph: true },
        ],
        textStyle: {
          color: '#94a3b8',
          fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 9 : 12)
        },
        top: isLandscape ? 5 : (window.innerWidth < 768 ? 5 : 10),
        left: isLandscape ? 15 : (window.innerWidth < 768 ? 5 : 20),
        itemWidth: isLandscape ? 12 : (window.innerWidth < 768 ? 8 : 12),
        itemHeight: isLandscape ? 6 : (window.innerWidth < 768 ? 8 : 6),
        itemGap: isLandscape ? 15 : (window.innerWidth < 768 ? 8 : 20),
        selected: {
          [config.totalReturnName]: false
        }
      },
      grid: {
        left: window.innerWidth < 768 ? '3%' : '5%',
        right: window.innerWidth < 768 ? '3%' : '5%',
        top: window.innerWidth < 768 ? '15%' : '12%',
        height: window.innerWidth < 768 ? '58%' : '65%',
        containLabel: true
      },
      xAxis: {
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
          rotate: window.innerWidth < 768 ? 45 : 0,
          interval: Math.floor(dates.length / 10),
          showMaxLabel: true
        },
        splitLine: {
          show: false
        }
      },
      yAxis: [
        {
          type: 'value',
          name: 'ERP %',
          nameTextStyle: {
            color: '#64748b',
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12)
          },
          min: Math.floor((minERP - erpPadding) * 2) / 2,
          max: Math.ceil((maxERP + erpPadding) * 2) / 2,
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
          name: config.displayName,
          nameTextStyle: {
            color: '#64748b',
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12)
          },
          min: Math.floor((minIndex - indexPadding) / 500) * 500,
          max: Math.ceil((maxIndex + indexPadding) / 500) * 500,
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
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: 0,
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          xAxisIndex: 0,
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
          textStyle: {
            color: '#94a3b8',
            fontSize: isLandscape ? 9 : (window.innerWidth < 768 ? 9 : 11)
          },
          showDataShadow: false,
          showDetail: false
        }
      ],
      series: [
        {
          name: config.displayName,
          type: 'line',
          yAxisIndex: 1,
          data: indexValues,
          lineStyle: {
            color: config.color,
            width: isLandscape ? 1.8 : 1.5,
            opacity: 0.9
          },
          showSymbol: false,
          smooth: 0.3,
          animationDuration: 0
        },
        {
          name: config.totalReturnName,
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
          name: '+1σ',
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
          name: '-1σ',
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
  }, [data, indexId, isLandscape, config]);

  return (
    <div className="w-full h-full">
      <div ref={chartRef} className="w-full h-full" />
    </div>
  );
}
