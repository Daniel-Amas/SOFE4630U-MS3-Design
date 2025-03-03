import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from transformers import DPTForDepthEstimation, DPTImageProcessor

# Load YOLOv8 for pedestrian detection
detector = YOLO("yolov8n.pt")  # You can use "yolov8s.pt" for better accuracy

# Load DA-Former (Depth Anything) for depth estimation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
depth_model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large").to(device)
depth_processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")

# Paths
INPUT_FOLDER = "Dataset_Occluded_Pedestrian"
OUTPUT_FOLDER = "pedestrians"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def detect_pedestrians(image):
    """ Detect pedestrians in the image and return bounding boxes. """
    results = detector.predict(image)
    detections = []
    
    for box in results[0].boxes:
        cls_id = int(box.cls[0].item())   # Class ID
        conf   = float(box.conf[0].item())  # Confidence score
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy()) 
        
        if cls_id == 0:  # Class ID 0 corresponds to 'person' in COCO dataset
            detections.append((x1, y1, x2, y2, conf))

    return detections

def estimate_depth(image):
    """ Estimate depth using DA-Former (Depth Anything) and return a depth map. """
    
    # Convert BGR -> RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Preprocess image for the depth model
    inputs = depth_processor(images=image_rgb, return_tensors="pt").to(device)

    # Run model
    with torch.no_grad():
        outputs = depth_model(**inputs)
    
    # Convert to numpy depth map
    depth_map = outputs.predicted_depth.squeeze().cpu().numpy()

    # Normalize depth values
    depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())

    # Resize to match input image
    depth_map = cv2.resize(depth_map, (image.shape[1], image.shape[0]))

    return depth_map

def average_depth_in_bbox(depth_map, bbox):
    """ Compute the average depth of a bounding box region. """
    x_min, y_min, x_max, y_max = bbox
    region = depth_map[y_min:y_max, x_min:x_max]
    
    if region.size == 0:
        return None

    return float(np.mean(region))

# Process all images
for filename in os.listdir(INPUT_FOLDER):
    if not (filename.endswith(".jpg") or filename.endswith(".png")):
        continue  # Skip non-image files

    img_path = os.path.join(INPUT_FOLDER, filename)
    img = cv2.imread(img_path)
    if img is None:
        print(f"Could not read {filename}, skipping.")
        continue

    # Detect pedestrians
    detections = detect_pedestrians(img)

    if not detections:
        print(f"No pedestrians found in {filename}, skipping.")
        continue  # Skip images without pedestrians

    # Save the image to the `pedestrians` folder
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    cv2.imwrite(output_path, img)

    # Estimate depth
    depth_map = estimate_depth(img)

    # Process detections and compute depth for each pedestrian
    for (x1, y1, x2, y2, conf) in detections:
        avg_depth = average_depth_in_bbox(depth_map, (x1, y1, x2, y2))
        print(f"Image: {filename} | BBox: ({x1}, {y1}, {x2}, {y2}) | Confidence: {conf:.2f} | Avg Depth: {avg_depth:.3f}")

print("Processing complete. Filtered images are saved in the 'pedestrians' folder.")
