import React from 'react'
import './TimelineStats.css'

function TimelineStats({ stats, fireTimeline }) {
  return (
    <div className="timeline-panel">
      <div className="panel-header">
        <h3>
          <i className="fas fa-chart-bar"></i>
          Timeline Analysis
        </h3>
      </div>
      
      <div className="timeline-stats">
        <div className="stat-item">
          <i className="fas fa-fire"></i>
          <span>Fire Frames: <strong>{stats?.fireFrames || 0}</strong></span>
        </div>
        <div className="stat-item">
          <i className="fas fa-exclamation-circle"></i>
          <span>Emergency Frames: <strong>{stats?.emergencyFrames || 0}</strong></span>
        </div>
      </div>
      
      <div className="timeline-content">
        {fireTimeline && fireTimeline.length > 0 ? (
          <div className="fire-periods">
            <h4>Fire Detection Periods</h4>
            {fireTimeline.map((period, index) => (
              <div key={index} className="fire-period">
                <span className="period-number">Period {index + 1}:</span>
                <span className="period-time">
                  {period.start.toFixed(1)}s - {period.end.toFixed(1)}s
                  ({(period.end - period.start).toFixed(1)}s)
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="timeline-chart">
            <p>No fire timeline data available</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TimelineStats