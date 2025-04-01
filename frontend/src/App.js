import React, { useState, useEffect } from 'react';
import { Box, CircularProgress } from '@mui/material';
import MainLayout from './components/MainLayout';
import LoginPage from './components/LoginPage';
import { AuthService } from './services/auth';
import { QueryClient, QueryClientProvider } from 'react-query';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      retry: 1, // Ограничиваем количество повторных попыток
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000) // Экспоненциальная задержка
    },
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      try {
        const authenticated = AuthService.isAuthenticated();
        setIsAuthenticated(authenticated);
      } catch (error) {
        console.error('Ошибка при проверке аутентификации:', error);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    try {
      AuthService.logout();
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Ошибка при выходе:', error);
    }
  };

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

  return (
    <QueryClientProvider client={queryClient}>
      <MainLayout 
        onLogout={handleLogout} 
        // Раскомментируйте следующую строку для полной аутентификации
        // isAuthenticated={isAuthenticated}
      />
    </QueryClientProvider>
  );
}

export default App;