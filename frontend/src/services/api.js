// src/services/api.js
import axios from 'axios';

// Создание экземпляра axios с базовым URL
const apiClient = axios.create({
  baseURL: 'http://localhost:9000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});


apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    
    const errorMessage = error.response?.data?.detail 
      || error.message 
      || 'Произошла ошибка при выполнении запроса';
    
    console.error('API Error:', errorMessage, error);
    
    return Promise.reject({
      message: errorMessage,
      statusCode: error.response?.status || 500,
      originalError: error
    });
  }
);

// Кэш для запросов к API
const apiCache = {
  _store: {},
  
  // Получение данных из кэша
  get(key) {
    const item = this._store[key];
    if (!item) return null;
    
    // Проверяем, не истекло ли время жизни кэша
    if (Date.now() > item.expiry) {
      delete this._store[key];
      return null;
    }
    
    return item.data;
  },
  
  // Сохранение данных в кэш
  set(key, data, ttl = 300000) { // ttl по умолчанию 5 минут
    this._store[key] = {
      data,
      expiry: Date.now() + ttl
    };
  },
  
  // Очистка кэша
  clear() {
    this._store = {};
  }
};

/**
 * Обрабатывает запрос на анализ данных с кэшированием
 * 
 * @param {string} query - Текстовый запрос пользователя
 * @param {Object} options - Дополнительные опции запроса
 * @returns {Promise} Промис с результатом запроса
 */
export const analyzeQuery = async (query, options = {}) => {
  const response = await fetch('http://localhost:9000/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, ...options }),
  });

  if (!response.ok) {
    throw new Error('Ошибка при выполнении запроса');
  }

  return response.json();
};

/**
 * Получает метаданные базы данных с кэшированием
 * 
 * @param {string} tableName - Имя таблицы для получения метаданных (опционально)
 * @returns {Promise} Промис с результатом запроса
 */
export const getDbMetadata = async (tableName = null) => {
  try {
    const params = tableName ? { table_name: tableName } : {};
    
    // Создаем ключ для кэша
    const cacheKey = `metadata:${tableName || 'all'}`;
    
    // Проверяем кэш
    const cachedData = apiCache.get(cacheKey);
    if (cachedData) {
      return cachedData;
    }
    
    const response = await apiClient.get('/metadata', { params });
    
    // Сохраняем результат в кэш на 1 час
    apiCache.set(cacheKey, response.data, 3600000);
    
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
    const { pageSize = 100, page = 1, useCache = true } = options;
    
    // Создаем ключ для кэша
    const cacheKey = `sql:${sqlQuery}:${pageSize}:${page}`;
    
    // Проверяем кэш, если разрешено использование кэша
    if (useCache) {
      const cachedData = apiCache.get(cacheKey);
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await apiClient.post('/execute-sql', {
      sql_query: sqlQuery,
      pagination: {
        page_size: pageSize,
        page
      }
    });
    
    // Сохраняем результат в кэш
    if (useCache) {
      apiCache.set(cacheKey, response.data);
    }
    
    return response.data;
  } catch (error) {
    console.error('Ошибка при выполнении SQL-запроса:', error);
    throw error;
  }
};

export default apiClient;