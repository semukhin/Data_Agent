// src/services/historyService.js

// Константа для ключа хранения в localStorage
const QUERY_HISTORY_KEY = 'data_agent_query_history';

/**
 * Сервис для работы с историей запросов
 */
export const HistoryService = {
  /**
   * Получает историю запросов
   * 
   * @returns {Array} Массив запросов
   */
  getHistory: () => {
    try {
      const savedHistory = localStorage.getItem(QUERY_HISTORY_KEY);
      return savedHistory ? JSON.parse(savedHistory) : [];
    } catch (error) {
      console.error('Ошибка при получении истории запросов:', error);
      return [];
    }
  },
  
  /**
   * Добавляет запрос в историю
   * 
   * @param {string} query - Текст запроса
   * @param {string} visualization - Название типа визуализации
   * @param {Object} result - Результат запроса (опционально)
   */
  addToHistory: (query, visualization, result = null) => {
    try {
      const history = HistoryService.getHistory();
      
      // Ограничиваем размер истории до 50 записей
      if (history.length >= 50) {
        history.pop(); // Удаляем самый старый запрос
      }
      
      // Проверяем, есть ли такой запрос уже в истории
      const existingIndex = history.findIndex(item => item.query === query);
      
      if (existingIndex !== -1) {
        // Если запрос уже есть, обновляем его и перемещаем в начало
        history.splice(existingIndex, 1);
      }
      
      // Добавляем новый запрос в начало массива
      history.unshift({
        query,
        visualization,
        timestamp: Date.now(),
        result: result ? {
          title: result.title,
          type: result.visualization_type
        } : null
      });
      
      // Сохраняем обновленную историю
      localStorage.setItem(QUERY_HISTORY_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Ошибка при добавлении запроса в историю:', error);
    }
  },
  
  /**
   * Удаляет запрос из истории
   * 
   * @param {number} index - Индекс запроса для удаления
   */
  removeFromHistory: (index) => {
    try {
      const history = HistoryService.getHistory();
      
      if (index >= 0 && index < history.length) {
        history.splice(index, 1);
        localStorage.setItem(QUERY_HISTORY_KEY, JSON.stringify(history));
      }
    } catch (error) {
      console.error('Ошибка при удалении запроса из истории:', error);
    }
  },
  
  /**
   * Очищает всю историю запросов
   */
  clearHistory: () => {
    try {
      localStorage.removeItem(QUERY_HISTORY_KEY);
    } catch (error) {
      console.error('Ошибка при очистке истории запросов:', error);
    }
  }
};

export default HistoryService;