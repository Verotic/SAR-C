/**
 * SAR-C API Client
 * Handles communication with the FastAPI backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Calculate drift area based on LKP and parameters
 * @param {Object} params - Drift calculation parameters
 * @param {Object} params.lkp - Last Known Position {lat, lon}
 * @param {string} params.incident_time - ISO timestamp of incident
 * @param {number} params.projection_hours - Hours to project forward
 * @param {string} params.object_type - Type of drifting object
 * @param {number} params.num_particles - Number of Monte Carlo particles
 * @returns {Promise<Object>} Drift calculation result with GeoJSON polygons
 */
export async function calculateDrift(params) {
    const response = await api.post('/api/drift/calculate', params);
    return response.data;
}

/**
 * Get available object types and their leeway coefficients
 * @returns {Promise<Object>} Object types with coefficients
 */
export async function getObjectTypes() {
    const response = await api.get('/api/drift/object-types');
    return response.data;
}

/**
 * Quick preview calculation with fewer particles
 * @param {Object} params - Same as calculateDrift
 * @returns {Promise<Object>} Preview result
 */
export async function previewDrift(params) {
    const response = await api.post('/api/drift/preview', params);
    return response.data;
}

/**
 * Check API and Copernicus connection status
 * @returns {Promise<Object>} Status information
 */
export async function getStatus() {
    const response = await api.get('/api/data/status');
    return response.data;
}

/**
 * Get currents data for an area
 * @param {Object} bbox - Bounding box {min_lat, max_lat, min_lon, max_lon}
 * @returns {Promise<Object>} Currents summary
 */
export async function getCurrentsData(bbox) {
    const response = await api.get('/api/data/currents', { params: bbox });
    return response.data;
}

/**
 * Get wind data for an area
 * @param {Object} bbox - Bounding box {min_lat, max_lat, min_lon, max_lon}
 * @returns {Promise<Object>} Wind summary
 */
export async function getWindData(bbox) {
    const response = await api.get('/api/data/wind', { params: bbox });
    return response.data;
}

export default api;
