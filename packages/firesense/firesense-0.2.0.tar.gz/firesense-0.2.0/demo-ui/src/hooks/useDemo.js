import { useState, useEffect, useCallback } from 'react'

export function useDemo(videoId) {
  const [demoData, setDemoData] = useState(null)
  const [currentStatus, setCurrentStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  
  // Fetch demo data when videoId changes
  useEffect(() => {
    if (!videoId) {
      setError('No video ID provided')
      return
    }
    
    const fetchDemo = async () => {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch(`http://localhost:8000/api/demo/${videoId}`)
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || `Failed to load demo: ${videoId}`)
        }
        
        const data = await response.json()
        
        // Transform data to ensure consistent structure
        const transformedData = {
          ...data,
          // Use 'url' field as video_url if video_url is not present
          video_url: data.video_url || data.url,
          // Ensure detections array exists
          detections: data.detections || [],
          // Add title from video_info if not present
          title: data.title || data.video_info?.title || data.id || videoId
        }
        
        setDemoData(transformedData)
        
        // Set initial status to first detection
        if (transformedData.detections && transformedData.detections.length > 0) {
          setCurrentStatus(transformedData.detections[0])
        }
      } catch (err) {
        console.error('Failed to fetch demo:', err)
        setError(err.message || 'Failed to load demo data')
        setDemoData(null)
      } finally {
        setLoading(false)
      }
    }
    
    fetchDemo()
  }, [videoId])
  
  // Update current status based on video timestamp
  const handleTimeUpdate = useCallback((currentTime) => {
    if (!demoData?.detections || demoData.detections.length === 0) {
      return
    }
    
    // Find the detection that matches the current timestamp
    // We look for the last detection that occurred before or at the current time
    let matchingDetection = demoData.detections[0]
    
    for (const detection of demoData.detections) {
      if (detection.timestamp <= currentTime) {
        matchingDetection = detection
      } else {
        // We've gone past the current time, so use the previous detection
        break
      }
    }
    
    // Only update if the status has changed
    if (!currentStatus || currentStatus.timestamp !== matchingDetection.timestamp) {
      setCurrentStatus(matchingDetection)
    }
  }, [demoData, currentStatus])
  
  return {
    demoData,
    currentStatus,
    error,
    loading,
    handleTimeUpdate
  }
}