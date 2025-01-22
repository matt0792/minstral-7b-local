// main.jsx (corrected)
import { ChakraProvider, extendTheme } from '@chakra-ui/react'; // Named import
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Create a theme
const theme = extendTheme({ /* customizations */ });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>
);