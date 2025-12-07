import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Home.css';
import { useNavigate } from 'react-router-dom';

const API_URL = "http://localhost:8000";

const Home = () => {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);
    const [showCreate, setShowCreate] = useState(false);

    // Create Form State
    const [newSessionName, setNewSessionName] = useState("");
    const [selectedStrategies, setSelectedStrategies] = useState(["GoldenCross_SMA"]);

    const fetchSessions = async () => {
        try {
            const res = await axios.get(`${API_URL}/sessions`);
            setSessions(res.data);
        } catch (e) {
            console.error("Failed to fetch sessions", e);
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        if (selectedStrategies.length === 0) {
            alert("Please select at least one strategy");
            return;
        }
        try {
            await axios.post(`${API_URL}/sessions`, {
                name: newSessionName,
                strategies: selectedStrategies,
                mode: "PAPER"
            });
            setShowCreate(false);
            fetchSessions();
            setNewSessionName("");
            setSelectedStrategies(["GoldenCross_SMA"]);
        } catch (e) {
            if (e.response && e.response.status === 400) {
                alert(e.response.data.detail);
            } else {
                alert("Failed to create session: " + (e.response?.data?.detail || e.message));
            }
        }
    };

    const handleDelete = async (sessionId, sessionName, e) => {
        e.stopPropagation();

        if (!window.confirm(`Are you sure you want to delete "${sessionName}"? This will remove all associated data.`)) {
            return;
        }

        try {
            await axios.delete(`${API_URL}/sessions/${sessionId}`);
            fetchSessions();
        } catch (e) {
            alert("Failed to delete session: " + (e.response?.data?.detail || e.message));
        }
    };

    const toggleStrategy = (stratName) => {
        if (selectedStrategies.includes(stratName)) {
            setSelectedStrategies(selectedStrategies.filter(s => s !== stratName));
        } else {
            setSelectedStrategies([...selectedStrategies, stratName]);
        }
    };

    return (
        <div className="home-container">
            <div className="home-content">
                <h1>Algo Trading Platform</h1>
                <p>Manage your trading sessions and strategies.</p>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '2rem 0' }}>
                    <h2>Active Sessions</h2>
                    <button className="primary-btn" onClick={() => setShowCreate(true)}>+ New Session</button>
                </div>

                <div className="sessions-list">
                    {sessions.length === 0 ? (
                        <div style={{ textAlign: 'center', opacity: 0.7 }}>No active sessions found. Create one to get started!</div>
                    ) : (
                        sessions.map(session => (
                            <div key={session.id} className="session-card" onClick={() => navigate(`/dashboard?session_id=${session.id}`)}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div style={{ flex: 1 }}>
                                        <h3>{session.name}</h3>
                                        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#ccc' }}>
                                            Mode: {session.mode} • Created: {new Date(session.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                        <span className={`badge ${session.status === 'RUNNING' ? 'badge-buy' : 'badge-sell'}`}>{session.status}</span>
                                        <button
                                            className="delete-btn"
                                            onClick={(e) => handleDelete(session.id, session.name, e)}
                                            title="Delete session"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Create Modal */}
                {showCreate && (
                    <div className="modal-overlay">
                        <div className="modal">
                            <h2>Create New Session</h2>
                            <form onSubmit={handleCreate}>
                                <label>Session Name (must be unique)</label>
                                <input
                                    value={newSessionName}
                                    onChange={e => setNewSessionName(e.target.value)}
                                    placeholder="e.g. Multi-Strategy Test"
                                    required
                                />

                                <label>Select Strategies (one or more)</label>
                                <div className="strategy-options">
                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={selectedStrategies.includes("GoldenCross_SMA")}
                                            onChange={() => toggleStrategy("GoldenCross_SMA")}
                                        />
                                        <strong>Golden Cross (SMA)</strong> - Moving Average Crossover (10/30)
                                    </label>

                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={selectedStrategies.includes("RSI_Oscillator")}
                                            onChange={() => toggleStrategy("RSI_Oscillator")}
                                        />
                                        <strong>RSI Oscillator</strong> - Buy oversold (&lt;30), Sell overbought (&gt;70)
                                    </label>

                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={selectedStrategies.includes("MACD_Crossover")}
                                            onChange={() => toggleStrategy("MACD_Crossover")}
                                        />
                                        <strong>MACD Crossover</strong> - Trend following with signal line
                                    </label>

                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={selectedStrategies.includes("Bollinger_Bands")}
                                            onChange={() => toggleStrategy("Bollinger_Bands")}
                                        />
                                        <strong>Bollinger Bands</strong> - Mean reversion (20-period, 2σ)
                                    </label>

                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={selectedStrategies.includes("Momentum_Trend")}
                                            onChange={() => toggleStrategy("Momentum_Trend")}
                                        />
                                        <strong>Momentum Trend</strong> - Price momentum (10-day, 2% threshold)
                                    </label>
                                </div>

                                <div className="modal-actions">
                                    <button type="button" onClick={() => setShowCreate(false)}>Cancel</button>
                                    <button type="submit" className="primary-btn">Create & Launch</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default Home;
