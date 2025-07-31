# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-31

### Added
- 🎯 **Initial release** of Speech Tension Detector Module
- 🚀 **High-accuracy tension detection** with 100% validation accuracy
- 🧠 **Pre-trained deep learning models** (Wav2Vec2 + Whisper)
- ⚡ **Speed optimization** with 2x performance improvement
- 🔄 **Parallel batch processing** with up to 23x speedup
- 📊 **Comprehensive feature extraction**:
  - Prosodic features (F0, intensity, HNR, jitter, shimmer)
  - Spectral analysis (spectral tilt, centroids, rolloff)
  - Advanced vocal effort detection
  - Quality separation engine
  - Glottal source analysis
  - Wavelet-fractal analysis
- 🎵 **Multi-format audio support** (WAV files, 22kHz+ recommended)
- 💻 **Command-line interface** (`speech-tension-detect`)
- 🐍 **Python API** with simple and detailed interfaces
- 📈 **Three-level tension classification**:
  - Low tension (0.0-0.333): Whisper, soft voice
  - Medium tension (0.333-0.666): Normal conversation
  - High tension (0.666-1.0): Shouting, excitement
- 🖥️ **GPU acceleration** with CUDA auto-detection
- 📦 **Modular architecture** with pluggable components
- 🔧 **Flexible installation options**:
  - Basic: Core functionality
  - Full: High-precision analysis
  - GPU: CUDA acceleration
  - Advanced: Extended features
  - All: Complete feature set

### Technical Features
- **Ensemble learning** with multiple classifiers
- **Volume-independent detection** through RMS normalization
- **Real-time processing** capabilities
- **Thread-safe parallel processing**
- **Comprehensive error handling**
- **Memory-efficient processing**
- **Cross-platform compatibility** (Windows, Linux, macOS)

### Documentation
- 📚 Complete API documentation
- 🚀 Quick start guide
- 💡 Practical usage examples
- 🔧 Configuration and customization guide
- 🚨 Error handling and troubleshooting
- 📊 Performance optimization tips

### Performance Benchmarks
- **Processing speed**: 18.66s → 0.81s (23x improvement with parallel processing)
- **Accuracy**: 100% on validation dataset (9/9 samples)
- **Model sizes**: 
  - Wav2Vec2: ~95MB
  - Whisper: ~139MB
  - Lightweight classifier: 17KB
- **Memory usage**: ~200MB with full features

### Supported Environments
- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Windows, Linux, macOS
- **Hardware**: CPU (basic), GPU with CUDA (recommended)
- **Audio formats**: WAV (primary), other formats via librosa

### Package Structure
```
speech_tension_detector/
├── core/           # Main detection engines
├── analyzers/      # Feature extraction modules
├── classifiers/    # ML/DL classification models
├── utils/          # Utility functions
└── cli.py          # Command-line interface
```

### Installation Options
```bash
# Basic installation
pip install speech-tension-detector

# Full features (recommended)
pip install speech-tension-detector[full]

# GPU acceleration
pip install speech-tension-detector[gpu]

# All features
pip install speech-tension-detector[all]
```

### Breaking Changes
- N/A (initial release)

### Known Issues
- Some TensorFlow warnings on first run (harmless)
- CUDA setup required for GPU acceleration
- Large model download on first use (~234MB total)

### Contributors
- hiroshi-tamura - Initial development and implementation

---

## Future Roadmap

### [1.1.0] - Planned Features
- Real-time audio stream processing
- Additional language support
- Web API interface
- Docker container support
- Enhanced visualization tools

### [1.2.0] - Advanced Features
- Custom model training interface
- Emotion classification integration
- Multi-speaker detection
- Audio quality assessment

---

For more information, see the [API Documentation](API_DOCUMENTATION.md) and [README](README.md).