import React, { forwardRef } from 'react'
import './VideoPlayer.css'

const VideoPlayer = forwardRef(({ videoFile, onUpload }, ref) => {
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUpload(file)
    }
  }

  return (
    <div className="video-wrapper">
      {videoFile ? (
        <video
          ref={ref}
          id="videoPlayer"
          src={videoFile.url}
          controls={false}
        />
      ) : (
        <div className="video-overlay">
          <div className="upload-prompt">
            <i className="fas fa-video"></i>
            <p>No video loaded</p>
            <input
              type="file"
              id="videoFileInput"
              accept="video/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            <button
              className="btn btn-primary"
              onClick={() => document.getElementById('videoFileInput').click()}
            >
              <i className="fas fa-upload"></i>
              Select Video File
            </button>
          </div>
        </div>
      )}
    </div>
  )
})

VideoPlayer.displayName = 'VideoPlayer'

export default VideoPlayer