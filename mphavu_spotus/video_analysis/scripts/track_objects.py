import cv2
import os
import subprocess
import math

def initialize_tracker(frame, bbox):
    """Initialize a tracker based on the available algorithms in OpenCV."""
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
    """Update the tracker with the current frame and draw a rectangle around the tracked object."""
    success, bbox = tracker.update(frame)
    if success:
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return success, bbox

def calculate_angle(prev_position, current_position, goal_position):
    """Calculate the shooting angle between the object and the goal."""
    # Calculate the vector from the object to the goal
    vector_to_goal = (goal_position[0] - current_position[0], goal_position[1] - current_position[1])
    
    # Calculate the vector of object movement
    movement_vector = (current_position[0] - prev_position[0], current_position[1] - prev_position[1])
    
    # Calculate the dot product of the two vectors
    dot_product = (vector_to_goal[0] * movement_vector[0]) + (vector_to_goal[1] * movement_vector[1])
    
    # Calculate the magnitude of the vectors
    magnitude_goal = math.sqrt(vector_to_goal[0]**2 + vector_to_goal[1]**2)
    magnitude_movement = math.sqrt(movement_vector[0]**2 + movement_vector[1]**2)
    
    if magnitude_goal == 0 or magnitude_movement == 0:
        return 0  # If either vector has no length, return zero angle
    
    # Calculate the angle using the dot product formula
    angle_radians = math.acos(dot_product / (magnitude_goal * magnitude_movement))
    
    # Convert radians to degrees
    angle_degrees = math.degrees(angle_radians)
    
    return angle_degrees

def calculate_accuracy(current_position, goal_position, tolerance=30):
    """Calculate the shooting accuracy based on distance to the goal."""
    distance_to_goal = math.sqrt((goal_position[0] - current_position[0])**2 + (goal_position[1] - current_position[1])**2)
    
    # Accuracy as a percentage based on distance (the closer to the goal, the higher the accuracy)
    if distance_to_goal <= tolerance:
        return 100
    elif distance_to_goal > tolerance * 5:
        return 0
    else:
        return max(0, 100 - (distance_to_goal / tolerance) * 20)

def compress_video(input_path, output_path, bitrate='500k'):
    """Compress the video using FFmpeg."""
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,
            '-b:v', bitrate,
            '-vcodec', 'libx264',
            '-preset', 'fast',
            '-crf', '28',
            output_path
        ]
        subprocess.run(ffmpeg_command, check=True)
        print(f"Video compressed and saved to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while compressing video: {e}")

def process_video(video_path, output_folder, tracking_data_path, goal_position):
    """Process the video: track an object, write tracking data, and calculate shooting angles and accuracy."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file at {video_path}")
        return
    
    ret, frame = cap.read()
    if not ret:
        print("Failed to read video.")
        return

    bbox = (50, 50, 100, 100)  # Adjust this for the initial object location
    tracker = initialize_tracker(frame, bbox)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with open(tracking_data_path, 'w') as file:
        frame_count = 0
        prev_position = None
        total_angle = 0
        total_accuracy = 0
        count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            success, bbox = update_tracker(frame, tracker)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                current_position = (x + w // 2, y + h // 2)  # Calculate the center of the object
                
                if prev_position is not None:
                    # Calculate shooting angle based on movement
                    angle = calculate_angle(prev_position, current_position, goal_position)
                    total_angle += angle

                    # Calculate accuracy based on the object's proximity to the goal
                    accuracy = calculate_accuracy(current_position, goal_position)
                    total_accuracy += accuracy
                    
                    count += 1
                
                prev_position = current_position  # Update the previous position
                
                file.write(f"{frame_count},{x},{y},{w},{h},{angle:.2f},{accuracy:.2f}\n")
                frame_count += 1
            
            if cv2.waitKey(30) & 0xFF == 27:
                break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames and saved tracking data to {tracking_data_path}.")
    
    if count > 0:
        avg_angle = total_angle / count
        avg_accuracy = total_accuracy / count
        print(f"Average Shooting Angle: {avg_angle:.2f} degrees")
        print(f"Average Shooting Accuracy: {avg_accuracy:.2f}%")
    else:
        print("No valid frames for shooting analysis.")
    
    compressed_video_path = os.path.join(output_folder, 'compressed_video.mp4')
    compress_video(video_path, compressed_video_path)

if __name__ == "__main__":
    video_path = '/path/to/your/video.mp4'  # Update with your video path
    output_folder = './tracked_frames/'
    tracking_data_path = 'tracking_data.txt'
    
    # Set the position of the goal for shooting analysis
    goal_position = (500, 100)  # Adjust based on your video frame (e.g., goalpost position)
    
    # Process the video (track object, calculate angle and accuracy, save data)
    process_video(video_path, output_folder, tracking_data_path, goal_position)
