import { NavLink, Outlet } from 'react-router-dom'
import { DEMO_MODE } from '../api/client'

const navigation = [
  ['/', 'Обзор'],
  ['/listings', 'Участки'],
  ['/negotiations', 'Переговоры'],
  ['/deals', 'Сделки']
]

function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 48 48" role="img" aria-label="ЮрЖил CRM">
      <path d="M7 38V18l17-10 17 10v20H7Z" fill="none" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" />
      <path d="M16 38V25h16v13M24 8v17" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  )
}

export default function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><BrandMark /><span>ЮрЖил<small>CRM</small></span></div>
        <nav aria-label="Основная навигация">
          {navigation.map(([to, label]) => <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>)}
        </nav>
        <div className="sidebar-note">Домодедово · МО<br />Инвестиционные участки</div>
        {DEMO_MODE && <div className="demo-badge">Демо-режим<br /><small>данные условные, backend не подключён</small></div>}
      </aside>
      <main className="content"><Outlet /></main>
    </div>
  )
}
