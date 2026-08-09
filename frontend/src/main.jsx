import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import App from './App'
import { DEMO_MODE } from './api/client'
import './styles.css'

// В витринном режиме сборка раздаётся как статика без сервера,
// поэтому маршрутизация идёт через hash, чтобы прямые ссылки не отдавали 404.
const Router = DEMO_MODE ? HashRouter : BrowserRouter

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>
)
