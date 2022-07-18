import React from 'react';
import ReactDOM from 'react-dom';
import './assets/styles/container/index.css';
import App from './containers/App.jsx';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter } from 'react-router-dom';


ReactDOM.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
  document.getElementById('root')
);