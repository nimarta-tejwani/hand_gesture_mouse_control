import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize MediaPipe Drawing
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Screen dimensions (adjust as needed)
screen_width, screen_height = pyautogui.size()

# Variables for click gesture detection
click_threshold = 50  # Adjust this value to control the click sensitivity
click_counter = 0
is_clicking = False
last_click_time = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Get the coordinates of the index finger tip (landmark 8)
            index_finger_x = int(landmarks.landmark[8].x * screen_width)
            index_finger_y = int(landmarks.landmark[8].y * screen_height)

            # Move the mouse pointer to the index finger's position
            pyautogui.moveTo(index_finger_x, index_finger_y, duration=0.2)

            # Detect a click gesture (make a fist)
            thumb_tip_x = int(landmarks.landmark[4].x * screen_width)
            thumb_tip_y = int(landmarks.landmark[4].y * screen_height)
            distance = np.sqrt((index_finger_x - thumb_tip_x)**2 + (index_finger_y - thumb_tip_y)**2)

            if distance < click_threshold:
                if not is_clicking:
                    is_clicking = True
                    click_counter = 0
                else:
                    click_counter += 1
                    current_time = time.time()
                    if click_counter == 2 and current_time - last_click_time < 1:  # Detect a double-click within 1 second
                        pyautogui.doubleClick()
                    last_click_time = current_time
            else:
                if is_clicking:
                    is_clicking = False
                    if click_counter == 1:  # Perform a single click if there was only one click
                        pyautogui.click()

            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    # Display the frame
    cv2.imshow('Hand Gesture Mouse Control', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
