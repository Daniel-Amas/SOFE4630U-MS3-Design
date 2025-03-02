import os
import glob
import base64
import json
from google.cloud import pubsub_v1

# 1. Automatically discover your service account JSON key in the current directory:
json_key_files = glob.glob("*.json")
if not json_key_files:
    raise FileNotFoundError("No service account JSON key file found in the current directory.")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_files[0]

# 2. Define your GCP project and the Pub/Sub topic to publish images.
PROJECT_ID = "sofe4630u-ms3-design"    
TOPIC_ID = "images_topic"             

# 3. Point this to the folder containing your images, e.g., "Dataset_Occluded_Pedestrian"
IMAGE_FOLDER = "Dataset_Occluded_Pedestrian"

def publish_images_to_topic():
    """
    Reads all images in IMAGE_FOLDER, base64-encodes each one, and publishes
    it to the Pub/Sub topic with the image name in an attribute.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    # Grab all files in the folder that look like images (jpeg, png, etc.)
    image_paths = glob.glob(os.path.join(IMAGE_FOLDER, "*.png"))

    if not image_paths:
        print(f"No images found in folder: {IMAGE_FOLDER}")
        return

    for img_path in image_paths:
        # Extract only the filename (e.g., "A_001.png")
        image_name = os.path.basename(img_path)

        # Read image in binary mode
        with open(img_path, "rb") as f:
            image_bytes = f.read()

        # Serialize image by base64-encoding it
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # Build message data
        # Option B (alternative): Just send the raw base64 data and use attributes for the filename
        message_data = image_b64.encode("utf-8")

        # Publish message
        future = publisher.publish(
            topic_path,
            data=message_data,
            filename=image_name
        )

        print(f"Publishing image: {image_name}")
        # Wait for the publish to complete
        future.result()

if __name__ == "__main__":
    publish_images_to_topic()
