import React from 'react';
import './Home.css';
import { useNavigate } from 'react-router-dom';

const Home = () => {
    const navigate = useNavigate();

    return (
        <div className="home-container">
            <div className="home-content">
                <h1>Algo Trading Platform</h1>
                <p>Choose your trading mode</p>

                <div className="mode-cards">
                    <div className="mode-card paper" onClick={() => navigate('/paper')}>
                        <div className="mode-icon">📝</div>
                        <h2>Paper Trading</h2>
                        <p>Practice with virtual money - Risk-free testing</p>
                        <button className="mode-btn">Enter Paper Trading →</button>
                    </div>

                    <div className="mode-card live" onClick={() => navigate('/live')}>
                        <div className="mode-icon">🔴</div>
                        <h2>Live Trading</h2>
                        <p>Trade with real money - Use with caution</p>
                        <button className="mode-btn danger">Enter Live Trading →</button>
                    </div>

                    <div className="mode-card docs" onClick={() => navigate('/docs')}>
                        <div className="mode-icon">📚</div>
                        <h2>Documentation</h2>
                        <p>Learn about strategies and how the bot works</p>
                        <button className="mode-btn" style={{ background: '#a78bfa', color: '#fff' }}>Read Docs →</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
