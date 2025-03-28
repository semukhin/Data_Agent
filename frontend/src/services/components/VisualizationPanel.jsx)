import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box, Tabs, Tab, CircularProgress } from '@mui/material';
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

function VisualizationPanel({ visualizationData, loading, error }) {
  const [tabValue, setTabValue] = useState(0);
  const [figure, setFigure] = useState(null);

  useEffect(() => {
    if (visualizationData?.figure) {
      try {
        setFigure(JSON.parse(visualizationData.figure));
      } catch (e) {
        console.error('Failed to parse figure data', e);
      }
    }
  }, [visualizationData]);

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
          <Typography color="error">{error}</Typography>
        ) : figure ? (
          <Plot
            data={figure.data}
            layout={{
              ...figure.layout,
              autosize: true,
              height: 500
            }}
            style={{ width: '100%', height: 500 }}
            useResizeHandler={true}
          />
        ) : (
          <Typography>Введите запрос для отображения данных</Typography>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        {/* Таблица с данными */}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        {/* SQL-запрос и его объяснение */}
      </TabPanel>
    </Paper>
  );
}

export default VisualizationPanel;