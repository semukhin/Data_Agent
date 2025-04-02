import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Создание темы приложения
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// Корневой элемент для рендеринга приложения
const rootElement = document.getElementById('root');

// Проверяем существование корневого элемента
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </React.StrictMode>
  );
} else {
  console.error('Root element not found');
}

// Глобальный обработчик ошибок
window.onerror = function(message, source, lineno, colno, error) {
  console.error("Global error:", message, "at", source, ":", lineno, ":", colno);
  console.error("Error details:", error);
  
  // Показать сообщение пользователю с более подробной информацией
  if (document.getElementById('root')) {
    document.getElementById('root').innerHTML = `
      <div style="padding: 20px; color: red; text-align: center;">
        <h2>Произошла критическая ошибка при загрузке приложения</h2>
        <p>Детали ошибки: ${message}</p>
        <p>Источник: ${source}</p>
        <p>Строка: ${lineno}</p>
        <p>Пожалуйста, обновите страницу или обратитесь к администратору.</p>
        <button onclick="window.location.reload()" style="margin-top: 20px; padding: 10px 20px;">Обновить страницу</button>
      </div>
    `;
  }
  
  return false; // Позволяем дефолтному обработчику ошибок сработать
};