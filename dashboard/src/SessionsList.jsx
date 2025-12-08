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
        strategies: ["GoldenCross_SMA"] // Default selection
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
            .then(res => setAvailStrategies(res.data))
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

        if (formData.strategies.length === 0) {
            alert("Please select at least one strategy.");
            return;
        }

        const sessionName = formData.name.trim() || `${mode} - ${new Date().toLocaleString()}`;

        try {
            await axios.post(`${API_URL}/sessions`, {
                name: sessionName,
                strategies: formData.strategies,
                tickers: tickersList,
                initial_balance: parseFloat(formData.capital),
                mode: mode
            });
            setShowModal(false);
            fetchSessions();
            // Reset form
            setFormData({
                name: "",
                capital: 10000,
                tickers: "AAPL, GOOGL, TSLA",
                strategies: ["GoldenCross_SMA"]
            });
        } catch (e) {
            alert("Failed to start session: " + (e.response?.data?.detail || e.message));
        }
    };

    const toggleStrategy = (stratName) => {
        setFormData(prev => {
            if (prev.strategies.includes(stratName)) {
                return { ...prev, strategies: prev.strategies.filter(s => s !== stratName) };
            }
            return { ...prev, strategies: [...prev.strategies, stratName] };
        });
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
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <h2>Create New Session</h2>

                        <div className="form-group">
                            <label>Session Name (Optional)</label>
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

                        <div className="form-group">
                            <label>Strategies</label>
                            <div className="strategies-grid">
                                {availStrategies.map((s, i) => (
                                    <div
                                        key={i}
                                        className="strategy-check"
                                        onClick={() => toggleStrategy(s.name)}
                                        style={{ borderColor: formData.strategies.includes(s.name) ? 'var(--accent-blue)' : 'transparent' }}
                                    >
                                        <input
                                            type="checkbox"
                                            checked={formData.strategies.includes(s.name)}
                                            readOnly
                                        />
                                        <span>{s.name}</span>
                                    </div>
                                ))}
                                {availStrategies.length === 0 && <p style={{ color: '#666' }}>No strategies found.</p>}
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Tickers</label>
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
