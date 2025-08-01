import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react'
import './VideoPlayer.css'

const VideoPlayer = forwardRef(({ videoUrl, detections, onTimeUpdate, onDurationUpdate }, ref) => {
  const videoRef = useRef(null)
  const youtubePlayerRef = useRef(null)
  const [isYouTube, setIsYouTube] = useState(false)
  const [youtubeId, setYoutubeId] = useState(null)
  
  // Expose seekTo method via ref
  useImperativeHandle(ref, () => ({
    seekTo: (time) => {
      if (isYouTube && youtubePlayerRef.current) {
        youtubePlayerRef.current.seekTo(time, true)
      } else if (videoRef.current) {
        videoRef.current.currentTime = time
      }
    }
  }))
  
  // Extract YouTube video ID from URL
  const extractYouTubeId = (url) => {
    if (!url) return null
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)
    return match ? match[1] : null
  }
  
  // Handle time update events for HTML5 video
  const handleTimeUpdate = () => {
    if (videoRef.current && onTimeUpdate) {
      onTimeUpdate(videoRef.current.currentTime)
    }
  }
  
  
  // Handle video ended event
  const handleVideoEnded = () => {
    if (videoRef.current) {
      // Pause the video to keep showing the last frame
      videoRef.current.pause()
      // Set current time to just before the end to show last frame
      const duration = videoRef.current.duration
      if (duration && !isNaN(duration)) {
        videoRef.current.currentTime = duration - 0.01
      }
    }
  }
  
  // Set up YouTube player
  useEffect(() => {
    const ytId = extractYouTubeId(videoUrl)
    if (ytId) {
      setIsYouTube(true)
      setYoutubeId(ytId)
      
      // Load YouTube IFrame API
      if (!window.YT) {
        const tag = document.createElement('script')
        tag.src = 'https://www.youtube.com/iframe_api'
        const firstScriptTag = document.getElementsByTagName('script')[0]
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag)
        
        window.onYouTubeIframeAPIReady = () => {
          createYouTubePlayer(ytId)
        }
      } else {
        createYouTubePlayer(ytId)
      }
    } else {
      setIsYouTube(false)
    }
  }, [videoUrl])
  
  // Create YouTube player
  const createYouTubePlayer = (videoId) => {
    if (youtubePlayerRef.current) {
      youtubePlayerRef.current.destroy()
    }
    
    youtubePlayerRef.current = new window.YT.Player('youtube-player', {
      height: '100%',
      width: '100%',
      videoId: videoId,
      playerVars: {
        autoplay: 0,
        controls: 1,
        modestbranding: 1,
        rel: 0
      },
      events: {
        onReady: (event) => {
          console.log('YouTube player ready')
          const duration = event.target.getDuration()
          if (onDurationUpdate && duration) {
            onDurationUpdate(duration)
          }
          // Start polling immediately to catch scrubbing even when paused
          startTimePolling()
        },
        onStateChange: (event) => {
          if (event.data === window.YT.PlayerState.PLAYING) {
            // Start polling for time updates
            startTimePolling()
          } else if (event.data === window.YT.PlayerState.ENDED) {
            // Video ended - pause and seek to just before end
            stopTimePolling()
            const duration = youtubePlayerRef.current.getDuration()
            if (duration) {
              youtubePlayerRef.current.seekTo(duration - 0.1, true)
              youtubePlayerRef.current.pauseVideo()
            }
          } else if (event.data === window.YT.PlayerState.PAUSED) {
            // Keep polling while paused to catch scrubbing
            startTimePolling()
          } else {
            stopTimePolling()
          }
        }
      }
    })
  }
  
  // Poll YouTube player for time updates
  let timeInterval = null
  const startTimePolling = () => {
    if (timeInterval) return
    timeInterval = setInterval(() => {
      if (youtubePlayerRef.current && youtubePlayerRef.current.getCurrentTime) {
        const currentTime = youtubePlayerRef.current.getCurrentTime()
        if (onTimeUpdate) {
          onTimeUpdate(currentTime)
        }
      }
    }, 50) // Poll every 50ms for more responsive updates
  }
  
  const stopTimePolling = () => {
    if (timeInterval) {
      clearInterval(timeInterval)
      timeInterval = null
    }
  }
  
  // Set up HTML5 video event listeners
  useEffect(() => {
    if (isYouTube) return
    
    const video = videoRef.current
    if (!video) return
    
    // Add event listeners
    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('seeking', handleTimeUpdate)
    video.addEventListener('seeked', handleTimeUpdate)
    video.addEventListener('loadedmetadata', () => {
      console.log('Video loaded:', video.duration, 'seconds')
      if (onDurationUpdate && video.duration) {
        onDurationUpdate(video.duration)
      }
    })
    video.addEventListener('ended', handleVideoEnded)
    
    // Cleanup
    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('seeking', handleTimeUpdate)
      video.removeEventListener('seeked', handleTimeUpdate)
      video.removeEventListener('ended', handleVideoEnded)
    }
  }, [onTimeUpdate, isYouTube])
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopTimePolling()
      if (youtubePlayerRef.current) {
        youtubePlayerRef.current.destroy()
      }
    }
  }, [])
  
  // Handle video source for local videos
  const fullVideoUrl = videoUrl?.startsWith('http') && !isYouTube
    ? videoUrl 
    : !isYouTube && videoUrl
    ? `http://localhost:8000${videoUrl}`
    : null
  
  return (
    <div className="video-player-container">
      <div className="video-wrapper">
        {isYouTube ? (
          <div id="youtube-player" className="youtube-player"></div>
        ) : (
          <video 
            ref={videoRef}
            className="video-element"
            controls
            preload="metadata"
            loop={false}
          >
            {fullVideoUrl && <source src={fullVideoUrl} type="video/mp4" />}
            Your browser does not support the video tag.
          </video>
        )}
      </div>
      
    </div>
  )
})

export default VideoPlayer