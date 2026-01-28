import { useState, useEffect } from 'react';
import { getObjectTypes } from '../../services/api';

// Object type display names in Portuguese
const OBJECT_TYPE_LABELS = {
    person_in_water_vertical: 'Pessoa na Água (Vertical)',
    person_in_water_survival: 'Pessoa na Água (Sobrevivência)',
    life_raft: 'Bote Salva-vidas',
    fishing_boat: 'Barco de Pesca',
    kayak: 'Kayak',
    debris: 'Destroços',
};

/**
 * Mission setup form component
 */
export default function MissionSetup({ lkp, onLkpChange, onCalculate, loading }) {
    const [objectType, setObjectType] = useState('person_in_water_vertical');
    const [projectionHours, setProjectionHours] = useState(24);
    const [incidentTime, setIncidentTime] = useState('');
    const [objectTypes, setObjectTypes] = useState(null);

    // Set default incident time to now
    useEffect(() => {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        setIncidentTime(now.toISOString().slice(0, 16));
    }, []);

    // Fetch object types from API
    useEffect(() => {
        async function fetchTypes() {
            try {
                const types = await getObjectTypes();
                setObjectTypes(types);
            } catch (err) {
                console.error('Failed to fetch object types:', err);
            }
        }
        fetchTypes();
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!lkp) {
            alert('Clique no mapa para definir a Última Posição Conhecida (LKP)');
            return;
        }

        onCalculate({
            lkp,
            incident_time: new Date(incidentTime).toISOString(),
            projection_hours: projectionHours,
            object_type: objectType,
            num_particles: 1000,
        });
    };

    const handleClearLkp = () => {
        onLkpChange(null);
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* LKP Section */}
            <div className="form-group">
                <label className="form-label">Última Posição Conhecida (LKP)</label>
                {lkp ? (
                    <div className="coord-display active">
                        <span>📍</span>
                        <span>
                            {lkp.lat.toFixed(4)}°, {lkp.lon.toFixed(4)}°
                        </span>
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={handleClearLkp}
                            style={{ marginLeft: 'auto', padding: '0.25rem 0.5rem' }}
                        >
                            ✕
                        </button>
                    </div>
                ) : (
                    <div className="coord-display">
                        <span>🖱️</span>
                        <span>Clique no mapa para definir</span>
                    </div>
                )}
                <p className="tooltip">
                    Clique na localização aproximada onde o objeto foi visto pela última vez
                </p>
            </div>

            {/* Manual coordinate input */}
            <div className="form-group">
                <div className="form-row">
                    <div>
                        <label className="form-label">Latitude</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="38.7223"
                            value={lkp?.lat?.toFixed(4) || ''}
                            onChange={(e) => {
                                const val = parseFloat(e.target.value);
                                if (!isNaN(val) && val >= -90 && val <= 90) {
                                    onLkpChange({ ...lkp, lat: val, lon: lkp?.lon || 0 });
                                }
                            }}
                        />
                    </div>
                    <div>
                        <label className="form-label">Longitude</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="-9.1393"
                            value={lkp?.lon?.toFixed(4) || ''}
                            onChange={(e) => {
                                const val = parseFloat(e.target.value);
                                if (!isNaN(val) && val >= -180 && val <= 180) {
                                    onLkpChange({ ...lkp, lon: val, lat: lkp?.lat || 0 });
                                }
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Incident Time */}
            <div className="form-group">
                <label className="form-label">Data/Hora do Incidente</label>
                <input
                    type="datetime-local"
                    className="form-input"
                    value={incidentTime}
                    onChange={(e) => setIncidentTime(e.target.value)}
                    required
                />
                <p className="tooltip">
                    Quando o objeto foi visto pela última vez
                </p>
            </div>

            {/* Projection Hours */}
            <div className="form-group">
                <label className="form-label">Projeção (horas)</label>
                <input
                    type="range"
                    className="form-input"
                    min="1"
                    max="72"
                    value={projectionHours}
                    onChange={(e) => setProjectionHours(parseInt(e.target.value))}
                    style={{ cursor: 'pointer' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.25rem' }}>
                    <span className="tooltip">1h</span>
                    <span style={{ fontWeight: 600, color: 'var(--color-primary-light)' }}>
                        {projectionHours} horas
                    </span>
                    <span className="tooltip">72h</span>
                </div>
            </div>

            {/* Object Type */}
            <div className="form-group">
                <label className="form-label">Tipo de Objeto</label>
                <select
                    className="form-input form-select"
                    value={objectType}
                    onChange={(e) => setObjectType(e.target.value)}
                >
                    {Object.entries(OBJECT_TYPE_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>
                            {label}
                        </option>
                    ))}
                </select>
                {objectTypes && objectTypes[objectType] && (
                    <p className="tooltip">
                        Leeway: {objectTypes[objectType].leeway_percent_min.toFixed(1)}% -
                        {objectTypes[objectType].leeway_percent_max.toFixed(1)}% |
                        Divergência: ±{objectTypes[objectType].divergence_angle}°
                    </p>
                )}
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                className="btn btn-primary btn-block"
                disabled={loading || !lkp}
            >
                {loading ? (
                    <>
                        <span className="loading-spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></span>
                        Calculando...
                    </>
                ) : (
                    <>
                        🔍 Calcular Área de Busca
                    </>
                )}
            </button>
        </form>
    );
}
