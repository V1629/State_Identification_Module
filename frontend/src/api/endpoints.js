/**
 * API Endpoints
 * All API calls to backend
 */

import client from './client';

// ==================== Analysis Endpoints ====================

/**
 * Analyze a message for emotional state
 */
export const analyzeMessage = async (message, userId = 'default_user') => {
  try {
    const response = await client.post('/api/analyze', {
      message,
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing message:', error);
    throw error;
  }
};

/**
 * Get current emotional states
 */
export const getCurrentStates = async (userId = 'default_user') => {
  try {
    const response = await client.get('/api/states', {
      params: { user_id: userId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching states:', error);
    throw error;
  }
};

/**
 * Get EMA score timeline data
 */
export const getEMATimeline = async (userId = 'default_user', days = 1) => {
  try {
    const response = await client.get('/api/ema-scores', {
      params: { user_id: userId, days },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching EMA timeline:', error);
    throw error;
  }
};

/**
 * Reset user state (for testing)
 */
export const resetUserState = async (userId = 'default_user') => {
  try {
    const response = await client.post('/api/reset', null, {
      params: { user_id: userId },
    });
    return response.data;
  } catch (error) {
    console.error('Error resetting user state:', error);
    throw error;
  }
};

// ==================== Health Check ====================

/**
 * Check if backend is alive
 */
export const healthCheck = async () => {
  try {
    const response = await client.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};
