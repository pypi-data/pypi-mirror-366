import React from 'react'
import Timeline from './Timeline'
import { formatTime } from '../utils/time'
import './VideoControls.css'

function VideoControls({
  isPlaying,
  currentTime,
  duration,
  playbackRate,
  analysisResults,
  onPlayPause,
  onSeek,
  onSpeedChange,
  onFrameStep,
  onFullscreen
}) {
  return (
    <div className="video-controls">
      <div className="controls-row">
        <div className="play-controls">
          <button 
            className={`control-btn play-pause ${isPlaying ? 'playing' : ''}`}
            onClick={onPlayPause}
          >
            <i className={`fas fa-${isPlaying ? 'pause' : 'play'}`}></i>
          </button>
          <button 
            className="control-btn"
            onClick={() => onFrameStep('prev')}
          >
            <i className="fas fa-step-backward"></i>
          </button>
          <button 
            className="control-btn"
            onClick={() => onFrameStep('next')}
          >
            <i className="fas fa-step-forward"></i>
          </button>
        </div>
        
        <Timeline
          currentTime={currentTime}
          duration={duration}
          analysisResults={analysisResults}
          onSeek={onSeek}
        />
        
        <div className="additional-controls">
          <div className="speed-control">
            <select 
              value={playbackRate}
              onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            >
              <option value="0.25">0.25x</option>
              <option value="0.5">0.5x</option>
              <option value="1">1x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
            </select>
          </div>
          <button 
            className="control-btn"
            onClick={onFullscreen}
          >
            <i className="fas fa-expand"></i>
          </button>
        </div>
      </div>
    </div>
  )
}

export default VideoControls