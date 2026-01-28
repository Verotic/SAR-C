/**
 * Results panel displaying drift calculation results
 */
export default function ResultsPanel({ result, error }) {
    if (error) {
        return (
            <div className="results-panel">
                <h3>
                    <span>⚠️</span>
                    Erro
                </h3>
                <p style={{ color: 'var(--color-danger)' }}>{error}</p>
            </div>
        );
    }

    if (!result) {
        return null;
    }

    return (
        <div className="results-panel">
            <h3>
                <span>✅</span>
                Resultados
            </h3>

            <div className="result-item">
                <span className="result-label">Deriva Estimada</span>
                <span className="result-value">
                    {result.estimated_drift_distance_km.toFixed(1)} km
                </span>
            </div>

            <div className="result-item">
                <span className="result-label">Confiança</span>
                <span className="result-value">
                    {(result.confidence_level * 100).toFixed(0)}%
                </span>
            </div>

            <div className="result-item">
                <span className="result-label">Tempo de Cálculo</span>
                <span className="result-value">
                    {result.calculation_time_seconds.toFixed(2)}s
                </span>
            </div>

            <div className="result-item">
                <span className="result-label">Partículas</span>
                <span className="result-value">
                    {result.particles_summary?.total_particles || 1000}
                </span>
            </div>

            <div style={{ marginTop: 'var(--spacing-md)' }}>
                <div className="status-badge success">
                    <span>●</span>
                    Área de busca calculada
                </div>
            </div>

            <div style={{ marginTop: 'var(--spacing-md)', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                <p><strong style={{ color: 'var(--color-secondary)' }}>□ Laranja:</strong> Área total de busca</p>
                <p><strong style={{ color: 'var(--color-danger)' }}>□ Vermelho:</strong> Zona prioritária (80%)</p>
            </div>
        </div>
    );
}
