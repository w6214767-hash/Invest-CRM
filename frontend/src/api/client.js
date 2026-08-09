const API_PREFIX = import.meta.env.VITE_API_URL || '/api/v1'

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

export const getDashboard = () => api('/analytics/dashboard')
export const getListings = () => api('/listings')
export const getListing = (id) => api(`/listings/${id}`)
export const getDeals = () => api('/deals')
export const login = (email, password) => api('/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
})
