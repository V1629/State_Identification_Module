/**
 * Custom React Hook: useStates
 * Fetch current emotional states
 */

import { useState, useEffect } from 'react';
import { getCurrentStates } from '../api/endpoints';

export const useStates = (userId = 'default_user') => {
  const [states, setStates] = useState({
    short_term: 'Neutral',
    mid_term: 'Stable',
    long_term: 'Positive',
    short_term_score: 5.0,
    mid_term_score: 5.0,
    long_term_score: 5.0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getCurrentStates(userId);
      setStates(result);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch states';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
  }, [userId]);

  return { states, loading, error, refetch };
};
