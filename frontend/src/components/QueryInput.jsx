import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, FormControl, InputLabel, Select, MenuItem, Divider } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import HistoryIcon from '@mui/icons-material/History';
import { analyzeQuery } from '../services/api';
import { t } from '../services/language';

const DEFAULT_PAGE_SIZE = 100;

function QueryInput({ onQueryResult, onQueryStart, onQueryError }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    if (onQueryStart) {
      onQueryStart();
    }
    
    try {
      // Добавляем запрос в историю
      const newHistory = [query, ...queryHistory.filter(q => q !== query)].slice(0, 10);
      setQueryHistory(newHistory);
      localStorage.setItem('query_history', JSON.stringify(newHistory));
      
      // Передаем размер страницы как параметр
      const result = await analyzeQuery(query, { pageSize });
      
      if (onQueryResult) {
        onQueryResult(result);
      }
    } catch (err) {
      const errorMessage = err.message || t('dashboard', 'queryError');
      setError(errorMessage);
      
      if (onQueryError) {
        onQueryError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleHistorySelect = (historicalQuery) => {
    setQuery(historicalQuery);
    setShowHistory(false);
  };
  
  // Загружаем историю запросов при монтировании компонента
  React.useEffect(() => {
    const savedHistory = localStorage.getItem('query_history');
    if (savedHistory) {
      try {
        setQueryHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Ошибка при загрузке истории запросов:', e);
      }
    }
  }, []);

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          {t('dashboard', 'askQuestion')}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
            <InputLabel id="page-size-label">Строк</InputLabel>
            <Select
              labelId="page-size-label"
              value={pageSize}
              label="Строк"
              onChange={(e) => setPageSize(e.target.value)}
              disabled={loading}
            >
              <MenuItem value={50}>50</MenuItem>
              <MenuItem value={100}>100</MenuItem>
              <MenuItem value={500}>500</MenuItem>
              <MenuItem value={1000}>1000</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<HistoryIcon />}
            onClick={() => setShowHistory(!showHistory)}
            disabled={queryHistory.length === 0}
          >
            История
          </Button>
        </Box>
      </Box>
      
      {showHistory && queryHistory.length > 0 && (
        <Box sx={{ mb: 2, maxHeight: '150px', overflowY: 'auto' }}>
          <Paper variant="outlined" sx={{ p: 1 }}>
            {queryHistory.map((historyItem, index) => (
              <React.Fragment key={index}>
                <Box 
                  sx={{
                    p: 1, 
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover'
                    }
                  }}
                  onClick={() => handleHistorySelect(historyItem)}
                >
                  <Typography noWrap variant="body2">{historyItem}</Typography>
                </Box>
                {index < queryHistory.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </Paper>
        </Box>
      )}
      
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
          <TextField
            fullWidth
            variant="outlined"
            label={t('dashboard', 'queryPlaceholder')}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            multiline
            rows={2}
            disabled={loading}
            sx={{ mr: 2 }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            startIcon={<SendIcon />}
            disabled={loading || !query.trim()}
            sx={{ height: '56px' }}
          >
            {loading ? t('dashboard', 'processingQuery') : t('dashboard', 'sendQuery')}
          </Button>
        </Box>
      </form>
      
      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {error}
        </Typography>
      )}
    </Paper>
  );
}

export default QueryInput;