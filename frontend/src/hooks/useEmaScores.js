/**
 * Custom React Hook: useEmaScores
 * Fetch EMA score timeline data
 */

import { useState, useEffect } from 'react';
import { getEMATimeline } from '../api/endpoints';

export const useEmaScores = (userId = 'default_user', days = 1) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getEMATimeline(userId, days);
      setData(result.data || []);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch EMA scores';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
  }, [userId, days]);

  return { data, loading, error, refetch };
};
