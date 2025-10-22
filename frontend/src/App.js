import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Select from 'react-select';
import { FaSearch, FaHeartbeat, FaInfoCircle, FaSpinner } from 'react-icons/fa';
import './App.css';

// Sample symptoms to show when no search is performed
const SAMPLE_SYMPTOMS = [
  'fever', 'headache', 'fatigue', 'cough', 'nausea',
  'dizziness', 'sore_throat', 'shortness_of_breath', 'body_ache'
];

// Custom styles for react-select
const customStyles = {
  control: (provided) => ({
    ...provided,
    minHeight: '56px',
    border: '2px solid #e1e5ee',
    boxShadow: 'none',
    '&:hover': {
      borderColor: '#a5c0ee',
    },
  }),
  menu: (provided) => ({
    ...provided,
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
  }),
  multiValue: (provided) => ({
    ...provided,
    backgroundColor: '#e9f5ff',
    borderRadius: '16px',
    padding: '2px 8px',
  }),
  multiValueLabel: (provided) => ({
    ...provided,
    color: '#4a6fa5',
    fontSize: '0.9rem',
  }),
  multiValueRemove: (provided) => ({
    ...provided,
    color: '#4a6fa5',
    ':hover': {
      backgroundColor: '#d1e5fb',
      color: '#2c5282',
    },
  }),
};

function App() {
  const [symptomList, setSymptomList] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showInfo, setShowInfo] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  // Fetch symptoms from API
  useEffect(() => {
    const fetchSymptoms = async () => {
      try {
        const response = await axios.get('/api/symptoms');
        console.log('API Response Data:', response.data);
        const options = response.data.symptoms.map(s => ({
          value: s,
          label: s.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        }));
        setSymptomList(options);
      } catch (err) {
        console.error('Error fetching symptoms:', err);
        setError('Failed to load symptoms. Please try again later.');
      }
    };

    fetchSymptoms();
  }, []);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (selectedSymptoms.length === 0) {
      setError("Please select at least one symptom");
      return;
    }

    setLoading(true);
    setError('');
    setPredictions([]);

    const symptoms = selectedSymptoms.map(s => s.value);

    try {
      const response = await axios.post('/api/predict', { symptoms });
      setPredictions(response.data.top3_predictions);
    } catch (err) {
      setError(err.response?.data?.error || 'Error connecting to the prediction service. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Format probability to percentage
  const formatProbability = (prob) => {
    return Math.round(prob * 100);
  };

  // Get severity color based on probability
  const getSeverityColor = (prob) => {
    const percentage = prob * 100;
    if (percentage > 70) return '#dc3545'; // High probability - red
    if (percentage > 40) return '#ffc107'; // Medium probability - yellow
    return '#28a745'; // Low probability - green
  };

  // Handle input change for typing animation
  const handleInputChange = useCallback(() => {
    if (!isTyping) {
      setIsTyping(true);
      setTimeout(() => setIsTyping(false), 1000);
    }
  }, [isTyping]);

  // Get sample symptoms for the info card
  const getSampleSymptoms = () => {
    return SAMPLE_SYMPTOMS
      .sort(() => 0.5 - Math.random())
      .slice(0, 5)
      .map(s => s.replace(/_/g, ' '))
      .join(', ');
  };

  return (
    <div className="App">
      <header className="header">
        <h1><FaHeartbeat className="pulse" /> Symptom Checker</h1>
        <p>Select your symptoms and get instant predictions about possible conditions</p>
      </header>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="symptom-select">
              What symptoms are you experiencing? <span className="required">*</span>
            </label>
            <div className="select-container">
              <Select
                id="symptom-select"
                className="custom-select"
                classNamePrefix="custom-select"
                options={symptomList}
                isMulti
                isSearchable
                isClearable
                placeholder="Type or select symptoms (e.g., fever, headache, fatigue)..."
                noOptionsMessage={() => "No symptoms found. Try a different search term."}
                onChange={(selected) => setSelectedSymptoms(selected || [])}
                onInputChange={handleInputChange}
                styles={customStyles}
                isLoading={symptomList.length === 0}
                loadingMessage={() => "Loading symptoms..."}
              />
            </div>
            <div className="symptom-hint">
              {selectedSymptoms.length === 0 && (
                <span>Start typing to search for symptoms or select from the list</span>
              )}
              {selectedSymptoms.length > 0 && (
                <span>{selectedSymptoms.length} symptom{selectedSymptoms.length !== 1 ? 's' : ''} selected</span>
              )}
            </div>
          </div>

          <button 
            type="submit" 
            disabled={selectedSymptoms.length === 0 || loading}
            className={isTyping ? 'typing' : ''}
          >
            {loading ? (
              <>
                <FaSpinner className="spinner" /> Analyzing...
              </>
            ) : (
              <>
                <FaSearch /> Check Symptoms
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <FaInfoCircle /> {error}
          </div>
        )}
      </div>

      {loading && (
        <div className="loading">
          <FaSpinner className="spinner" /> Analyzing your symptoms...
        </div>
      )}

      {predictions.length > 0 && (
        <div className="results">
          <h2>Possible Conditions</h2>
          <p className="results-description">
            Based on your symptoms, here are the most likely conditions (in order of probability):
          </p>
          
          <ul className="prediction-list">
            {predictions.map((prediction, idx) => (
              <li key={idx} className="prediction-item">
                <div className="prediction-rank">
                  <div className="rank-badge">{idx + 1}</div>
                  <div>
                    <h3 className="prediction-name">
                      {prediction.disease.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </h3>
                    <div className="confidence-meter">
                      <div 
                        className="confidence-bar"
                        style={{
                          width: `${formatProbability(prediction.probability)}%`,
                          backgroundColor: getSeverityColor(prediction.probability)
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
                <div 
                  className="prediction-probability"
                  style={{ color: getSeverityColor(prediction.probability) }}
                >
                  {formatProbability(prediction.probability)}% confidence
                </div>
              </li>
            ))}
          </ul>

          <div className="disclaimer">
            <FaInfoCircle /> <strong>Disclaimer:</strong> This tool is for informational purposes only and is not a 
            substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your 
            physician or other qualified health provider with any questions you may have regarding a medical condition.
          </div>
        </div>
      )}

      {!loading && predictions.length === 0 && (
        <div className="info-card">
          <h3>How to use this tool:</h3>
          <ol>
            <li>Type or select your symptoms in the search box above</li>
            <li>You can select multiple symptoms</li>
            <li>Click "Check Symptoms" to get predictions</li>
          </ol>
          <p className="example">
            <strong>Example:</strong> Try searching for "<em>{getSampleSymptoms()}</em>"
          </p>
        </div>
      )}

      <footer className="footer">
        <p>
          &copy; {new Date().getFullYear()} HealthCheck AI | 
          <button 
            className="info-link" 
            onClick={() => setShowInfo(!showInfo)}
          >
            {showInfo ? 'Hide' : 'Show'} Info
          </button>
        </p>
        
        {showInfo && (
          <div className="info-panel">
            <p>
              This application uses machine learning to predict possible medical conditions based on symptoms. 
              The predictions are based on patterns in the training data and should not be considered a diagnosis.
            </p>
            <p>
              <strong>Model:</strong> Random Forest Classifier | 
              <strong>Top-3 Accuracy:</strong> ~92%
            </p>
          </div>
        )}
      </footer>
    </div>
  );
}

export default App;
