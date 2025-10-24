import axios from 'axios';

const api = axios.create({
  baseURL: 'https://healthcheck-backend.onrender.com/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: false,  // Disable credentials for now to simplify CORS
  timeout: 10000,  // 10 second timeout
  crossDomain: true,
  responseType: 'json'
});

// Add a request interceptor to handle errors
api.interceptors.request.use(
  config => {
    // You can add auth headers here if needed
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // The request was made and the server responded with a status code
      console.error('Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

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
