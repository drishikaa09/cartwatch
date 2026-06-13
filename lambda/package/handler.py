import json
import base64
import boto3
import psycopg2
from datetime import datetime, timezone

# --- Config ---
REGION = "eu-north-1"
SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:732778637529:cartwatch-abandonment-alerts"
S3_BUCKET = "cartwatch-events-732778637529"
DB_HOST = "cartwatch-db.cp26g6s4i09v.eu-north-1.rds.amazonaws.com"
DB_NAME = "cartwatch"
DB_USER = "cartwatch_user"
DB_PASS = "cartwatch_pass_2024"

# --- AWS Clients ---
sns = boto3.client("sns", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=5432,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def lambda_handler(event, context):
    for record in event["Records"]:
        raw = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        cart_event = json.loads(raw)

        print(f"Received: {cart_event}")

        log_to_s3(cart_event)
        log_to_rds(cart_event)

        if cart_event["event_type"] == "abandon_cart":
            send_alert(cart_event)

    return {"statusCode": 200}

def log_to_rds(cart_event):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (user_id, event_type, product_name, price, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        cart_event["user_id"],
        cart_event["event_type"],
        cart_event["product_name"],
        cart_event["price"],
        cart_event["timestamp"]
    ))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Logged to RDS: {cart_event['event_type']} for {cart_event['user_id']}")

def log_to_s3(cart_event):
    key = f"events/{cart_event['event_type']}/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/{cart_event['user_id']}-{datetime.now(timezone.utc).timestamp()}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(cart_event)
    )

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