import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import QueryInput from './QueryInput';
import QueryHistory from './QueryHistory';
import VisualizationPanel from './VisualizationPanel';
import LanguageSelector from './LanguageSelector';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { t } from '../services/language';

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  }),
);

function MainLayout({ onLogout }) {
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  const saveQueryToHistory = (query, result) => {
    const historyKey = 'data_agent_query_history';
    const historyItem = {
      query,
      visualization: result.visualization_type || 'line',
      timestamp: new Date().toISOString()
    };

    try {
      const savedHistory = JSON.parse(localStorage.getItem(historyKey) || '[]');
      savedHistory.unshift(historyItem);
      // Ограничиваем историю последними 50 запросами
      const limitedHistory = savedHistory.slice(0, 50);
      localStorage.setItem(historyKey, JSON.stringify(limitedHistory));
    } catch (error) {
      console.error('Ошибка при сохранении истории запросов:', error);
    }
  };

  const handleQueryResult = (result) => {
    // Проверяем наличие result и его основных свойств
    const safeResult = result ? {
      ...result,
      visualization: result.visualization || null,
      data: result.data || [],
      sql_query: result.sql_query || '',
      title: result.title || 'Результаты запроса',
      description: result.description || ''
    } : null;
  
    // Логирование для отладки
    console.log('Safe Query Result:', safeResult);
  
    setQueryResult(safeResult);
    setLoading(false);
    setError(null);
  };

  const handleQueryStart = () => {
    setLoading(true);
    setError(null);
  };

  const handleQueryError = (errorMessage) => {
    setLoading(false);
    setError(errorMessage);
  };

  const handleSelectQueryFromHistory = (query) => {
    // TODO: Реализуйте логику выполнения запроса из истории
    // Например, можно вызвать метод отправки запроса в QueryInput
  };

  const handleSnackbarClose = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="fixed">
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {t('common', 'appName')}
          </Typography>
          
          <LanguageSelector />
          
          <QueryHistory 
            onSelectQuery={handleSelectQueryFromHistory} 
          />
        </Toolbar>
      </AppBar>
      <Main>
        <Toolbar />
        <Container maxWidth="xl">
          <Box sx={{ my: 2 }}>
            <QueryInput 
              onQueryResult={handleQueryResult}
              onQueryStart={handleQueryStart}
              onQueryError={handleQueryError}
              showSnackbar={showSnackbar}
            />
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <VisualizationPanel 
              queryResult={queryResult}
              loading={loading}
              error={error}
            />
          </Box>
        </Container>
      </Main>

      {/* Snackbar для уведомлений */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={4000} 
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleSnackbarClose} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default MainLayout;