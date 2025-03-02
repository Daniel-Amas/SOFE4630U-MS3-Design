import os
import json
import glob
import csv
from google.cloud import pubsub_v1

# Automatically detect a .json key file in the current directory
files = glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = files[0]

# Replace with your own GCP project and Pub/Sub topic
project_id = "sofe4630u-ms3-design"
topic_id = "labels_topic"

csv_file_path = "Labels.csv"

# Create a Pub/Sub publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def produce_messages():
    with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Convert row to dictionary
            record = dict(row)
            # Serialize dictionary to JSON
            message = json.dumps(record).encode("utf-8")
            # Publish message to Pub/Sub topic
            print(f"Producing record: {record}")
            future = publisher.publish(topic_path, message)

            # Wait for publish call to complete. You can omit future.result() 
            # for performance, but it’s helpful for error handling.
            future.result()

if __name__ == "__main__":
    produce_messages()
