import React from 'react'
import './FireStatus.css'

function FireStatus({ status, isDangerous, currentTime, duration }) {
  // Default state when no status
  if (!status) {
    return (
      <div className="fire-status-container">
        <div className="fire-status-content">
          <div className="status-card no-data">
            <div>
              <div className="status-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="6" y="4" width="4" height="16" rx="1" stroke="currentColor" strokeWidth="2"/>
                  <rect x="14" y="4" width="4" height="16" rx="1" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <p className="status-text">Waiting for video playback...</p>
            </div>
          </div>
          <div className="timestamp-info">
            <span>No timestamp</span>
          </div>
        </div>
      </div>
    )
  }
  
  // Determine the status type and styling
  const statusClass = status.fire_detected 
    ? (isDangerous ? 'fire-dangerous' : 'no-fire')
    : 'no-fire'
  
  return (
    <div className="fire-status-container">
      <div className="fire-status-content">
        <div className={`status-card ${statusClass}`}>
          <div>
          {status.fire_detected ? (
            <>
              <div className="status-icon">
                {isDangerous ? (
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                    <path d="M12 8V12M12 16H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : (
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 14C19 18.4183 15.4183 22 11 22C6.58172 22 3 18.4183 3 14C3 11.5 5 5.5 5 5.5C5 5.5 6.5 9 9 9C9 9 8 2 13 2C13 2 11.5 6 14 6C14 6 12.5 10 15 10C15 10 19 9.5 19 14Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </div>
              <p className="status-text">{isDangerous ? 'Fire Detected' : 'No Danger'}</p>
              
              <div className="status-details">
                {isDangerous && (
                  <div className="danger-alert">
                    <span className="danger-icon">⚠️</span>
                    <span className="danger-text">DANGEROUS FIRE</span>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <div className="status-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <p className="status-text">No Fire Detected</p>
              <p className="status-subtext">Area is clear</p>
            </>
          )}
          </div>
        </div>
        
        <div className="timestamp-info">
          <span>Video Position: {currentTime?.toFixed(1)}s / {duration?.toFixed(1)}s</span>
          <span className="detection-time">Detection at: {status.timestamp?.toFixed(1)}s</span>
        </div>
      </div>
    </div>
  )
}

export default FireStatus