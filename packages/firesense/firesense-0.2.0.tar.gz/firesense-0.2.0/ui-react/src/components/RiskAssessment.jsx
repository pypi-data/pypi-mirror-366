import React from 'react'
import classNames from 'classnames'
import './RiskAssessment.css'

function RiskAssessment({ fireCharacteristics, isAnalyzing }) {
  const getDisplayValue = (value, isAnalyzing) => {
    if (isAnalyzing && !value) return 'Analyzing...'
    return value || '-'
  }

  const getRiskLevelClass = (level) => {
    if (!level) return ''
    if (level === 'extreme') return 'extreme'
    if (level === 'high') return 'high'
    if (level === 'moderate') return 'moderate'
    return 'low'
  }

  const spreadPotential = fireCharacteristics?.spread_potential || 'low'

  return (
    <div className="risk-card">
      <div className="risk-header">
        <h4>
          <i className="fas fa-shield-alt"></i>
          Risk Assessment
        </h4>
      </div>
      
      <div className="risk-details">
        <div className="risk-item">
          <div className="risk-label">
            <i className="fas fa-arrows-alt"></i>
            <span>Spread Potential</span>
          </div>
          <span className={classNames('risk-level', getRiskLevelClass(spreadPotential))}>
            {isAnalyzing && !fireCharacteristics ? 'Analyzing...' : spreadPotential}
          </span>
        </div>
        
        <div className="risk-item">
          <div className="risk-label">
            <i className="fas fa-tree"></i>
            <span>Vegetation Risk</span>
          </div>
          <p className="risk-description">
            {getDisplayValue(fireCharacteristics?.vegetation_risk, isAnalyzing)}
          </p>
        </div>
        
        <div className="risk-item">
          <div className="risk-label">
            <i className="fas fa-map-marker-alt"></i>
            <span>Location</span>
          </div>
          <p className="risk-description">
            {getDisplayValue(fireCharacteristics?.location, isAnalyzing)}
          </p>
        </div>
      </div>
    </div>
  )
}

export default RiskAssessment