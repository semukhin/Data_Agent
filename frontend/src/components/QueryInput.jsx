import React, { useState, useEffect, useCallback } from 'react';
import { Box, TextField, Button, Paper, Typography, FormControl, InputLabel, Select, MenuItem, Divider, Alert } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import HistoryIcon from '@mui/icons-material/History';
import { analyzeQuery } from '../services/api';
import { t } from '../services/language';

const DEFAULT_PAGE_SIZE = 100;
const QUERY_CACHE_KEY = 'query_results_cache';

function QueryInput({ onQueryResult, onQueryStart, onQueryError }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [queryCache, setQueryCache] = useState(() => {
    // Инициализация кэша из localStorage
    const cachedResults = localStorage.getItem(QUERY_CACHE_KEY);
    return cachedResults ? JSON.parse(cachedResults) : {};
  });

  // Сохранение кэша в localStorage при изменении
  useEffect(() => {
    try {
      localStorage.setItem(QUERY_CACHE_KEY, JSON.stringify(queryCache));
    } catch (e) {
      console.error('Ошибка при сохранении кэша:', e);
    }
  }, [queryCache]);

  // Мемоизированная функция выполнения запроса
  const executeQuery = useCallback(async (queryText, options) => {
    try {
      const cacheKey = `${queryText}:${options.pageSize}`;
      
      // Проверяем, есть ли результат в кэше и не устарел ли он
      if (queryCache[cacheKey]) {
        const { timestamp, result } = queryCache[cacheKey];
        const now = Date.now();
        
        // Если кэш не старше 5 минут, используем его
        if (now - timestamp < 5 * 60 * 1000) {
          console.log('Используем кэшированный результат для запроса:', queryText);
          return result;
        }
      }
      
      // Если кэша нет или он устарел, выполняем запрос
      const result = await analyzeQuery(queryText, options);
      
      // Обновляем кэш
      setQueryCache(prevCache => ({
        ...prevCache,
        [cacheKey]: {
          timestamp: Date.now(),
          result
        }
      }));
      
      return result;
    } catch (error) {
      throw error;
    }
  }, [queryCache]);

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
      
      // Выполняем запрос с кэшированием
      const result = await executeQuery(query, { pageSize });
      
      if (onQueryResult) {
        onQueryResult(result);
      }
    } catch (err) {
      console.error('Ошибка при выполнении запроса:', err);
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
  useEffect(() => {
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
      
      {/* Остальной код компонента без изменений */}
      
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
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Paper>
  );
}

export default React.memo(QueryInput);