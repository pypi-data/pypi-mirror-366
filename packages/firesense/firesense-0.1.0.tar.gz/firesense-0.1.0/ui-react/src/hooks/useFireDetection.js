import { useState, useCallback, useRef } from 'react'
import { performFireDetectionAnalysis, performStreamingAnalysis } from '../utils/fireDetection'

export function useFireDetection() {
  const [analysisResults, setAnalysisResults] = useState([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [alertStatus, setAlertStatus] = useState('No Analysis Running')
  const [alertType, setAlertType] = useState('')
  const [currentFrameAnalysis, setCurrentFrameAnalysis] = useState(null)
  const [stats, setStats] = useState({ fireFrames: 0, emergencyFrames: 0 })
  const [fireTimeline, setFireTimeline] = useState([])
  
  const analysisConfigRef = useRef(null)

  const updateStats = useCallback((results) => {
    const fireFrames = results.filter(r => r.fire_detected).length
    const emergencyFrames = results.filter(r => 
      r.fire_characteristics && r.fire_characteristics.call_911_warranted
    ).length
    
    setStats({ fireFrames, emergencyFrames })
    
    // Calculate fire timeline
    const timeline = []
    let currentPeriod = null
    
    results.forEach((result) => {
      if (result.fire_detected) {
        if (!currentPeriod) {
          currentPeriod = { start: result.timestamp, end: result.timestamp }
        } else {
          currentPeriod.end = result.timestamp
        }
      } else if (currentPeriod) {
        timeline.push(currentPeriod)
        currentPeriod = null
      }
    })
    
    if (currentPeriod) {
      timeline.push(currentPeriod)
    }
    
    setFireTimeline(timeline)
  }, [])

  const updateAlertStatus = useCallback((results) => {
    const fireFrames = results.filter(r => r.fire_detected).length
    const emergencyFrames = results.filter(r => 
      r.fire_characteristics && r.fire_characteristics.call_911_warranted
    ).length
    
    if (fireFrames > 0) {
      setAlertStatus(`Analysis complete: ${fireFrames} fire detections found`)
      
      if (emergencyFrames > 0) {
        setAlertType('emergency')
        setAlertStatus(`EMERGENCY: ${emergencyFrames} frames require 911 call!`)
      } else {
        setAlertType('fire-detected')
      }
    } else {
      setAlertStatus('Analysis complete: No fire detected')
      setAlertType('')
    }
  }, [])

  const analyzeVideo = useCallback(async (videoFile, progressCallback) => {
    setIsAnalyzing(true)
    setAlertStatus('Starting pre-analysis fire detection...')
    setAlertType('')
    
    try {
      const results = await performFireDetectionAnalysis(
        videoFile,
        analysisConfigRef.current,
        progressCallback
      )
      
      setAnalysisResults(results)
      updateStats(results)
      updateAlertStatus(results)
      
      return results
    } finally {
      setIsAnalyzing(false)
    }
  }, [updateStats, updateAlertStatus])

  const processVideoStream = useCallback(async (videoFile, progressCallback) => {
    setIsAnalyzing(true)
    setAlertStatus('Real-time streaming analysis in progress...')
    setAlertType('')
    
    try {
      const results = await performStreamingAnalysis(
        videoFile,
        analysisConfigRef.current,
        {
          onFrameAnalyzed: (result) => {
            setCurrentFrameAnalysis(result)
            
            if (result.fire_detected) {
              const alertType = result.fire_characteristics?.call_911_warranted ? 
                'emergency' : 'fire-detected'
              setAlertType(alertType)
              
              if (result.fire_characteristics?.call_911_warranted) {
                setAlertStatus(`🚨 EMERGENCY: 911 call warranted at ${result.timestamp.toFixed(1)}s!`)
              } else {
                setAlertStatus(`🔥 Fire detected at ${result.timestamp.toFixed(1)}s (${(result.confidence * 100).toFixed(0)}% confidence)`)
              }
            } else {
              setAlertStatus(`🎥 Streaming analysis active - Frame at ${result.timestamp.toFixed(1)}s`)
              setAlertType('')
            }
          },
          onProgress: progressCallback
        }
      )
      
      setAnalysisResults(results)
      updateStats(results)
      updateAlertStatus(results)
      
      return results
    } finally {
      setIsAnalyzing(false)
    }
  }, [updateStats, updateAlertStatus])

  const setAnalysisConfig = useCallback((config) => {
    analysisConfigRef.current = config
  }, [])

  const reset = useCallback(() => {
    setAnalysisResults([])
    setIsAnalyzing(false)
    setAlertStatus('No Analysis Running')
    setAlertType('')
    setCurrentFrameAnalysis(null)
    setStats({ fireFrames: 0, emergencyFrames: 0 })
    setFireTimeline([])
  }, [])

  return {
    analysisResults,
    isAnalyzing,
    alertStatus,
    alertType,
    currentFrameAnalysis,
    stats,
    fireTimeline,
    analyzeVideo,
    processVideoStream,
    setAnalysisConfig,
    reset
  }
}