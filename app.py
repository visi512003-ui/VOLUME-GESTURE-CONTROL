import cv2
import os
import threading
import time
from flask import Flask, render_template, Response, jsonify
from hand_tracker import HandTracker
from volume_controller import VolumeController

app = Flask(__name__)

# Global variables
hand_tracker = HandTracker()
volume_controller = VolumeController()
camera = None
current_volume = 50
gesture_active = False
last_finger_y = None
volume_smoothing_buffer = []
SMOOTHING_WINDOW = 5

def initialize_camera():
    """Initialize camera with error handling - fallback to simulation if no camera"""
    global camera
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            # Try different camera indices
            for i in range(1, 4):
                camera = cv2.VideoCapture(i)
                if camera.isOpened():
                    break
        
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            camera.set(cv2.CAP_PROP_FPS, 30)
            print("Real camera initialized successfully!")
            return True
        else:
            # Fallback to simulation for demo purposes
            camera = "simulation"
            print("No camera found - using simulation for demonstration")
            return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        camera = "simulation"
        return True

def smooth_volume(new_volume):
    """Smooth volume changes to avoid jitter"""
    global volume_smoothing_buffer
    
    volume_smoothing_buffer.append(new_volume)
    if len(volume_smoothing_buffer) > SMOOTHING_WINDOW:
        volume_smoothing_buffer.pop(0)
    
    return sum(volume_smoothing_buffer) / len(volume_smoothing_buffer)

def generate_frames():
    """Generate video frames with hand tracking overlay"""
    global current_volume, gesture_active, last_finger_y
    import time
    import numpy as np
    
    # Initialize simulation variables if needed
    simulated_finger_y = 240
    finger_direction = 1
    
    while True:
        if camera == "simulation":
            # Simulation mode - create synthetic frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame_height, frame_width = frame.shape[:2]
            
            # Simulate finger movement
            simulated_finger_y += finger_direction * 2
            if simulated_finger_y <= 100:
                finger_direction = 1
            elif simulated_finger_y >= 380:
                finger_direction = -1
            
            # Calculate volume based on finger height
            relative_height = max(0, min(100, 100 - ((simulated_finger_y - 240) / 140 * 50)))
            
            # Apply smoothing
            smooth_height = smooth_volume(relative_height)
            
            # Update volume
            if abs(smooth_height - current_volume) > 1:
                current_volume = int(smooth_height)
                volume_controller.set_volume(current_volume)
                gesture_active = True
            
            # Draw simulated finger
            finger_x = 320
            cv2.circle(frame, (finger_x, int(simulated_finger_y)), 15, (0, 255, 255), -1)
            cv2.line(frame, (0, 240), (640, 240), (100, 100, 100), 1)
            
            # Add simulation labels
            cv2.putText(frame, "SIMULATION MODE - Will use real camera on your PC", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, "Finger UP = Volume UP | Finger DOWN = Volume DOWN", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            movement_text = "Moving UP" if finger_direction == -1 else "Moving DOWN"
            cv2.putText(frame, movement_text, (10, frame_height - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            time.sleep(0.05)
            
        else:
            # Real camera mode
            if camera is None or not camera.isOpened():
                break
                
            success, frame = camera.read()
            if not success:
                break
        
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            frame_height, frame_width = frame.shape[:2]
            
            # Process hand tracking
            landmarks = hand_tracker.process_frame(frame)
            
            if landmarks:
                # Get index finger tip (landmark 8) and wrist (landmark 0)
                index_tip = landmarks[8]
                wrist = landmarks[0]
                
                # Calculate finger position relative to wrist
                finger_x = int(index_tip.x * frame_width)
                finger_y = int(index_tip.y * frame_height)
                wrist_y = int(wrist.y * frame_height)
                
                # Calculate relative finger height (0-100)
                # Higher finger position (lower Y value) = higher volume
                relative_height = max(0, min(100, 100 - ((finger_y - wrist_y + 200) / 400 * 100)))
                
                # Apply smoothing
                smooth_height = smooth_volume(relative_height)
                
                # Update volume if there's significant change
                if abs(smooth_height - current_volume) > 2:
                    current_volume = int(smooth_height)
                    volume_controller.set_volume(current_volume)
                    gesture_active = True
                
                # Draw hand landmarks and volume indicator
                hand_tracker.draw_landmarks(frame, landmarks)
                
                # Finger position indicator
                cv2.circle(frame, (finger_x, finger_y), 10, (0, 255, 255), -1)
                
            else:
                gesture_active = False
            
            # Add instructions for real camera
            cv2.putText(frame, "REAL CAMERA MODE - Show your hand and move index finger up/down", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Common elements for both modes
        frame_height, frame_width = frame.shape[:2]
        
        # Draw volume bar
        bar_x = frame_width - 60
        bar_y_start = 50
        bar_height = 300
        bar_width = 20
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y_start), 
                     (bar_x + bar_width, bar_y_start + bar_height), 
                     (100, 100, 100), -1)
        
        # Volume fill
        fill_height = int((current_volume / 100) * bar_height)
        if fill_height > 0:
            cv2.rectangle(frame, (bar_x, bar_y_start + bar_height - fill_height), 
                         (bar_x + bar_width, bar_y_start + bar_height), 
                         (0, 255, 0), -1)
        
        # Volume text
        cv2.putText(frame, f"Vol: {current_volume}%", (bar_x - 50, bar_y_start - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Status indicator
        status_color = (0, 255, 0) if gesture_active else (0, 0, 255)
        status_text = "ACTIVE" if gesture_active else "INACTIVE"
        cv2.putText(frame, f"Status: {status_text}", (10, frame_height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    """Get current system status"""
    global current_volume, gesture_active
    return jsonify({
        'volume': current_volume,
        'gesture_active': gesture_active,
        'camera_active': camera == "simulation" or (camera is not None and camera.isOpened())
    })

@app.route('/calibrate')
def calibrate():
    """Reset calibration"""
    global volume_smoothing_buffer
    volume_smoothing_buffer = []
    return jsonify({'status': 'calibrated'})

if __name__ == '__main__':
    # Initialize camera
    if not initialize_camera():
        print("Error: Could not initialize camera")
        exit(1)
    
    print("Gesture Volume Control System Starting...")
    print("Open your browser and go to http://localhost:5000")
    if camera == "simulation":
        print("DEMO MODE: Showing simulation - will use real camera on your PC")
    else:
        print("REAL MODE: Show your hand to the camera and move your index finger up/down to control volume")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        if camera:
            camera.release()
        cv2.destroyAllWindows()
