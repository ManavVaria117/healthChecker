import axios from 'axios';

const api = axios.create({
  baseURL: 'https://healthcheck-backend.onrender.com/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getSymptoms = async () => {
  try {
    const response = await api.get('/symptoms');
    return response.data;
  } catch (error) {
    console.error('Error fetching symptoms:', error);
    throw error;
  }
};

export const getPredictions = async (symptoms) => {
  try {
    const response = await api.post('/predict', { symptoms });
    return response.data;
  } catch (error) {
    console.error('Error getting predictions:', error);
    throw error;
  }
};
