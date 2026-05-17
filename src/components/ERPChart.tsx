import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import {
  getDates,
  getERPValues,
  getMeanValues,
  getSigmaUpper,
  getSigmaLower,
  getIndexValues,
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

  const hexToRgba = (hex: string, alpha: number) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    if (chartInstance.current) {
      chartInstance.current.dispose();
    }

    chartInstance.current = echarts.init(chartRef.current, 'dark', {
      renderer: 'canvas',
      devicePixelRatio: window.devicePixelRatio || 2
    });
    chartInstance.current.group = 'valuationGroup';

    const dates = getDates(data);
    const erpValues = getERPValues(data);
    const meanValues = getMeanValues(data);
    const sigmaUpper = getSigmaUpper(data);
    const sigmaLower = getSigmaLower(data);
    const indexValues = getIndexValues(data);

    const currentERP = erpValues[erpValues.length - 1];
    const erpPercentile = (erpValues.filter(v => v <= currentERP).length / erpValues.length * 100).toFixed(0);

    const minERP = Math.min(...erpValues);
    const maxERP = Math.max(...erpValues);
    const erpPadding = (maxERP - minERP) * 0.15;
    
    const minIndex = Math.min(...indexValues);
    const maxIndex = Math.max(...indexValues);
    const indexPadding = (maxIndex - minIndex) * 0.1;

    const logMinVal = Math.log10(Math.max(1, minIndex));
    const logMaxVal = Math.log10(maxIndex);
    const logRange = logMaxVal - logMinVal;
    const logPad = logRange * 0.1;
    const logMin = Number(Math.pow(10, logMinVal - logPad).toPrecision(2));
    const logMax = Number(Math.pow(10, logMaxVal + logPad).toPrecision(2));

    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      color: ['#3b82f6', '#6b7280', '#6b7280', '#22c55e', '#ef4444'],
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
          { name: '均值线', icon: 'rect' },
          { name: '+1σ', icon: 'rect' },
          { name: '-1σ', icon: 'rect' },
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
      },
      grid: {
        left: isLandscape ? '6%' : (window.innerWidth < 768 ? '6%' : '7%'),
        right: isLandscape ? '16%' : (window.innerWidth < 768 ? '14%' : '16%'),
        top: isLandscape ? '14%' : (window.innerWidth < 768 ? '18%' : '14%'),
        bottom: isLandscape ? '8%' : (window.innerWidth < 768 ? '16%' : '12%'),
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
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12),
            padding: [0, 0, 0, 40]
          },
          nameGap: 15,
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
          type: 'log',
          name: config.displayName,
          nameTextStyle: {
            color: '#64748b',
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12)
          },
          nameGap: 20,
          min: logMin,
          max: logMax,
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
            fontSize: isLandscape ? 9 : (window.innerWidth < 768 ? 8 : 10),
            showMinLabel: true,
            showMaxLabel: true,
            formatter: (value: number) => {
              if (value >= 10000) return (value / 10000).toFixed(1) + '万';
              if (value >= 1000) return (value / 1000).toFixed(1) + 'k';
              return value.toString();
            }
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
          fillerColor: 'rgba(59, 130, 246, 0.2)',
          handleStyle: {
            color: '#3b82f6',
            borderColor: '#60a5fa'
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
          name: 'ERP',
          type: 'line',
          data: erpValues,
          lineStyle: {
            color: '#3b82f6',
            width: isLandscape ? 2.5 : 2.5,
            opacity: 1
          },
          showSymbol: false,
          smooth: 0.35,
          animationDuration: 0,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(59, 130, 246, 0.35)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
            ])
          }
        },
        {
          name: config.displayName,
          type: 'line',
          yAxisIndex: 1,
          data: indexValues,
          lineStyle: {
            color: config.color,
            width: isLandscape ? 1.5 : 1.5,
            opacity: 0.85
          },
          showSymbol: false,
          smooth: 0.3,
          animationDuration: 0,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: config.color + '33' },
              { offset: 1, color: config.color + '08' }
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
            color: '#22c55e',
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
            color: '#ef4444',
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
            color: '#3b82f6',
            borderColor: '#fff',
            borderWidth: 2,
            shadowColor: 'rgba(59, 130, 246, 0.6)',
            shadowBlur: 10
          },
          label: {
            show: true,
            position: 'right',
            offset: [isLandscape ? 10 : 5, 0],
            color: '#3b82f6',
            fontSize: isLandscape ? 11 : 12,
            fontWeight: 'bold',
            formatter: `${currentERP.toFixed(2)}% · ${erpPercentile}分位`
          },
          animationDuration: 1500,
          animationDelay: 1000
        }
      ]
    };

    chartInstance.current.setOption(option);

    const handleDataZoom = () => {
      if (!chartInstance.current) return;
      const fullOption = chartInstance.current.getOption();
      const zoom = (fullOption.dataZoom as any[])[0];
      const start = zoom.start as number;
      const end = zoom.end as number;
      const totalLen = dates.length;
      const startIdx = Math.max(0, Math.floor(totalLen * start / 100));
      const endIdx = Math.min(totalLen, Math.ceil(totalLen * end / 100));

      const visERP = erpValues.slice(startIdx, endIdx);
      const visIdx = indexValues.slice(startIdx, endIdx);
      const vMin = Math.min(...visERP);
      const vMax = Math.max(...visERP);
      const vPad = (vMax - vMin) * 0.15;
      const iMin = Math.min(...visIdx);
      const iMax = Math.max(...visIdx);
      const iPad = (iMax - iMin) * 0.1;

      const visMean = visERP.reduce((a, b) => a + b, 0) / visERP.length;
      const visStd = Math.sqrt(visERP.reduce((sq, v) => sq + (v - visMean) ** 2, 0) / visERP.length);
      const visCur = visERP[visERP.length - 1];
      const visPct = (visERP.filter(v => v <= visCur).length / visERP.length * 100).toFixed(0);

      chartInstance.current.setOption({
        yAxis: [{
          type: 'value',
          min: Math.floor((vMin - vPad) * 2) / 2,
          max: Math.ceil((vMax + vPad) * 2) / 2
        }, {
          type: 'log',
          min: Number(Math.pow(10, Math.log10(Math.max(1, iMin)) - Math.log10(iMax / Math.max(1, iMin)) * 0.1).toPrecision(2)),
          max: Number(Math.pow(10, Math.log10(iMax) + Math.log10(iMax / Math.max(1, iMin)) * 0.1).toPrecision(2))
        }],
        series: [
          { name: '均值线', data: erpValues.map(() => +visMean.toFixed(2)) },
          { name: '+1σ', data: erpValues.map(() => +(visMean + visStd).toFixed(2)) },
          { name: '-1σ', data: erpValues.map(() => +(visMean - visStd).toFixed(2)) },
          { name: '当前ERP', data: [[dates.length - 1, visCur]], label: { formatter: `${visCur.toFixed(2)}% · ${visPct}分位` } }
        ]
      });
    };

    chartInstance.current.on('dataZoom', handleDataZoom);

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