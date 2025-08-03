import React, { useState, useRef } from 'react'
import VideoPlayer from './components/VideoPlayer'
import FireStatus from './components/FireStatus'
import DetectionSlider from './components/DetectionSlider'
import { useDemo } from './hooks/useDemo'
import './styles/App.css'

function App() {
  // Get video ID from URL parameters
  const urlParams = new URLSearchParams(window.location.search)
  const videoId = urlParams.get('id')
  
  // Use demo hook to fetch data and manage state
  const { demoData, currentStatus, error, handleTimeUpdate } = useDemo(videoId)
  
  // Track current time and duration
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [currentDetectionIndex, setCurrentDetectionIndex] = useState(0)
  const videoPlayerRef = useRef(null)
  
  // Show error if no video ID provided
  if (!videoId) {
    return (
      <div className="app-container error-state">
        <div className="error-message">
          <h1>No Video ID Provided</h1>
          <p>Please specify a video ID in the URL: <code>?id=VIDEO_ID</code></p>
          <p>Example: <code>http://localhost:5173?id=wildfire_example_01</code></p>
        </div>
      </div>
    )
  }
  
  // Show error if demo data failed to load
  if (error) {
    return (
      <div className="app-container error-state">
        <div className="error-message">
          <h1>Error Loading Demo</h1>
          <p>{error}</p>
        </div>
      </div>
    )
  }
  
  // Show loading state
  if (!demoData) {
    return (
      <div className="app-container loading-state">
        <div className="loading-message">
          <h1>Loading Demo...</h1>
          <p>Fetching data for video: {videoId}</p>
        </div>
      </div>
    )
  }
  
  // Handle time updates from video
  const handleVideoTimeUpdate = (time) => {
    setCurrentTime(time)
    handleTimeUpdate(time)
    
    // Update detection index based on current time
    if (demoData?.detections) {
      const index = findClosestDetectionIndex(time, demoData.detections)
      setCurrentDetectionIndex(index)
    }
  }
  
  // Handle duration update
  const handleDurationUpdate = (dur) => {
    setDuration(dur)
  }
  
  // Find closest detection index for a given time
  const findClosestDetectionIndex = (time, detections) => {
    let closestIndex = 0
    let minDiff = Math.abs(detections[0].timestamp - time)
    
    for (let i = 1; i < detections.length; i++) {
      const diff = Math.abs(detections[i].timestamp - time)
      if (diff < minDiff) {
        minDiff = diff
        closestIndex = i
      }
    }
    
    return closestIndex
  }
  
  // Handle detection index change from slider
  const handleDetectionIndexChange = (index) => {
    setCurrentDetectionIndex(index)
    
    if (demoData?.detections && demoData.detections[index]) {
      const detection = demoData.detections[index]
      const targetTime = detection.timestamp
      
      // Update video position
      if (videoPlayerRef.current) {
        videoPlayerRef.current.seekTo(targetTime)
      }
      
      // Update status immediately
      handleTimeUpdate(targetTime)
      setCurrentTime(targetTime)
    }
  }
  
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Gemma-3N Fire Detection System</h1>
        <p className="demo-title">{demoData.title || videoId}</p>
      </header>
      
      <main className="demo-content">
        <div className="video-section">
          <VideoPlayer 
            ref={videoPlayerRef}
            videoUrl={demoData.video_url}
            detections={demoData.detections}
            onTimeUpdate={handleVideoTimeUpdate}
            onDurationUpdate={handleDurationUpdate}
          />
          
          <DetectionSlider
            detections={demoData.detections}
            currentIndex={currentDetectionIndex}
            currentTime={currentTime}
            onIndexChange={handleDetectionIndexChange}
          />
        </div>
        
        <div className="status-section">
          <FireStatus 
            status={currentStatus}
            isDangerous={currentStatus?.is_dangerous}
            currentTime={currentTime}
            duration={duration}
          />
        </div>
      </main>
    </div>
  )
}

export default App