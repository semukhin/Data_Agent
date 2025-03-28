// src/services/auth.js
import axios from 'axios';

// Константы для работы с локальным хранилищем
const TOKEN_KEY = 'data_agent_auth_token';
const USER_KEY = 'data_agent_user';

// Создание экземпляра axios с базовым URL
const authClient = axios.create({
  baseURL: 'http://localhost:8000/api',
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
    // В реальном приложении здесь был бы запрос к бэкенду
    // Для простой авторизации просто проверяем учетные данные
    if (username === 'atlantix' && password === 'atlantix') {
      // Создание имитации JWT токена (в реальном приложении это был бы настоящий JWT)
      const mockToken = btoa(JSON.stringify({
        username,
        role: 'admin',
        exp: new Date().getTime() + 86400000 // 24 часа
      }));
      
      // Сохранение данных пользователя и токена в локальном хранилище
      localStorage.setItem(TOKEN_KEY, mockToken);
      localStorage.setItem(USER_KEY, JSON.stringify({ username, role: 'admin' }));
      
      return { success: true, user: { username, role: 'admin' } };
    } else {
      throw new Error('Неверное имя пользователя или пароль');
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
    const token = localStorage.getItem(TOKEN_KEY);
    
    if (!token) return false;
    
    try {
      // Декодирование токена для проверки срока действия
      const decodedToken = JSON.parse(atob(token));
      const currentTime = new Date().getTime();
      
      if (decodedToken.exp < currentTime) {
        // Токен истек
        AuthService.logout();
        return false;
      }
      
      return true;
    } catch (error) {
      AuthService.logout();
      return false;
    }
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
    if (!AuthService.isAuthenticated()) return null;
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