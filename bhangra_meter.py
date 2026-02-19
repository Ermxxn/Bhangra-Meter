import cv2
import mediapipe as mp
import pygame
import os
import time
import math

print("Initializing The Bhangra Meter (Punjabi Edition)...")

# 1. SETUP
pygame.mixer.init()

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# 2. ASSETS (The Vibe)
assets = {
    "dhol": "assets/dhol.mp3",
    "img": "assets/balle.png"
}

# Load Sound
dhol_sound = None
if os.path.exists(assets["dhol"]):
    dhol_sound = pygame.mixer.Sound(assets["dhol"])
    dhol_sound.set_volume(0.5)

# Load Image
balle_img = None
if os.path.exists(assets["img"]):
    balle_img = cv2.imread(assets["img"])
    if balle_img is not None:
        balle_img = cv2.resize(balle_img, (300, 300))

# 3. STATE
is_bhangra = False
last_trigger = 0

while True:
    success, img = cap.read()
    if not success: break
    
    # Flip logic is tricky for Full Body, usually we don't flip or we flip carefully
    # Let's flip for mirror feel
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    results = pose.process(img_rgb)
    
    status_text = "Thanda... (Do Bhangra!)"
    color = (0, 0, 255) # Red (Boring)
    
    if results.pose_landmarks:
        # Draw Skeleton
        mp_draw.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        lm = results.pose_landmarks.landmark
        
        # LOGIC: ARE HANDS IN THE AIR?
        # In MediaPipe, Y coordinates start at 0 (top) and go to 1 (bottom).
        # So "Higher" means a SMALLER Y number.
        
        # Get Y coordinates
        nose_y = lm[0].y
        left_wrist_y = lm[15].y
        right_wrist_y = lm[16].y
        
        # Check if BOTH wrists are HIGHER (smaller Y) than the NOSE
        if left_wrist_y < nose_y and right_wrist_y < nose_y:
            status_text = "CHAK DE PHATTE!!"
            color = (0, 255, 0) # Green (Lit)
            
            if not is_bhangra:
                is_bhangra = True
                if dhol_sound: dhol_sound.play(-1) # -1 means loop forever
                
        else:
            # Stopped Bhangra
            if is_bhangra:
                is_bhangra = False
                if dhol_sound: dhol_sound.stop()
    
    # --- UI DRAWING ---
    
    # 1. Status Bar
    cv2.rectangle(img, (0, 0), (1280, 100), color, -1)
    cv2.putText(img, status_text, (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 
               2, (255, 255, 255), 5)

    # 2. Show Meme Image when dancing
    if is_bhangra and balle_img is not None:
        # 1. MAKE IT BIGGER: Resize to 600x600 (or whatever size you want)
        img_big = cv2.resize(balle_img, (600, 600))
        
        h, w, c = img_big.shape
        
        # Put image in center
        center_x = 1280 // 2 - w // 2
        center_y = 720 // 2 - h // 2
        
        try:
            # Create a copy to draw the overlay on
            overlay = img.copy()
            
            # Place the bigger image onto the overlay
            overlay[center_y:center_y+h, center_x:center_x+w] = img_big
            
            # 2. MAKE IT LESS TRANSPARENT: 
            # 0.9 = 90% opacity (The Meme)
            # 0.1 = 10% opacity (The Background)
            cv2.addWeighted(overlay, 0.9, img, 0.1, 0, img)
            
        except Exception as e: 
            pass

    cv2.imshow("The Bhangra Meter", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()