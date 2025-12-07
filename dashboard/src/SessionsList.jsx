import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import './SessionsList.css';

const API_URL = "http://localhost:8000";

const SessionsList = ({ mode }) => {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);
    const [showCreate, setShowCreate] = useState(false);
    const [newSessionName, setNewSessionName] = useState("");

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
    }, [mode]);

    const quickStart = async () => {
        const sessionName = `${mode} - ${new Date().toLocaleString()}`;
        try {
            const response = await axios.post(`${API_URL}/sessions`, {
                name: sessionName,
                strategies: ["GoldenCross_SMA", "RSI_Oscillator"],
                tickers: ["AAPL", "GOOGL", "TSLA"],
                initial_balance: 10000,
                mode: mode
            });
            navigate(`/dashboard?session_id=${response.data.id}`);
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
                    <button className="new-session-btn" onClick={quickStart}>
                        + New Session
                    </button>
                </div>

                {sessions.length === 0 ? (
                    <div className="empty-state">
                        <p>No sessions yet. Create one to get started!</p>
                        <button className="create-first-btn" onClick={quickStart}>
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
        </div>
    );
};

export default SessionsList;
