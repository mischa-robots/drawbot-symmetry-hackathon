import cv2
import numpy as np
import sys
import os
import time
import threading

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

class DualCameraCapture:
    def __init__(self, robot_ip="192.168.129.84", stream_port=8554):
        self.stream_urls = [
            f"rtsp://{robot_ip}:{stream_port}/cam0",
            f"rtsp://{robot_ip}:{stream_port}/cam1"
        ]
        self.window_name = "Robot Cameras"
        self.latest_numbers = get_latest_image_number()
        self.recording = False
        self.last_capture_time = 0
        self.capture_interval = 1.0
        self.frames = {0: None, 1: None}
        self.threads = []
        self.running = True
        self.ffmpeg_options = "rtsp_transport;tcp|buffer_size;1024"
        
    def capture_frames(self, cam_index, url):
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size to lower latency
        if not cap.isOpened():
            print(f"Failed to open camera {cam_index}")
            return
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frames[cam_index] = frame
            else:
                print(f"Camera {cam_index}: Failed to grab frame")
                time.sleep(0.1)  # Prevent excessive CPU usage
        
        cap.release()
    
    def start_cameras(self):
        for i, url in enumerate(self.stream_urls):
            thread = threading.Thread(target=self.capture_frames, args=(i, url), daemon=True)
            thread.start()
            self.threads.append(thread)
    
    def take_picture(self):
        current_time = time.time()
        if not self.recording or (current_time - self.last_capture_time) >= self.capture_interval:
            for i in range(2):
                frame = self.frames[i]
                if frame is not None:
                    self.latest_numbers[i] += 1
                    filename = f"{target_dir}/cam{i}_{self.latest_numbers[i]:04d}.png"
                    cv2.imwrite(filename, frame)
                    print(f"Saved {filename}")
            self.last_capture_time = current_time

    def run(self):
        print("CAMERA CAPTURE\nPress R to toggle continuous recording, SPACE for single capture, and ESC to quit.\n")
        print("Starting camera threads...")
        
        self.start_cameras()
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        try:
            while True:
                frames = [self.frames[0], self.frames[1]]
                
                if all(frame is not None for frame in frames):
                    combined_frame = np.hstack(frames)
                    
                    if self.recording:
                        cv2.putText(combined_frame, "REC", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        self.take_picture()
                    
                    cv2.imshow(self.window_name, combined_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                elif key == ord('r'):
                    self.recording = not self.recording
                    print("Recording " + ("started" if self.recording else "stopped"))
                elif key == 32:  # SPACE
                    self.take_picture()
        
        except KeyboardInterrupt:
            print("\nStopping camera capture...")
        finally:
            self.running = False
            for thread in self.threads:
                thread.join()
            cv2.destroyAllWindows()
            print("Capture system closed.")

def main():
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.129.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554
    
    controller = DualCameraCapture(robot_ip=robot_ip, stream_port=stream_port)
    controller.run()

if __name__ == "__main__":
    main()
