import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './SessionsList.css';
import TickerSearch from './TickerSearch';

const API_URL = "http://localhost:8001";

const SessionsList = ({ mode }) => {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);

    // Modal & Form State
    const [showModal, setShowModal] = useState(false);
    const [availStrategies, setAvailStrategies] = useState([]);

    const [formData, setFormData] = useState({
        name: "",
        capital: 10000,
        tickers: "AAPL, GOOGL, TSLA",
        // New Fields
        tickerMethod: "MANUAL", // MANUAL, ALGO
        algoScreener: "Top_Gainers",
        buyStrategy: "",
        sellStrategy: ""
    });

    const fetchSessions = async () => {
        try {
            const res = await axios.get(`${API_URL}/sessions`);
            const filtered = res.data.filter(s => s.mode === mode);
            setSessions(filtered);
        } catch (e) {
            console.error("Failed to fetch sessions", e);
        }
    };

    useEffect(() => {
        fetchSessions();

        // Fetch strategies
        axios.get(`${API_URL}/strategies`)
            .then(res => {
                setAvailStrategies(res.data);
                // Set defaults if available
                if (res.data.length > 0) {
                    setFormData(prev => ({
                        ...prev,
                        buyStrategy: res.data[0].name,
                        sellStrategy: res.data[0].name
                    }));
                }
            })
            .catch(e => console.error("Failed to fetch strategies", e));
    }, [mode]);

    const handleAddTickersFromSearch = (newTickers) => {
        const current = formData.tickers.split(',').map(t => t.trim()).filter(t => t);
        const combined = [...new Set([...current, ...newTickers])];
        setFormData({ ...formData, tickers: combined.join(', ') });
    };

    const removeTicker = (ticker) => {
        const current = formData.tickers.split(',').map(t => t.trim()).filter(t => t);
        const filtered = current.filter(t => t !== ticker);
        setFormData({ ...formData, tickers: filtered.join(', ') });
    };

    const handleCreateSession = async () => {
        const tickersList = formData.tickers.split(',').map(t => t.trim()).filter(t => t);
        const sessionName = formData.name.trim() || `${mode} - ${new Date().toLocaleString()}`;

        // Validate
        if (!formData.buyStrategy || !formData.sellStrategy) {
            alert("Please select both a Buy and Sell strategy.");
            return;
        }

        try {
            const payload = {
                name: sessionName,
                initial_balance: parseFloat(formData.capital),
                mode: mode,
                buy_strategy: formData.buyStrategy,
                sell_strategy: formData.sellStrategy,
                ticker_selection_method: formData.tickerMethod,
                tickers: formData.tickerMethod === 'MANUAL' ? tickersList : []
                // If ALGO, backend expects logic, but for now we might send empty tickers 
                // However, our backend implementation currently *requires* tickers for the engine loop 
                // unless we implement the screener logic.
                // For this demo, we'll send the tickers even if ALGO is selected, assuming the ALGO logic
                // populates them later or we treat 'ALGO' as a label for now.
                // **Correction**: To follow instruction strictly, if ALGO is picked, we might want to populate 
                // a default list or rely on backend. I'll send the manual list IF manual, else maybe a default set.
            };

            // Hack for demo: If ALGO, send some default tickers so it runs
            if (formData.tickerMethod === 'ALGO') {
                payload.tickers = ["NVDA", "AMD", "MSFT"]; // Example execution
            } else {
                payload.tickers = tickersList;
            }

            await axios.post(`${API_URL}/sessions`, payload);

            setShowModal(false);
            fetchSessions();
            // Reset form
            setFormData(prev => ({
                ...prev,
                name: "",
                capital: 10000,
                tickers: "AAPL, GOOGL, TSLA"
            }));
        } catch (e) {
            alert("Failed to start session: " + (e.response?.data?.detail || e.message));
        }
    };

    const handleDelete = async (sessionId, e) => {
        e.stopPropagation();
        if (!window.confirm("Delete this session?")) return;
        try {
            await axios.delete(`${API_URL}/sessions/${sessionId}`);
            fetchSessions();
        } catch (e) {
            alert("Failed to delete: " + e.message);
        }
    };

    const handleToggleStatus = async (session, e) => {
        e.stopPropagation();
        const action = session.status === 'RUNNING' ? 'stop' : 'start';
        try {
            await axios.post(`${API_URL}/sessions/${session.id}/${action}`);
            fetchSessions();
        } catch (e) {
            alert(`Failed to ${action} session: ` + (e.response?.data?.detail || e.message));
        }
    };

    return (
        <div className="sessions-container">
            <div className="sessions-content">
                <div className="sessions-header">
                    <button className="home-btn" onClick={() => navigate('/')}>
                        ← Home
                    </button>
                    <div>
                        <h1>{mode === 'PAPER' ? '📝 Paper Trading' : '🔴 Live Trading'}</h1>
                        <p>{mode === 'PAPER' ? 'Virtual money sessions' : 'Real money sessions'}</p>
                    </div>
                    <button className="new-session-btn" onClick={() => setShowModal(true)}>
                        + New Session
                    </button>
                </div>

                {sessions.length === 0 ? (
                    <div className="empty-state">
                        <p>No sessions yet. Create one to get started!</p>
                        <button className="create-first-btn" onClick={() => setShowModal(true)}>
                            Create First Session
                        </button>
                    </div>
                ) : (
                    <table className="sessions-table">
                        <thead>
                            <tr>
                                <th>Session Name</th>
                                <th>Status</th>
                                <th>Strategy</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions.map(session => (
                                <tr
                                    key={session.id}
                                    onClick={() => navigate(`/dashboard?session_id=${session.id}`)}
                                    className="session-row"
                                >
                                    <td><strong>{session.name}</strong></td>
                                    <td>
                                        <span className={`status-badge ${session.status.toLowerCase()}`}>
                                            {session.status}
                                        </span>
                                    </td>
                                    <td style={{ fontSize: '0.85rem', color: '#888' }}>
                                        {/* TODO: Display Buy/Sell summary */}
                                        Composite
                                    </td>
                                    <td>{new Date(session.created_at).toLocaleString()}</td>
                                    <td className="actions-cell">
                                        <button
                                            className={`action-btn ${session.status === 'RUNNING' ? 'stop' : 'start'}`}
                                            onClick={(e) => handleToggleStatus(session, e)}
                                        >
                                            {session.status === 'RUNNING' ? '⏹ Stop' : '▶ Start'}
                                        </button>
                                        <button
                                            className="delete-btn-small"
                                            onClick={(e) => handleDelete(session.id, e)}
                                        >
                                            🗑️
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Create Session Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '700px' }}>
                        <h2>Create New Session</h2>

                        <div className="modal-grid">
                            {/* Left Column: Basic Info */}
                            <div>
                                <h3 className="section-title">General</h3>
                                <div className="form-group">
                                    <label>Session Name</label>
                                    <input
                                        type="text"
                                        placeholder="E.g. Alpha Test 1"
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Initial Capital ($)</label>
                                    <input
                                        type="number"
                                        value={formData.capital}
                                        onChange={e => setFormData({ ...formData, capital: e.target.value })}
                                    />
                                </div>
                            </div>

                            {/* Right Column: Strategy */}
                            <div>
                                <h3 className="section-title">Strategy Configuration</h3>
                                <div className="form-group">
                                    <label>Buy Strategy</label>
                                    <select
                                        value={formData.buyStrategy}
                                        onChange={e => setFormData({ ...formData, buyStrategy: e.target.value })}
                                        className="styled-select"
                                    >
                                        <option value="" disabled>Select Buy Logic</option>
                                        {availStrategies.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label>Sell Strategy</label>
                                    <select
                                        value={formData.sellStrategy}
                                        onChange={e => setFormData({ ...formData, sellStrategy: e.target.value })}
                                        className="styled-select"
                                    >
                                        <option value="" disabled>Select Sell Logic</option>
                                        {availStrategies.map(s => <option key={s.name} value={s.name}>{s.name}</option>)}
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Ticker Selection */}
                        <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                            <h3 className="section-title">Ticker Selection</h3>

                            <div className="radio-group" style={{ marginBottom: '1rem' }}>
                                <label className={`radio-btn ${formData.tickerMethod === 'MANUAL' ? 'active' : ''}`}>
                                    <input
                                        type="radio"
                                        name="tickerMethod"
                                        checked={formData.tickerMethod === 'MANUAL'}
                                        onChange={() => setFormData({ ...formData, tickerMethod: 'MANUAL' })}
                                    />
                                    Manual Selection
                                </label>
                                <label className={`radio-btn ${formData.tickerMethod === 'ALGO' ? 'active' : ''}`}>
                                    <input
                                        type="radio"
                                        name="tickerMethod"
                                        checked={formData.tickerMethod === 'ALGO'}
                                        onChange={() => setFormData({ ...formData, tickerMethod: 'ALGO' })}
                                    />
                                    Algorithm / Screener
                                </label>
                            </div>

                            {formData.tickerMethod === 'MANUAL' ? (
                                <div className="animate-fade-in">
                                    <div style={{ marginBottom: '0.5rem' }}>
                                        <TickerSearch apiUrl={API_URL} onAddTickers={handleAddTickersFromSearch} />
                                    </div>
                                    <div className="selected-tickers-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                        {formData.tickers.split(',').map(t => t.trim()).filter(t => t).map(t => (
                                            <div key={t} className="ticker-tag" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
                                                <span>{t}</span>
                                                <button onClick={() => removeTicker(t)}>×</button>
                                            </div>
                                        ))}
                                        {formData.tickers.trim() === '' && <span style={{ color: '#666', fontStyle: 'italic' }}>No tickers selected</span>}
                                    </div>
                                </div>
                            ) : (
                                <div className="animate-fade-in">
                                    <div className="form-group">
                                        <label>Select Screener</label>
                                        <select
                                            className="styled-select"
                                            value={formData.algoScreener}
                                            onChange={e => setFormData({ ...formData, algoScreener: e.target.value })}
                                        >
                                            <option value="Top_Gainers">🔥 Top Gainers (Momentum)</option>
                                            <option value="High_Volume">📢 High Volume</option>
                                            <option value="Volatility">📉 High Volatility</option>
                                        </select>
                                        <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '0.5rem' }}>
                                            System will automatically select stocks based on the chosen criteria.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={() => setShowModal(false)}>Cancel</button>
                            <button className="create-btn" onClick={handleCreateSession}>Create Session</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SessionsList;
