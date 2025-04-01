import React, { useEffect, useState, useMemo } from 'react';
import { Paper, Typography, Box, Tabs, Tab, CircularProgress, Alert } from '@mui/material';
import Plot from 'react-plotly.js';

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

function VisualizationPanel({ queryResult, loading, error }) {
  const [tabValue, setTabValue] = useState(0);
  
  // Оптимизация: используем мемоизацию для предотвращения излишних ререндеров
  const memoizedFigure = useMemo(() => {
    if (queryResult?.visualization) {
      try {
        // Если visualization уже в формате JSON-объекта, используем его напрямую
        if (typeof queryResult.visualization === 'object') {
          return queryResult.visualization;
        } else {
          // Иначе пытаемся распарсить из строки
          return JSON.parse(queryResult.visualization);
        }
      } catch (e) {
        console.error('Failed to parse figure data', e);
        return null;
      }
    }
    return null;
  }, [queryResult?.visualization]);
  
  // Оптимизация: предварительная компиляция конфигурации Plotly
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
  
  // Оптимизация: сокращение размера данных для таблицы и форматирование
  const displayData = useMemo(() => {
    if (!queryResult?.data || !Array.isArray(queryResult.data)) {
      return [];
    }
    
    return queryResult.data.slice(0, 100).map(row => {
      // Форматирование дат и чисел для лучшего отображения
      const formattedRow = {};
      Object.entries(row).forEach(([key, value]) => {
        if (value instanceof Date) {
          formattedRow[key] = new Date(value).toLocaleDateString('ru-RU');
        } else if (typeof value === 'number') {
          formattedRow[key] = Number.isInteger(value) 
            ? value.toLocaleString('ru-RU') 
            : value.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        } else {
          formattedRow[key] = value;
        }
      });
      return formattedRow;
    });
  }, [queryResult?.data]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Оптимизированная отрисовка вкладки визуализации
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
    
    if (memoizedFigure) {
      return (
        <Plot
          data={memoizedFigure.data}
          layout={{
            ...memoizedFigure.layout,
            autosize: true,
            height: 500
          }}
          config={plotlyConfig}
          style={{ width: '100%', height: 500 }}
          useResizeHandler={true}
        />
      );
    }
    
    return (
      <Typography>Введите запрос для отображения данных</Typography>
    );
  }, [loading, error, memoizedFigure, plotlyConfig]);
  
  // Оптимизированная отрисовка вкладки данных
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
        <Alert severity="error">{error}</Alert>
      );
    }
    
    if (queryResult?.data && queryResult.data.length > 0) {
      return (
        <Box sx={{ maxHeight: '500px', overflow: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {Object.keys(queryResult.data[0]).map((key, index) => (
                  <th key={index} style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f2f2f2' }}>
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {displayData.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {Object.values(row).map((value, cellIndex) => (
                    <td key={cellIndex} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {queryResult.pagination && (
            <Box sx={{ mt: 2, textAlign: 'right' }}>
              <Typography variant="body2">
                Показаны записи {(queryResult.pagination.page - 1) * queryResult.pagination.page_size + 1} - 
                {Math.min(queryResult.pagination.page * queryResult.pagination.page_size, queryResult.pagination.total)} из {queryResult.pagination.total}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }
    
    return (
      <Typography>Нет данных для отображения</Typography>
    );
  }, [loading, error, queryResult, displayData]);
  
  // Оптимизированная отрисовка вкладки SQL-запроса
  const renderSqlTab = useMemo(() => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (error) {
      return (
        <Alert severity="error">{error}</Alert>
      );
    }
    
    if (queryResult?.sql_query) {
      return (
        <Box>
          <Typography variant="h6" gutterBottom>SQL-запрос:</Typography>
          <pre style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '16px', 
            borderRadius: '4px',
            overflowX: 'auto',
            maxHeight: '200px'
          }}>
            {queryResult.sql_query}
          </pre>
          
          {queryResult.explanation && (
            <>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>Объяснение:</Typography>
              <Typography>{queryResult.explanation}</Typography>
            </>
          )}
        </Box>
      );
    }
    
    return (
      <Typography>SQL-запрос не доступен</Typography>
    );
  }, [loading, error, queryResult]);

  return (
    <Paper elevation={3} sx={{ p: 2, height: '600px' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Визуализация" />
          <Tab label="Данные" />
          <Tab label="SQL-запрос" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0}>
        {renderVisualizationTab}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        {renderDataTab}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        {renderSqlTab}
      </TabPanel>
    </Paper>
  );
}

// Глобальные настройки для всех графиков Plotly
Plotly.setPlotConfig({
  displayModeBar: true,
  staticPlot: false,
  doubleClick: 'reset+autosize',
  showTips: false,
  displaylogo: false,
  scrollZoom: true,
  responsive: true
});

// Более оптимальные настройки макета
const optimizedLayout = {
  autosize: true,
  font: { family: 'Arial, sans-serif' },
  margin: { l: 50, r: 30, t: 50, b: 50 },
  hovermode: 'closest',
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  modebar: {
    orientation: 'v',
    bgcolor: 'transparent',
    color: '#1976d2',
    activecolor: '#1565c0'
  }
};


export default React.memo(VisualizationPanel);