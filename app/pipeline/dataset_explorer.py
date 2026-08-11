"""
AEGIS-Traffic — Dataset Explorer Service
Provides statistics, class breakdowns, annotated bounding box counts, and sample manifests for training datasets.
"""


class DatasetExplorerService:
    def __init__(self):
        pass

    def get_dataset_metadata(self) -> dict:
        """
        Returns dataset exploration statistics for UCF Crime and Custom Smart City Traffic datasets.
        """
        return {
            "datasets": [
                {
                    "id": "traffic-coco-delhi",
                    "name": "AEGIS Delhi-NCR Multi-Lane Traffic Dataset",
                    "total_images": 14250,
                    "annotated_frames": 14250,
                    "total_bounding_boxes": 118400,
                    "resolution": "1920x1080 & 1280x720",
                    "format": "YOLOv8 PyTorch / COCO JSON",
                    "splits": {"train": 10000, "val": 2800, "test": 1450},
                    "classes": [
                        {"name": "car", "count": 68400, "color": "#00f0ff"},
                        {"name": "motorcycle", "count": 24200, "color": "#a855f7"},
                        {"name": "truck", "count": 14100, "color": "#f59e0b"},
                        {"name": "bus", "count": 8200, "color": "#10b981"},
                        {"name": "autorickshaw", "count": 3500, "color": "#ef4444"}
                    ],
                    "sample_videos": [
                        {"title": "Connaught Place Roundabout Peak", "duration": "03:45", "fps": 30},
                        {"title": "Cyber City Expressway Corridor", "duration": "05:12", "fps": 30},
                        {"title": "Noida Toll Plaza Gate 4", "duration": "02:30", "fps": 25}
                    ]
                },
                {
                    "id": "ucf-crime-anomaly",
                    "name": "UCF Crime & Anomaly Benchmark Dataset",
                    "total_images": 9500,
                    "annotated_frames": 9500,
                    "total_bounding_boxes": 34200,
                    "resolution": "320x240",
                    "format": "NumPy / Torch Tensors",
                    "splits": {"train": 6500, "val": 1800, "test": 1200},
                    "classes": [
                        {"name": "Abuse", "count": 1200, "color": "#ef4444"},
                        {"name": "Arrest", "count": 950, "color": "#f59e0b"},
                        {"name": "Arson", "count": 800, "color": "#a855f7"},
                        {"name": "Assault", "count": 1400, "color": "#3b82f6"},
                        {"name": "Road Accident", "count": 2800, "color": "#00f0ff"}
                    ],
                    "sample_videos": [
                        {"title": "Road Accident Scene 012", "duration": "01:15", "fps": 30},
                        {"title": "Vehicle Collision Night 004", "duration": "00:45", "fps": 30}
                    ]
                }
            ]
        }


dataset_explorer = DatasetExplorerService()
