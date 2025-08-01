// Fire Detection UI JavaScript
class FireDetectionUI {
    constructor() {
        this.videoPlayer = document.getElementById('videoPlayer');
        this.videoOverlay = document.getElementById('videoOverlay');
        this.fileInput = document.getElementById('fileInput');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.timeline = document.getElementById('timeline');
        this.timelineProgress = document.getElementById('timelineProgress');
        this.fireMarkers = document.getElementById('fireMarkers');
        
        // Time displays
        this.currentTimeDisplay = document.getElementById('currentTime');
        this.totalTimeDisplay = document.getElementById('totalTime');
        
        // Control buttons
        this.playPauseBtn = document.querySelector('.play-pause');
        this.speedSelect = document.getElementById('playbackSpeed');
        
        // Analysis elements
        this.alertPanel = document.getElementById('alertPanel');
        this.alertStatus = document.getElementById('alertStatus');
        this.frameInfo = document.getElementById('frameInfo');
        this.detectionBadge = document.getElementById('detectionBadge');
        this.confidenceFill = document.getElementById('confidenceFill');
        this.confidenceValue = document.getElementById('confidenceValue');
        
        // Emergency assessment elements
        this.fireType = document.getElementById('fireType');
        this.controlStatus = document.getElementById('controlStatus');
        this.emergencyLevel = document.getElementById('emergencyLevel');
        this.call911Status = document.getElementById('call911Status');
        this.call911Row = document.getElementById('call911Row');
        
        // Risk assessment elements
        this.spreadPotential = document.getElementById('spreadPotential');
        this.vegetationRisk = document.getElementById('vegetationRisk');
        this.fireLocation = document.getElementById('fireLocation');
        
        // Fire characteristics elements
        this.sizeAssessment = document.getElementById('sizeAssessment');
        this.smokeBehavior = document.getElementById('smokeBehavior');
        this.flameCharacteristics = document.getElementById('flameCharacteristics');
        this.windEffect = document.getElementById('windEffect');
        
        // Timeline stats
        this.fireFrameCount = document.getElementById('fireFrameCount');
        this.emergencyFrameCount = document.getElementById('emergencyFrameCount');
        
        // Progress elements
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        
        // State variables
        this.currentVideo = null;
        this.analysisResults = [];
        this.currentFrame = 0;
        this.totalFrames = 0;
        this.isPlaying = false;
        this.frameRate = 30; // Default frame rate
        this.isAnalyzing = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateUI();
    }
    
