import React, { useEffect, useState } from 'react';
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
  const [figure, setFigure] = useState(null);
  
  // Конфигурация для удаления брендирования Plotly
  const plotlyConfig = {
    displaylogo: false,
    modeBarButtonsToRemove: [
      'sendDataToCloud', 
      'autoScale2d', 
      'resetScale2d', 
      'toggleSpikelines',
      'hoverClosestCartesian', 
      'hoverCompareCartesian'
    ],
    responsive: true
  };

  useEffect(() => {
    if (queryResult?.visualization) {
      try {
        // Если visualization уже в формате JSON-объекта, используем его напрямую
        if (typeof queryResult.visualization === 'object') {
          setFigure(queryResult.visualization);
        } else {
          // Иначе пытаемся распарсить из строки
          setFigure(JSON.parse(queryResult.visualization));
        }
      } catch (e) {
        console.error('Failed to parse figure data', e);
      }
    }
  }, [queryResult]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

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
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        ) : figure ? (
          <Plot
            data={figure.data}
            layout={{
              ...figure.layout,
              autosize: true,
              height: 500
            }}
            config={plotlyConfig} // Используем конфигурацию для удаления брендирования
            style={{ width: '100%', height: 500 }}
            useResizeHandler={true}
          />
        ) : (
          <Typography>Введите запрос для отображения данных</Typography>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : queryResult?.data ? (
          <Box sx={{ maxHeight: '500px', overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  {queryResult.data.length > 0 && 
                    Object.keys(queryResult.data[0]).map((key, index) => (
                      <th key={index} style={{ border: '1px solid #ddd', padding: '8px', backgroundColor: '#f2f2f2' }}>
                        {key}
                      </th>
                    ))
                  }
                </tr>
              </thead>
              <tbody>
                {queryResult.data.map((row, rowIndex) => (
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
        ) : (
          <Typography>Нет данных для отображения</Typography>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : queryResult?.sql_query ? (
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
        ) : (
          <Typography>SQL-запрос не доступен</Typography>
        )}
      </TabPanel>
    </Paper>
  );
}

export default VisualizationPanel;