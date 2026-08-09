import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import ScoreBadge from '../components/ScoreBadge'
import {
  createDraft,
  getNegotiation,
  getNegotiations,
  sendMessage
} from '../api/client'
import { label, negotiationActionLabels, negotiationStageLabels } from '../labels'

const scenarios = [
  ['first_contact', 'Проверка актуальности'],
  ['facts', 'Сбор фактов'],
  ['motivation', 'Мотивация продавца'],
  ['bargain_test', 'Тест на торг']
]

const modeHints = {
  draft: 'Черновик: каждое сообщение остаётся под контролем менеджера.',
  assisted: 'С сопровождением: помощник предлагает формулировки, отправка — после проверки.',
  negotiation: 'Переговоры: используйте только при низком риске; юридические вопросы передавайте менеджеру.'
}

function formatPrice(value) {
  return `${Number(value || 0).toLocaleString('ru-RU')} ₽`
}

function formatTime(value, withDate = false) {
  if (!value) return 'Нет сообщений'
  const date = new Date(value)
  return date.toLocaleString('ru-RU', withDate
    ? { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }
    : { hour: '2-digit', minute: '2-digit' })
}

function messageAuthor(message) {
  if (message.direction === 'in') return 'Продавец'
  if (message.sent_by_human) return 'Менеджер'
  return message.is_draft ? 'Черновик Hermes' : 'Отправлено агентом'
}

