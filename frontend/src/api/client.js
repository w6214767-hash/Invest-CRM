import {
  createDemoDraft,
  demoDashboard,
  demoDeals,
  demoListings,
  getDemoNegotiation,
  getDemoNegotiations,
  sendDemoMessage
} from './demoData'

const API_PREFIX = import.meta.env.VITE_API_URL || '/api/v1'

/** Витринный режим: интерфейс работает на фикстурах, без обращения к backend. */
export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === '1'

function delay(payload, ms = 180) {
  return new Promise((resolve) => setTimeout(() => resolve(payload), ms))
}

export async function api(path, options = {}) {
  const token = localStorage.getItem('yurzil_token')
  const response = await fetch(`${API_PREFIX}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    },
    ...options
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    throw new Error(payload.detail || 'Не удалось получить данные CRM')
  }
  if (response.status === 204) return null
  return response.json()
}

export const getDashboard = () =>
  DEMO_MODE ? delay(demoDashboard) : api('/analytics/dashboard')

export const getListings = () =>
  DEMO_MODE ? delay(demoListings) : api('/listings')

export const getListing = (id) => {
  if (!DEMO_MODE) return api(`/listings/${id}`)
  const found = demoListings.find((item) => String(item.id) === String(id))
  if (!found) return Promise.reject(new Error('Участок не найден в демо-данных'))
  return delay(found)
}

export const getDeals = () => (DEMO_MODE ? delay(demoDeals) : api('/deals'))

export const getIntegrationsOverview = () =>
  DEMO_MODE ? delay(null) : api('/integrations/overview')

export const saveSearchProfile = (profile) =>
  DEMO_MODE ? delay(profile) : api('/integrations/profile', {
    method: 'PUT', body: JSON.stringify(profile)
  })

export const runIntegrationSearch = () =>
  DEMO_MODE ? delay(null, 900) : api('/integrations/run', { method: 'POST' })

export const getNegotiations = () =>
  DEMO_MODE ? delay(getDemoNegotiations()) : api('/negotiation')

export const getNegotiation = (id) =>
  DEMO_MODE ? delay(getDemoNegotiation(id)) : api(`/negotiation/${id}`)

export const createDraft = (id, intent) =>
  DEMO_MODE
    ? delay(createDemoDraft(id, intent))
    : api(`/negotiation/${id}/draft`, {
      method: 'POST',
      body: JSON.stringify(intent ? { intent } : {})
    })

export const sendMessage = (id, body) =>
  DEMO_MODE
    ? delay(sendDemoMessage(id, body))
    : api(`/negotiation/${id}/message`, {
      method: 'POST',
      body: JSON.stringify({ body })
    })

export const login = (email, password) => {
  if (DEMO_MODE) return delay({ access_token: 'demo-token', token_type: 'bearer' })
  return api('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  })
}
