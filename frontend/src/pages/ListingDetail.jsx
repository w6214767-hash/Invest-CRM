import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ScoreBadge from '../components/ScoreBadge'
import { getListing } from '../api/client'

export default function ListingDetail() {
  const { id } = useParams()
  const [listing, setListing] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { getListing(id).then(setListing).catch((requestError) => setError(requestError.message)) }, [id])
  if (error) return <section><Link to="/listings">← К списку</Link><div className="notice">{error}</div></section>
  if (!listing) return <section className="loading">Загружаем карточку участка…</section>
  const price = Number(listing.price_rub).toLocaleString('ru-RU')
  return <section>
    <Link className="back-link" to="/listings">← Все участки</Link>
    <header className="page-header detail-header"><div><p className="eyebrow">КАРТОЧКА УЧАСТКА</p><h1>{listing.title}</h1><p>{listing.district || listing.region || 'Район не указан'}</p></div><ScoreBadge score={listing.score} /></header>
    <div className="detail-grid"><article className="panel"><h2>Экономика</h2><dl><dt>Цена</dt><dd>{price} ₽</dd><dt>Площадь</dt><dd>{listing.area_sotka} сот.</dd><dt>Цена за сотку</dt><dd>{listing.price_per_sotka ? `${Number(listing.price_per_sotka).toLocaleString('ru-RU')} ₽` : '—'}</dd><dt>Дисконт</dt><dd>{listing.discount_pct === null ? 'Не рассчитан' : `${listing.discount_pct}%`}</dd></dl></article><article className="panel"><h2>Контроль</h2><dl><dt>Статус</dt><dd>{listing.status}</dd><dt>Переговоры</dt><dd>{listing.negotiation_stage}</dd><dt>Кадастровый номер</dt><dd>{listing.cadastral_number || 'Не указан'}</dd></dl></article></div>
    <article className="panel"><h2>Описание</h2><p className="description">{listing.description || 'Описание отсутствует.'}</p><h3>Флаги проверки</h3><div className="flag-list">{listing.red_flags.length ? listing.red_flags.map((flag) => <span key={flag}>{flag}</span>) : <span>Явных флагов нет</span>}</div></article>
  </section>
}
