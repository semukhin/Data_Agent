import React, { useState } from 'react';
import { useMutation } from 'react-query';
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

  // Use react-query mutation for handling the query
  const mutation = useMutation(
    (queryData) => analyzeQuery(queryData.query, { pageSize: queryData.pageSize }),
    {
      onMutate: () => {
        setLoading(true);
        setError(null);
        onQueryStart && onQueryStart();
      },
      onSuccess: (data) => {
        // Add query to history
        const newHistory = [query, ...queryHistory.filter(q => q !== query)].slice(0, 10);
        setQueryHistory(newHistory);
        localStorage.setItem('query_history', JSON.stringify(newHistory));

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
    
    mutation.mutate({ query, pageSize });
  };

  // Load query history on component mount
  React.useEffect(() => {
    const savedHistory = localStorage.getItem('query_history');
    if (savedHistory) {
      try {
        setQueryHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Error loading query history:', e);
      }
    }
  }, []);

  const handleHistorySelect = (historicalQuery) => {
    setQuery(historicalQuery);
    setShowHistory(false);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      {/* Rest of the component remains the same as in your original implementation */}
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