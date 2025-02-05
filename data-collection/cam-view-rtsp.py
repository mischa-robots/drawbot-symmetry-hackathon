import cv2
import numpy as np
import sys

class DualCameraViewer:
    def __init__(self, robot_ip="192.168.129.84", stream_port=8554):
        # Using RTSP URLs from mediamtx
        self.stream_urls = [
            f"rtsp://{robot_ip}:{stream_port}/cam0",
            f"rtsp://{robot_ip}:{stream_port}/cam1"
        ]
        self.caps = []
        self.window_name = "Robot Cameras"

    def connect_cameras(self):
        for i, url in enumerate(self.stream_urls):
            print(f"Connecting to camera {i}: {url}")
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                raise Exception(f"Failed to open camera stream: {url}")
            self.caps.append(cap)
            
    def create_side_by_side_view(self, frame1, frame2):
        # Ensure both frames have the same height
        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]
        
        # Use the smaller height for both frames
        target_height = min(h1, h2)
        
        # Calculate new widths maintaining aspect ratio
        new_w1 = int(w1 * (target_height / h1))
        new_w2 = int(w2 * (target_height / h2))
        
        # Resize frames
        frame1 = cv2.resize(frame1, (new_w1, target_height))
        frame2 = cv2.resize(frame2, (new_w2, target_height))
        
        # Combine frames horizontally
        return np.hstack((frame1, frame2))

    def run(self):
        try:
            print("Connecting to cameras...")
            self.connect_cameras()
            
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            
            print("Displaying camera feeds. Press 'q' to quit.")
            while True:
                frames = []
                for cap in self.caps:
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to read frame from camera")
                        continue
                    frames.append(frame)
                
                if len(frames) == 2:
                    #combined_frame = self.create_side_by_side_view(frames[0], frames[1])
                    cv2.imshow(self.window_name, np.hstack((frames[0], frames[1])))
                
                # Break loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nStopping video display...")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            for cap in self.caps:
                cap.release()
            cv2.destroyAllWindows()
            print("Viewer closed.")

def main():
    # Allow IP and port override from command line
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.129.84"
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8554  # Default RTSP port from mediamtx
    
    viewer = DualCameraViewer(robot_ip=robot_ip, stream_port=stream_port)
    viewer.run()

if __name__ == "__main__":
    main()
