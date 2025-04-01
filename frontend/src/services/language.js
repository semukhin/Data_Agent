// src/services/language.js

// Константа для хранения ключа в localStorage
const LANGUAGE_KEY = 'data_agent_language';

/**
 * Поддерживаемые языки
 */
export const LANGUAGES = {
  RU: 'ru',
  EN: 'en'
};

/**
 * Константы локализации для UI
 */
export const TRANSLATIONS = {
  // Общие
  [LANGUAGES.RU]: {
    common: {
      appName: 'Data Agent',
      loading: 'Загрузка...',
      error: 'Ошибка',
      success: 'Успешно',
      submit: 'Отправить',
      cancel: 'Отмена',
      save: 'Сохранить',
      delete: 'Удалить',
      edit: 'Редактировать',
      search: 'Поиск',
      noData: 'Нет данных',
      actions: 'Действия',
      yes: 'Да',
      no: 'Нет',
      back: 'Назад',
      next: 'Далее',
      language: 'Язык',
      russian: 'Русский',
      english: 'Английский',
      history: 'История запросов',
      queryHistory: 'История запросов',
      noHistory: 'История запросов пуста',
      clearHistory: 'Очистить историю',
      confirmation: 'Подтверждение',
      clearHistoryConfirm: 'Вы уверены, что хотите очистить всю историю запросов?',
      confirm: 'Подтвердить'
    },
    auth: {
      login: 'Вход',
      logout: 'Выход',
      username: 'Имя пользователя',
      password: 'Пароль',
      loginButton: 'Войти',
      logoutButton: 'Выйти',
      invalidCredentials: 'Неверное имя пользователя или пароль'
    },
    dashboard: {
      title: 'Аналитическая панель',
      queryPlaceholder: 'Например: Покажи график активных пользователей по неделям за последние 3 месяца',
      askQuestion: 'Задайте вопрос о ваших данных',
      sendQuery: 'Отправить запрос',
      processingQuery: 'Обработка запроса...',
      visualization: 'Визуализация',
      data: 'Данные',
      sqlQuery: 'SQL-запрос',
      explanation: 'Объяснение',
      noVisualization: 'Нет данных для отображения. Пожалуйста, введите запрос.',
      showDataLabels: 'Показывать значения',
      saveQuery: 'Сохранить запрос',
      savedQueries: 'Сохраненные запросы',
      querySaved: 'Запрос сохранен',
      queryDeleted: 'Запрос удален',
      enterQueryName: 'Введите название для запроса',
      save: 'Сохранить'
    }
  },
  [LANGUAGES.EN]: {
    common: {
      appName: 'Data Agent',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      submit: 'Submit',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      search: 'Search',
      noData: 'No data',
      actions: 'Actions',
      yes: 'Yes',
      no: 'No',
      back: 'Back',
      next: 'Next',
      language: 'Language',
      russian: 'Russian',
      english: 'English',
      history: 'Query History',
      queryHistory: 'Query History',
      noHistory: 'Query history is empty',
      clearHistory: 'Clear History',
      confirmation: 'Confirmation',
      clearHistoryConfirm: 'Are you sure you want to clear all query history?',
      confirm: 'Confirm'
    },
    auth: {
      login: 'Login',
      logout: 'Logout',
      username: 'Username',
      password: 'Password',
      loginButton: 'Login',
      logoutButton: 'Logout',
      invalidCredentials: 'Invalid username or password'
    },
    dashboard: {
      title: 'Analytics Dashboard',
      queryPlaceholder: 'For example: Show a chart of active users by week for the last 3 months',
      askQuestion: 'Ask a question about your data',
      sendQuery: 'Send Query',
      processingQuery: 'Processing query...',
      visualization: 'Visualization',
      data: 'Data',
      sqlQuery: 'SQL Query',
      explanation: 'Explanation',
      noVisualization: 'No data to display. Please enter a query.',
      showDataLabels: 'Show values',
      saveQuery: 'Save Query',
      savedQueries: 'Saved Queries',
      querySaved: 'Query saved',
      queryDeleted: 'Query deleted',
      enterQueryName: 'Enter a name for the query',
      save: 'Save'
    }
  }
};

/**
 * Сервис для работы с локализацией
 */
export const LanguageService = {
  /**
   * Получает текущий язык приложения
   * 
   * @returns {string} Код языка
   */
  getCurrentLanguage: () => {
    return localStorage.getItem(LANGUAGE_KEY) || LANGUAGES.RU;
  },
  
  /**
   * Устанавливает новый язык
   * 
   * @param {string} lang - Код языка
   */
  setLanguage: (lang) => {
    if (Object.values(LANGUAGES).includes(lang)) {
      localStorage.setItem(LANGUAGE_KEY, lang);
    }
  },
  
  /**
   * Получает словарь перевода для текущего языка
   * 
   * @returns {Object} Словарь перевода
   */
  getTranslations: () => {
    const currentLang = LanguageService.getCurrentLanguage();
    return TRANSLATIONS[currentLang] || TRANSLATIONS[LANGUAGES.RU];
  },
  
  /**
   * Получает перевод по ключу
   * 
   * @param {string} section - Раздел перевода
   * @param {string} key - Ключ перевода
   * @returns {string} Текст перевода
   */
  translate: (section, key) => {
    const translations = LanguageService.getTranslations();
    
    if (translations && translations[section] && translations[section][key]) {
      return translations[section][key];
    }
    
    // Если перевод не найден, возвращаем ключ
    return key;
  }
};

/**
 * Удобная функция для получения перевода
 */
export const t = (section, key) => LanguageService.translate(section, key);