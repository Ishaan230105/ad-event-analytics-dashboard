from kafka import KafkaProducer
from faker import Faker
import json
import random
import time

fake = Faker()
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

devices = ['mobile', 'desktop', 'tablet']
locations = ['India', 'USA', 'Germany', 'UK', 'Canada']

def generate_event():
    event_type = random.choices(
        ['impression', 'click', 'conversion'],
        weights=[0.7, 0.25, 0.05],  # More impressions
        k=1
    )[0]

    # Revenue only for conversions
    if event_type == 'conversion':
        revenue = round(random.uniform(0.50, 5.00), 2)
    else:
        revenue = 0.0

    return {
        "ad_id": f"ad_{random.randint(1, 5)}",
        "user_id": fake.uuid4(),
        "event_type": event_type,
        "device": random.choice(devices),
        "location": random.choice(locations),
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "revenue": revenue,
        "campaign_id": "campaign_1"
    }

while True:
    event = generate_event()
    producer.send('ad_events', event)
    print(f"Produced: {event}")
    time.sleep(1)
