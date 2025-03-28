// src/services/api.js
import axios from 'axios';
import { AuthService } from './auth';

// Создание экземпляра axios с базовым URL
const apiClient = axios.create({
  baseURL: 'http://localhost:9000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Перехватчик для добавления токена авторизации
apiClient.interceptors.request.use(
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

// Перехватчик для обработки ответов
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Обработка ошибки авторизации
    if (error.response && error.response.status === 401) {
      AuthService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Обрабатывает запрос на анализ данных
 * 
 * @param {string} query - Текстовый запрос пользователя
 * @param {Object} options - Дополнительные опции запроса
 * @returns {Promise} Промис с результатом запроса
 */
export const analyzeQuery = async (query, options = {}) => {
  try {
    const { pageSize = 100, page = 1, visualizationType, filters } = options;
    
    const response = await apiClient.post('/analyze', {
      query,
      visualization_type: visualizationType,
      filters,
      pagination: {
        page_size: pageSize,
        page
      }
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Ошибка сервера');
    } else if (error.request) {
      throw new Error('Проблема с сетевым соединением');
    } else {
      throw new Error('Ошибка при формировании запроса');
    }
  }
};

/**
 * Получает метаданные базы данных
 * 
 * @param {string} tableName - Имя таблицы для получения метаданных (опционально)
 * @returns {Promise} Промис с результатом запроса
 */
export const getDbMetadata = async (tableName = null) => {
  try {
    const params = tableName ? { table_name: tableName } : {};
    const response = await apiClient.get('/metadata', { params });
    return response.data;
  } catch (error) {
    console.error('Ошибка при получении метаданных:', error);
    throw error;
  }
};

/**
 * Выполняет произвольный SQL-запрос
 * 
 * @param {string} sqlQuery - SQL-запрос для выполнения
 * @param {Object} options - Дополнительные опции запроса
 * @returns {Promise} Промис с результатом запроса
 */
export const executeSqlQuery = async (sqlQuery, options = {}) => {
  try {
    const { pageSize = 100, page = 1 } = options;
    
    const response = await apiClient.post('/execute-sql', {
      sql_query: sqlQuery,
      pagination: {
        page_size: pageSize,
        page
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Ошибка при выполнении SQL-запроса:', error);
    throw error;
  }
};

export default apiClient;