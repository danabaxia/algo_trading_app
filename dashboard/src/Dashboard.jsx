import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
    AreaChart, Area,
    ComposedChart, Line, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import './App.css';
import TickerSearch from './TickerSearch';

const API_URL = "http://localhost:8001";

const Dashboard = () => {
    const [params] = useSearchParams();
    const navigate = useNavigate();
    const sessionId = params.get('session_id');
    const mode = params.get('mode');

    const [account, setAccount] = useState(null);
    const [holdings, setHoldings] = useState([]);
    const [trades, setTrades] = useState([]);
    const [sessionStrategies, setSessionStrategies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState("OFFLINE");
    const [sessionDetails, setSessionDetails] = useState(null);

    // Tabs
    const [activeTab, setActiveTab] = useState('overview');

    // Backtest State
    const [btStart, setBtStart] = useState("2023-01-01");
    const [btEnd, setBtEnd] = useState(new Date().toISOString().split('T')[0]);
    const [btLoading, setBtLoading] = useState(false);
    const [btResult, setBtResult] = useState(null);
    const [btError, setBtError] = useState(null);
    const [selectedTicker, setSelectedTicker] = useState(null);
    const [newTicker, setNewTicker] = useState("");

    const handleAddTicker = async () => {
        if (!newTicker || !sessionId) return;
        try {
            await axios.post(`${API_URL}/sessions/${sessionId}/tickers`, { symbol: newTicker });
            setNewTicker("");
            fetchData();
        } catch (e) {
            console.error(e);
            const msg = e.response?.data?.detail || "Error adding ticker";
            alert(msg);
        }
    };

    const handleBatchAddTickers = async (tickers) => {
        if (!sessionId) return;
        try {
            for (const t of tickers) {
                await axios.post(`${API_URL}/sessions/${sessionId}/tickers`, { symbol: t });
            }
            fetchData();
        } catch (e) {
            console.error(e);
            alert("Error adding tickers: " + (e.response?.data?.detail || e.message));
        }
    };

    const handleRemoveTicker = async (symbol) => {
        if (!sessionId) return;
        if (!window.confirm(`Remove ${symbol} from watchlist?`)) return;
        try {
            await axios.delete(`${API_URL}/sessions/${sessionId}/tickers/${symbol}`);
            fetchData();
        } catch (e) {
            console.error(e);
        }
    };

    // 1. Initialize Session
    useEffect(() => {
        if (sessionId) {
            axios.get(`${API_URL}/sessions/${sessionId}`)
                .then(res => setSessionDetails(res.data))
                .catch(e => console.error("Err session details", e));

            axios.post(`${API_URL}/sessions/${sessionId}/start`)
                .then(() => setStatus("ONLINE"))
                .catch(e => {
                    console.error("Failed to start session:", e);
                    setStatus(e.response?.data?.detail?.includes("already running") ? "ONLINE" : "ERROR");
                });
        }
    }, [sessionId, mode]);

    // 2. Poll Data
    const fetchData = async () => {
        try {
            let query = "";
            if (sessionId) query = `session_id=${sessionId}`;
            else if (mode) query = `mode=${mode}`;

            const [accRes, holdRes, tradeRes] = await Promise.all([
                axios.get(`${API_URL}/account?${query}`),
                axios.get(`${API_URL}/holdings?${query}`),
                axios.get(`${API_URL}/trades?limit=20&${query}`)
            ]);

            setAccount(accRes.data);
            setHoldings(holdRes.data);
            setTrades(tradeRes.data);

            if (sessionId) {
                const stratRes = await axios.get(`${API_URL}/sessions/${sessionId}/strategies`);
                setSessionStrategies(stratRes.data);
            }

        } catch (error) {
            console.error("Error fetching data", error);
        } finally {
            if (loading) setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, [sessionId]);

    const handleToggleStrategy = async (name) => {
        if (!sessionId) return;
        try {
            await axios.post(`${API_URL}/sessions/${sessionId}/strategies/${name}/toggle`);
            // Immediate refresh
            const stratRes = await axios.get(`${API_URL}/sessions/${sessionId}/strategies`);
            setSessionStrategies(stratRes.data);
        } catch (e) {
            alert("Failed to toggle strategy: " + e.message);
        }
    };

    const handleRunBacktest = async () => {
        setBtLoading(true);
        setBtError(null);
        setBtResult(null);
        setSelectedTicker(null);
        try {
            // Send empty strategies to force backend to use Session Strategies
            const payload = {
                start_date: btStart,
                end_date: btEnd,
                strategies: null,
                tickers: null, // Use session tickers if backend supports, or default
                initial_balance: 10000
            };

            const res = await axios.post(`${API_URL}/sessions/${sessionId}/backtest`, payload);
            setBtResult(res.data);
            if (res.data.daily_prices && Object.keys(res.data.daily_prices).length > 0) {
                setSelectedTicker(Object.keys(res.data.daily_prices)[0]);
            }
        } catch (e) {
            setBtError(e.response?.data?.detail || e.message);
        } finally {
            setBtLoading(false);
        }
    };

    const getChartData = () => {
        if (!btResult || !selectedTicker || !btResult.daily_prices[selectedTicker]) return [];

        const prices = btResult.daily_prices[selectedTicker];
        const tickerTrades = btResult.trades.filter(t => t.ticker === selectedTicker);

        return prices.map(p => {
            const trade = tickerTrades.find(t => t.date === p.date);
            return {
                ...p,
                buy: trade && trade.action === 'BUY' ? p.close : null,
                sell: trade && trade.action === 'SELL' ? p.close : null
            };
        });
    };

    const chartData = getChartData();

    if (loading) return <div className="dashboard-container">Loading data...</div>;

    return (
        <div className="dashboard-container">
            <header className="header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <button onClick={() => navigate('/')} className="home-btn-nav">← Home</button>
                    <div>
                        <h1 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Trading Dashboard</h1>
                        <span className={`badge ${sessionDetails?.mode === 'LIVE' ? 'badge-sell' : 'badge-buy'}`}>
                            {sessionDetails?.mode || mode} TRADING
                        </span>
                    </div>
                </div>

                <div className="tab-controls">
                    <button className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</button>
                    <button className={`tab-btn ${activeTab === 'backtest' ? 'active' : ''}`} onClick={() => setActiveTab('backtest')}>Backtest Analysis</button>
                </div>

                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className="status-dot" style={{ background: status === 'ONLINE' ? 'var(--accent-green)' : 'var(--accent-red)' }}></span>
                    <span style={{ color: status === 'ONLINE' ? 'var(--accent-green)' : 'var(--accent-red)', fontWeight: 600 }}>SYSTEM {status}</span>
                </div>
            </header>

            {status === 'ERROR' && <div className="error-banner">Connection to Trading Engine Failed. Ensure Backend is running.</div>}

            {activeTab === 'overview' && (
                <div className="overview-content">
                    <div className="grid">
                        <div className="card">
                            <h2>Total Account Value</h2>
                            <div className="big-number">${account?.total_equity?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                            <div style={{ color: 'var(--text-secondary)' }}>Cash: ${account?.cash_balance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        </div>
                        <div className="card">
                            <h2>Profit/Loss</h2>
                            <div className="big-number" style={{ color: account?.total_equity >= 10000 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                                {((account?.total_equity - 10000) / 10000 * 100).toFixed(2)}%
                            </div>
                        </div>
                        <div className="card">
                            <h2>Active Positions</h2>
                            <div className="big-number">{holdings.length}</div>
                        </div>
                    </div>

                    {/* Active Strategies Table */}
                    <div className="card" style={{ marginBottom: '2rem' }}>
                        <h3>Active Strategies</h3>
                        {sessionStrategies.length === 0 ? <p>No strategies configured.</p> : (
                            <table className="sessions-table">
                                <thead>
                                    <tr>
                                        <th>Strategy Name</th>
                                        <th>Status</th>
                                        <th>Toggle</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sessionStrategies.map(s => (
                                        <tr key={s.id}>
                                            <td><b>{s.name}</b></td>
                                            <td>
                                                <span className={`badge ${s.is_active ? 'badge-buy' : 'badge-sell'}`}>
                                                    {s.is_active ? 'ACTIVE' : 'INACTIVE'}
                                                </span>
                                            </td>
                                            <td>
                                                <button
                                                    className="primary-btn"
                                                    style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem', background: s.is_active ? 'var(--accent-red)' : 'var(--accent-green)' }}
                                                    onClick={() => handleToggleStrategy(s.name)}
                                                >
                                                    {s.is_active ? 'Disable' : 'Enable'}
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>

                    <div className="grid-2col">
                        <div>
                            <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>PORTFOLIO / WATCHLIST</h3>
                            <div style={{ marginBottom: '1rem' }}>
                                <TickerSearch apiUrl={API_URL} onAddTickers={handleBatchAddTickers} />
                            </div>
                            <div className="table-container">
                                <table>
                                    <thead><tr><th>Ticker</th><th>Price</th><th>Qty</th><th>Value</th><th>Gain/Loss</th><th>Action</th></tr></thead>
                                    <tbody>
                                        {holdings.length === 0 ? <tr><td colSpan="6" style={{ textAlign: 'center', padding: '1rem' }}>No stocks monitored</td></tr> : holdings.map((h, i) => (
                                            <tr key={h.ticker}>
                                                <td><b>{h.ticker}</b></td>
                                                <td>${h.current_price?.toFixed(2)}</td>
                                                <td>{h.quantity?.toFixed(2)}</td>
                                                <td>${h.current_val?.toFixed(2)}</td>
                                                <td className={h.unrealized_pl >= 0 ? "pos" : "neg"}>
                                                    {h.unrealized_pl >= 0 ? "+" : ""}{h.unrealized_pl?.toFixed(2)}
                                                </td>
                                                <td>
                                                    <button
                                                        onClick={() => handleRemoveTicker(h.ticker)}
                                                        style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}
                                                        title="Remove from Watchlist"
                                                    >
                                                        ✕
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div>
                            <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>RECENT ACTIVITY</h3>
                            <div className="table-container">
                                <table>
                                    <thead><tr><th>Action</th><th>Ticker</th><th>Price</th></tr></thead>
                                    <tbody>
                                        {trades.map(t => (
                                            <tr key={t.id}>
                                                <td><span className={`badge ${t.action === 'BUY' ? 'badge-buy' : 'badge-sell'}`}>{t.action}</span></td>
                                                <td><b>{t.ticker}</b></td><td>${t.price.toFixed(2)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'backtest' && (
                <div className="backtest-content card">
                    <h2 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>Strategy Backtest (Uses Session Strategies)</h2>
                    <div className="backtest-controls">
                        <div><label>Start</label><input type="date" value={btStart} onChange={e => setBtStart(e.target.value)} /></div>
                        <div><label>End</label><input type="date" value={btEnd} onChange={e => setBtEnd(e.target.value)} /></div>
                        <button className="primary-btn" onClick={handleRunBacktest} disabled={btLoading}>{btLoading ? "Running..." : "▶ Run Backtest"}</button>
                    </div>

                    {btError && <div className="error-msg">{btError}</div>}

                    {btResult && (
                        <div className="backtest-results animate-fade-in">
                            <div className="metrics-grid">
                                <div className="metric-box"><label>Total Return</label><span className={btResult.total_return_pct >= 0 ? "pos" : "neg"}>{btResult.total_return_pct}%</span></div>
                                <div className="metric-box"><label>Max Drawdown</label><span className="neg">{btResult.max_drawdown_pct}%</span></div>
                                <div className="metric-box"><label>Trades</label><span>{btResult.total_trades}</span></div>
                            </div>

                            {/* Performance Breakdown Table */}
                            <div className="card" style={{ marginBottom: '2rem' }}>
                                <h3>Performance Breakdown</h3>
                                <div className="table-container" style={{ marginTop: '1rem' }}>
                                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <thead>
                                            <tr>
                                                <th style={{ textAlign: 'left', padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Stock</th>
                                                <th style={{ textAlign: 'right', padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Total Return ($)</th>
                                                <th style={{ textAlign: 'right', padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Max Drawdown</th>
                                                <th style={{ textAlign: 'right', padding: '1rem', borderBottom: '1px solid var(--border-color)' }}>Trades</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {btResult.per_stock_performance && Object.entries(btResult.per_stock_performance).map(([ticker, stats]) => (
                                                <tr key={ticker} style={{ borderBottom: '1px solid var(--border-color-light)' }}>
                                                    <td style={{ padding: '1rem' }}><b>{ticker}</b></td>
                                                    <td style={{ padding: '1rem', textAlign: 'right', color: stats.pnl >= 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                                                        {stats.pnl >= 0 ? "+" : ""}{stats.pnl.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                                                    </td>
                                                    <td style={{ padding: '1rem', textAlign: 'right' }} className="neg">
                                                        {stats.max_drawdown_pct}%
                                                    </td>
                                                    <td style={{ padding: '1rem', textAlign: 'right' }}>{stats.trades}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            <div className="chart-container" style={{ marginBottom: '2rem' }}>
                                <h3>Total Equity Curve</h3>
                                <ResponsiveContainer width="100%" height={300}>
                                    <AreaChart data={btResult.equity_curve}>
                                        <defs>
                                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                        <XAxis dataKey="date" stroke="#94a3b8" />
                                        <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                                        <Tooltip contentStyle={{ backgroundColor: '#1e293b' }} itemStyle={{ color: '#fff' }} />
                                        <Area type="monotone" dataKey="value" stroke="#82ca9d" fillOpacity={1} fill="url(#colorValue)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>

                            <div className="chart-container">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                    <h3>Stock Price Analysis</h3>
                                    <select
                                        style={{ padding: '0.5rem', background: '#0f172a', color: 'white', border: '1px solid var(--border-color)', borderRadius: '0.5rem' }}
                                        value={selectedTicker || ''}
                                        onChange={e => setSelectedTicker(e.target.value)}
                                    >
                                        {Object.keys(btResult.daily_prices).map(t => <option key={t} value={t}>{t}</option>)}
                                    </select>
                                </div>
                                <ResponsiveContainer width="100%" height={400}>
                                    <ComposedChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                        <XAxis dataKey="date" stroke="#94a3b8" />
                                        <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                                        <Tooltip contentStyle={{ backgroundColor: '#1e293b' }} itemStyle={{ color: '#fff' }} />
                                        <Legend />
                                        <Line type="monotone" dataKey="close" stroke="#3b82f6" dot={false} name="Price" />
                                        <Scatter name="Buy" dataKey="buy" fill="#10b981" shape="circle" />
                                        <Scatter name="Sell" dataKey="sell" fill="#ef4444" shape="triangle" />
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
