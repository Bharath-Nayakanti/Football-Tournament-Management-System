import cv2
import numpy as np

def detect_visual_excitement(video_path, threshold=0.7):
    """
    Detects visual excitement (celebrations, close-ups) using OpenCV
    Returns timestamps of exciting moments
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    timestamps = []
    prev_frame = None
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert to grayscale and resize for faster processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (320, 240))
        
        if prev_frame is not None:
            # Calculate frame difference
            diff = cv2.absdiff(gray, prev_frame)
            diff_score = np.mean(diff)
            
            # Detect sudden movements (celebration)
            if diff_score > 30:  # Adjust based on your video
                motion_score = diff_score / 255.0
                
                # Detect close-ups (face detection)
                faces = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                ).detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0 or motion_score > threshold:
                    timestamp = frame_count / fps
                    timestamps.append(timestamp)
        
        prev_frame = gray.copy()
        frame_count += 1
    
    cap.release()
    return timestamps
