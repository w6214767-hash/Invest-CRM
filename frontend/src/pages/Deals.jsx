import { useEffect, useState } from 'react'
import Table from '../components/Table'
import { getDeals } from '../api/client'

const labels = { lead: 'Лид', qualification: 'Квалификация', due_diligence: 'Проверка', offer: 'Оффер', contract: 'Договор', won: 'Выиграна', lost: 'Потеряна' }

export default function Deals() {
  const [deals, setDeals] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { getDeals().then(setDeals).catch((requestError) => setError(requestError.message)) }, [])
  return <section><header className="page-header"><div><p className="eyebrow">СДЕЛКИ</p><h1>Инвестиционная воронка</h1><p>Сделки готовы для передачи в Bitrix24 через входящий вебхук.</p></div></header>{error && <div className="notice">{error}</div>}<section className="panel"><Table rows={deals} emptyText="Сделок пока нет." columns={[
    { key: 'id', label: '№', render: (item) => `#${item.id}` },
    { key: 'listing_id', label: 'Участок', render: (item) => `Лот #${item.listing_id}` },
    { key: 'stage', label: 'Стадия', render: (item) => labels[item.stage] || item.stage },
    { key: 'amount_rub', label: 'Сумма', render: (item) => item.amount_rub ? `${Number(item.amount_rub).toLocaleString('ru-RU')} ₽` : '—' },
    { key: 'manager_name', label: 'Менеджер', render: (item) => item.manager_name || 'Не назначен' }
  ]} /></section></section>
}
