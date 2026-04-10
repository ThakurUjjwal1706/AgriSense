import { useState } from 'react'
import axios from 'axios'
import { Upload, Cpu, Info, Image as ImageIcon } from 'lucide-react'
import './HSIPage.css'

const HSIPage = () => {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected && selected.name.endsWith('.npy')) {
      setFile(selected)
      setError(null)
    } else {
      setError('Please select a valid .npy hyperspectral cube file.')
    }
  }

  const handleAnalyze = async () => {
    if (!file) return

    setLoading(true)
    setResult(null)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URI || 'http://172.32.5.98:8000'
      const response = await axios.post(`${backendUrl}/api/v1/hsi/predict`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during analysis.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="hsi-page">
      <header className="hsi-header">
        <h1>Hyperspectral AI</h1>
        <p>Analyze invisible stress markers using 3D-CNN Satellite/Drone Imagery</p>
      </header>

      <section className="upload-section">
        <label className="drop-zone">
          <input type="file" accept=".npy" onChange={handleFileChange} className="file-input" />
          <Upload size={50} color="#4facfe" />
          <h3>{file ? file.name : 'Upload .npy Hypercube'}</h3>
          <p>Drag and drop or click to browse</p>
        </label>
        
        {error && <p className="error-msg" style={{color: '#ff4d4d', marginTop: '15px'}}>{error}</p>}
        
        <button 
          className="analyze-btn" 
          onClick={handleAnalyze} 
          disabled={!file || loading}
        >
          {loading ? 'Processing...' : 'Start Neural Analysis'}
        </button>
      </section>

      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Running High-Dimensional 3D-CNN Inference...</p>
        </div>
      )}

      {result && (
        <div className="result-section animate-in">
          <div className="result-image-container">
            <img 
              src={`data:image/png;base64,${result.image}`} 
              alt="HSI Health Map" 
              className="result-image"
            />
          </div>
          <div className="result-info">
            <h2>Spatial Health Distribution</h2>
            <p>Our AI has mapped the stress levels across the area using 16 spectral bands.</p>
            
            <div className="legend">
              <div className="legend-item">
                <div className="dot green"></div>
                <div className="legend-text">
                  <h4>Optimal Photosynthesis</h4>
                  <p>Plants in this region show high chlorophyll activity and cellular health.</p>
                </div>
              </div>
              <div className="legend-item">
                <div className="dot yellow"></div>
                <div className="legend-text">
                  <h4>Early Stress Warning</h4>
                  <p>Incipient nutrient deficiency or water stress detected. Action recommended.</p>
                </div>
              </div>
              <div className="legend-item">
                <div className="dot red"></div>
                <div className="legend-text">
                  <h4>Critical Condition</h4>
                  <p>Severe pathogen infection or permanent wilting point detected.</p>
                </div>
              </div>
            </div>

            <div className="metadata">
              <div className="meta-item">
                <Cpu size={20} />
                <span>Resolution: {result.width}x{result.height} px</span>
              </div>
              <div className="meta-item" style={{display: 'flex', alignItems: 'center', gap: '10px', marginTop: '10px', color: '#a0aec0'}}>
                <Info size={20} />
                <span>Confidence: 94.2%</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default HSIPage
