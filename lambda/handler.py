import json
import base64
import boto3
from datetime import datetime, timezone

# --- Config ---
REGION = "eu-north-1"
SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:732778637529:cartwatch-abandonment-alerts"
S3_BUCKET = "cartwatch-events-732778637529"

# --- AWS Clients ---
sns = boto3.client("sns", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

def lambda_handler(event, context):
    for record in event["Records"]:
        # Kinesis data is base64 encoded — decode it first
        raw = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        cart_event = json.loads(raw)

        print(f"Received: {cart_event}")

        # Log every event to S3
        log_to_s3(cart_event)

        # Only alert on abandonment
        if cart_event["event_type"] == "abandon_cart":
            send_alert(cart_event)

    return {"statusCode": 200}

def log_to_s3(cart_event):
    key = f"events/{cart_event['event_type']}/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/{cart_event['user_id']}-{datetime.now(timezone.utc).timestamp()}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(cart_event)
    )
    print(f"Logged to S3: {key}")

def send_alert(cart_event):
    message = (
        f"🚨 Cart Abandonment Detected!\n\n"
        f"User: {cart_event['user_id']}\n"
        f"Product: {cart_event['product_name']}\n"
        f"Price: ₹{cart_event['price']}\n"
        f"Time: {cart_event['timestamp']}"
    )
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="CartWatch Alert — Abandoned Cart",
        Message=message
    )
    print(f"Alert sent for {cart_event['user_id']}")