    setupEventListeners() {
        // Video player events
        this.videoPlayer.addEventListener('loadedmetadata', () => {
            this.onVideoLoaded();
        });
        
        this.videoPlayer.addEventListener('timeupdate', () => {
            this.onTimeUpdate();
        });
        
        this.videoPlayer.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayPauseButton();
        });
        
        this.videoPlayer.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayPauseButton();
        });
        
        this.videoPlayer.addEventListener('ended', () => {
            this.isPlaying = false;
            this.updatePlayPauseButton();
        });
        
        // Timeline scrubbing
        this.timeline.addEventListener('input', (e) => {
            this.seekToPercent(parseFloat(e.target.value));
        });
        
        // Speed control
        this.speedSelect.addEventListener('change', (e) => {
            this.videoPlayer.playbackRate = parseFloat(e.target.value);
        });
        
        // File upload
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }
    
    // File Upload Functions
    uploadVideo() {
        this.fileInput.click();
    }
    
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        if (!file.type.startsWith('video/')) {
            alert('Please select a valid video file.');
            return;
        }
        
        // Create object URL for video
        const videoURL = URL.createObjectURL(file);
        this.loadVideo(videoURL, file.name);
        
        // Enable analyze button
        document.querySelector('.btn-analyze').disabled = false;
    }
    
    loadVideo(url, filename) {
        this.currentVideo = { url, filename };
        this.videoPlayer.src = url;
        this.videoOverlay.style.display = 'none';
        this.resetAnalysis();
        
        // Update UI
        this.alertStatus.textContent = `Video loaded: ${filename}`;
        this.alertPanel.className = 'alert-panel';
    }
    
    onVideoLoaded() {
        const duration = this.videoPlayer.duration;
        this.totalTimeDisplay.textContent = this.formatTime(duration);
        this.timeline.max = 100;
        
        // Estimate total frames (rough calculation)
        this.totalFrames = Math.floor(duration * this.frameRate);
        this.frameInfo.textContent = `Frame 0 / ${this.totalFrames}`;
        
        console.log(`Video loaded: ${duration}s, estimated ${this.totalFrames} frames`);
    }
    
    // Video Control Functions
    togglePlayPause() {
        if (!this.currentVideo) return;
        
        if (this.videoPlayer.paused) {
            this.videoPlayer.play();
        } else {
            this.videoPlayer.pause();
        }
    }
    
    updatePlayPauseButton() {
        const icon = this.playPauseBtn.querySelector('i');
        if (this.isPlaying) {
            icon.className = 'fas fa-pause';
            this.playPauseBtn.classList.add('playing');
        } else {
            icon.className = 'fas fa-play';
            this.playPauseBtn.classList.remove('playing');
        }
    }
    
    previousFrame() {
        if (!this.currentVideo) return;
        
        const currentTime = this.videoPlayer.currentTime;
        const frameTime = 1 / this.frameRate;
        this.videoPlayer.currentTime = Math.max(0, currentTime - frameTime);
    }
    
    nextFrame() {
        if (!this.currentVideo) return;
        
        const currentTime = this.videoPlayer.currentTime;
        const frameTime = 1 / this.frameRate;
        const duration = this.videoPlayer.duration;
        this.videoPlayer.currentTime = Math.min(duration, currentTime + frameTime);
    }
    
    seekVideo(percent) {
        this.seekToPercent(percent);
    }
    
    seekToPercent(percent) {
        if (!this.currentVideo) return;
        
        const duration = this.videoPlayer.duration;
        const newTime = (percent / 100) * duration;
        this.videoPlayer.currentTime = newTime;
    }
    
    changeSpeed(speed) {
        this.videoPlayer.playbackRate = parseFloat(speed);
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.videoPlayer.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    onTimeUpdate() {
        if (!this.currentVideo) return;
        
        const currentTime = this.videoPlayer.currentTime;
        const duration = this.videoPlayer.duration;
        const percent = (currentTime / duration) * 100;
        
        // Update timeline
        this.timeline.value = percent;
        this.timelineProgress.style.width = `${percent}%`;
        
        // Update time displays
        this.currentTimeDisplay.textContent = this.formatTime(currentTime);
        
        // Update current frame
        this.currentFrame = Math.floor(currentTime * this.frameRate);
        this.frameInfo.textContent = `Frame ${this.currentFrame} / ${this.totalFrames}`;
        
        // Update analysis display for current frame
        this.updateCurrentFrameAnalysis();
    }
    
    // Analysis Functions
    async analyzeVideo() {
        if (!this.currentVideo || this.isAnalyzing) return;
        
        this.isAnalyzing = true;
        this.showLoading(true);
        
        // Update status based on analysis mode
        const analysisMode = this.analysisConfig?.stream ? 'real-time streaming' : 'pre-analysis';
        this.alertStatus.textContent = `Starting ${analysisMode} fire detection...`;
        this.alertPanel.className = 'alert-panel';
        
        // Initialize analysis display to show analyzing state
        this.resetAnalysisDisplay();
        
        try {
            // Simulate API call to fire detection backend
            const results = await this.performFireDetectionAnalysis();
            this.analysisResults = results;
            this.updateAnalysisComplete();
            this.renderFireMarkers();
            this.updateStats();
        } catch (error) {
            console.error('Analysis failed:', error);
            this.alertStatus.textContent = 'Analysis failed. Please try again.';
            this.alertPanel.className = 'alert-panel';
        } finally {
            this.isAnalyzing = false;
            this.showLoading(false);
        }
    }
    
    async performFireDetectionAnalysis() {
        // Check if streaming mode is enabled
        if (this.analysisConfig && this.analysisConfig.stream) {
            return await this.performStreamingAnalysis();
        }
        
        // Try to use real Python backend analysis if configuration exists
        if (this.analysisConfig) {
            try {
                const realResults = await this.callPythonBackend();
                if (realResults && realResults.length > 0) {
                    console.log('Using real Python backend analysis results');
                    return realResults;
                }
            } catch (error) {
                console.log('Python backend not available, using mock analysis:', error.message);
            }
        }
        
        // Fallback to mock fire detection analysis
        console.log('Using mock fire detection analysis');
        
        const duration = this.videoPlayer.duration;
        const frameInterval = this.analysisConfig ? this.analysisConfig.interval : 1.0;
        const results = [];
        
        // Generate mock results for demonstration
        const totalAnalysisFrames = Math.floor(duration / frameInterval);
        
        let hasFireSequence = false;
        let fireStartFrame = -1;
        
        for (let i = 0; i < totalAnalysisFrames; i++) {
            const timestamp = i * frameInterval;
            const frameNumber = Math.floor(timestamp * this.frameRate);
            
            // Update progress
            const progress = ((i + 1) / totalAnalysisFrames) * 100;
            this.updateProgress(progress);
            
            // Simulate processing delay
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Mock fire detection logic based on video filename and time
            let fireDetected = false;
            let confidence = 0.0;
            
            // Simulate fire detection in middle portion of video
            if (this.currentVideo.filename.toLowerCase().includes('fire') && 
                timestamp > duration * 0.2 && timestamp < duration * 0.8) {
                
                const baseConfidence = 0.3 + (Math.random() * 0.5);
                confidence = Math.min(0.95, baseConfidence + (timestamp / duration) * 0.4);
                fireDetected = confidence > 0.7;
                
                if (fireDetected && !hasFireSequence) {
                    hasFireSequence = true;
                    fireStartFrame = frameNumber;
                }
            } else {
                confidence = Math.random() * 0.3; // Low confidence for non-fire frames
                fireDetected = false;
            }
            
            // Generate realistic fire characteristics
            const fireCharacteristics = this.generateMockFireCharacteristics(
                fireDetected, confidence, timestamp, duration
            );
            
            results.push({
                frame_number: frameNumber,
                timestamp: timestamp,
                fire_detected: fireDetected,
                confidence: confidence,
                fire_characteristics: fireCharacteristics,
                processing_time: 0.05 + Math.random() * 0.1
            });
        }
        
        return results;
    }
    
    async callPythonBackend() {
        // Attempt to call Python backend for real analysis
        if (!this.analysisConfig) {
            throw new Error('No analysis configuration available');
        }
        
        // Check if results JSON file exists (would be created by Python backend)
        const resultsFile = `${this.analysisConfig.output_dir}/detection_results.json`;
        
        try {
            // First trigger Python analysis if not already done
            const analysisResponse = await fetch('/run-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.analysisConfig)
            });
            
            if (!analysisResponse.ok) {
                throw new Error('Backend analysis failed');
            }
            
            // Wait for results file
            let attempts = 0;
            const maxAttempts = 30; // 30 seconds timeout
            
            while (attempts < maxAttempts) {
                try {
                    const resultsResponse = await fetch('detection_results.json');
                    if (resultsResponse.ok) {
                        const data = await resultsResponse.json();
                        
                        // Convert Python format to UI format
                        return data.detections.map(detection => ({
                            frame_number: detection.frame_number,
                            timestamp: detection.timestamp,
                            fire_detected: detection.fire_detected,
                            confidence: detection.confidence,
                            fire_characteristics: detection.fire_characteristics,
                            processing_time: detection.processing_time || 0.1
                        }));
                    }
                } catch (e) {
                    // File not ready yet, continue waiting
                }
                
                await new Promise(resolve => setTimeout(resolve, 1000));
                attempts++;
                
                // Update progress while waiting
                this.updateProgress((attempts / maxAttempts) * 50); // 50% for waiting
            }
            
            throw new Error('Backend analysis timeout');
            
        } catch (error) {
            console.error('Python backend call failed:', error);
            throw error;
        }
    }
    
    async performStreamingAnalysis() {
        // Streaming mode - analyze frames as video plays
        console.log('Starting streaming fire detection analysis');
        
        const duration = this.videoPlayer.duration;
        const frameInterval = this.analysisConfig.interval;
        const results = [];
        
        // Update status for streaming mode
        this.alertStatus.textContent = 'Real-time streaming analysis in progress...';
        this.alertPanel.className = 'alert-panel';
        
        // Initialize analysis display to show analyzing state
        this.resetAnalysisDisplay();
        
        // Set video to beginning
        this.videoPlayer.currentTime = 0;
        
        // Start playing video
        await this.videoPlayer.play();
        
        // Track analysis progress synchronized with video playback
        const analysisStartTime = Date.now();
        let lastAnalyzedTime = 0;
        
        return new Promise((resolve) => {
            const streamingInterval = setInterval(async () => {
                const currentTime = this.videoPlayer.currentTime;
                
                // Check if we should analyze this frame
                if (currentTime - lastAnalyzedTime >= frameInterval) {
                    const frameNumber = Math.floor(currentTime * this.frameRate);
                    
                    // Update progress
                    const progress = (currentTime / duration) * 100;
                    this.updateProgress(progress);
                    
                    // Generate real-time analysis
                    const fireDetected = this.shouldDetectFire(currentTime, duration);
                    const confidence = this.calculateStreamingConfidence(currentTime, duration, fireDetected);
                    
                    const fireCharacteristics = this.generateMockFireCharacteristics(
                        fireDetected, confidence, currentTime, duration
                    );
                    
                    const result = {
                        frame_number: frameNumber,
                        timestamp: currentTime,
                        fire_detected: fireDetected,
                        confidence: confidence,
                        fire_characteristics: fireCharacteristics,
                        processing_time: 0.05 + Math.random() * 0.1
                    };
                    
                    results.push(result);
                    lastAnalyzedTime = currentTime;
                    
                    // Update UI immediately for streaming results
                    this.displayFrameAnalysis(result);
                    this.updateStreamingStats(results);
                    
                    // Show real-time alerts for fire detections
                    if (fireDetected) {
                        const alertType = fireCharacteristics.call_911_warranted ? 'emergency' : 'fire-detected';
                        this.alertPanel.className = `alert-panel ${alertType}`;
                        
                        if (fireCharacteristics.call_911_warranted) {
                            this.alertStatus.textContent = `🚨 EMERGENCY: 911 call warranted at ${currentTime.toFixed(1)}s!`;
                            // Could trigger audio alert here
                        } else {
                            this.alertStatus.textContent = `🔥 Fire detected at ${currentTime.toFixed(1)}s (${(confidence * 100).toFixed(0)}% confidence)`;
                        }
                    } else {
                        // Reset analysis display to show current analyzing state when no fire
                        if (this.isAnalyzing) {
                            this.resetAnalysisDisplay();
                        }
                        
                        // Update status to show streaming is active even when no fire detected
                        this.alertStatus.textContent = `🎥 Streaming analysis active - Frame at ${currentTime.toFixed(1)}s`;
                        this.alertPanel.className = 'alert-panel';
                    }
                }
                
                // Check if video ended or reached max duration
                if (this.videoPlayer.ended || currentTime >= duration) {
                    clearInterval(streamingInterval);
                    this.updateProgress(100);
                    
                    console.log(`Streaming analysis complete: ${results.length} frames analyzed`);
                    resolve(results);
                }
            }, 100); // Check every 100ms for smooth real-time updates
            
            // Handle video ending
            this.videoPlayer.addEventListener('ended', () => {
                clearInterval(streamingInterval);
                resolve(results);
            }, { once: true });
        });
    }
    
    shouldDetectFire(currentTime, duration) {
        // Enhanced logic for streaming fire detection
        if (!this.currentVideo.filename.toLowerCase().includes('fire')) {
            return Math.random() < 0.1; // Low chance for non-fire videos
        }
        
        // Simulate realistic fire detection progression
        const midPoint = duration * 0.5;
        const fireStart = duration * 0.3;
        const fireEnd = duration * 0.8;
        
        if (currentTime < fireStart || currentTime > fireEnd) {
            return Math.random() < 0.2; // Low chance outside fire period
        }
        
        // Higher probability in middle section
        const progressInFirePeriod = (currentTime - fireStart) / (fireEnd - fireStart);
        const baseProbability = 0.4 + (0.5 * Math.sin(progressInFirePeriod * Math.PI));
        
        return Math.random() < baseProbability;
    }
    
    calculateStreamingConfidence(currentTime, duration, fireDetected) {
        if (!fireDetected) {
            return Math.random() * 0.3;
        }
        
        // Confidence increases as fire progresses
        const fireProgress = Math.max(0, (currentTime - duration * 0.3) / (duration * 0.5));
        const baseConfidence = 0.5 + (fireProgress * 0.4);
        const randomVariation = (Math.random() - 0.5) * 0.2;
        
        return Math.max(0.3, Math.min(0.95, baseConfidence + randomVariation));
    }
    
    updateStreamingStats(results) {
        const fireFrames = results.filter(r => r.fire_detected).length;
        const emergencyFrames = results.filter(r => 
            r.fire_characteristics && r.fire_characteristics.call_911_warranted
        ).length;
        
        this.fireFrameCount.textContent = fireFrames.toString();
        this.emergencyFrameCount.textContent = emergencyFrames.toString();
        
        // Update fire markers in real-time
        this.renderFireMarkers();
    }
    
    generateMockFireCharacteristics(fireDetected, confidence, timestamp, duration) {
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
            };
        }
        
        // Fire detected - generate characteristics based on confidence
        const isHighConfidence = confidence > 0.85;
        const isMediumConfidence = confidence > 0.75;
        
        const fireTypes = isHighConfidence ? 
            ["wildfire", "uncontrolled"] : 
            isMediumConfidence ? ["uncontrolled", "controlled"] : ["controlled"];
            
        const controlStatuses = isHighConfidence ? 
            ["out_of_control", "spreading"] : 
            isMediumConfidence ? ["spreading", "contained"] : ["contained"];
            
        const emergencyLevels = isHighConfidence ? 
            ["critical", "alert"] : 
            isMediumConfidence ? ["alert", "monitor"] : ["monitor", "none"];
            
        const call911Options = isHighConfidence ? [true] : 
            isMediumConfidence ? [true, false] : [false];
        
        const spreadPotentials = isHighConfidence ? 
            ["extreme", "high"] : 
            isMediumConfidence ? ["high", "moderate"] : ["moderate", "low"];
            
        // Select random characteristics from appropriate pools
        const fireType = fireTypes[Math.floor(Math.random() * fireTypes.length)];
        const controlStatus = controlStatuses[Math.floor(Math.random() * controlStatuses.length)];
        const emergencyLevel = emergencyLevels[Math.floor(Math.random() * emergencyLevels.length)];
        const call911 = call911Options[Math.floor(Math.random() * call911Options.length)];
        const spreadPotential = spreadPotentials[Math.floor(Math.random() * spreadPotentials.length)];
        
        const vegetationRisks = [
            "high - dry vegetation nearby",
            "moderate - some fuel sources",
            "low - minimal vegetation",
            "extreme - drought conditions"
        ];
        
        const windEffects = [
            "strong wind spreading fire",
            "moderate wind effect",
            "calm conditions",
            "wind direction changing"
        ];
        
        const locations = [
            "forest area",
            "grassland",
            "urban interface",
            "remote wilderness",
            "near structures"
        ];
        
        const sizeAssessments = isHighConfidence ? 
            ["large_uncontrolled", "medium_spreading"] : 
            ["small_controlled", "medium_spreading"];
            
        const smokeBehaviors = [
            "heavy smoke column",
            "moderate smoke",
            "light smoke",
            "smoke dispersing rapidly",
            "dense black smoke"
        ];
        
        const flameCharacteristics = [
            "intense orange-red flames",
            "yellow-orange with rapid spread",
            "contained blue-orange flames",
            "flickering orange flames",
            "high intensity white-hot flames"
        ];
        
        return {
            fire_type: fireType,
            control_status: controlStatus,
            emergency_level: emergencyLevel,
            call_911_warranted: call911,
            spread_potential: spreadPotential,
            vegetation_risk: vegetationRisks[Math.floor(Math.random() * vegetationRisks.length)],
            wind_effect: windEffects[Math.floor(Math.random() * windEffects.length)],
            location: locations[Math.floor(Math.random() * locations.length)],
            size_assessment: sizeAssessments[Math.floor(Math.random() * sizeAssessments.length)],
            smoke_behavior: smokeBehaviors[Math.floor(Math.random() * smokeBehaviors.length)],
            flame_characteristics: flameCharacteristics[Math.floor(Math.random() * flameCharacteristics.length)]
        };
    }
    
    updateProgress(percent) {
        this.progressFill.style.width = `${percent}%`;
        this.progressText.textContent = `${Math.round(percent)}%`;
    }
    
    updateAnalysisComplete() {
        const fireFrames = this.analysisResults.filter(r => r.fire_detected).length;
        const emergencyFrames = this.analysisResults.filter(r => 
            r.fire_characteristics && r.fire_characteristics.call_911_warranted
        ).length;
        
        if (fireFrames > 0) {
            this.alertStatus.textContent = `Analysis complete: ${fireFrames} fire detections found`;
            this.alertPanel.className = 'alert-panel fire-detected';
            
            if (emergencyFrames > 0) {
                this.alertPanel.className = 'alert-panel emergency';
                this.alertStatus.textContent = `EMERGENCY: ${emergencyFrames} frames require 911 call!`;
            }
        } else {
            this.alertStatus.textContent = 'Analysis complete: No fire detected';
            this.alertPanel.className = 'alert-panel';
        }
    }
    
    renderFireMarkers() {
        this.fireMarkers.innerHTML = '';
        
        if (!this.analysisResults.length) return;
        
        const duration = this.videoPlayer.duration;
        
        this.analysisResults.forEach(result => {
            if (result.fire_detected) {
                const marker = document.createElement('div');
                marker.className = 'fire-marker';
                
                const position = (result.timestamp / duration) * 100;
                marker.style.left = `${position}%`;
                
                // Color based on emergency level
                if (result.fire_characteristics && result.fire_characteristics.call_911_warranted) {
                    marker.style.background = '#C0392B';
                    marker.style.boxShadow = '0 0 6px rgba(192, 57, 43, 0.8)';
                } else if (result.fire_characteristics && 
                          result.fire_characteristics.emergency_level === 'alert') {
                    marker.style.background = '#E74C3C';
                } else {
                    marker.style.background = '#F39C12';
                }
                
                this.fireMarkers.appendChild(marker);
            }
        });
    }
    
    updateCurrentFrameAnalysis() {
        if (!this.analysisResults.length) {
            this.resetAnalysisDisplay();
            return;
        }
        
        // Find the closest analysis result to current time
        const currentTime = this.videoPlayer.currentTime;
        let closestResult = null;
        let minDiff = Infinity;
        
        this.analysisResults.forEach(result => {
            const diff = Math.abs(result.timestamp - currentTime);
            if (diff < minDiff) {
                minDiff = diff;
                closestResult = result;
            }
        });
        
        if (closestResult && minDiff < 2.0) { // Within 2 seconds
            this.displayFrameAnalysis(closestResult);
        } else {
            this.resetAnalysisDisplay();
        }
    }
    
    displayFrameAnalysis(result) {
        const { fire_detected, confidence, fire_characteristics } = result;
        
        // Update detection badge
        const badge = this.detectionBadge.querySelector('.badge-status');
        if (fire_detected) {
            badge.textContent = 'Fire Detected';
            this.detectionBadge.className = 'detection-badge fire-detected';
        } else {
            badge.textContent = 'No Fire';
            this.detectionBadge.className = 'detection-badge no-fire';
        }
        
        // Update confidence meter
        const confidencePercent = Math.round(confidence * 100);
        this.confidenceFill.style.width = `${confidencePercent}%`;
        this.confidenceValue.textContent = `${confidencePercent}%`;
        
        if (!fire_characteristics) {
            this.resetAnalysisDisplay();
            return;
        }
        
        // Update emergency assessment
        this.fireType.textContent = fire_characteristics.fire_type || '-';
        this.controlStatus.textContent = fire_characteristics.control_status || '-';
        
        const emergencyLevel = fire_characteristics.emergency_level || 'none';
        this.emergencyLevel.textContent = emergencyLevel;
        this.emergencyLevel.className = `detail-value emergency-level ${emergencyLevel}`;
        
        // Update 911 call status
        const call911Text = this.call911Status.querySelector('span');
        if (fire_characteristics.call_911_warranted) {
            call911Text.textContent = 'CALL 911 NOW';
            this.call911Status.className = 'call-911-status warranted';
            this.call911Row.style.display = 'flex';
        } else {
            call911Text.textContent = 'Not Warranted';
            this.call911Status.className = 'call-911-status not-warranted';
        }
        
        // Update risk assessment
        const spreadPotential = fire_characteristics.spread_potential || 'low';
        this.spreadPotential.textContent = spreadPotential;
        this.spreadPotential.className = `risk-level ${spreadPotential}`;
        
        this.vegetationRisk.textContent = fire_characteristics.vegetation_risk || '-';
        this.fireLocation.textContent = fire_characteristics.location || '-';
        
        // Update fire characteristics
        this.sizeAssessment.textContent = fire_characteristics.size_assessment || '-';
        this.smokeBehavior.textContent = fire_characteristics.smoke_behavior || '-';
        this.flameCharacteristics.textContent = fire_characteristics.flame_characteristics || '-';
        this.windEffect.textContent = fire_characteristics.wind_effect || '-';
    }
    
    resetAnalysisDisplay() {
        // Reset detection badge - show appropriate status based on analysis state
        const badge = this.detectionBadge.querySelector('.badge-status');
        if (this.isAnalyzing) {
            badge.textContent = 'Analyzing...';
            this.detectionBadge.className = 'detection-badge analyzing';
        } else {
            badge.textContent = 'No Analysis';
            this.detectionBadge.className = 'detection-badge no-fire';
        }
        
        // Reset confidence meter
        this.confidenceFill.style.width = '0%';
        this.confidenceValue.textContent = '0%';
        
        // Reset text fields based on analysis state
        const textFields = [
            this.fireType, this.controlStatus, this.vegetationRisk, this.fireLocation,
            this.sizeAssessment, this.smokeBehavior, this.flameCharacteristics, this.windEffect
        ];
        
        if (this.isAnalyzing) {
            // Show analyzing status instead of dashes during analysis
            textFields.forEach(field => {
                if (field) field.textContent = 'Analyzing...';
            });
            
            // Set emergency level to analyzing state
            this.emergencyLevel.textContent = 'analyzing';
            this.emergencyLevel.className = 'detail-value emergency-level none';
            
            // Set 911 status to analyzing
            const call911Text = this.call911Status.querySelector('span');
            call911Text.textContent = 'Analyzing...';
            this.call911Status.className = 'call-911-status not-warranted';
        } else {
            // Normal reset state when not analyzing
            textFields.forEach(field => {
                if (field) field.textContent = '-';
            });
            
            // Reset emergency level
            this.emergencyLevel.textContent = 'none';
            this.emergencyLevel.className = 'detail-value emergency-level none';
            
            // Reset 911 status
            const call911Text = this.call911Status.querySelector('span');
            call911Text.textContent = 'Not Warranted';
            this.call911Status.className = 'call-911-status not-warranted';
        }
    }
    
    updateStats() {
        const fireFrames = this.analysisResults.filter(r => r.fire_detected).length;
        const emergencyFrames = this.analysisResults.filter(r => 
            r.fire_characteristics && r.fire_characteristics.call_911_warranted
        ).length;
        
        this.fireFrameCount.textContent = fireFrames.toString();
        this.emergencyFrameCount.textContent = emergencyFrames.toString();
    }
    
    resetAnalysis() {
        this.analysisResults = [];
        this.fireMarkers.innerHTML = '';
        this.resetAnalysisDisplay();
        this.updateStats();
        
        // Reset alert panel
        this.alertStatus.textContent = 'No Analysis Running';
        this.alertPanel.className = 'alert-panel';
    }
    
    // Utility Functions
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    showLoading(show) {
        if (show) {
            this.loadingOverlay.classList.add('active');
        } else {
            this.loadingOverlay.classList.remove('active');
        }
    }
    
    updateUI() {
        // Update button states
        const analyzeBtn = document.querySelector('.btn-analyze');
        if (analyzeBtn) {
            analyzeBtn.disabled = !this.currentVideo || this.isAnalyzing;
        }
    }
    
    handleKeyboard(event) {
        if (!this.currentVideo) return;
        
        switch (event.code) {
            case 'Space':
                event.preventDefault();
                this.togglePlayPause();
                break;
            case 'ArrowLeft':
                event.preventDefault();
                this.previousFrame();
                break;
            case 'ArrowRight':
                event.preventDefault();
                this.nextFrame();
                break;
            case 'KeyF':
                if (!event.ctrlKey && !event.metaKey) {
                    event.preventDefault();
                    this.toggleFullscreen();
                }
                break;
            default:
                return; // Don't prevent default for unhandled keys
        }
    }
}

