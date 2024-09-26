import cv2
import numpy as np
import os

def detect_ball(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    return frame

def process_frames(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.jpg'):
            frame_path = os.path.join(input_folder, filename)
            frame = cv2.imread(frame_path)
            processed_frame = detect_ball(frame)
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, processed_frame)
            print(f"Processed {filename}")

if __name__ == "__main__":
    input_folder = '../frames/'
    output_folder = '../processed_frames/'
    process_frames(input_folder, output_folder)
