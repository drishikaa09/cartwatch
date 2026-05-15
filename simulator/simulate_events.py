import json
import random
import time
import boto3
from datetime import datetime, timezone

# --- Config ---
STREAM_NAME = "cartwatch-stream"
REGION = "eu-north-1"

# --- Setup ---
session = boto3.Session(profile_name="cartwatch")
kinesis = session.client("kinesis", region_name=REGION)

PRODUCTS = [
    {"id": "P001", "name": "Wireless Earbuds", "price": 1299},
    {"id": "P002", "name": "Yoga Mat", "price": 599},
    {"id": "P003", "name": "Water Bottle", "price": 349},
    {"id": "P004", "name": "Notebook Set", "price": 199},
    {"id": "P005", "name": "Phone Stand", "price": 449},
]

EVENTS = ["page_view", "add_to_cart", "checkout", "abandon_cart"]

def generate_event():
    product = random.choice(PRODUCTS)
    event = {
        "user_id": f"user_{random.randint(1, 50)}",
        "event_type": random.choices(
            EVENTS,
            weights=[40, 30, 15, 15]  # page_view most common, abandon realistic
        )[0],
        "product_id": product["id"],
        "product_name": product["name"],
        "price": product["price"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return event

def send_event(event):
    kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(event),
        PartitionKey=event["user_id"]
    )
    print(f"[{event['timestamp']}] {event['user_id']} → {event['event_type']} → {event['product_name']}")

if __name__ == "__main__":
    print("CartWatch simulator starting...")
    while True:
        event = generate_event()
        send_event(event)
        time.sleep(1)  # one event per second
