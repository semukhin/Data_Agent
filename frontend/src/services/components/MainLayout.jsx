import React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import QueryInput from './QueryInput';
import VisualizationPanel from './VisualizationPanel';
import MetadataPanel from './MetadataPanel';

const drawerWidth = 240;

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

function MainLayout() {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed">
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            AI-Powered BI Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Main>
        <Toolbar />
        <Container maxWidth="xl">
          <Box sx={{ my: 2 }}>
            <QueryInput />
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ width: '70%' }}>
              <VisualizationPanel />
            </Box>
            <Box sx={{ width: '30%' }}>
              <MetadataPanel />
            </Box>
          </Box>
        </Container>
      </Main>
    </Box>
  );
}

export default MainLayout;