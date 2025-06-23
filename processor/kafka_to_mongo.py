from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# Kafka setup
KAFKA_TOPIC = "ad_events"
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='ad-analytics-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# MongoDB setup
client = MongoClient("mongodb+srv://ishaanvats83:poym8XoADTppsi7j@cluster0.mongodb.net/?retryWrites=true&w=majority") 
db = client["ad_analytics"]
collection = db["campaign_metrics"]

# Metrics storage
metrics = {}

print("✅ Listening to Kafka topic...")

try:
    for message in consumer:
        event = message.value

        campaign_id = event.get("campaign_id")
        ad_id = event.get("ad_id")
        event_type = event.get("event_type")
        revenue = float(event.get("revenue", 0.0))
        device = event.get("device")
        location = event.get("location")

        key = f"{campaign_id}_{ad_id}"

        # Initialize if key is new
        if key not in metrics:
            metrics[key] = {
                "campaign_id": campaign_id,
                "ad_id": ad_id,
                "device": event.get("device"),
                "location": event.get("location"),
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "revenue": 0.0
            }


        # Update device and location for latest event
        metrics[key]["device"] = device
        metrics[key]["location"] = location

        # Count events
        if event_type == "impression":
            metrics[key]["impressions"] += 1
        elif event_type == "click":
            metrics[key]["clicks"] += 1
        elif event_type == "conversion":
            metrics[key]["conversions"] += 1
            metrics[key]["revenue"] += revenue

        impressions = metrics[key]["impressions"]
        clicks = metrics[key]["clicks"]
        conversions = metrics[key]["conversions"]
        ctr = (clicks / impressions) if impressions > 0 else 0.0
        cvr = (conversions / clicks) if clicks > 0 else 0.0

        metrics[key]["ctr"] = round(ctr, 4)
        metrics[key]["cvr"] = round(cvr, 4)

        # CTR calculation

        # Upsert into MongoDB
        collection.update_one(
            {"campaign_id": campaign_id, "ad_id": ad_id},
            {"$set": metrics[key]},
            upsert=True
        )

        print(f"📊 Updated metrics for {key}: {metrics[key]}")

except KeyboardInterrupt:
    print("\n🛑 Stopped Kafka consumer.")
finally:
    consumer.close()
    client.close()
