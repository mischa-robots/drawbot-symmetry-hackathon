import cv2
import numpy as np
import sys
import asyncio
import websockets
import json
import os

target_dir = "pictures"
os.makedirs(target_dir, exist_ok=True)

def get_latest_image_number():
    numbers = [0, 0]
    for i in range(2):
        files = [f for f in os.listdir(target_dir) if f.startswith(f"cam{i}_") and f.endswith(".png")]
        if files:
            latest = max(files, key=lambda x: int(x.split('_')[1].split('.')[0]))
            numbers[i] = int(latest.split('_')[1].split('.')[0])
    return numbers

class DualCameraRobotController:
    def __init__(self, robot_ip="192.168.158.84", stream_port=8554, ws_port=8000):
        # Using RTSP URLs from mediamtx
        self.stream_urls = [
            f"rtsp://{robot_ip}:{stream_port}/cam0",
            f"rtsp://{robot_ip}:{stream_port}/cam1"
        ]
        self.ws_url = f"ws://{robot_ip}:{ws_port}/ws"
        self.caps = []
        self.window_name = "Robot Cameras"
        self.latest_numbers = get_latest_image_number()
        self.ws = None
        
    def connect_cameras(self):
        for i, url in enumerate(self.stream_urls):
            print(f"Connecting to camera {i}: {url}")
            cap = cv2.VideoCapture(url)
            if not cap.isOpened():
                raise Exception(f"Failed to open camera stream: {url}")
            self.caps.append(cap)
    
    async def connect_websocket(self):
        try:
            self.ws = await websockets.connect(self.ws_url)
            print("Connected to robot WebSocket.")
        except Exception as e:
            print(f"Failed to connect to WebSocket: {str(e)}")
            self.ws = None

    async def send_command(self, left, right):
        if self.ws:
            try:
                command = json.dumps({"left": left, "right": right})
                await self.ws.send(command)
                print(f"Sent command: {command}")
            except Exception as e:
                print(f"Error sending command: {str(e)}")

    def handle_keypress(self, key):
        commands = {
            ord('w'): (1.0, 1.0),  # Forward
            ord('s'): (-1.0, -1.0),  # Backward
            ord('a'): (-1.0, 1.0),  # Left turn
            ord('d'): (1.0, -1.0),  # Right turn
            ord('q'): (0.0, 0.0)   # Stop
        }
        if key in commands:
            left, right = commands[key]
            asyncio.run(self.send_command(left, right))

    def create_side_by_side_view(self, frame1, frame2):
        # both streams have the same size, so resize not required
        #h1, w1 = frame1.shape[:2]
        #h2, w2 = frame2.shape[:2]
        #target_height = min(h1, h2)
        #frame1 = cv2.resize(frame1, (int(w1 * (target_height / h1)), target_height))
        #frame2 = cv2.resize(frame2, (int(w2 * (target_height / h2)), target_height))
        return np.hstack((frame1, frame2))

    def take_picture(self, frames):
        for i, frame in enumerate(frames):
            self.latest_numbers[i] += 1
            filename = f"{target_dir}/cam{i}_{self.latest_numbers[i]:04d}.png"
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")

    def run(self):
        try:
            print("ROBOT CONTROL\nUse WASD to move, Q to stop, R to record pictures and ESC to quit.\n\n")
            print("Connecting to cameras...")
            self.connect_cameras()
            asyncio.run(self.connect_websocket())
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            print("Displaying camera feeds.\n")
            
            while True:
                frames = []
                for cap in self.caps:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to read frame from camera")
                        continue
                    frames.append(frame)
                
                if len(frames) == 2:
                    combined_frame = self.create_side_by_side_view(frames[0], frames[1])
                    cv2.imshow(self.window_name, combined_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC key to exit
                    break
                elif key == ord('r'):
                    self.take_picture(frames)
                self.handle_keypress(key)
        
        except KeyboardInterrupt:
            print("\nStopping video display...")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            for cap in self.caps:
                cap.release()
            cv2.destroyAllWindows()
            print("Viewer closed.")
            if self.ws:
                asyncio.run(self.ws.close())

def main():
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.158.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554
    ws_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
    
    controller = DualCameraRobotController(robot_ip=robot_ip, stream_port=stream_port, ws_port=ws_port)
    controller.run()

if __name__ == "__main__":
    main()
