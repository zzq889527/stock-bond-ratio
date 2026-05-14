import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import {
  getDates,
  getPBValues,
  getIndexValues,
  ERPDataItem
} from '../data/erpData';
import { getIndexConfig } from '../data/indexConfig';

interface ValuationChartProps {
  data: ERPDataItem[];
  indexId?: string;
  isLandscape?: boolean;
}

export function PBChart({ data, indexId = 'hs300', isLandscape = false }: ValuationChartProps) {
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
    chartInstance.current.group = 'valuationGroup';

    const dates = getDates(data);
    const pbValues = getPBValues(data);
    const indexValues = getIndexValues(data);

    const meanVal = pbValues.reduce((a, b) => a + b, 0) / pbValues.length;
    const stdVal = Math.sqrt(pbValues.reduce((sq, v) => sq + (v - meanVal) ** 2, 0) / pbValues.length);
    const currentVal = pbValues[pbValues.length - 1];
    const percentile = (pbValues.filter(v => v <= currentVal).length / pbValues.length * 100).toFixed(0);

    const meanLine = pbValues.map(() => meanVal);
    const sigmaUpper = pbValues.map(() => meanVal + stdVal);
    const sigmaLower = pbValues.map(() => meanVal - stdVal);

    const minVal = Math.min(...pbValues);
    const maxVal = Math.max(...pbValues);
    const valPadding = (maxVal - minVal) * 0.15;

    const minIndex = Math.min(...indexValues);
    const maxIndex = Math.max(...indexValues);
    const indexPadding = (maxIndex - minIndex) * 0.1;

    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      color: ['#a855f7', config.color, '#6b7280', '#22c55e', '#ef4444'],
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
          { name: 'PB', icon: 'circle' },
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
          name: 'PB',
          nameTextStyle: {
            color: '#64748b',
            fontSize: isLandscape ? 11 : (window.innerWidth < 768 ? 10 : 12)
          },
          min: Math.max(0, Math.floor((minVal - valPadding) * 2) / 2),
          max: Math.ceil((maxVal + valPadding) * 2) / 2,
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
            formatter: '{value}x'
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
          fillerColor: 'rgba(168, 85, 247, 0.2)',
          handleStyle: {
            color: '#a855f7',
            borderColor: '#c084fc'
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
          name: 'PB',
          type: 'line',
          data: pbValues,
          lineStyle: {
            color: '#a855f7',
            width: isLandscape ? 2.5 : 2.5,
            opacity: 1
          },
          showSymbol: false,
          smooth: 0.35,
          animationDuration: 0,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(168, 85, 247, 0.35)' },
              { offset: 1, color: 'rgba(168, 85, 247, 0.05)' }
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
            width: isLandscape ? 1.8 : 1.5,
            opacity: 0.9
          },
          showSymbol: false,
          smooth: 0.3,
          animationDuration: 0
        },
        {
          name: '均值线',
          type: 'line',
          data: meanLine,
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
          name: '当前PB',
          type: 'scatter',
          data: [[dates.length - 1, currentVal]],
          symbol: 'circle',
          symbolSize: isLandscape ? 8 : 10,
          itemStyle: {
            color: '#a855f7',
            borderColor: '#fff',
            borderWidth: 2,
            shadowColor: 'rgba(168, 85, 247, 0.6)',
            shadowBlur: 10
          },
          label: {
            show: true,
            position: 'right',
            offset: [isLandscape ? 10 : 5, 0],
            color: '#a855f7',
            fontSize: isLandscape ? 11 : 12,
            fontWeight: 'bold',
            formatter: `${currentVal.toFixed(2)}x · ${percentile}分位`
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

      const visVals = pbValues.slice(startIdx, endIdx);
      const visIdx = indexValues.slice(startIdx, endIdx);
      const vMin = Math.min(...visVals);
      const vMax = Math.max(...visVals);
      const vPad = (vMax - vMin) * 0.15;
      const iMin = Math.min(...visIdx);
      const iMax = Math.max(...visIdx);
      const iPad = (iMax - iMin) * 0.1;

      chartInstance.current.setOption({
        yAxis: [{
          min: Math.max(0, Math.floor((vMin - vPad) * 2) / 2),
          max: Math.ceil((vMax + vPad) * 2) / 2
        }, {
          min: Math.floor((iMin - iPad) / 500) * 500,
          max: Math.ceil((iMax + iPad) / 500) * 500
        }]
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