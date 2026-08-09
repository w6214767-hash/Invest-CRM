import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/client'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  async function submit(event) {
    event.preventDefault()
    try { const token = await login(email, password); localStorage.setItem('yurzil_token', token.access_token); navigate('/') }
    catch (requestError) { setError(requestError.message) }
  }
  return <main className="login-page"><form className="login-card" onSubmit={submit}><p className="eyebrow">ЮРЖИЛСЕРВИС</p><h1>Вход в CRM</h1><p>Используйте учётную запись, созданную через API администратора.</p><label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label><label>Пароль<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>{error && <div className="notice">{error}</div>}<button className="button" type="submit">Войти</button></form></main>
}
