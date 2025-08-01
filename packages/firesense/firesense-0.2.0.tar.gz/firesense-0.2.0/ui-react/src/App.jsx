import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import VideoSection from './components/VideoSection'
import AnalysisSection from './components/AnalysisSection'
import LoadingOverlay from './components/LoadingOverlay'
import { useFireDetection } from './hooks/useFireDetection'
import { loadAnalysisConfig } from './utils/api'
import './styles/App.css'

function App() {
  const [videoFile, setVideoFile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState('')
  const [analysisConfig, setAnalysisConfig] = useState(null)
  const [autoStartAnalysis, setAutoStartAnalysis] = useState(false)

  const {
    analysisResults,
    isAnalyzing,
    alertStatus,
    alertType,
    currentFrameAnalysis,
    stats,
    fireTimeline,
    analyzeVideo,
    processVideoStream,
    reset
  } = useFireDetection()

  // Load analysis configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await loadAnalysisConfig()
        if (config) {
          setAnalysisConfig(config)
          if (config.video_path) {
            const videoFilename = config.video_path.split('/').pop()
            handleVideoLoad({
              url: videoFilename,
              filename: videoFilename
            })
            
            // Check if user wants to auto-start analysis
            const modeText = config.stream ? "Real-time streaming" : "Pre-analysis"
            const startAnalysis = window.confirm(
              `Video "${videoFilename}" loaded from CLI.\n\n` +
              `Configuration:\n` +
              `• Mode: ${modeText}\n` +
              `• Frame interval: ${config.interval}s\n` +
              `• Confidence threshold: ${config.confidence}\n` +
              `• Output format: ${config.format}\n\n` +
              `Start fire detection analysis now?`
            )
            
            if (startAnalysis) {
              setAutoStartAnalysis(true)
            }
          }
        }
      } catch (error) {
        console.log('No analysis configuration found - manual mode')
      }
    }
    
    loadConfig()
  }, [])

  // Auto-start analysis when video is loaded and config says so
  useEffect(() => {
    if (videoFile && autoStartAnalysis && !isAnalyzing) {
      setTimeout(() => {
        handleAnalyze()
        setAutoStartAnalysis(false)
      }, 1000)
    }
  }, [videoFile, autoStartAnalysis, isAnalyzing])

  const handleVideoUpload = (file) => {
    if (!file || !file.type.startsWith('video/')) {
      alert('Please select a valid video file.')
      return
    }

    const videoURL = URL.createObjectURL(file)
    handleVideoLoad({
      url: videoURL,
      filename: file.name,
      file: file
    })
  }

  const handleVideoLoad = (video) => {
    setVideoFile(video)
    reset()
  }

  const handleAnalyze = async () => {
    if (!videoFile || isAnalyzing) return

    setIsLoading(true)
    setLoadingMessage('Analyzing video for fire detection...')
    setLoadingProgress(0)

    try {
      const progressCallback = (progress) => {
        setLoadingProgress(progress)
      }

      if (analysisConfig?.stream) {
        await processVideoStream(videoFile, progressCallback)
      } else {
        await analyzeVideo(videoFile, progressCallback)
      }
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setIsLoading(false)
      setLoadingProgress(0)
      setLoadingMessage('')
    }
  }

  return (
    <div className="app-container">
      <Header 
        onUpload={handleVideoUpload}
        onAnalyze={handleAnalyze}
        canAnalyze={!!videoFile && !isAnalyzing}
        isAnalyzing={isAnalyzing}
      />
      
      <main className="main-content">
        <VideoSection 
          videoFile={videoFile}
          onUpload={handleVideoUpload}
          analysisResults={analysisResults}
          currentFrameAnalysis={currentFrameAnalysis}
          isAnalyzing={isAnalyzing}
        />
        
        <AnalysisSection
          alertStatus={alertStatus}
          alertType={alertType}
          currentFrameAnalysis={currentFrameAnalysis}
          stats={stats}
          fireTimeline={fireTimeline}
          isAnalyzing={isAnalyzing}
        />
      </main>
      
      <LoadingOverlay
        isVisible={isLoading}
        progress={loadingProgress}
        message={loadingMessage}
      />
    </div>
  )
}

export default App