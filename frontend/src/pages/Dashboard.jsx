import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ScoreBadge from '../components/ScoreBadge'
import Table from '../components/Table'
import { getDashboard, getListings } from '../api/client'

const initialMetrics = { leads_count: 0, conversion_pct: 0, average_discount_pct: 0, active_deals_count: 0 }

export default function Dashboard() {
  const [metrics, setMetrics] = useState(initialMetrics)
  const [listings, setListings] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getDashboard(), getListings()])
      .then(([dashboard, items]) => { setMetrics(dashboard); setListings(items.slice(0, 5)) })
      .catch((requestError) => setError(requestError.message))
  }, [])

  const cards = [
    ['Лиды', metrics.leads_count, 'Все найденные участки'],
    ['Средний дисконт', `${metrics.average_discount_pct}%`, 'К медиане кластера'],
    ['Конверсия', `${metrics.conversion_pct}%`, 'Выигранные сделки'],
    ['Активные сделки', metrics.active_deals_count, 'Без финального статуса']
  ]

  return <section>
    <header className="page-header"><div><p className="eyebrow">РАБОЧИЙ СТОЛ</p><h1>Инвестиционная воронка</h1><p>Приоритет — участки ниже рынка в Домодедово и Московской области.</p></div><Link className="button" to="/listings">Открыть участки</Link></header>
    {error && <div className="notice">{error}. Запустите backend и создайте данные через API.</div>}
    <div className="metric-grid">{cards.map(([label, value, caption]) => <article className="metric-card" key={label}><span>{label}</span><strong>{value}</strong><small>{caption}</small></article>)}</div>
    <section className="panel"><div className="panel-heading"><h2>Приоритетные участки</h2><Link to="/listings">Все объявления</Link></div><Table rows={listings} columns={[
      { key: 'title', label: 'Участок', render: (item) => <Link to={`/listings/${item.id}`}>{item.title}</Link> },
      { key: 'district', label: 'Район', render: (item) => item.district || item.region || '—' },
      { key: 'price_rub', label: 'Цена', render: (item) => `${Number(item.price_rub).toLocaleString('ru-RU')} ₽` },
      { key: 'discount_pct', label: 'Дисконт', render: (item) => item.discount_pct === null ? '—' : `${item.discount_pct}%` },
      { key: 'score', label: 'Балл', render: (item) => <ScoreBadge score={item.score} /> }
    ]} /></section>
  </section>
}
