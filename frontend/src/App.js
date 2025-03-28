import React, { useState, useEffect } from 'react';
import { Box, CircularProgress } from '@mui/material';
import MainLayout from './components/MainLayout';
import LoginPage from './components/LoginPage';
import { AuthService } from './services/auth';

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
    <>
      {isAuthenticated ? (
        <MainLayout onLogout={handleLogout} />
      ) : (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}
    </>
  );
}

export default App;