 🎵 Gesture Volume Control

A real-time hand gesture recognition system that allows you to control your computer's volume using simple hand movements. Point your index finger up to increase volume, down to decrease volume - no touching required!

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.0+-green.svg)
![MediaPipe](https://img.shields.io/badge/mediapipe-latest-orange.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)
![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

 ✨ Features

- 🖐️ Real-time hand tracking- using MediaPipe
- 🎚️ Intuitive volume control - point your index finger up/down
- 🌐 Web-based interface - with live video feed
- 🖥️ Cross-platform support - (Windows, macOS, Linux)
- 📱 Responsive design - works on desktop and mobile browsers
- 🎯 Smart gesture detection - with noise filtering
- 📊 Visual feedback - with volume bar and status indicators
- 🔄 Automatic fallback - to simulation mode if no camera detected

🎥 Demo

The system provides both real camera mode and simulation mode:
- Real Mode: Uses your webcam to track hand gestures
- Simulation Mode: Shows how the system works with animated demonstrations

🚀 Quick Start

Prerequisites

- Python 3.7 or higher
- Webcam (optional - simulation mode available)
- Internet connection for initial setup

Installation

Windows
bash
 Clone the repository
git clone https://github.com/yourusername/gesture-volume-control.git
cd gesture-volume-control

 Run setup
setup.bat

 Start the application
run.bat


macOS/Linux
bash
 Clone the repository
git clone https://github.com/yourusername/gesture-volume-control.git
cd gesture-volume-control

 Make scripts executable
chmod +x setup.sh run.sh

 Run setup
./setup.sh

 Start the application
./run.sh
```

#### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

 Usage

1. Start the application using one of the methods above
2. Open your browser and navigate to `http://localhost:5000`
3. Allow camera access when prompted (or use simulation mode)
4. Show your hand to the camera
5. Point your index finger:
   - Up = Increase volume
   - Down = Decrease volume

 🎯 How It Works

 Hand Tracking Pipeline

1. **Video Capture**: Captures frames from your webcam using OpenCV
2. **Hand Detection**: Uses MediaPipe to detect and track hand landmarks
3. **Gesture Recognition**: Analyzes index finger position relative to wrist
4. **Volume Mapping**: Maps finger height to volume level (0-100%)
5. **System Integration**: Updates system volume using platform-specific APIs

 Gesture Recognition

```
Index Finger Position → Volume Level
        ↑ Higher      → Higher Volume (100%)
        ↓ Lower       → Lower Volume (0%)
```

The system tracks 21 hand landmarks and specifically uses:
- Landmark 8: Index finger tip
- Landmark 0: Wrist position
- Relative positioning for accurate volume control

 📁 Project Structure

```
gesture-volume-control/
├── app.py                 # Main Flask application
├── hand_tracker.py        # MediaPipe hand tracking logic
├── volume_controller.py   # Cross-platform volume control
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── setup.bat             # Windows setup script
├── setup.sh              # Unix setup script
├── run.bat               # Windows run script
├── run.sh                # Unix run script
└── README.md             # This file
```

 🛠️ Technical Details

 Dependencies

- Flask: Web framework for the interface
- OpenCV: Computer vision and video processing
- MediaPipe: Google's hand tracking solution
- NumPy: Numerical computations
- Platform-specific:
  - Windows: PowerShell integration
  - macOS: osascript for volume control
  - Linux: PulseAudio/ALSA support

 Volume Control Methods

| Platform | Primary Method | Fallback |
|----------|---------------|----------|
| Windows | PowerShell + Windows API | Keyboard simulation |
| macOS | osascript | AppleScript |
| Linux | PulseAudio (pactl) | ALSA (amixer) |

 Performance Features

- Volume smoothing prevents jittery movements
- Rate limiting avoids system overload
- Gesture filtering reduces false positives
- Automatic calibration adapts to different users

 🎨 Web Interface Features

- Live video feed with hand tracking overlay
- Real-time volume bar showing current level
- Status indicators (Active/Inactive)
- Responsive design for different screen sizes
- Cross-browser compatibility

 🔧 Configuration

 Camera Settings
```python
# In app.py - adjust camera resolution and FPS
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)
```

 Gesture Sensitivity
```python
# In hand_tracker.py - adjust detection confidence
detection_confidence = 0.7  # Lower = more sensitive
tracking_confidence = 0.7   # Higher = more stable
```

 Volume Smoothing
```python
# In app.py - adjust smoothing window
SMOOTHING_WINDOW = 5  # Number of frames to average
```

 🚨 Troubleshooting

 Camera Issues
- **No camera detected**: System automatically switches to simulation mode
- **Poor tracking**: Ensure good lighting and clear hand visibility
- **Permission denied**: Allow camera access in browser settings

 Volume Control Issues
- **Windows**: Ensure PowerShell execution policy allows scripts
- **macOS**: Grant terminal/app accessibility permissions
- **Linux**: Install PulseAudio (`sudo apt install pulseaudio-utils`)

 Performance Issues
- **High CPU usage**: Reduce camera resolution or FPS
- **Laggy response**: Check system resources and close other applications

 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

 Areas for Contribution
- Additional gesture recognition patterns
- Mobile app development
- UI/UX improvements
- Performance optimizations
- Multi-hand support
- Voice command integration

 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

 🙏 Acknowledgments

- **Google MediaPipe** for excellent hand tracking
- **OpenCV** for computer vision capabilities
- **Flask** for the web framework
- The open-source community for inspiration and tools

 📊 System Requirements

 Minimum Requirements
- Python 3.7+
- 2GB RAM
- Webcam (optional)
- Modern web browser

 Recommended Requirements
- Python 3.9+
- 4GB RAM
- HD webcam with good lighting
- Chrome/Firefox/Safari latest version

 🔮 Future Enhancements

- [ ] **Multi-gesture support** (volume, brightness, media controls)
- [ ] **Voice commands** integration
- [ ] **Mobile app** for remote control
- [ ] **AI gesture learning** for custom gestures
- [ ] **Multi-user support** with gesture profiles
- [ ] **Gesture macros** for complex actions
- [ ] **Integration with smart home** systems

 📞 Support

- Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the Wiki for detailed guides



⭐ **Star this repository** if you found it helpful!

🔗 **Share** with others who might find it useful!

📧 **Contact**: [your-email@example.com](mailto:your-email@example.com)
