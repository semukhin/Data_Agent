// src/services/auth.js
import axios from 'axios';

// Константы для работы с локальным хранилищем
const TOKEN_KEY = 'data_agent_auth_token';
const USER_KEY = 'data_agent_user';

// Создание экземпляра axios с базовым URL
const authClient = axios.create({
  baseURL: 'http://localhost:9000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Сервис авторизации пользователей
 */
export const AuthService = {
  /**
   * Выполняет вход пользователя
   * 
   * @param {string} username - Имя пользователя
   * @param {string} password - Пароль пользователя
   * @returns {Promise} Промис с результатом запроса
   */
  login: async (username, password) => {
    try {
      // Формируем тело запроса в формате x-www-form-urlencoded (требуется для OAuth2)
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      // Отправляем запрос к API для получения токена
      const response = await authClient.post('/api/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      if (response.data && response.data.access_token) {
        // Сохраняем токен в локальном хранилище
        localStorage.setItem(TOKEN_KEY, response.data.access_token);
        
        // Получаем информацию о пользователе
        const userResponse = await authClient.get('/api/me', {
          headers: {
            'Authorization': `Bearer ${response.data.access_token}`
          }
        });
        
        // Сохраняем данные пользователя
        localStorage.setItem(USER_KEY, JSON.stringify(userResponse.data));
        
        return { success: true, user: userResponse.data };
      } else {
        throw new Error('Токен не получен');
      }
    } catch (error) {
      console.error('Ошибка авторизации:', error);
      throw new Error(error.response?.data?.detail || 'Неверное имя пользователя или пароль');
    }
  },
  
  /**
   * Выполняет выход пользователя
   */
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
  
  /**
   * Проверяет, авторизован ли пользователь
   * 
   * @returns {boolean} Флаг авторизации
   */
  isAuthenticated: () => {
    return !!localStorage.getItem(TOKEN_KEY);
  },
  
  /**
   * Получает информацию о текущем пользователе
   * 
   * @returns {Object|null} Информация о пользователе или null
   */
  getCurrentUser: () => {
    if (!AuthService.isAuthenticated()) return null;
    
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch (error) {
      return null;
    }
  },
  
  /**
   * Получает токен авторизации
   * 
   * @returns {string|null} Токен авторизации или null
   */
  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  }
};

// Добавляем перехватчик запросов для добавления токена авторизации
authClient.interceptors.request.use(
  (config) => {
    const token = AuthService.getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default authClient;