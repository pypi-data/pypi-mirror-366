import React from 'react'
import classNames from 'classnames'
import './LoadingOverlay.css'

function LoadingOverlay({ isVisible, progress, message }) {
  return (
    <div className={classNames('loading-overlay', { active: isVisible })}>
      <div className="loading-content">
        <div className="loading-spinner"></div>
        <h3>Processing Video</h3>
        <p>{message || 'Analyzing frames for fire detection...'}</p>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="progress-text">{Math.round(progress)}%</p>
      </div>
    </div>
  )
}

export default LoadingOverlay