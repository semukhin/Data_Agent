import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  IconButton, 
  List, 
  ListItem, 
  ListItemText, 
  Paper, 
  Tooltip, 
  Switch, 
  FormControlLabel,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import DeleteIcon from '@mui/icons-material/Delete';
import CloseIcon from '@mui/icons-material/Close';
import { t } from '../services/language';

// Ключ для хранения истории в localStorage
const QUERY_HISTORY_KEY = 'data_agent_query_history';

const QueryHistory = ({ onSelectQuery }) => {
  const [open, setOpen] = useState(false);
  const [history, setHistory] = useState([]);
  const [confirmClearOpen, setConfirmClearOpen] = useState(false);

  // Загрузка истории при монтировании
  useEffect(() => {
    loadHistory();
  }, []);

  // Загрузка истории из localStorage
  const loadHistory = () => {
    try {
      const savedHistory = localStorage.getItem(QUERY_HISTORY_KEY);
      if (savedHistory) {
        setHistory(JSON.parse(savedHistory));
      }
    } catch (error) {
      console.error('Ошибка при загрузке истории запросов:', error);
    }
  };

  // Открытие диалога истории
  const handleOpenHistory = () => {
    setOpen(true);
    loadHistory(); // Обновляем историю при открытии
  };

  // Закрытие диалога истории
  const handleCloseHistory = () => {
    setOpen(false);
  };

  // Выбор запроса из истории
  const handleSelectQuery = (query) => {
    if (onSelectQuery) {
      onSelectQuery(query);
    }
    setOpen(false);
  };

  // Удаление запроса из истории
  const handleDeleteQuery = (index) => {
    const updatedHistory = [...history];
    updatedHistory.splice(index, 1);
    setHistory(updatedHistory);
    localStorage.setItem(QUERY_HISTORY_KEY, JSON.stringify(updatedHistory));
  };

  // Очистка всей истории
  const handleClearHistory = () => {
    setConfirmClearOpen(true);
  };

  // Подтверждение очистки истории
  const confirmClearHistory = () => {
    setHistory([]);
    localStorage.removeItem(QUERY_HISTORY_KEY);
    setConfirmClearOpen(false);
  };

  return (
    <>
      <Tooltip title={t('common', 'history') || "История запросов"}>
        <IconButton 
          color="primary" 
          onClick={handleOpenHistory}
          sx={{ ml: 1 }}
        >
          <HistoryIcon />
        </IconButton>
      </Tooltip>

      <Dialog
        open={open}
        onClose={handleCloseHistory}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">{t('common', 'queryHistory') || "История запросов"}</Typography>
            <IconButton onClick={handleCloseHistory} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {history.length === 0 ? (
            <Typography variant="body2" color="textSecondary" align="center" sx={{ py: 4 }}>
              {t('common', 'noHistory') || "История запросов пуста"}
            </Typography>
          ) : (
            <List>
              {history.map((item, index) => (
                <React.Fragment key={index}>
                  <ListItem 
                    button 
                    onClick={() => handleSelectQuery(item.query)}
                    secondaryAction={
                      <IconButton 
                        edge="end" 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteQuery(index);
                        }}
                        size="small"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemText 
                      primary={item.query} 
                      secondary={`${new Date(item.timestamp).toLocaleString()} • ${item.visualization || 'Визуализация'}`}
                    />
                  </ListItem>
                  {index < history.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={handleClearHistory} 
            color="error" 
            disabled={history.length === 0}
          >
            {t('common', 'clearHistory') || "Очистить историю"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Диалог подтверждения очистки истории */}
      <Dialog
        open={confirmClearOpen}
        onClose={() => setConfirmClearOpen(false)}
      >
        <DialogTitle>{t('common', 'confirmation') || "Подтверждение"}</DialogTitle>
        <DialogContent>
          <Typography>
            {t('common', 'clearHistoryConfirm') || "Вы уверены, что хотите очистить всю историю запросов?"}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmClearOpen(false)}>
            {t('common', 'cancel') || "Отмена"}
          </Button>
          <Button onClick={confirmClearHistory} color="error" autoFocus>
            {t('common', 'confirm') || "Подтвердить"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default QueryHistory;