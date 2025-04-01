import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import LogoutIcon from '@mui/icons-material/Logout';
import QueryInput from './QueryInput';
import VisualizationPanel from './VisualizationPanel';
import LanguageSelector from './LanguageSelector';
import { t } from '../services/language';

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme }) => ({
    flexGrow: 1,
    padding: theme.spacing(3),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  }),
);

function MainLayout({ onLogout }) {
  console.log("MainLayout is rendering");
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleQueryResult = (result) => {
    setQueryResult(result);
    setLoading(false);
    setError(null);
  };

  const handleQueryStart = () => {
    setLoading(true);
    setError(null);
  };

  const handleQueryError = (errorMessage) => {
    setLoading(false);
    setError(errorMessage);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="fixed">
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {t('common', 'appName')}
          </Typography>
          
          <LanguageSelector />
          
          <IconButton 
            color="inherit" 
            onClick={onLogout} 
            sx={{ ml: 2 }}
            title={t('auth', 'logout')}
          >
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Main>
        <Toolbar />
        <Container maxWidth="xl">
          <Box sx={{ my: 2 }}>
            <QueryInput 
              onQueryResult={handleQueryResult}
              onQueryStart={handleQueryStart}
              onQueryError={handleQueryError}
            />
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <VisualizationPanel 
              queryResult={queryResult}
              loading={loading}
              error={error}
            />
          </Box>
        </Container>
      </Main>
    </Box>
  );
}

export default MainLayout;