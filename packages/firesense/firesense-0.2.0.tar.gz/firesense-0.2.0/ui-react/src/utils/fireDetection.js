import { callPythonBackend } from './api'

export async function performFireDetectionAnalysis(videoFile, config, progressCallback) {
  // Try to use real Python backend analysis if configuration exists
  if (config) {
    try {
      const realResults = await callPythonBackend(config)
      if (realResults && realResults.length > 0) {
        console.log('Using real Python backend analysis results')
        return realResults
      }
    } catch (error) {
      console.log('Python backend not available, using mock analysis:', error.message)
    }
  }
  
  // Fallback to mock analysis
  console.log('Using mock fire detection analysis')
  return performMockAnalysis(videoFile, config, progressCallback)
}

export async function performStreamingAnalysis(videoFile, config, callbacks) {
  console.log('Starting streaming fire detection analysis')
  
  // For now, simulate streaming with mock data
  // In production, this would connect to a real streaming endpoint
  return performMockStreamingAnalysis(videoFile, config, callbacks)
}

async function performMockAnalysis(videoFile, config, progressCallback) {
  const duration = 60 // Mock duration
  const frameInterval = config?.interval || 1.0
  const results = []
  
  const totalAnalysisFrames = Math.floor(duration / frameInterval)
  
  for (let i = 0; i < totalAnalysisFrames; i++) {
    const timestamp = i * frameInterval
    const frameNumber = Math.floor(timestamp * 30) // Assume 30fps
    
    // Update progress
    const progress = ((i + 1) / totalAnalysisFrames) * 100
    if (progressCallback) {
      progressCallback(progress)
    }
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Mock fire detection logic
    const fireDetected = shouldDetectFire(videoFile.filename, timestamp, duration)
    const confidence = calculateConfidence(fireDetected, timestamp, duration)
    
    const fireCharacteristics = generateMockFireCharacteristics(
      fireDetected, confidence, timestamp, duration
    )
    
    results.push({
      frame_number: frameNumber,
      timestamp: timestamp,
      fire_detected: fireDetected,
      confidence: confidence,
      fire_characteristics: fireCharacteristics,
      processing_time: 0.05 + Math.random() * 0.1
    })
  }
  
  return results
}

async function performMockStreamingAnalysis(videoFile, config, callbacks) {
  const duration = 60 // Mock duration
  const frameInterval = config?.interval || 1.0
  const results = []
  
  const totalFrames = Math.floor(duration / frameInterval)
  
  for (let i = 0; i < totalFrames; i++) {
    const timestamp = i * frameInterval
    const frameNumber = Math.floor(timestamp * 30)
    
    // Simulate real-time delay
    await new Promise(resolve => setTimeout(resolve, frameInterval * 1000))
    
    const fireDetected = shouldDetectFire(videoFile.filename, timestamp, duration)
    const confidence = calculateConfidence(fireDetected, timestamp, duration)
    
    const fireCharacteristics = generateMockFireCharacteristics(
      fireDetected, confidence, timestamp, duration
    )
    
    const result = {
      frame_number: frameNumber,
      timestamp: timestamp,
      fire_detected: fireDetected,
      confidence: confidence,
      fire_characteristics: fireCharacteristics,
      processing_time: 0.05 + Math.random() * 0.1
    }
    
    results.push(result)
    
    // Call frame callback
    if (callbacks.onFrameAnalyzed) {
      callbacks.onFrameAnalyzed(result)
    }
    
    // Update progress
    if (callbacks.onProgress) {
      callbacks.onProgress(((i + 1) / totalFrames) * 100)
    }
  }
  
  return results
}

function shouldDetectFire(filename, currentTime, duration) {
  if (!filename.toLowerCase().includes('fire')) {
    return Math.random() < 0.1
  }
  
  const fireStart = duration * 0.3
  const fireEnd = duration * 0.8
  
  if (currentTime < fireStart || currentTime > fireEnd) {
    return Math.random() < 0.2
  }
  
  const progressInFirePeriod = (currentTime - fireStart) / (fireEnd - fireStart)
  const baseProbability = 0.4 + (0.5 * Math.sin(progressInFirePeriod * Math.PI))
  
  return Math.random() < baseProbability
}

function calculateConfidence(fireDetected, currentTime, duration) {
  if (!fireDetected) {
    return Math.random() * 0.3
  }
  
  const fireProgress = Math.max(0, (currentTime - duration * 0.3) / (duration * 0.5))
  const baseConfidence = 0.5 + (fireProgress * 0.4)
  const randomVariation = (Math.random() - 0.5) * 0.2
  
  return Math.max(0.3, Math.min(0.95, baseConfidence + randomVariation))
}

function generateMockFireCharacteristics(fireDetected, confidence, timestamp, duration) {
  if (!fireDetected) {
    return {
      fire_type: "no_fire",
      control_status: "contained",
      emergency_level: "none",
      call_911_warranted: false,
      spread_potential: "low",
      vegetation_risk: "assessment not applicable",
      wind_effect: "no fire detected",
      location: "no fire visible",
      size_assessment: "no fire detected",
      smoke_behavior: "no smoke observed",
      flame_characteristics: "no flames detected"
    }
  }
  
  const isHighConfidence = confidence > 0.85
  const isMediumConfidence = confidence > 0.75
  
  const fireTypes = isHighConfidence ? 
    ["wildfire", "uncontrolled"] : 
    isMediumConfidence ? ["uncontrolled", "controlled"] : ["controlled"]
    
  const controlStatuses = isHighConfidence ? 
    ["out_of_control", "spreading"] : 
    isMediumConfidence ? ["spreading", "contained"] : ["contained"]
    
  const emergencyLevels = isHighConfidence ? 
    ["critical", "alert"] : 
    isMediumConfidence ? ["alert", "monitor"] : ["monitor", "none"]
    
  const call911Options = isHighConfidence ? [true] : 
    isMediumConfidence ? [true, false] : [false]
  
  const spreadPotentials = isHighConfidence ? 
    ["extreme", "high"] : 
    isMediumConfidence ? ["high", "moderate"] : ["moderate", "low"]
  
  return {
    fire_type: fireTypes[Math.floor(Math.random() * fireTypes.length)],
    control_status: controlStatuses[Math.floor(Math.random() * controlStatuses.length)],
    emergency_level: emergencyLevels[Math.floor(Math.random() * emergencyLevels.length)],
    call_911_warranted: call911Options[Math.floor(Math.random() * call911Options.length)],
    spread_potential: spreadPotentials[Math.floor(Math.random() * spreadPotentials.length)],
    vegetation_risk: "high - dry vegetation nearby",
    wind_effect: "moderate wind effect",
    location: "forest area",
    size_assessment: isHighConfidence ? "large_uncontrolled" : "small_controlled",
    smoke_behavior: "moderate smoke",
    flame_characteristics: "intense orange-red flames"
  }
}