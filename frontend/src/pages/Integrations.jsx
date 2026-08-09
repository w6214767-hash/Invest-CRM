import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { demoListings } from '../api/demoData'
import { DEMO_MODE, getIntegrationsOverview, runIntegrationSearch, saveSearchProfile } from '../api/client'

const sourceDefaults = [
  { id: 'avito', name: 'Авито', logo: 'А', tone: 'avito', status: 'online', synced: '5 минут назад', imported: 124, errors: 0 },
  { id: 'domclick', name: 'Домклик', logo: 'Д', tone: 'domclick', status: 'online', synced: '12 минут назад', imported: 86, errors: 2 },
  { id: 'yandex', name: 'Яндекс Недвижимость', logo: 'Я', tone: 'yandex', status: 'setup', synced: 'Ожидает ключ доступа', imported: 0, errors: 0 }
]

const defaultProfile = {
  name: 'Юг Московской области',
  districts: 'Домодедово, Ступино, Чехов, Подольск',
  minPrice: 700000,
  maxPrice: 5000000,
  minArea: 6,
  maxArea: 30,
  minDiscount: 12,
  landUse: 'ИЖС, ЛПХ',
  exclude: 'аренда, доля, переуступка'
}

const auditEvents = [
  { time: '14:24', agent: 'Агент CRM', action: 'Лот №7 передан в Bitrix24', reason: 'Балл 73,9 · дисконт 18,5%', status: 'success' },
  { time: '14:21', agent: 'Агент проверки', action: 'Лот №5 отправлен на ручную проверку', reason: 'Нет кадастрового номера', status: 'warning' },
  { time: '14:18', agent: 'Агент-аналитик', action: 'Удалены 6 дублей', reason: 'Совпали координаты и телефон', status: 'neutral' },
  { time: '14:12', agent: 'Агент-скаут', action: 'Импортировано 32 объявления', reason: 'Профиль «Юг Московской области»', status: 'success' }
]

function StatusPill({ status }) {
  const online = status === 'online'
  return <span className={`status-pill ${online ? 'connected' : ''}`}><i />{online ? 'Подключено' : 'Требует настройки'}</span>
}

function SearchProfile({ profile, onChange, onSave }) {
  return <form className="profile-form" onSubmit={(event) => { event.preventDefault(); onSave() }}>
    <label className="wide">Название профиля<input value={profile.name} onChange={(event) => onChange('name', event.target.value)} /></label>
    <label className="wide">Районы поиска<input value={profile.districts} onChange={(event) => onChange('districts', event.target.value)} /></label>
    <label>Цена от, ₽<input type="number" value={profile.minPrice} onChange={(event) => onChange('minPrice', Number(event.target.value))} /></label>
    <label>Цена до, ₽<input type="number" value={profile.maxPrice} onChange={(event) => onChange('maxPrice', Number(event.target.value))} /></label>
    <label>Площадь от, сот.<input type="number" value={profile.minArea} onChange={(event) => onChange('minArea', Number(event.target.value))} /></label>
    <label>Площадь до, сот.<input type="number" value={profile.maxArea} onChange={(event) => onChange('maxArea', Number(event.target.value))} /></label>
    <label>Минимальный дисконт, %<input type="number" value={profile.minDiscount} onChange={(event) => onChange('minDiscount', Number(event.target.value))} /></label>
    <label>Вид использования<input value={profile.landUse} onChange={(event) => onChange('landUse', event.target.value)} /></label>
    <label className="wide">Исключающие слова<input value={profile.exclude} onChange={(event) => onChange('exclude', event.target.value)} /></label>
    <div className="profile-actions wide"><span>Изменения применятся при следующем запуске агентов.</span><button className="button" type="submit">Сохранить профиль</button></div>
  </form>
}

