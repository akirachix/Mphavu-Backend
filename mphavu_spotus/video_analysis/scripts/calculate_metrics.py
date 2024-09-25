import math
import numpy as np

def read_tracking_data(tracking_data_path):
    player_foot_position = (100, 200) 
    ball_positions = []
    with open(tracking_data_path, 'r') as file:
        for line in file:
            _, x, y, w, h = map(float, line.strip().split(','))
            ball_positions.append((x + w / 2, y + h / 2)) 
    return player_foot_position, ball_positions

def calculate_angle(player_foot_position, ball_position):
    x1, y1 = player_foot_position
    x2, y2 = ball_position
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return angle % 160

def calculate_accuracy(ball_position, target_position, target_radius):
    dist = np.linalg.norm(np.array(ball_position) - np.array(target_position))
    accuracy = 100 - min(dist / target_radius * 100, 100)
    return max(accuracy, 0)

def main():
    tracking_data_path = 'tracking_data.txt'
    player_foot_position, ball_positions = read_tracking_data(tracking_data_path)
    
    target_position = (160, 240)  
    target_radius = 50            

    if not ball_positions:
        print("No ball positions found in tracking data.")
        return

    # Example: calculate metrics for the last ball position
    last_ball_position = ball_positions[-1]
    angle = calculate_angle(player_foot_position, last_ball_position)
    accuracy = calculate_accuracy(last_ball_position, target_position, target_radius)
    
    print(f"Shooting Angle: {angle:.2f} degrees")
    print(f"Shooting Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    main()
