
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Documentation.css';

const strategies = [
    {
        name: "Golden Cross (SMA)",
        key: "GoldenCross_SMA",
        desc: "A trend-following strategy that identifies potential bullish breakouts.",
        logic: "Buys when the short-term Simple Moving Average (SMA 10) crosses ABOVE the long-term SMA (30). Sells when it crosses BELOW.",
        pros: "Captures strong trends; simple to understand.",
        cons: "Lagging indicator; produces false signals in sideways markets.",
        icon: "📈"
    },
    {
        name: "RSI Oscillator",
        key: "RSI_Oscillator",
        desc: "A momentum strategy that exploits overbought and oversold conditions.",
        logic: "Buys when RSI drops below 30 (Oversold). Sells when RSI rises above 70 (Overbought). Uses a 14-period standard setting.",
        pros: "Good for oscillating markets and mean reversion.",
        cons: "Can sell too early in strong bull runs.",
        icon: "📉"
    },
    {
        name: "MACD Crossover",
        key: "MACD_Crossover",
        desc: "Uses the convergence and divergence of moving averages to find momentum shifts.",
        logic: "Buys when the MACD line crosses above the Signal line. Sells when it crosses below. Uses (12, 26, 9) standard parameters.",
        pros: "Combines trend and momentum; very popular.",
        cons: "Also lagging; can whipsaw in chop.",
        icon: "🌊"
    },
    {
        name: "Bollinger Bands Mean Reversion",
        key: "Bollinger_MeanReversion",
        desc: "Assumes price will return to the mean after deviating significantly.",
        logic: "Buys when price touches the Lower Band (2 SD below SMA 20). Sells when it touches the Upper Band.",
        pros: "Excellent in range-bound 'sideways' markets.",
        cons: "Dangerous in strong trending markets (can catch falling knives).",
        icon: "↕️"
    },
    {
        name: "Momentum Breakout",
        key: "Momentum_Breakout",
        desc: "Chases assets that are showing strong recent performance.",
        logic: "Buys if price increased by >2% in the last 10 periods. Sells if momentum fades or price drops.",
        pros: "Capitalizes on FOMO and strong runs.",
        cons: "High risk of buying the top.",
        icon: "🚀"
    }
];

const Documentation = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState("");

    const filteredStrategies = strategies.filter(s =>
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.desc.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.logic.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.key.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getImageSrc = (key) => {
        if (key.includes("MACD")) return "/macd.png";
        if (key.includes("RSI")) return "/macd.png"; // Fallback reuse for style
        return "/golden_cross.png"; // Default for trend/breakout
    };

    return (
        <div className="docs-container">
            <header className="docs-header">
                <button className="home-btn" onClick={() => navigate('/')}>← Home</button>
                <h1>Strategy Documentation</h1>
                <p>Learn how the Algo Trading Bot makes decisions</p>

                <div className="search-bar-container">
                    <input
                        type="text"
                        placeholder="Search strategies (e.g. 'crossover', 'momentum')..."
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                        className="docs-search-input"
                    />
                </div>
            </header>

            <div className="strategies-list">
                {filteredStrategies.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>No matching strategies found.</div>
                ) : filteredStrategies.map(s => (
                    <div key={s.key} className="strategy-detail-card">
                        <div className="strat-visual">
                            <img
                                src={getImageSrc(s.key)}
                                alt={s.name}
                                className="strat-image"
                            />
                        </div>
                        <div className="strat-content">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                                <div className="strat-icon">{s.icon}</div>
                                <h2>{s.name}</h2>
                            </div>

                            <div className="tags">
                                <span className="tag-key">{s.key}</span>
                            </div>
                            <p className="description">{s.desc}</p>

                            <div className="logic-box">
                                <strong>⚙️ Logic:</strong> {s.logic}
                            </div>

                            <div className="pros-cons">
                                <div className="pros">
                                    <strong>✅ Pros:</strong> {s.pros}
                                </div>
                                <div className="cons">
                                    <strong>⚠️ Cons:</strong> {s.cons}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Documentation;
