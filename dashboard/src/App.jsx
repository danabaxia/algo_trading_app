import { BrowserRouter as Router, Routes, Route, useSearchParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import Home from './Home'

const API_URL = "http://localhost:8000"

function Dashboard() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  // Legacy: mode, New: session_id
  const sessionId = params.get('session_id')
  const mode = params.get('mode')

  const [account, setAccount] = useState(null)
  const [holdings, setHoldings] = useState([])
  const [trades, setTrades] = useState([])
  const [strategies, setStrategies] = useState([])
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState("OFFLINE")

  useEffect(() => {
    if (sessionId) {
      // New Session Logic
      axios.post(`${API_URL}/sessions/${sessionId}/start`)
        .then(() => setStatus("ONLINE"))
        .catch(e => {
          console.error("Failed to start session:", e)
          setStatus("ERROR")
        })
    } else {
      // Legacy Mode Logic
      const startEngine = async () => {
        try {
          await axios.post(`${API_URL}/control/start`, {
            mode: mode === 'live' ? 'live' : 'paper'
          })
          setStatus("ONLINE")
        } catch (e) {
          console.error("Failed to start engine:", e)
          setStatus("ERROR")
        }
      }
      startEngine()
    }
  }, [sessionId, mode])

  // Poll status to keep UI updated
  useEffect(() => {
    const checkStatus = async () => {
      try {
        // If session specific, we might want session status
        if (sessionId) {
          const res = await axios.get(`${API_URL}/sessions/${sessionId}`)
          if (res.data.status === 'RUNNING') setStatus("ONLINE")
          else setStatus(res.data.status)
        } else {
          const res = await axios.get(`${API_URL}/control/status`)
          setStatus(res.data.status)
        }
      } catch (e) { }
    }
    const interval = setInterval(checkStatus, 5000)
    return () => clearInterval(interval)
  }, [sessionId])

  const fetchData = async () => {
    try {
      let query = ""
      if (sessionId) query = `session_id=${sessionId}`
      else if (mode) query = `mode=${mode}`

      const [accRes, holdRes, tradeRes, stratRes] = await Promise.all([
        axios.get(`${API_URL}/account?${query}`),
        axios.get(`${API_URL}/holdings?${query}`),
        axios.get(`${API_URL}/trades?limit=10&${query}`),
        axios.get(`${API_URL}/strategies`)
      ])


      setAccount(accRes.data)
      setHoldings(holdRes.data)
      setTrades(tradeRes.data)
      setStrategies(stratRes.data)
    } catch (error) {
      console.error("Error fetching data", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 2000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="dashboard-container">Loading data...</div>

  return (
    <div className="dashboard-container">
      <header className="header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => navigate('/')}
            style={{
              background: 'rgba(255,255,255,0.1)',
              border: 'none',
              color: 'var(--text-primary)',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              fontWeight: 600
            }}
          >
            ← Home
          </button>
          <div>
            <h1 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Trading Dashboard</h1>
            <span className={`badge ${mode === 'live' ? 'badge-sell' : 'badge-buy'}`}>
              {mode === 'live' ? 'LIVE TRADING MODE' : 'PAPER TRADING MODE'}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span className="status-dot" style={{
            background: status === 'ONLINE' ? 'var(--accent-green)' : 'var(--accent-red)',
            boxShadow: `0 0 10px ${status === 'ONLINE' ? 'var(--accent-green)' : 'var(--accent-red)'}`
          }}></span>
          <span style={{ color: status === 'ONLINE' ? 'var(--accent-green)' : 'var(--accent-red)', fontWeight: 600 }}>
            SYSTEM {status}
          </span>
        </div>
      </header>

      {/* Account Summary */}
      <div className="grid">
        <div className="card">
          <h2>Total Account Value</h2>
          <div className="big-number">
            ${account?.total_equity?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ color: 'var(--text-secondary)' }}>
            Cash: ${account?.cash_balance?.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div className="card">
          <h2>Profit/Loss</h2>
          {/* Mock calculation for PnL color */}
          <div className="big-number" style={{ color: account?.total_equity >= 10000 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
            {((account?.total_equity - 10000) / 10000 * 100).toFixed(2)}%
          </div>
          <div style={{ color: 'var(--text-secondary)' }}>
            Total Return
          </div>
        </div>

        <div className="card">
          <h2>Active Strategy Count</h2>
          <div className="big-number">1</div>
          <div style={{ color: 'var(--text-secondary)' }}>strategies running</div>
        </div>
      </div>

      {/* Strategies Table */}
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>STRATEGIES</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Class</th>
              <th>Parameters</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {strategies.length === 0 ? (
              <tr><td colSpan="4" style={{ textAlign: 'center' }}>No strategies configured</td></tr>
            ) : (
              strategies.map((s, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 'bold' }}>{s.name}</td>
                  <td>{s.class_name}</td>
                  <td style={{ fontSize: '0.85rem', fontFamily: 'monospace' }}>
                    {JSON.stringify(s.parameters)}
                  </td>
                  <td>
                    <span className={`badge ${s.active ? 'badge-buy' : 'badge-sell'}`}>
                      {s.active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Holdings Table */}
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>PORTFOLIO HOLDINGS</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Strategy</th>
              <th>Ticker</th>
              <th>Qty</th>
              <th>Avg Price</th>
              <th>Current Value</th>
            </tr>
          </thead>
          <tbody>
            {holdings.length === 0 ? (
              <tr><td colSpan="5" style={{ textAlign: 'center' }}>No active positions</td></tr>
            ) : (
              holdings.map((h, i) => (
                <tr key={i}>
                  <td>{h.strategy}</td>
                  <td style={{ fontWeight: 'bold', color: 'var(--accent-blue)' }}>{h.ticker}</td>
                  <td>{h.quantity.toFixed(4)}</td>
                  <td>${h.avg_price.toFixed(2)}</td>
                  <td>${h.current_val.toFixed(2)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Recent Trades Table */}
      <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>RECENT ACTIVITY</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Signal</th>
              <th>Ticker</th>
              <th>Action</th>
              <th>Qty</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t) => (
              <tr key={t.id}>
                <td>{new Date(t.timestamp).toLocaleTimeString()}</td>
                <td>{t.strategy}</td>
                <td style={{ fontWeight: 'bold' }}>{t.ticker}</td>
                <td>
                  <span className={`badge ${t.action === 'BUY' ? 'badge-buy' : 'badge-sell'}`}>
                    {t.action}
                  </span>
                </td>
                <td>{t.quantity}</td>
                <td>${t.price.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}

export default App
