import React, { useState, useEffect } from 'react';
import { Box, ToggleButtonGroup, ToggleButton, useTheme } from '@mui/material';
import { LanguageService, LANGUAGES } from '../services/language';

/**
 * Компонент выбора языка приложения
 */
const LanguageSelector = () => {
  const theme = useTheme();
  const [language, setLanguage] = useState(LanguageService.getCurrentLanguage());

  useEffect(() => {
    // При монтировании компонента устанавливаем текущий язык
    setLanguage(LanguageService.getCurrentLanguage());
  }, []);

  /**
   * Обработчик изменения языка
   * @param {Event} event - событие изменения
   * @param {string} newValue - новое значение языка
   */
  const handleLanguageChange = (event, newValue) => {
    if (newValue !== null) {
      setLanguage(newValue);
      LanguageService.setLanguage(newValue);
      // Принудительно перезагружаем страницу для применения нового языка
      window.location.reload();
    }
  };

  return (
    <Box sx={{ minWidth: 120 }}>
      <ToggleButtonGroup
        value={language}
        exclusive
        onChange={handleLanguageChange}
        aria-label="language selector"
        size="small"
        sx={{
          bgcolor: theme.palette.background.paper,
          '& .MuiToggleButton-root': {
            textTransform: 'none',
            fontSize: '0.875rem',
            px: 2
          }
        }}
      >
        <ToggleButton value={LANGUAGES.RU} aria-label="russian">
          RU
        </ToggleButton>
        <ToggleButton value={LANGUAGES.EN} aria-label="english">
          EN
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
};

export default LanguageSelector;