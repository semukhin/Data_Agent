import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { Box, TextField, Button, IconButton, Tooltip } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { analyzeQuery } from '../services/api';
import { HistoryService } from '../services/historyService';
import { t } from '../services/language';
import QueryHistory from './QueryHistory';

const DEFAULT_PAGE_SIZE = 100;

function QueryInput({ onQueryResult, onQueryStart, onQueryError }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Use react-query mutation for handling the query
  const mutation = useMutation(
    (queryData) => analyzeQuery(queryData.query, { pageSize: DEFAULT_PAGE_SIZE }),
    {
      onMutate: () => {
        setLoading(true);
        setError(null);
        onQueryStart && onQueryStart();
      },
      onSuccess: (data) => {
        // Добавляем успешный запрос в историю
        HistoryService.addToHistory(
          query, 
          data.visualization_type || 'line',
          {
            title: data.title,
            visualization_type: data.visualization_type
          }
        );
        onQueryResult && onQueryResult(data);
      },
      onError: (error) => {
        setError(error.message || t('dashboard', 'queryError'));
        onQueryError && onQueryError(error.message);
      },
      onSettled: () => {
        setLoading(false);
      }
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    mutation.mutate({ query });
  };

  // Обработчик выбора запроса из истории
  const handleSelectFromHistory = (selectedQuery) => {
    setQuery(selectedQuery);
    // Опционально: можно сразу выполнить запрос
    // mutation.mutate({ query: selectedQuery });
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit} 
      sx={{ display: 'flex', alignItems: 'flex-start' }}
    >
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
      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
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
        
        {/* Кнопка истории запросов */}
        <QueryHistory onSelectQuery={handleSelectFromHistory} />
      </Box>
    </Box>
  );
}

export default React.memo(QueryInput);