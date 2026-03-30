from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'events_raw1',
    bootstrap_servers=['localhost:29092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='test-group'
)

print("Kafka Consumer Started...")
print("Listening for messages on events_raw topic...\n")

message_count = 0
for message in consumer:
    message_count += 1
    print(f"✓ Message {message_count}:")
    print(f"  Partition: {message.partition}, Offset: {message.offset}")
    print(f"  Data: {message.value}\n")
    
    if message_count >= 5:
        break

consumer.close()
print(f"Total messages received: {message_count}")
