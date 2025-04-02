import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { Paper, Typography, Box, Tabs, Tab, CircularProgress, Alert, Switch, FormControlLabel } from '@mui/material';
import Plot from 'react-plotly.js';
// eslint-disable-next-line no-unused-vars
import * as Plotly from 'plotly.js';
import { t } from '../services/language';

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

function VisualizationPanel({ queryResult, loading, error }) {
  const [tabValue, setTabValue] = useState(0);
  const [showDataLabels, setShowDataLabels] = useState(false);
  
  // Обработчик изменения вкладки
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Обработчик переключения отображения меток данных
  const handleToggleDataLabels = (event) => {
    setShowDataLabels(event.target.checked);
  };
  
  // Оборачиваем функцию в useCallback
  const createMultiSeriesData = useCallback((rawData) => {
    if (!rawData || !Array.isArray(rawData) || rawData.length === 0) {
      return [];
    }
    
    // Получаем все доступные колонки из данных
    const columns = Object.keys(rawData[0]);
    
    // Ищем колонку с датами/категориями (обычно это первая колонка)
    const xColumn = columns.find(col => 
      col.toLowerCase().includes('month') || 
      col.toLowerCase().includes('date') || 
      col.toLowerCase().includes('time') ||
      col.toLowerCase().includes('period')
    ) || columns[0];
    
    // Получаем все числовые колонки (кроме колонки с датами)
    const numericColumns = columns.filter(col => {
      // Проверяем, что колонка содержит числовые значения
      return col !== xColumn && typeof rawData[0][col] === 'number';
    });
    
    // Создаем серии данных для каждой числовой колонки
    return numericColumns.map(col => {
      // Преобразуем название колонки в более читаемый формат
      const seriesName = col
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase());
      
      return {
        x: rawData.map(item => item[xColumn]),
        y: rawData.map(item => item[col]),
        type: 'scatter',
        mode: 'lines+markers',
        name: seriesName,
        hovertemplate: `${seriesName}: %{y}<extra></extra>`
      };
    });
  }, []); // Пустой массив зависимостей, так как функция не зависит от состояния компонента
  

  // Безопасное создание memoizedFigure с проверками
  const memoizedFigure = useMemo(() => {
    if (queryResult?.visualization) {
      try {
        return typeof queryResult.visualization === 'object' 
          ? queryResult.visualization 
          : JSON.parse(queryResult.visualization);
      } catch (e) {
        console.error('Failed to parse figure data', e);
        return null;
      }
    }
    return null;
  }, [queryResult?.visualization]);
  


  const updatedFigure = useMemo(() => {
    // Если есть сырые данные запроса, используем их напрямую
    if (queryResult?.data && Array.isArray(queryResult.data) && queryResult.data.length > 0) {
      const seriesData = createMultiSeriesData(queryResult.data);
      
      // Цветовая палитра для графиков
      const colors = [
        '#1976d2',   // основной синий
        '#ff5722',   // оранжевый
        '#4caf50',   // зеленый
        '#9c27b0',   // фиолетовый
        '#ff9800',   // оранжевый акцент
        '#2196f3',   // голубой
      ];
      
      const styledData = seriesData.map((series, index) => ({
        ...series,
        mode: showDataLabels ? 'lines+markers+text' : 'lines+markers',
        marker: { 
          color: colors[index % colors.length],
          size: 8
        },
        line: {
          width: 2,
          color: colors[index % colors.length]
        },
        text: showDataLabels ? series.y : undefined,
        textposition: 'top center',
        textfont: {
          family: 'Arial, sans-serif',
          size: 12,
          color: colors[index % colors.length]
        }
      }));
      
      return {
        data: styledData,
        layout: {
          title: queryResult.title || 'Динамика показателей',
          xaxis: {
            title: 'Период',
            tickangle: -45
          },
          yaxis: {
            title: 'Значение'
          },
          legend: { 
            x: 1.05,
            y: 1,
            xanchor: 'left',
            yanchor: 'top'
          },
          margin: {
            r: 150  // Увеличиваем правый отступ для легенды
          },
          hovermode: 'closest',
          plot_bgcolor: 'white',
          showlegend: true
        }
      };
    }
    
    // Если нет сырых данных или если уже есть преобразованная фигура, используем старую логику
    if (!memoizedFigure || !memoizedFigure.data) {
      return null;
    }
    
    // Цветовая палитра для графиков
    const colors = [
      '#1976d2',   // основной синий
      '#ff5722',   // оранжевый
      '#4caf50',   // зеленый
      '#9c27b0',   // фиолетовый
      '#ff9800',   // оранжевый акцент
      '#2196f3',   // голубой
    ];
  
    // Обновляем каждый трек, добавляя уникальные настройки
    const updatedData = Array.isArray(memoizedFigure.data) 
      ? memoizedFigure.data.map((trace, index) => ({
          ...trace,
          type: trace.type || 'scatter',
          mode: showDataLabels ? 'lines+markers+text' : 'lines+markers', // Включаем текстовые метки
          marker: { 
            ...(trace.marker || {}),
            color: colors[index % colors.length],
            size: 8
          },
          line: {
            ...(trace.line || {}),
            width: 2,
            color: colors[index % colors.length]
          },
          // Добавляем текстовые метки
          text: showDataLabels ? trace.y : undefined,
          textposition: 'top center',
          textfont: {
            family: 'Arial, sans-serif',
            size: 12,
            color: colors[index % colors.length]
          },
          // Переводим название колонки в более читаемый формат
          name: trace.name 
            ? trace.name
            : trace.label || 
              (typeof trace.y === 'object' && trace.y.name) || 
              `Показатель ${index + 1}`
        }))
      : [memoizedFigure.data].map((trace, index) => ({
          // То же самое, что и выше, для случая, когда memoizedFigure.data не является массивом
          ...trace,
          type: trace.type || 'scatter',
          mode: showDataLabels ? 'lines+markers+text' : 'lines+markers',
          marker: { 
            ...(trace.marker || {}),
            color: colors[index % colors.length],
            size: 8
          },
          line: {
            ...(trace.line || {}),
            width: 2,
            color: colors[index % colors.length]
          },
          text: showDataLabels ? trace.y : undefined,
          textposition: 'top center',
          textfont: {
            family: 'Arial, sans-serif',
            size: 12,
            color: colors[index % colors.length]
          },
          name: trace.name 
            ? trace.name
            : trace.label || 
              (typeof trace.y === 'object' && trace.y.name) || 
              `Показатель ${index + 1}`
        }));
  
    // Обновляем макет для лучшей читаемости
    const updatedLayout = {
      ...(memoizedFigure.layout || {}),
      title: memoizedFigure.layout?.title || 'Динамика показателей',
      xaxis: {
        ...(memoizedFigure.layout?.xaxis || {}),
        title: memoizedFigure.layout?.xaxis?.title || 'Период',
        tickangle: -45
      },
      yaxis: {
        ...(memoizedFigure.layout?.yaxis || {}),
        title: memoizedFigure.layout?.yaxis?.title || 'Значение',
      },
      legend: { 
        x: 1.05,
        y: 1,
        xanchor: 'left',
        yanchor: 'top'
      },
      margin: {
        ...(memoizedFigure.layout?.margin || {}),
        r: 150  // Увеличиваем правый отступ для легенды
      }
    };
  
    return {
      ...memoizedFigure,
      data: updatedData,
      layout: updatedLayout
    };
  }, [memoizedFigure, showDataLabels, queryResult]);

  // Plotly configuration
  const plotlyConfig = useMemo(() => ({
    displaylogo: false,
    modeBarButtonsToRemove: [
      'sendDataToCloud', 
      'autoScale2d', 
      'resetScale2d', 
      'toggleSpikelines',
      'hoverClosestCartesian', 
      'hoverCompareCartesian'
    ],
    responsive: true,
    toImageButtonOptions: {
      format: 'png',
      filename: 'chart',
      height: 500,
      width: 700
    }
  }), []);

  // Visualization tab rendering
  const renderVisualizationTab = useMemo(() => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
          <CircularProgress />
        </Box>
      );
    } 
    
    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      );
    } 
    
    // Проверяем, что updatedFigure существует и содержит данные
    if (updatedFigure && updatedFigure.data && updatedFigure.data.length > 0) {
      return (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={showDataLabels}
                  onChange={handleToggleDataLabels}
                  color="primary"
                />
              }
              label={t('dashboard', 'showDataLabels') || "Показывать значения"}
            />
          </Box>
          <div id="plotContainer">
          <Plot
            data={updatedFigure?.data || []}
            layout={{
              ...(updatedFigure?.layout || {}),
              autosize: true,
              height: 500
            }}
            config={plotlyConfig}
            style={{ width: '100%', height: 500 }}
            useResizeHandler={true}
          />
          </div>
        </>
      );
    }
    
    // Показываем сообщение, если нет данных для визуализации
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px', flexDirection: 'column' }}>
        <Typography variant="body1" align="center" sx={{ mt: 4 }}>
          {queryResult ? "Нет данных для визуализации" : "Введите запрос для отображения данных"}
        </Typography>
      </Box>
    );
  }, [loading, error, updatedFigure, plotlyConfig, showDataLabels, queryResult]);

  // Data tab rendering
  const renderDataTab = useMemo(() => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      );
    }
    
    if (queryResult?.data && queryResult.data.length > 0) {
      // Получаем заголовки столбцов из первого объекта
      const headers = Object.keys(queryResult.data[0]);
      
      return (
        <Box sx={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                {headers.map((header, index) => (
                  <th key={index} style={{ padding: '8px 16px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {queryResult.data.map((row, rowIndex) => (
                <tr key={rowIndex} style={{ borderBottom: '1px solid #eee' }}>
                  {headers.map((header, cellIndex) => (
                    <td key={cellIndex} style={{ padding: '8px 16px' }}>
                      {row[header] !== null && row[header] !== undefined ? String(row[header]) : ''}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      );
    }
    
    return (
      <Typography>Нет данных для отображения</Typography>
    );
  }, [queryResult?.data, loading, error]);

  // SQL Query tab rendering
  const renderSqlQueryTab = useMemo(() => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (queryResult?.sql_query) {
      return (
        <Box sx={{ 
          backgroundColor: '#f5f5f5', 
          padding: 2, 
          borderRadius: 1,
          overflowX: 'auto',
          fontFamily: '"Roboto Mono", monospace'
        }}>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {queryResult.sql_query}
          </pre>
          
          {queryResult.explanation && (
            <Box sx={{ mt: 3, p: 2, backgroundColor: '#e3f2fd', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Объяснение запроса:
              </Typography>
              <Typography variant="body2">
                {queryResult.explanation}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }
    
    return (
      <Typography>SQL-запрос будет отображен после выполнения запроса</Typography>
    );
  }, [queryResult?.sql_query, queryResult?.explanation, loading]);

  useEffect(() => {
    if (queryResult?.data && queryResult.data.length > 0) {
      console.log('Raw data:', queryResult.data);
      console.log('Generated series:', createMultiSeriesData(queryResult.data));
      console.log('Styled figure:', updatedFigure);
    }
  }, [queryResult, updatedFigure, createMultiSeriesData]);

  return (
    <Paper elevation={3} sx={{ p: 2, height: '600px' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label={t('dashboard', 'visualization') || "Визуализация"} {...a11yProps(0)} />
          <Tab label={t('dashboard', 'data') || "Данные"} {...a11yProps(1)} />
          <Tab label={t('dashboard', 'sqlQuery') || "SQL-запрос"} {...a11yProps(2)} />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0}>
        {renderVisualizationTab}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        {renderDataTab}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        {renderSqlQueryTab}
      </TabPanel>
    </Paper>
  );
}


export default React.memo(VisualizationPanel);