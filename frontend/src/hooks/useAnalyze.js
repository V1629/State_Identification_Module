/**
 * Custom React Hook: useAnalyze
 * Handle message analysis with loading and error states
 */

import { useState } from 'react';
import { analyzeMessage as apiAnalyzeMessage } from '../api/endpoints';

export const useAnalyze = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const analyze = async (message, userId = 'default_user') => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiAnalyzeMessage(message, userId);
      setResult(data);
      return data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Analysis failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setLoading(false);
    setError(null);
    setResult(null);
  };

  return { analyze, loading, error, result, reset };
};
