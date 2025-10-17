import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';
import './App.css';

function App() {
  const [symptomList, setSymptomList] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/symptoms')
      .then(res => {
        // react-select expects options as {value, label}
        const options = res.data.symptoms.map(s => ({ value: s, label: s.replace(/_/g,' ') }));
        setSymptomList(options);
      })
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedSymptoms.length === 0) {
      setError("Select at least one symptom");
      return;
    }

    setLoading(true);
    setError('');
    setPredictions([]);

    const symptoms = selectedSymptoms.map(s => s.value);

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', { symptoms });
      setPredictions(response.data.top3_predictions);
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
        <label>Enter symptoms:</label>
        <Select
          options={symptomList}
          isMulti
          onChange={setSelectedSymptoms}
          placeholder="Type to search symptoms..."
        />
        <button type="submit">Predict</button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p style={{color:'red'}}>{error}</p>}

      {predictions.length > 0 && (
        <div>
          <h2>Top 3 Predictions:</h2>
          <ol>
            {predictions.map((p, idx) => (
              <li key={idx}>{p.disease} ({p.probability * 100}%)</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export default App;
