import React from 'react'
import './Header.css'

function Header({ onUpload, onAnalyze, canAnalyze, isAnalyzing }) {
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUpload(file)
    }
  }

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="logo">
          <i className="fas fa-fire-flame-curved"></i>
          <h1>Fire Detection Analysis</h1>
        </div>
        <div className="header-actions">
          <input
            type="file"
            id="fileInput"
            accept="video/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <button 
            className="btn btn-upload"
            onClick={() => document.getElementById('fileInput').click()}
          >
            <i className="fas fa-upload"></i>
            Upload Video
          </button>
          <button 
            className="btn btn-analyze"
            onClick={onAnalyze}
            disabled={!canAnalyze || isAnalyzing}
          >
            <i className="fas fa-search"></i>
            {isAnalyzing ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header