import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getListings } from '../api/client'
import ScoreBadge from '../components/ScoreBadge'
import Table from '../components/Table'

export default function Listings() {
  const [listings, setListings] = useState([])
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  useEffect(() => { getListings().then(setListings).catch((requestError) => setError(requestError.message)) }, [])
  const filtered = listings.filter((item) => `${item.title} ${item.region || ''} ${item.district || ''}`.toLowerCase().includes(query.toLowerCase()))
  return <section>
    <header className="page-header"><div><p className="eyebrow">ОБЪЯВЛЕНИЯ</p><h1>Земельные участки</h1><p>Оценка строится на медиане цены за сотку и качественных факторах.</p></div></header>
    <input className="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Найти участок или район" />
    {error && <div className="notice">{error}</div>}
    <section className="panel"><Table rows={filtered} emptyText="Объявлений пока нет. Добавьте их через API или синхронизацию Авито." columns={[
      { key: 'title', label: 'Участок', render: (item) => <Link to={`/listings/${item.id}`}>{item.title}</Link> },
      { key: 'area_sotka', label: 'Площадь', render: (item) => `${item.area_sotka} сот.` },
      { key: 'price_rub', label: 'Цена', render: (item) => `${Number(item.price_rub).toLocaleString('ru-RU')} ₽` },
      { key: 'discount_pct', label: 'Дисконт', render: (item) => item.discount_pct === null ? 'Не оценён' : `${item.discount_pct}%` },
      { key: 'negotiation_stage', label: 'Переговоры', render: (item) => item.negotiation_stage },
      { key: 'score', label: 'Балл', render: (item) => <ScoreBadge score={item.score} /> }
    ]} /></section>
  </section>
}
