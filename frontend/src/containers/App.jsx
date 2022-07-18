import '../assets/styles/container/App.css';
import { Provider } from 'react-redux'

import generateStore from '../redux/store'
import Routes from '../routes/routes';



const store = generateStore()

function App() {
  return (
    <Provider store={store}>
          <Routes/>
    </Provider>
  );
}

export default App;
