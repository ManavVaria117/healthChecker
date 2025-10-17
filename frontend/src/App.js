import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [symptoms, setSymptoms] = useState('');
  const [prediction, setPrediction] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setPrediction('');
    setError('');
    setLoading(true);

    // Convert comma-separated input to array
    const symptomsArray = symptoms.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', {
        symptoms: symptomsArray
      });
      setPrediction(response.data.predicted_disease);
    } catch (err) {
      setError(err.response?.data?.error || 'Error connecting to API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Symptom → Disease Predictor</h1>
      <form onSubmit={handleSubmit}>
        <label>Enter symptoms (comma-separated):</label>
        <br />
        <input
          type="text"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          placeholder="fever, cough, tiredness"
          size="50"
        />
        <br />
        <button type="submit">Predict</button>
      </form>

      {loading && <p>Loading...</p>}
      {prediction && <h2>Predicted Disease: {prediction}</h2>}
      {error && <p style={{color:'red'}}>{error}</p>}
    </div>
  );
}

export default App;
