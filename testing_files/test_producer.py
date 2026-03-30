import json
import time
from kafka import KafkaProducer

# Simple test producer without external dependencies
producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Test Producer Started...")
print("Sending 5 test messages to events_raw topic...\n")

for i in range(5):
    test_data = {
        "id": i,
        "message": f"Test message {i+1}",
        "timestamp": time.time(),
        "value": 100 + i
    }
    
    print(f"Sending: {test_data}")
    future = producer.send("events_raw", test_data)
    result = future.get(timeout=10)
    print(f"✓ Sent to partition: {result.partition}, offset: {result.offset}\n")
    time.sleep(0.5)

producer.close()
print("All messages sent!")
