export async function loadAnalysisConfig() {
  try {
    const response = await fetch('/analysis_config.json')
    if (response.ok) {
      const config = await response.json()
      console.log('Analysis configuration loaded:', config)
      return config
    }
  } catch (error) {
    console.log('No analysis configuration found')
  }
  return null
}

export async function callPythonBackend(config) {
  try {
    // First trigger Python analysis
    const analysisResponse = await fetch('/run-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config)
    })
    
    if (!analysisResponse.ok) {
      throw new Error('Backend analysis failed')
    }
    
    // Wait for results file
    let attempts = 0
    const maxAttempts = 30 // 30 seconds timeout
    
    while (attempts < maxAttempts) {
      try {
        const resultsResponse = await fetch('/detection_results.json')
        if (resultsResponse.ok) {
          const data = await resultsResponse.json()
          
          // Convert Python format to UI format
          return data.detections.map(detection => ({
            frame_number: detection.frame_number,
            timestamp: detection.timestamp,
            fire_detected: detection.fire_detected,
            confidence: detection.confidence,
            fire_characteristics: detection.fire_characteristics,
            processing_time: detection.processing_time || 0.1
          }))
        }
      } catch (e) {
        // File not ready yet, continue waiting
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000))
      attempts++
    }
    
    throw new Error('Backend analysis timeout')
  } catch (error) {
    console.error('Python backend call failed:', error)
    throw error
  }
}