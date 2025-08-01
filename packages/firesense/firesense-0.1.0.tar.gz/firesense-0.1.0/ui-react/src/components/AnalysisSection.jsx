import React from 'react'
import AlertPanel from './AlertPanel'
import FireDetectionPanel from './FireDetectionPanel'
import EmergencyAssessment from './EmergencyAssessment'
import RiskAssessment from './RiskAssessment'
import FireCharacteristics from './FireCharacteristics'
import TimelineStats from './TimelineStats'
import './AnalysisSection.css'

function AnalysisSection({
  alertStatus,
  alertType,
  currentFrameAnalysis,
  stats,
  fireTimeline,
  isAnalyzing
}) {
  return (
    <aside className="analysis-section">
      <div className="analysis-container">
        <AlertPanel 
          status={alertStatus}
          type={alertType}
        />
        
        <FireDetectionPanel
          currentFrameAnalysis={currentFrameAnalysis}
          isAnalyzing={isAnalyzing}
        />
        
        <EmergencyAssessment
          fireCharacteristics={currentFrameAnalysis?.fire_characteristics}
          isAnalyzing={isAnalyzing}
        />
        
        <RiskAssessment
          fireCharacteristics={currentFrameAnalysis?.fire_characteristics}
          isAnalyzing={isAnalyzing}
        />
        
        <FireCharacteristics
          fireCharacteristics={currentFrameAnalysis?.fire_characteristics}
          isAnalyzing={isAnalyzing}
        />
        
        <TimelineStats
          stats={stats}
          fireTimeline={fireTimeline}
        />
      </div>
    </aside>
  )
}

export default AnalysisSection