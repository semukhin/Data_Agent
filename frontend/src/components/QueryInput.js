import React, { useState } from 'react';
import { useQuery, useMutation, QueryClient, QueryClientProvider } from 'react-query';
import { analyzeQuery } from '../services/api';

// Создание клиента запросов
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 минут
      cacheTime: 30 * 60 * 1000, // 30 минут
    },
  },
});

// Компонент ввода запроса с использованием React Query
function QueryInput({ onQueryResult, onQueryStart, onQueryError }) {
  const [query, setQuery] = useState('');
  const [pageSize, setPageSize] = useState(100);
  
  const mutation = useMutation(
    (queryData) => analyzeQuery(queryData.query, { pageSize: queryData.pageSize }),
    {
      onMutate: () => {
        onQueryStart && onQueryStart();
      },
      onSuccess: (data) => {
        onQueryResult && onQueryResult(data);
        // Добавляем результат в кэш для последующего использования
        queryClient.setQueryData(['analyzeQuery', query, pageSize], data);
      },
      onError: (error) => {
        onQueryError && onQueryError(error.message || 'Ошибка при выполнении запроса');
      }
    }
  );
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    // Проверяем, есть ли кэшированные данные
    const cachedData = queryClient.getQueryData(['analyzeQuery', query, pageSize]);
    if (cachedData) {
      // Если данные в кэше, используем их
      onQueryResult && onQueryResult(cachedData);
    } else {
      // Иначе делаем новый запрос
      mutation.mutate({ query, pageSize });
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Введите ваш запрос..."
      />
      <input
        type="number"
        value={pageSize}
        onChange={(e) => setPageSize(Number(e.target.value))}
        min="1"
        max="1000"
      />
      <button type="submit">Отправить</button>
    </form>
  );
}

export default QueryInput; 