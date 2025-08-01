import React, { useEffect, useRef } from 'react'
import './Timeline.css'

function Timeline({ currentTime, duration, detections, onSeek }) {
  const sliderRef = useRef(null)
  
  // Calculate percentage of current position
  const percentage = duration > 0 ? (currentTime / duration) * 100 : 0
  
  // Handle slider change
  const handleSliderChange = (e) => {
    const newTime = (e.target.value / 100) * duration
    if (onSeek) {
      onSeek(newTime)
    }
  }
  
  // Format time display
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }
  
  // Calculate fire detection markers
  const getDetectionMarkers = () => {
    if (!detections || !duration) return []
    
    return detections
      .filter(d => d.fire_detected)
      .map(d => ({
        position: (d.timestamp / duration) * 100,
        isDangerous: d.is_dangerous,
        timestamp: d.timestamp
      }))
  }
  
  const markers = getDetectionMarkers()
  
  return (
    <div className="timeline-container">
      <div className="timeline-header">
        <h3>Detection Timeline</h3>
        <div className="time-display">
          <span className="current-time">{formatTime(currentTime)}</span>
          <span className="separator">/</span>
          <span className="total-time">{formatTime(duration)}</span>
        </div>
      </div>
      
      <div className="timeline-content">
        <div className="timeline-track">
          {/* Fire detection markers */}
          {markers.map((marker, index) => (
            <div
              key={index}
              className={`detection-marker ${marker.isDangerous ? 'dangerous' : 'normal'}`}
              style={{ left: `${marker.position}%` }}
              title={`Fire detected at ${formatTime(marker.timestamp)}`}
            />
          ))}
          
          {/* Progress bar */}
          <div className="timeline-progress" style={{ width: `${percentage}%` }} />
          
          {/* Slider input */}
          <input
            ref={sliderRef}
            type="range"
            className="timeline-slider"
            min="0"
            max="100"
            value={percentage}
            onChange={handleSliderChange}
            step="0.1"
          />
        </div>
        
        {/* Timeline labels */}
        <div className="timeline-labels">
          <span className="label-start">Start</span>
          <span className="label-end">End</span>
        </div>
        
        {/* Detection zones */}
        <div className="detection-zones">
          {detections && detections.length > 0 && (
            <>
              {detections.some(d => !d.fire_detected) && (
                <div className="zone-label safe">
                  <span className="zone-icon">✓</span>
                  <span>Safe</span>
                </div>
              )}
              {detections.some(d => d.fire_detected && !d.is_dangerous) && (
                <div className="zone-label warning">
                  <span className="zone-icon">🔥</span>
                  <span>Fire Detected</span>
                </div>
              )}
              {detections.some(d => d.is_dangerous) && (
                <div className="zone-label danger">
                  <span className="zone-icon">⚠️</span>
                  <span>Dangerous</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Timeline