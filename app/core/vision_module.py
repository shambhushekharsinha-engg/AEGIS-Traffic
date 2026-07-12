import os
import cv2
from ultralytics import YOLO

class FolderStreamAnalyzer:
    def __init__(self):
        # Load a standard YOLOv8 pre-trained model
        self.model = YOLO("yolov8n.pt") 

    def process_frame_sequence(self, folder_path, max_frames=30):
        """Simulates video processing by reading extracted sequential frames from the UCF folder."""
        if not os.path.exists(folder_path):
            print(f"[Error]: Path {folder_path} not found.")
            return []

        # Sort files to maintain chronological sequence of the event
        frame_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))])[:max_frames]
        aggregated_detections = set()

        print(f"👁️ Analyzing {len(frame_files)} sequential frames from folder...")
        
        for file in frame_files:
            img_path = os.path.join(folder_path, file)
            frame = cv2.imread(img_path)
            
            # Run inference on the 64x64 frame
            results = self.model(frame, verbose=False)[0]
            
            for box in results.boxes:
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                confidence = float(box.conf[0])
                
                # Flag objects relevant to public safety/anomalies (e.g., person, car)
                if confidence > 0.4:
                    aggregated_detections.add(label)
                    
        return list(aggregated_detections)