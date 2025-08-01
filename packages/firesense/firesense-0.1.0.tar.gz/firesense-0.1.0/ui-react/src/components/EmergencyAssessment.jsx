import React from 'react'
import classNames from 'classnames'
import './EmergencyAssessment.css'

function EmergencyAssessment({ fireCharacteristics, isAnalyzing }) {
  const getDisplayValue = (value, isAnalyzing) => {
    if (isAnalyzing && !value) return 'Analyzing...'
    return value || '-'
  }

  const getEmergencyLevelClass = (level) => {
    if (!level || level === 'none') return 'none'
    if (level === 'critical') return 'critical'
    if (level === 'alert') return 'alert'
    if (level === 'monitor') return 'monitor'
    return 'none'
  }

  const emergencyLevel = fireCharacteristics?.emergency_level || 'none'
  const call911 = fireCharacteristics?.call_911_warranted || false

  return (
    <div className="emergency-card">
      <div className="emergency-header">
        <h4>
          <i className="fas fa-exclamation-triangle"></i>
          Emergency Assessment
        </h4>
      </div>
      
      <div className="emergency-details">
        <div className="detail-row">
          <span className="detail-label">Fire Type</span>
          <span className="detail-value">
            {getDisplayValue(fireCharacteristics?.fire_type, isAnalyzing)}
          </span>
        </div>
        
        <div className="detail-row">
          <span className="detail-label">Control Status</span>
          <span className="detail-value">
            {getDisplayValue(fireCharacteristics?.control_status, isAnalyzing)}
          </span>
        </div>
        
        <div className="detail-row">
          <span className="detail-label">Emergency Level</span>
          <span className={classNames('detail-value', 'emergency-level', getEmergencyLevelClass(emergencyLevel))}>
            {isAnalyzing && !fireCharacteristics ? 'analyzing' : emergencyLevel}
          </span>
        </div>
        
        {(call911 || isAnalyzing) && (
          <div className="detail-row call-911-row">
            <div className={classNames('call-911-status', call911 ? 'warranted' : 'not-warranted')}>
              <i className="fas fa-phone-alt"></i>
              <span>
                {isAnalyzing && !fireCharacteristics ? 'Analyzing...' : 
                 call911 ? 'CALL 911 NOW' : 'Not Warranted'}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EmergencyAssessment