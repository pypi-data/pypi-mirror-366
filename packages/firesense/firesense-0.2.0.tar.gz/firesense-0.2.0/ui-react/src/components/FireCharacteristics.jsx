import React from 'react'
import './FireCharacteristics.css'

function FireCharacteristics({ fireCharacteristics, isAnalyzing }) {
  const getDisplayValue = (value, isAnalyzing) => {
    if (isAnalyzing && !value) return 'Analyzing...'
    return value || '-'
  }

  return (
    <div className="characteristics-card">
      <div className="characteristics-header">
        <h4>
          <i className="fas fa-fire"></i>
          Fire Characteristics
        </h4>
      </div>
      
      <div className="characteristics-details">
        <div className="char-item">
          <span className="char-label">Size Assessment</span>
          <span className="char-value">
            {getDisplayValue(fireCharacteristics?.size_assessment, isAnalyzing)}
          </span>
        </div>
        
        <div className="char-item">
          <span className="char-label">Smoke Behavior</span>
          <span className="char-value">
            {getDisplayValue(fireCharacteristics?.smoke_behavior, isAnalyzing)}
          </span>
        </div>
        
        <div className="char-item">
          <span className="char-label">Flame Characteristics</span>
          <span className="char-value">
            {getDisplayValue(fireCharacteristics?.flame_characteristics, isAnalyzing)}
          </span>
        </div>
        
        <div className="char-item">
          <span className="char-label">Wind Effect</span>
          <span className="char-value">
            {getDisplayValue(fireCharacteristics?.wind_effect, isAnalyzing)}
          </span>
        </div>
      </div>
    </div>
  )
}

export default FireCharacteristics