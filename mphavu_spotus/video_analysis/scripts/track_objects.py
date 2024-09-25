import cv2
import os

def initialize_tracker(frame, bbox):
    # Use an available tracker
    if hasattr(cv2, 'TrackerMIL_create'):
        tracker = cv2.TrackerMIL_create()
    elif hasattr(cv2, 'TrackerBoosting_create'):
        tracker = cv2.TrackerBoosting_create()
    elif hasattr(cv2, 'TrackerMedianFlow_create'):
        tracker = cv2.TrackerMedianFlow_create()
    else:
        raise RuntimeError("No suitable tracker found in the OpenCV installation.")
    tracker.init(frame, bbox)
    return tracker

def update_tracker(frame, tracker):
    success, bbox = tracker.update(frame)
    if success:
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return success, bbox

def process_video(video_path, output_folder, tracking_data_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file at {video_path}")
        return
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to read video.")
        return

    bbox = (50, 50, 100, 100)  # Example initial bounding box
    tracker = initialize_tracker(frame, bbox)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with open(tracking_data_path, 'w') as file:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            success, bbox = update_tracker(frame, tracker)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                ball_position = (x + w // 2, y + h // 2)  # Example calculation
                file.write(f"{frame_count},{x},{y},{w},{h}\n")
                frame_count += 1
            
            if cv2.waitKey(30) & 0xFF == 27:
                break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames and saved tracking data to {tracking_data_path}.")

if __name__ == "__main__":
    video_path = '/home/studen/Downloads/Screencast from 16-08-2024 12_00_15 WB.webm'
    output_folder = '../tracked_frames/'
    tracking_data_path = 'tracking_data.txt'
    process_video(video_path, output_folder, tracking_data_path)