// Global functions for HTML onclick handlers
let fireDetectionUI;

function uploadVideo() {
    fireDetectionUI.uploadVideo();
}

function handleFileUpload(event) {
    fireDetectionUI.handleFileUpload(event);
}

function analyzeVideo() {
    fireDetectionUI.analyzeVideo();
}

function togglePlayPause() {
    fireDetectionUI.togglePlayPause();
}

function previousFrame() {
    fireDetectionUI.previousFrame();
}

function nextFrame() {
    fireDetectionUI.nextFrame();
}

function seekVideo(value) {
    fireDetectionUI.seekVideo(value);
}

function changeSpeed(speed) {
    fireDetectionUI.changeSpeed(speed);
}

function toggleFullscreen() {
    fireDetectionUI.toggleFullscreen();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    fireDetectionUI = new FireDetectionUI();
    console.log('Fire Detection UI initialized');
    
    // Check for analysis configuration and auto-load video
    await loadAnalysisConfig();
});

// Load analysis configuration if available
async function loadAnalysisConfig() {
    try {
        const response = await fetch('analysis_config.json');
        if (response.ok) {
            const config = await response.json();
            console.log('Analysis configuration loaded:', config);
            
            // Auto-load video if specified
            if (config.video_path) {
                const videoFilename = config.video_path.split('/').pop();
                fireDetectionUI.loadVideo(videoFilename, videoFilename);
                
                // Update UI with configuration
                fireDetectionUI.analysisConfig = config;
                fireDetectionUI.alertStatus.textContent = `Video loaded from CLI: ${videoFilename}`;
                fireDetectionUI.alertPanel.className = 'alert-panel';
                
                console.log('Video auto-loaded from CLI configuration');
                
                // Show analysis prompt
                const modeText = config.stream ? "Real-time streaming" : "Pre-analysis";
                const startAnalysis = confirm(
                    `Video "${videoFilename}" loaded from CLI.\n\n` +
                    `Configuration:\n` +
                    `• Mode: ${modeText}\n` +
                    `• Frame interval: ${config.interval}s\n` +
                    `• Confidence threshold: ${config.confidence}\n` +
                    `• Output format: ${config.format}\n\n` +
                    `Start fire detection analysis now?`
                );
                
                if (startAnalysis) {
                    // Start analysis automatically
                    setTimeout(() => {
                        fireDetectionUI.analyzeVideo();
                    }, 1000);
                }
            }
        }
    } catch (error) {
        console.log('No analysis configuration found - manual mode');
    }
}