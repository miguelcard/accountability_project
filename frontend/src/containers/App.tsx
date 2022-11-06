import { Provider } from 'react-redux'

import generateStore from '../redux/store'
import Routes from '../routes/routes';
import { StyledEngineProvider } from '@mui/material/styles';

import createCache from '@emotion/cache';
import { CacheProvider } from '@emotion/react';

const cache = createCache({
  key: 'css',
  prepend: true,
});

const store = generateStore()

function App() {
  return (
    <Provider store={store}>
      <StyledEngineProvider injectFirst>
        <CacheProvider value={cache}>
          <Routes />
        </CacheProvider>
      </StyledEngineProvider>
    </Provider>
  );
}

export default App;
