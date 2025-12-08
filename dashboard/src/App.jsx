import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './Home';
import SessionsList from './SessionsList';
import Dashboard from './Dashboard';
import Documentation from './Documentation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/paper" element={<SessionsList mode="PAPER" />} />
        <Route path="/live" element={<SessionsList mode="LIVE" />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/docs" element={<Documentation />} />
      </Routes>
    </Router>
  );
}

export default App;
