import React from 'react'
import { formatTime } from '../utils/time'
import './Timeline.css'

function Timeline({ currentTime, duration, analysisResults, onSeek }) {
  const percentage = duration > 0 ? (currentTime / duration) * 100 : 0

  const handleTimelineClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const percent = ((e.clientX - rect.left) / rect.width) * 100
    onSeek(percent)
  }

  const renderFireMarkers = () => {
    if (!analysisResults || analysisResults.length === 0) return null

    return analysisResults
      .filter(result => result.fire_detected)
      .map((result, index) => {
        const position = (result.timestamp / duration) * 100
        const isEmergency = result.fire_characteristics?.call_911_warranted
        const emergencyLevel = result.fire_characteristics?.emergency_level

        let markerClass = 'fire-marker'
        if (isEmergency) {
          markerClass += ' emergency'
        } else if (emergencyLevel === 'alert') {
          markerClass += ' alert'
        }

        return (
          <div
            key={`marker-${index}`}
            className={markerClass}
            style={{ left: `${position}%` }}
          />
        )
      })
  }

  return (
    <div className="timeline-container">
      <span className="time-display">{formatTime(currentTime)}</span>
      
      <div className="timeline-wrapper" onClick={handleTimelineClick}>
        <div className="timeline-track">
          <div 
            className="timeline-progress" 
            style={{ width: `${percentage}%` }}
          />
          <div className="fire-markers">
            {renderFireMarkers()}
          </div>
        </div>
        <input
          type="range"
          className="timeline"
          min="0"
          max="100"
          value={percentage}
          onChange={(e) => onSeek(parseFloat(e.target.value))}
        />
      </div>
      
      <span className="time-display">{formatTime(duration)}</span>
    </div>
  )
}

export default Timeline