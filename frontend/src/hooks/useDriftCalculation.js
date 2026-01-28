import { useState, useCallback } from 'react';
import { calculateDrift, previewDrift } from '../services/api';

/**
 * Custom hook for drift calculations
 */
export function useDriftCalculation() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const calculate = useCallback(async (params) => {
        setLoading(true);
        setError(null);

        try {
            const data = await calculateDrift(params);
            setResult(data);
            return data;
        } catch (err) {
            const message = err.response?.data?.detail || err.message || 'Calculation failed';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const preview = useCallback(async (params) => {
        try {
            const data = await previewDrift(params);
            return data;
        } catch (err) {
            console.warn('Preview failed:', err);
            return null;
        }
    }, []);

    const clear = useCallback(() => {
        setResult(null);
        setError(null);
    }, []);

    return {
        loading,
        result,
        error,
        calculate,
        preview,
        clear,
    };
}
