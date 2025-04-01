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
const root = ReactDOM.createRoot(document.getElementById('root'));

// Рендеринг приложения
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);


window.onerror = function(message, source, lineno, colno, error) {
  console.error("Global error:", message, "at", source, ":", lineno, ":", colno);
  console.error("Error details:", error);
  
  // Показать сообщение пользователю
  if (document.getElementById('root')) {
    document.getElementById('root').innerHTML = `
      <div style="padding: 20px; color: red; text-align: center;">
        <h2>Произошла ошибка при загрузке приложения</h2>
        <p>${message}</p>
        <p>Пожалуйста, обновите страницу или обратитесь к администратору.</p>
      </div>
    `;
  }
  
  return true; // Предотвращает стандартное поведение ошибки
};