export default function Negotiations() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [negotiations, setNegotiations] = useState([])
  const [dialog, setDialog] = useState(null)
  const [draft, setDraft] = useState('')
  const [mode, setMode] = useState('assisted')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loadingDraft, setLoadingDraft] = useState('')
  const [sending, setSending] = useState(false)
  const feedRef = useRef(null)

  useEffect(() => {
    getNegotiations()
      .then((items) => {
        setNegotiations(items)
        if (!id && items[0]) navigate(`/negotiations/${items[0].listing_id}`, { replace: true })
      })
      .catch((requestError) => setError(requestError.message))
  }, [id, navigate])

  useEffect(() => {
    if (!id) return
    setDialog(null)
    setDraft('')
    setNotice('')
    getNegotiation(id)
      .then(setDialog)
      .catch((requestError) => setError(requestError.message))
  }, [id])

  useEffect(() => {
    // Чат всегда открывается на последнем сообщении, как в мессенджере.
    const feed = feedRef.current
    if (feed) feed.scrollTop = feed.scrollHeight
  }, [dialog])

  const currentListingId = String(id || '')
  const riskReasons = useMemo(() => dialog?.escalation_reasons || [], [dialog])

  async function generateDraft(intent) {
    if (!id) return
    setLoadingDraft(intent)
    setError('')
    try {
      const result = await createDraft(id, intent)
      setDraft(result.draft_message)
      setNotice('Черновик подготовлен. Проверьте текст перед отправкой.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoadingDraft('')
    }
  }

  async function submitMessage() {
    if (!id || !draft.trim()) return
    setSending(true)
    setError('')
    try {
      const message = await sendMessage(id, draft)
      setDialog((current) => current
        ? { ...current, messages: [...current.messages, message] }
        : current)
      setNegotiations((items) => items.map((item) => (
        String(item.listing_id) === String(id)
          ? { ...item, last_message: { body: message.body, sent_at: message.sent_at } }
          : item
      )))
      setDraft('')
      setNotice('Сообщение сохранено в диалоге.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSending(false)
    }
  }

  function handToManager() {
    setMode('draft')
    setNotice('Диалог отмечен для ручной работы менеджера. Автоматическая отправка отключена.')
  }

  return (
    <section className="negotiations-page">
      <header className="page-header negotiations-header">
        <div><p className="eyebrow">ПЕРЕГОВОРЫ</p><h1>Диалоги с продавцами</h1><p>Уточняйте факты, фиксируйте торг и вовремя передавайте рискованные темы менеджеру.</p></div>
      </header>
      {error && <div className="notice">{error}</div>}
      <div className="negotiation-workspace">
        <aside className="dialog-list panel" aria-label="Список диалогов">
          <div className="dialog-list-heading"><h2>Активные</h2><span>{negotiations.length}</span></div>
          {!negotiations.length && !error && <div className="empty-state">Активных переговоров пока нет.</div>}
          {negotiations.map((item) => {
            const active = String(item.listing_id) === currentListingId
            return <button className={`dialog-row ${active ? 'active' : ''}`} type="button" key={item.listing_id} onClick={() => navigate(`/negotiations/${item.listing_id}`)}>
              <span className="dialog-row-top"><strong>{item.title}</strong>{item.escalated && <span className="escalation-dot" aria-label="Требуется эскалация" />}</span>
              <span className="dialog-row-meta"><span>{item.district || 'Район не указан'}</span><ScoreBadge score={item.score} /></span>
              <span className="dialog-stage">{label(negotiationStageLabels, item.stage)}</span>
              <span className="dialog-preview">{item.last_message?.body || 'Сообщений пока нет'}</span>
              <span className="dialog-row-bottom"><span>{item.unread_count ? `Непрочитанных: ${item.unread_count}` : item.seller_name || 'Продавец'}</span><time>{formatTime(item.last_message?.sent_at)}</time></span>
            </button>
          })}
        </aside>
        <main className="negotiation-detail">
          {!dialog && !error && <div className="panel loading">Загружаем диалог…</div>}
          {dialog && <div className="negotiation-detail-grid">
            <div className="dialog-center">
              <article className="dialog-overview panel">
                <div><p className="eyebrow">ЛОТ #{dialog.listing.id}</p><h2>{dialog.listing.title}</h2><p>{dialog.listing.district || 'Район не указан'} · {formatPrice(dialog.listing.price_rub)} · дисконт {dialog.listing.discount_pct ?? '—'}%</p></div>
                <div className="dialog-overview-side"><ScoreBadge score={dialog.listing.score} /><span className="stage-badge">{label(negotiationStageLabels, dialog.stage)}</span><small>Продавец: {dialog.seller.name || 'не указан'} · срочность {Number(dialog.seller.urgency_score || 0).toFixed(0)}</small></div>
              </article>
              <article className="message-feed panel" aria-live="polite">
                <div className="panel-heading"><h2>Переписка</h2><span>{dialog.messages.length} сообщений</span></div>
                <div className="message-list" ref={feedRef}>
                  {dialog.messages.map((message) => <div className={`message-row ${message.direction === 'out' ? 'out' : 'in'}`} key={message.id}>
                    <div className="message-bubble"><span className="message-author">{messageAuthor(message)}</span><p>{message.body}</p><time>{formatTime(message.sent_at, true)}</time></div>
                  </div>)}
                </div>
              </article>
              <article className="action-panel panel">
                <div className="panel-heading"><h2>Следующее сообщение</h2><span className="mode-risk">{modeHints[mode]}</span></div>
                <div className="mode-switcher" role="group" aria-label="Режим работы">
                  <button type="button" className={mode === 'draft' ? 'active' : ''} onClick={() => setMode('draft')}>Черновик</button>
                  <button type="button" className={mode === 'assisted' ? 'active' : ''} onClick={() => setMode('assisted')}>С сопровождением</button>
                  <button type="button" className={mode === 'negotiation' ? 'active' : ''} onClick={() => setMode('negotiation')}>Переговоры</button>
                </div>
                <div className="scenario-buttons">{scenarios.map(([intent, text]) => <button type="button" className="scenario-button" key={intent} onClick={() => generateDraft(intent)} disabled={Boolean(loadingDraft)}>{loadingDraft === intent ? 'Готовим…' : text}</button>)}</div>
                <label className="draft-field">Текст сообщения<textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Выберите сценарий или напишите сообщение вручную." rows="5" /></label>
                <div className="action-buttons"><button className="button" type="button" onClick={submitMessage} disabled={!draft.trim() || sending}>{sending ? 'Сохраняем…' : 'Отправить'}</button><button className="button secondary-button" type="button" onClick={handToManager}>Передать менеджеру</button></div>
                {notice && <p className="action-notice">{notice}</p>}
                {riskReasons.length > 0 && <div className="escalation-reasons"><h3>Причины эскалации</h3><div>{riskReasons.map((reason) => <span key={reason}>{reason}</span>)}</div></div>}
              </article>
            </div>
            <aside className="stage-timeline panel">
              <h2>Таймлайн стадий</h2>
              <ol>{dialog.events.map((event) => <li key={event.id}><span className="timeline-dot" /><strong>{label(negotiationStageLabels, event.from_stage)} → {label(negotiationStageLabels, event.to_stage)}</strong><small>{event.actor} · {formatTime(event.created_at, true)}</small><p>{label(negotiationActionLabels, event.reason)}</p></li>)}</ol>
              <div className="allowed-actions"><h3>Разрешённые переходы</h3>{dialog.allowed_next_actions.length ? dialog.allowed_next_actions.map((stage) => <span key={stage}>{label(negotiationStageLabels, stage)}</span>) : <p>Финальная стадия</p>}</div>
            </aside>
          </div>}
        </main>
      </div>
    </section>
  )
}
