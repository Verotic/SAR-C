import { useState } from 'react';
import MapView from './components/Map/MapView';
import MissionSetup from './components/Controls/MissionSetup';
import ResultsPanel from './components/UI/ResultsPanel';
import { useDriftCalculation } from './hooks/useDriftCalculation';
import './index.css';

function App() {
  const [lkp, setLkp] = useState(null);
  const { loading, result, error, calculate, clear } = useDriftCalculation();

  const handleMapClick = (coords) => {
    setLkp(coords);
  };

  const handleLkpChange = (newLkp) => {
    setLkp(newLkp);
    if (!newLkp) {
      clear();
    }
  };

  const handleCalculate = async (params) => {
    try {
      await calculate(params);
    } catch (err) {
      console.error('Calculation failed:', err);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="app-logo">
          <h1>🌊 SAR-C</h1>
          <span className="subtitle">Search & Rescue with Copernicus</span>
        </div>
        <div className="status-badge success">
          <span>●</span>
          Sistema Operacional
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <h2>🎯 Configurar Missão</h2>
            <p>Defina os parâmetros de busca</p>
          </div>

          <div className="sidebar-content">
            <MissionSetup
              lkp={lkp}
              onLkpChange={handleLkpChange}
              onCalculate={handleCalculate}
              loading={loading}
            />
          </div>

          <ResultsPanel result={result} error={error} />
        </aside>

        {/* Map */}
        <MapView
          lkp={lkp}
          onMapClick={handleMapClick}
          searchResult={result}
        />

        {/* Loading Overlay */}
        {loading && (
          <div className="loading-overlay">
            <div style={{ textAlign: 'center' }}>
              <div className="loading-spinner"></div>
              <p style={{ marginTop: '1rem', color: 'var(--color-text-muted)' }}>
                Calculando área de busca...
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
