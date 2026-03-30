from kafka import KafkaConsumer
import json
from datetime import datetime

# Use unique group_id each run to read from earliest
group_id = f'test-group-{datetime.now().strftime("%Y%m%d_%H%M%S")}'

consumer = KafkaConsumer(
    'events_raw1',
    bootstrap_servers=['localhost:29092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id=group_id,
    consumer_timeout_ms=5000  # Stop after 5 seconds of no messages
)

print(f"Kafka Consumer Started... (Group ID: {group_id})")
print("Consuming all messages from events_raw1...\n")

message_count = 0
start_time = datetime.now()

try:
    for message in consumer:
        message_count += 1
        if message_count % 1000 == 0:  # Print progress every 1000 messages
            print(f"✓ Received {message_count} messages...")
except StopIteration:
    pass

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print(f"\n{'='*60}")
print(f"Total messages received: {message_count}")
print(f"Time taken: {duration:.2f} seconds")
if duration > 0:
    print(f"Messages per second: {message_count/duration:.2f}")
print(f"{'='*60}")

consumer.close()
