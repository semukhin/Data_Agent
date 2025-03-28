// services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeQuery = async (query) => {
  try {
    const response = await apiClient.post('/analyze', { query });
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

export const getDbMetadata = async () => {
  try {
    const response = await apiClient.get('/metadata');
    return response.data;
  } catch (error) {
    console.error('Error fetching metadata:', error);
    throw error;
  }
};