export default function Integrations() {
  const [activeTab, setActiveTab] = useState('sources')
  const [running, setRunning] = useState(false)
  const [message, setMessage] = useState('')
  const [profile, setProfile] = useState(() => {
    const saved = localStorage.getItem('invest_crm_search_profile')
    return saved ? JSON.parse(saved) : defaultProfile
  })
  const [sources, setSources] = useState(sourceDefaults)
  const [overview, setOverview] = useState(null)

  useEffect(() => {
    if (DEMO_MODE) return
    getIntegrationsOverview().then((data) => {
      setOverview(data)
      const value = data.profile
      setProfile({ name: value.name, districts: value.districts.join(', '), minPrice: value.min_price, maxPrice: value.max_price, minArea: value.min_area, maxArea: value.max_area, minDiscount: value.min_discount, landUse: value.land_use.join(', '), exclude: value.exclude_words.join(', ') })
      setSources((items) => items.map((item) => {
        const source = data.sources.find((candidate) => candidate.id === item.id)
        return source ? { ...item, status: source.status, synced: source.configured ? 'Подключено' : 'Ожидает настройки' } : item
      }))
    }).catch((error) => setMessage(error.message))
  }, [])

  const reviewListings = useMemo(() => demoListings.filter((item) => item.red_flags.length || !item.cadastral_number), [])
  const qualifiedListings = useMemo(() => demoListings.filter((item) => (item.discount_pct || 0) >= profile.minDiscount), [profile.minDiscount])
  const visibleReviewListings = DEMO_MODE ? reviewListings : (overview?.review_queue || [])
  const visibleAuditEvents = DEMO_MODE ? auditEvents : (overview?.audit || []).map((event) => ({
    id: event.id,
    time: new Date(event.created_at).toLocaleString('ru-RU'),
    agent: event.actor,
    action: event.action,
    reason: event.details.profile || `Запуск #${event.id}`,
    status: 'success'
  }))
  const metrics = overview?.metrics

  async function runSearch() {
    setRunning(true)
    setMessage('')
    try {
      const result = await runIntegrationSearch()
      if (!DEMO_MODE) setOverview(await getIntegrationsOverview())
      setRunning(false)
      setMessage(`Поиск завершён: найдено ${result?.qualified_count ?? qualifiedListings.length} лотов по профилю «${profile.name}».`)
      setSources((items) => items.map((item) => item.status === 'online' ? { ...item, synced: 'только что' } : item))
    } catch (error) { setRunning(false); setMessage(error.message) }
  }

  async function saveProfile() {
    localStorage.setItem('invest_crm_search_profile', JSON.stringify(profile))
    try {
      await saveSearchProfile({ name: profile.name, districts: profile.districts.split(',').map((item) => item.trim()).filter(Boolean), min_price: profile.minPrice, max_price: profile.maxPrice, min_area: profile.minArea, max_area: profile.maxArea, min_discount: profile.minDiscount, land_use: profile.landUse.split(',').map((item) => item.trim()).filter(Boolean), exclude_words: profile.exclude.split(',').map((item) => item.trim()).filter(Boolean) })
      setMessage('Поисковый профиль сохранён.')
    } catch (error) { setMessage(error.message) }
  }

  const tabs = [
    ['sources', 'Источники'],
    ['profile', 'Профиль поиска'],
    ['review', `Ручная проверка · ${visibleReviewListings.length}`],
    ['map', 'Карта и кластеры'],
    ['audit', 'Аудит агентов']
  ]

  return <section className="integrations-page">
    <header className="page-header integrations-header">
      <div><p className="eyebrow">АВТОМАТИЗАЦИЯ</p><h1>Поиск и интеграции</h1><p>Единый центр сбора, ИИ-анализа и передачи инвестиционных участков в CRM.</p></div>
      <button className="button run-button" onClick={runSearch} disabled={running}>{running ? 'Агенты работают…' : '⟳  Запустить поиск'}</button>
    </header>

    {message && <div className="success-notice" role="status">{message}<button onClick={() => setMessage('')} aria-label="Закрыть">×</button></div>}

    <div className="integration-summary">
      {[
        ['↗', metrics?.listings ?? '210', 'объявлений в базе'],
        ['✦', metrics?.qualified ?? '32', 'прошли ИИ-скоринг'],
        ['!', metrics?.review ?? '14', 'требуют проверки'],
        ['⟳', metrics?.runs ?? '—', 'запусков агентов']
      ].map(([icon, value, label]) => <article key={label}><span>{icon}</span><div><strong>{value}</strong><small>{label}</small></div></article>)}
    </div>

    <nav className="integration-tabs" aria-label="Разделы интеграций">
      {tabs.map(([id, label]) => <button className={activeTab === id ? 'active' : ''} onClick={() => setActiveTab(id)} key={id}>{label}</button>)}
    </nav>

    {activeTab === 'sources' && <>
      <div className="section-title"><div><p className="eyebrow">ИСТОЧНИКИ</p><h2>Площадки объявлений</h2></div><span>{sources.filter((source) => source.status === 'online').length} из {sources.length} подключены</span></div>
      <div className="source-grid">{sources.map((source) => <article className="source-card" key={source.id}>
        <div className="source-top"><b className={`source-logo ${source.tone}`}>{source.logo}</b><StatusPill status={source.status} /></div>
        <h3>{source.name}</h3><p>{source.synced}</p>
        <div className="source-stat"><strong>{source.imported || '—'}</strong><small>{source.imported ? 'объявлений сегодня' : 'нет данных'}</small></div>
        <div className="source-health"><span>Ошибки импорта</span><b className={source.errors ? 'has-errors' : ''}>{source.errors}</b></div>
        <button onClick={() => setMessage(`${source.name}: настройки подключения будут открыты администратору.`)}>{source.status === 'online' ? 'Настроить' : 'Подключить'} <b>→</b></button>
      </article>)}</div>
      <section className="automation-panel"><div className="automation-copy"><p className="eyebrow">AI PIPELINE</p><h2>Команда ИИ-агентов</h2><p>Поиск, дедупликация, оценка, юридическая проверка и передача в CRM выполняются по единому сценарию.</p><div className="guardrail"><b>✓</b><div><strong>Человек контролирует решения</strong><small>Офферы, платежи и юридически значимые действия требуют подтверждения.</small></div></div></div><ol>{[
        ['01', 'Агент-скаут', 'Подбирает объявления по активному профилю.'],
        ['02', 'Агент-аналитик', 'Удаляет дубли и рассчитывает рыночный дисконт.'],
        ['03', 'Агент проверки', 'Выявляет юридические и инфраструктурные риски.'],
        ['04', 'Агент CRM', 'Создаёт лид и назначает ответственного менеджера.']
      ].map(([number, title, copy], index) => <li key={number}><span>{number}</span><div><header><h3>{title}</h3><small>{index === 3 ? 'Передача' : 'Автоматически'}</small></header><p>{copy}</p></div></li>)}</ol></section>
      <section className="crm-strip"><div className="crm-logo">B24</div><div><p className="eyebrow">CRM-СИСТЕМА</p><h2>Bitrix24</h2><p>Лоты, контакты, задачи и статусы синхронизируются с инвестиционной воронкой.</p></div><StatusPill status="online" /><button onClick={() => setMessage('Сопоставление полей Bitrix24 доступно администратору.')}>Настроить поля</button></section>
    </>}

    {activeTab === 'profile' && <section className="workspace-panel"><div className="section-title"><div><p className="eyebrow">ФИЛЬТРЫ</p><h2>Профиль автоматического поиска</h2></div><span>{qualifiedListings.length} лотов соответствуют сейчас</span></div><SearchProfile profile={profile} onChange={(key, value) => setProfile((item) => ({ ...item, [key]: value }))} onSave={saveProfile} /></section>}

    {activeTab === 'review' && <section className="workspace-panel"><div className="section-title"><div><p className="eyebrow">HUMAN IN THE LOOP</p><h2>Очередь ручной проверки</h2></div><span>Решение принимает менеджер</span></div><div className="review-list">{visibleReviewListings.map((listing) => <article key={listing.id}><span className="risk-icon">!</span><div><Link to={`/listings/${listing.id}`}>{listing.title}</Link><p>{listing.red_flags.join(' · ') || 'Не указан кадастровый номер'}</p></div><strong>{listing.score == null ? '—' : Number(listing.score).toFixed(1)}</strong><Link className="review-action" to={`/listings/${listing.id}`}>Проверить →</Link></article>)}{!visibleReviewListings.length && <p>Лотов для ручной проверки нет.</p>}</div></section>}

    {activeTab === 'map' && <section className="workspace-panel map-workspace"><div><p className="eyebrow">ГЕОАНАЛИТИКА</p><h2>Кластеры цены за сотку</h2><p>Размер точки показывает площадь, цвет — инвестиционный балл. Карта демонстрационная; координаты будут поступать из источников.</p><div className="map-legend"><span><i className="good" />Балл 70+</span><span><i className="medium" />50–69</span><span><i className="low" />до 50</span></div></div><div className="cluster-map" aria-label="Схематичная карта кластеров">{demoListings.slice(0, 7).map((listing, index) => <Link title={`${listing.district}: ${listing.price_per_sotka.toLocaleString('ru-RU')} ₽/сот.`} className={`map-point ${listing.score >= 70 ? 'good' : listing.score >= 50 ? 'medium' : 'low'}`} style={{ left: `${12 + (index * 13) % 76}%`, top: `${18 + (index * 19) % 63}%` }} to={`/listings/${listing.id}`} key={listing.id}>{Math.round(listing.score)}</Link>)}</div></section>}

    {activeTab === 'audit' && <section className="workspace-panel"><div className="section-title"><div><p className="eyebrow">ПРОЗРАЧНОСТЬ</p><h2>Журнал решений агентов</h2></div></div><div className="audit-list">{visibleAuditEvents.map((event) => <article key={event.id || `${event.time}-${event.action}`}><time>{event.time}</time><i className={event.status} /><div><strong>{event.action}</strong><p>{event.agent} · {event.reason}</p></div></article>)}{!visibleAuditEvents.length && <p>Запусков агентов пока нет.</p>}</div></section>}
  </section>
}
