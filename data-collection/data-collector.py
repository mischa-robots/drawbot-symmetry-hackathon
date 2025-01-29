import asyncio
import websockets
import json
import cv2
import glob
import os
import time
from datetime import datetime
import numpy as np
import aiohttp

class RobotDataCollector:
    def __init__(self, robot_ip="192.168.158.84", ws_port=8000, stream_port=8889):
        self.robot_ip = robot_ip
        self.ws_url = f"ws://{robot_ip}:{ws_port}/ws"
        self.stream_urls = [
            f"http://{robot_ip}:{stream_port}/cam0",
            f"http://{robot_ip}:{stream_port}/cam1"
        ]
        self.caps = []
        self.last_numbers = self._get_last_numbers()
        
    def _get_last_numbers(self):
        numbers = []
        for cam_id in range(2):
            files = glob.glob(f"robot-cam{cam_id}-*.png")
            if not files:
                numbers.append(0)
                continue
            latest = max(files, key=lambda x: int(x.split('-')[-1].split('.')[0]))
            num = int(latest.split('-')[-1].split('.')[0])
            numbers.append(num)
        return numbers
    
    async def connect_cameras(self):
        for url in self.stream_urls:
            cap = cv2.VideoCapture(url)
            if not cap.isOpened():
                raise Exception(f"Failed to open camera stream: {url}")
            self.caps.append(cap)
    
    async def drive_pattern(self, ws):
        patterns = [
            # Forward
            {"left": 0.5, "right": 0.5},
            # Turn right
            {"left": 0.5, "right": -0.5},
            # Turn left
            {"left": -0.5, "right": 0.5},
            # Stop
            {"left": 0.0, "right": 0.0}
        ]
        
        for pattern in patterns:
            await ws.send(json.dumps(pattern))
            await asyncio.sleep(2)  # Execute each pattern for 2 seconds
    
    async def capture_frames(self):
        while True:
            for cam_id, cap in enumerate(self.caps):
                ret, frame = cap.read()
                if not ret:
                    continue
                
                self.last_numbers[cam_id] += 1
                filename = f"robot-cam{cam_id}-{self.last_numbers[cam_id]:04d}.png"
                cv2.imwrite(filename, frame)
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Captured {filename}")
            
            await asyncio.sleep(1)  # Capture every second
    
    async def run(self):
        try:
            print("Connecting to cameras...")
            await self.connect_cameras()
            
            print("Starting data collection...")
            async with websockets.connect(self.ws_url) as ws:
                # Start frame capture task
                capture_task = asyncio.create_task(self.capture_frames())
                
                # Drive robot in patterns continuously
                while True:
                    await self.drive_pattern(ws)
        
        except KeyboardInterrupt:
            print("\nStopping data collection...")
        finally:
            for cap in self.caps:
                cap.release()
            cv2.destroyAllWindows()

async def main():
    collector = RobotDataCollector()
    await collector.run()

if __name__ == "__main__":
    asyncio.run(main())

