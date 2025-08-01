import React, { useState, useRef, useEffect } from 'react'
import VideoPlayer from './VideoPlayer'
import VideoControls from './VideoControls'
import './VideoSection.css'

function VideoSection({ 
  videoFile, 
  onUpload, 
  analysisResults, 
  currentFrameAnalysis,
  isAnalyzing 
}) {
  const videoRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime)
    }

    const handleLoadedMetadata = () => {
      setDuration(video.duration)
    }

    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('loadedmetadata', handleLoadedMetadata)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)
    video.addEventListener('ended', handleEnded)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
      video.removeEventListener('ended', handleEnded)
    }
  }, [videoFile])

  const handlePlayPause = () => {
    const video = videoRef.current
    if (!video) return

    if (video.paused) {
      video.play()
    } else {
      video.pause()
    }
  }

  const handleSeek = (percent) => {
    const video = videoRef.current
    if (!video) return

    video.currentTime = (percent / 100) * duration
  }

  const handleSpeedChange = (speed) => {
    const video = videoRef.current
    if (!video) return

    video.playbackRate = speed
    setPlaybackRate(speed)
  }

  const handleFrameStep = (direction) => {
    const video = videoRef.current
    if (!video) return

    const frameTime = 1 / 30 // Assume 30fps
    if (direction === 'prev') {
      video.currentTime = Math.max(0, video.currentTime - frameTime)
    } else {
      video.currentTime = Math.min(duration, video.currentTime + frameTime)
    }
  }

  const handleFullscreen = () => {
    const video = videoRef.current
    if (!video) return

    if (!document.fullscreenElement) {
      video.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }

  return (
    <section className="video-section">
      <div className="video-container">
        <VideoPlayer
          ref={videoRef}
          videoFile={videoFile}
          onUpload={onUpload}
        />
        
        {videoFile && (
          <VideoControls
            isPlaying={isPlaying}
            currentTime={currentTime}
            duration={duration}
            playbackRate={playbackRate}
            analysisResults={analysisResults}
            onPlayPause={handlePlayPause}
            onSeek={handleSeek}
            onSpeedChange={handleSpeedChange}
            onFrameStep={handleFrameStep}
            onFullscreen={handleFullscreen}
          />
        )}
      </div>
    </section>
  )
}

export default VideoSection