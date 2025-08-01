import React from 'react'
import './DetectionSlider.css'

function DetectionSlider({ detections, currentIndex, currentTime, onIndexChange }) {
  if (!detections || detections.length === 0) {
    return null
  }

  const handleSliderChange = (e) => {
    const newIndex = parseInt(e.target.value)
    if (onIndexChange) {
      onIndexChange(newIndex)
    }
  }

  const currentDetection = detections[currentIndex] || detections[0]
  
  // Format time display
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="detection-slider-container">
      <div className="slider-header">
        <span className="slider-label">Detection Timeline</span>
        <span className="slider-position">
          Position {currentIndex + 1} of {detections.length} • {formatTime(currentDetection.timestamp)}
        </span>
      </div>
      
      <div className="slider-wrapper">
        <input
          type="range"
          className="detection-slider"
          min="0"
          max={detections.length - 1}
          step="1"
          value={currentIndex}
          onChange={handleSliderChange}
        />
        
        {/* Detection markers */}
        <div className="detection-markers">
          {detections.map((detection, index) => {
            // Calculate position with proper alignment
            let position;
            if (detections.length === 1) {
              position = 50; // Center if only one detection
            } else {
              // Use calc() to properly align with slider thumb
              const percentage = (index / (detections.length - 1)) * 100;
              position = percentage;
            }
            
            // Check if this detection is in the past (at or before current time)
            const isPast = detection.timestamp <= currentTime;
            const isActive = index === currentIndex;
            
            // Determine the marker class
            let markerClass = 'detection-marker';
            if (isPast) {
              // Show actual status for past detections
              if (detection.fire_detected) {
                markerClass += detection.is_dangerous ? ' dangerous' : ' fire';
              } else {
                markerClass += ' clear';
              }
            } else {
              // Future detections are empty/unknown
              markerClass += ' future';
            }
            
            if (isActive) {
              markerClass += ' active';
            }
            
            return (
              <div
                key={index}
                className={markerClass}
                style={{ 
                  left: `${position}%`,
                  transform: 'translateX(-50%)', // Center the dot on its position
                  animationDelay: `${index * 0.05}s` // Stagger animation
                }}
                title={`${formatTime(detection.timestamp)} - ${
                  isPast ? (
                    detection.fire_detected 
                      ? (detection.is_dangerous ? 'Dangerous Fire' : 'Fire Detected')
                      : 'Clear'
                  ) : 'Unknown'
                }`}
              />
            )
          })}
        </div>
      </div>
      
      <div className="slider-legend">
        <div className="legend-item">
          <span className="legend-dot clear"></span>
          <span>Clear</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot fire"></span>
          <span>Fire</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot dangerous"></span>
          <span>Dangerous</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot future"></span>
          <span>Unknown</span>
        </div>
      </div>
    </div>
  )
}

export default DetectionSlider