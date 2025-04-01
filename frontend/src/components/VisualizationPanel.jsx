import React, { useMemo } from 'react';
import { Paper, Typography, Box, Tabs, Tab, CircularProgress, Alert } from '@mui/material';
import Plot from 'react-plotly.js';
import * as Plotly from 'plotly.js';  // Change the import to this

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
  const [tabValue, setTabValue] = React.useState(0);
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Memoized figure with useMemo
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
      
      {/* Other tab panels remain the same */}
    </Paper>
  );
}

// Global Plotly configuration
Plotly.setPlotConfig({
  displayModeBar: true,
  staticPlot: false,
  doubleClick: 'reset+autosize',
  showTips: false,
  displaylogo: false,
  scrollZoom: true,
  responsive: true
});

export default React.memo(VisualizationPanel);