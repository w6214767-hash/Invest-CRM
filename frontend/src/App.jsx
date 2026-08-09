import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Deals from './pages/Deals'
import ListingDetail from './pages/ListingDetail'
import Listings from './pages/Listings'
import Login from './pages/Login'
import Negotiations from './pages/Negotiations'
import Integrations from './pages/Integrations'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/listings" element={<Listings />} />
        <Route path="/listings/:id" element={<ListingDetail />} />
        <Route path="/negotiations" element={<Negotiations />} />
        <Route path="/negotiations/:id" element={<Negotiations />} />
        <Route path="/deals" element={<Deals />} />
        <Route path="/integrations" element={<Integrations />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
