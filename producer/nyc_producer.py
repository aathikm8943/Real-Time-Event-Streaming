import pandas as pd
import s3fs
from kafka import KafkaProducer, future
import json
import time

# -----------------------------
# MinIO Config
# -----------------------------
S3_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password"
BUCKET = "warehouse"
FILE_PATH = "fhvhv_tripdata_2026-01.parquet"  # adjust path if inside folder

s3_path = f"s3://{BUCKET}/{FILE_PATH}"

df = pd.read_parquet(
    s3_path,
    storage_options={
        "key": ACCESS_KEY,
        "secret": SECRET_KEY,
        "client_kwargs": {"endpoint_url": S3_ENDPOINT},
    },
)

print("Loaded rows:", len(df))

processing_df = df[:10000]  # limit to 10000 rows for testing
print("Processing rows:", len(processing_df))

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    # bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Starting to stream data to Kafka...")
print("Press Ctrl+C to stop.")

# Stream row by row
for _, row in processing_df.iterrows():
    data = row.to_dict()

    print("Original data:", data)  # Debug: print original data types
    # Convert timestamps (important!)
    for k, v in data.items():
        if hasattr(v, 'isoformat'):
            data[k] = v.isoformat()

    future = producer.send("events_raw1", data)
    print("Sent:", data)
    result = future.get(timeout=10)
    print("Sent to partition:", result.partition)

    time.sleep(0.1)  # simulate streaming