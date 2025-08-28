import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.7):
        """Initialize MediaPipe hand tracking"""
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Track only one hand for better performance
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        
        self.landmarks = None
        self.last_valid_landmarks = None
        
    def process_frame(self, frame):
        """Process frame and return hand landmarks"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Extract landmarks if hands are detected
        if results.multi_hand_landmarks:
            # Get the first (and only) hand
            hand_landmarks = results.multi_hand_landmarks[0]
            self.landmarks = hand_landmarks.landmark
            self.last_valid_landmarks = self.landmarks
            return self.landmarks
        else:
            self.landmarks = None
            return None
    
    def draw_landmarks(self, frame, landmarks=None):
        """Draw hand landmarks on the frame"""
        if landmarks is None:
            landmarks = self.landmarks
            
        if landmarks:
            # Convert landmarks to format expected by MediaPipe
            from mediapipe.framework.formats import landmark_pb2
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            for landmark in landmarks:
                landmark_proto = landmark_pb2.NormalizedLandmark()
                landmark_proto.x = landmark.x
                landmark_proto.y = landmark.y
                landmark_proto.z = landmark.z
                hand_landmarks_proto.landmark.append(landmark_proto)
            
            # Draw landmarks and connections
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks_proto,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
    
    def get_finger_position(self, landmarks, finger_tip_id=8):
        """Get normalized finger tip position"""
        if landmarks and len(landmarks) > finger_tip_id:
            return {
                'x': landmarks[finger_tip_id].x,
                'y': landmarks[finger_tip_id].y,
                'z': landmarks[finger_tip_id].z
            }
        return None
    
    def get_hand_gesture_data(self, landmarks):
        """Extract gesture data from landmarks"""
        if not landmarks or len(landmarks) < 21:
            return None
        
        # Key landmarks for gesture recognition
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Calculate distances and angles
        gesture_data = {
            'wrist': {'x': wrist.x, 'y': wrist.y},
            'index_tip': {'x': index_tip.x, 'y': index_tip.y},
            'thumb_tip': {'x': thumb_tip.x, 'y': thumb_tip.y},
            'middle_tip': {'x': middle_tip.x, 'y': middle_tip.y},
            'ring_tip': {'x': ring_tip.x, 'y': ring_tip.y},
            'pinky_tip': {'x': pinky_tip.x, 'y': pinky_tip.y},
        }
        
        return gesture_data
    
    def is_pointing_gesture(self, landmarks):
        """Check if the hand is in a pointing gesture (index finger extended)"""
        if not landmarks or len(landmarks) < 21:
            return False
        
        # Index finger landmarks
        index_mcp = landmarks[5]   # Index MCP
        index_pip = landmarks[6]   # Index PIP
        index_dip = landmarks[7]   # Index DIP
        index_tip = landmarks[8]   # Index TIP
        
        # Check if index finger is extended (tip higher than other joints)
        index_extended = (index_tip.y < index_dip.y < index_pip.y < index_mcp.y)
        
        # Middle finger landmarks for comparison
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        
        # Check if middle finger is folded (tip lower than pip)
        middle_folded = middle_tip.y > middle_pip.y
        
        return index_extended and middle_folded
    
    def calculate_finger_distance_from_wrist(self, landmarks, finger_tip_id=8):
        """Calculate distance of finger tip from wrist"""
        if not landmarks or len(landmarks) <= max(finger_tip_id, 0):
            return 0
        
        wrist = landmarks[0]
        finger_tip = landmarks[finger_tip_id]
        
        # Calculate Euclidean distance
        distance = np.sqrt(
            (finger_tip.x - wrist.x) ** 2 + 
            (finger_tip.y - wrist.y) ** 2
        )
        
        return distance
    
    def get_normalized_finger_height(self, landmarks, frame_height):
        """Get normalized finger height for volume control"""
        if not landmarks or len(landmarks) < 9:
            return 50  # Default middle position
        
        # Use index finger tip
        finger_tip = landmarks[8]
        wrist = landmarks[0]
        
        # Calculate relative height (0-100)
        finger_pixel_y = finger_tip.y * frame_height
        wrist_pixel_y = wrist.y * frame_height
        
        # Normalize based on expected hand range (approximately 200 pixels)
        relative_y = (wrist_pixel_y - finger_pixel_y) + 100
        normalized_height = max(0, min(100, (relative_y / 200) * 100))
        
        return normalized_height
    
    def cleanup(self):
        """Clean up MediaPipe resources"""
        if hasattr(self, 'hands'):
            self.hands.close()
