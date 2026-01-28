import { useEffect } from 'react';
import { MapContainer, TileLayer, useMapEvents, Marker, Popup, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom LKP marker icon
const lkpIcon = new L.DivIcon({
    className: 'lkp-marker',
    html: `
    <div style="
      width: 24px;
      height: 24px;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="
        position: absolute;
        width: 40px;
        height: 40px;
        background: rgba(239, 68, 68, 0.3);
        border-radius: 50%;
        animation: pulse 2s infinite;
      "></div>
      <div style="
        width: 20px;
        height: 20px;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.5);
        position: relative;
        z-index: 1;
      "></div>
    </div>
  `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
});

// Map click handler component
function MapClickHandler({ onMapClick }) {
    useMapEvents({
        click: (e) => {
            onMapClick({ lat: e.latlng.lat, lon: e.latlng.lng });
        },
    });
    return null;
}

// Search area polygon style
const searchAreaStyle = {
    color: '#f97316',
    weight: 2,
    fillColor: '#f97316',
    fillOpacity: 0.15,
};

// Priority zone polygon style
const priorityZoneStyle = {
    color: '#ef4444',
    weight: 3,
    fillColor: '#ef4444',
    fillOpacity: 0.3,
};

/**
 * Main map component for SAR operations
 */
export default function MapView({ lkp, onMapClick, searchResult }) {
    // Default center (Portugal coast)
    const defaultCenter = [38.7223, -9.1393];
    const center = lkp ? [lkp.lat, lkp.lon] : defaultCenter;

    return (
        <div className="map-container">
            <MapContainer
                center={center}
                zoom={8}
                style={{ height: '100%', width: '100%' }}
                zoomControl={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {/* Click handler */}
                <MapClickHandler onMapClick={onMapClick} />

                {/* LKP Marker */}
                {lkp && (
                    <Marker position={[lkp.lat, lkp.lon]} icon={lkpIcon}>
                        <Popup>
                            <strong>Última Posição Conhecida (LKP)</strong>
                            <br />
                            Lat: {lkp.lat.toFixed(4)}°
                            <br />
                            Lon: {lkp.lon.toFixed(4)}°
                        </Popup>
                    </Marker>
                )}

                {/* Search Area Polygon */}
                {searchResult?.search_area && (
                    <GeoJSON
                        key={`search-${JSON.stringify(searchResult.search_area)}`}
                        data={searchResult.search_area}
                        style={searchAreaStyle}
                    />
                )}

                {/* Priority Zone Polygon */}
                {searchResult?.priority_zone && (
                    <GeoJSON
                        key={`priority-${JSON.stringify(searchResult.priority_zone)}`}
                        data={searchResult.priority_zone}
                        style={priorityZoneStyle}
                    />
                )}
            </MapContainer>
        </div>
    );
}
