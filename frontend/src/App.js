import React, { useState, useEffect } from 'react';
import { Box, CircularProgress } from '@mui/material';
import MainLayout from './components/MainLayout';
import LoginPage from './components/LoginPage';
import { AuthService } from './services/auth';
import { QueryClientProvider } from 'react-query';
import QueryInput from './components/QueryInput';
import './App.css';

const queryClient = new QueryClientProvider({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
      cacheTime: 30 * 60 * 1000,
    },
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Проверка аутентификации при загрузке приложения
  useEffect(() => {
    const checkAuth = () => {
      const authenticated = AuthService.isAuthenticated();
      setIsAuthenticated(authenticated);
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  // Обработчик успешной авторизации
  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  // Обработчик выхода из системы
  const handleLogout = () => {
    AuthService.logout();
    setIsAuthenticated(false);
  };

  // Отображение загрузки при проверке авторизации
  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        height: '100vh' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  // Отображение страницы авторизации или основного интерфейса
  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <header className="App-header">
          <h1>Data Agent</h1>
        </header>
        <main>
          <QueryInput 
            onQueryResult={(data) => console.log('Результат:', data)}
            onQueryStart={() => console.log('Запрос начат')}
            onQueryError={(error) => console.error('Ошибка:', error)}
          />
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;