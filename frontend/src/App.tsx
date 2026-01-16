import { Routes, Route } from 'react-router-dom';
import { ChatInterface } from './components/ChatInterface';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import './App.css';

function App() {
  return (
    <div className="app-container relative">
      <Routes>
        <Route path="/" element={<ChatInterface />} />
        <Route path="/analytics" element={<AnalyticsDashboard />} />
      </Routes>
    </div>
  );
}

export default App;
