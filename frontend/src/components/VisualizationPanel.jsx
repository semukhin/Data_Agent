import React, { useState, useMemo } from 'react';
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
  
  // Обновленный useMemo для updatedFigure с fallback
  const updatedFigure = useMemo(() => {
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
    const updatedData = (memoizedFigure.data || []).map((trace, index) => ({
      ...trace,
      type: trace.type || 'scatter',
      mode: trace.mode || 'lines+markers',
      marker: { 
        ...(trace.marker || {}),
        color: colors[index % colors.length],
        size: 8
      },
      line: {
        ...(trace.line || {}),
        width: 2
      },
      // Переводим название колонки в более читаемый формат
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
  }, [memoizedFigure]);

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
              data={updatedFigure.data}
              layout={{
                ...updatedFigure.layout,
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