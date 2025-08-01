import React from 'react'
import classNames from 'classnames'
import './AlertPanel.css'

function AlertPanel({ status, type }) {
  const panelClass = classNames('alert-panel', type)

  return (
    <div className={panelClass}>
      <div className="alert-content">
        <div className="alert-icon">
          <i className="fas fa-fire-flame-curved"></i>
        </div>
        <div className="alert-info">
          <h3>Fire Detection Status</h3>
          <p className="alert-status">{status || 'No Analysis Running'}</p>
        </div>
      </div>
    </div>
  )
}

export default AlertPanel