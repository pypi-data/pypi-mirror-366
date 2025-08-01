import React from 'react'
import classNames from 'classnames'
import './FireDetectionPanel.css'

function FireDetectionPanel({ currentFrameAnalysis, isAnalyzing }) {
  const getDetectionStatus = () => {
    if (isAnalyzing && !currentFrameAnalysis) {
      return { text: 'Analyzing...', className: 'analyzing' }
    }
    if (!currentFrameAnalysis) {
      return { text: 'No Analysis', className: 'no-fire' }
    }
    if (currentFrameAnalysis.fire_detected) {
      return { text: 'Fire Detected', className: 'fire-detected' }
    }
    return { text: 'No Fire', className: 'no-fire' }
  }

  const status = getDetectionStatus()
  const confidence = currentFrameAnalysis?.confidence || 0
  const confidencePercent = Math.round(confidence * 100)

  return (
    <div className="analysis-panel">
      <div className="panel-header">
        <h3>
          <i className="fas fa-chart-line"></i>
          Detection Analysis
        </h3>
        <span className="frame-info">
          {currentFrameAnalysis ? 
            `Frame ${currentFrameAnalysis.frame_number} / ${currentFrameAnalysis.timestamp.toFixed(1)}s` : 
            'Frame - / -'}
        </span>
      </div>
      
      <div className="analysis-content">
        <div className="status-card">
          <div className="status-header">
            <h4>Fire Detection</h4>
            <span className={classNames('detection-badge', status.className)}>
              <span className="badge-status">{status.text}</span>
            </span>
          </div>
          
          <div className="confidence-meter">
            <label>Confidence Level</label>
            <div className="meter-container">
              <div className="meter-bar">
                <div 
                  className="meter-fill"
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
              <span className="meter-value">{confidencePercent}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FireDetectionPanel