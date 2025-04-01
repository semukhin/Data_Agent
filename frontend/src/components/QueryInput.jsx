import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { Box, TextField, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { analyzeQuery } from '../services/api';
import { t } from '../services/language';

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
  );
}

export default React.memo(QueryInput);