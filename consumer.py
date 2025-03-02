import os
import json
import glob
import time
from google.cloud import pubsub_v1

# Automatically detect a .json key file in the current directory
files = glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = files[0]

# Replace with your own GCP project and Pub/Sub subscription
project_id = "sofe4630u-ms3-design"
subscription_id = "labels_topic-sub"

# Create a Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    """
    Callback function to process received messages.
    Deserializes the JSON string back into a dictionary and prints it.
    """
    data_as_json = message.data.decode("utf-8")
    record = json.loads(data_as_json)
    print(f"Consumed record: {record}")
    message.ack()  # Acknowledge the message so it's not re-delivered

def consume_messages():
    """
    Subscribes to the Pub/Sub subscription and listens for incoming messages.
    """
    print(f"Listening for messages on {subscription_path}...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    try:
        # Block the main thread and let the subscription receive messages
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()  # Trigger the shutdown
        streaming_pull_future.result()  # Block until the shutdown is complete

if __name__ == "__main__":
    consume_messages()
