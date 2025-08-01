# Fire Detection React UI

A modern React application for fire detection video analysis using the Gemma 3N E4B model.

## Features

- **Modern React Architecture**: Built with React 18, functional components, and hooks
- **Real-time Analysis**: Support for both pre-analysis and streaming modes
- **Interactive Video Player**: Custom video player with frame-by-frame controls
- **Fire Detection Visualization**: Timeline markers showing fire detections
- **Emergency Assessment**: Real-time emergency level and 911 call recommendations
- **Risk Analysis**: Vegetation risk, spread potential, and location assessment
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Development

### Prerequisites

- Node.js 18+ and npm
- Python fire detection backend running

### Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:9090

### Build for Production

```bash
npm run build
```

This creates a `dist/` folder with the production build.

## Integration with Python Backend

The React app integrates with the Python fire detection backend through:

1. **Configuration Loading**: Automatically loads `analysis_config.json` from CLI
2. **API Endpoints**: Calls `/run-analysis` for backend processing
3. **Results Fetching**: Polls `/detection_results.json` for analysis results
4. **Proxy Setup**: Vite development server proxies API calls to Python backend

## Architecture

### Components

- **App**: Main application component with state management
- **Header**: Navigation bar with upload and analyze buttons
- **VideoSection**: Video player and controls container
- **VideoPlayer**: Custom video player component
- **VideoControls**: Play/pause, timeline, and speed controls
- **Timeline**: Video timeline with fire detection markers
- **AnalysisSection**: Container for all analysis panels
- **AlertPanel**: Main fire detection status display
- **FireDetectionPanel**: Detection confidence and status
- **EmergencyAssessment**: Emergency level and 911 recommendations
- **RiskAssessment**: Fire spread and vegetation risk analysis
- **FireCharacteristics**: Detailed fire properties
- **TimelineStats**: Fire detection timeline statistics
- **LoadingOverlay**: Analysis progress indicator

### Hooks

- **useFireDetection**: Main hook for fire detection logic and state management

### Utils

- **api.js**: Backend API integration functions
- **fireDetection.js**: Fire detection analysis logic with mock fallback
- **time.js**: Time formatting utilities

## Styling

The app uses CSS custom properties (CSS variables) for consistent theming:

- **Color Scheme**: Dark theme with fire-themed accent colors
- **Responsive**: Mobile-first responsive design
- **Animations**: Smooth transitions and pulsing effects for alerts
- **Accessibility**: Focus indicators and high contrast support

## Mock Analysis

When the Python backend is unavailable, the app falls back to mock analysis that simulates:

- Fire detection based on video filename
- Realistic confidence scoring
- Emergency characteristics generation  
- Timeline-based fire progression
- Real-time streaming simulation