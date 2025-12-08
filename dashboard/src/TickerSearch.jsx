
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './TickerSearch.css';

const TickerSearch = ({ apiUrl, onAddTickers }) => {
    const [query, setQuery] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [selectedTags, setSelectedTags] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searching, setSearching] = useState(false);

    // Debounce search
    useEffect(() => {
        const delayDebounceFn = setTimeout(async () => {
            if (query.length >= 1) {
                setSearching(true);
                try {
                    const res = await axios.get(`${apiUrl}/stocks/search?query=${query}`);
                    // Filter out already selected
                    const filtered = res.data.filter(s => !selectedTags.includes(s.symbol));
                    setSuggestions(filtered);
                } catch (error) {
                    console.error("Search failed", error);
                } finally {
                    setSearching(false);
                }
            } else {
                setSuggestions([]);
            }
        }, 500);

        return () => clearTimeout(delayDebounceFn);
    }, [query, apiUrl, selectedTags]);

    const handleSelect = (symbol) => {
        if (!selectedTags.includes(symbol)) {
            setSelectedTags([...selectedTags, symbol]);
        }
        setQuery("");
        setSuggestions([]);
    };

    const handleRemoveTag = (symbol) => {
        setSelectedTags(selectedTags.filter(t => t !== symbol));
    };

    const handleSubmit = async () => {
        if (selectedTags.length === 0) return;
        setLoading(true);
        try {
            await onAddTickers(selectedTags);
            setSelectedTags([]);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ticker-search-container">
            <div className="search-input-group">
                <div style={{ position: 'relative', flex: 1 }}>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search stocks (e.g. Apple, NVDA)..."
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                    {searching && (
                        <div style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', color: '#666' }}>
                            ...
                        </div>
                    )}

                    {suggestions.length > 0 && (
                        <div className="suggestions-list">
                            {suggestions.map(s => (
                                <div key={s.symbol} className="suggestion-item" onClick={() => handleSelect(s.symbol)}>
                                    <span className="suggestion-symbol">{s.symbol}</span>
                                    <span className="suggestion-name">{s.name}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <button
                    className="btn-primary"
                    onClick={handleSubmit}
                    disabled={selectedTags.length === 0 || loading}
                    style={{ opacity: selectedTags.length === 0 ? 0.5 : 1, padding: '0.5rem 1rem' }}
                >
                    {loading ? "Adding..." : "Add Selected"}
                </button>
            </div>

            <div className="tags-container">
                {selectedTags.map(tag => (
                    <div key={tag} className="ticker-tag">
                        <span>{tag}</span>
                        <button onClick={() => handleRemoveTag(tag)}>×</button>
                    </div>
                ))}
                {selectedTags.length === 0 && (
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontStyle: 'italic', alignSelf: 'center' }}>
                        Type to search and add multiple tickers
                    </span>
                )}
            </div>
        </div>
    );
};

export default TickerSearch;
