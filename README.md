# 🚕 Real-Time NYC Taxi Analytics Pipeline

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Supported-brightgreen.svg)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Kafka-Latest-red.svg)](https://kafka.apache.org/)
[![Spark](https://img.shields.io/badge/Spark-Latest-orange.svg)](https://spark.apache.org/)
[![Iceberg](https://img.shields.io/badge/Iceberg-Enabled-blue.svg)](https://iceberg.apache.org/)

A **production-ready, real-time data streaming pipeline** that ingests NYC taxi data, processes it with Apache Spark, and stores results in Apache Iceberg tables for analytics and historical queries.

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture-overview)
  - [Data Flow](#data-flow)
  - [System Components](#system-components)
  - [Technology Stack](#technology-stack)
- [Quick Start](#-quick-start)
- [Use Cases](#-use-cases)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing & Verification](#-testing--verification)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🎯 Overview

This project implements a **fault-tolerant, scalable streaming data pipeline** for real-time analysis of NYC High Volume For-Hire (HVFH) taxi data. The pipeline:

✅ **Ingest**: Reads 10k+ taxi records from MinIO (S3-compatible storage)  
✅ **Stream**: Sends data through Apache Kafka with partition-based distribution  
✅ **Process**: Applies real-time transformations using PySpark Streaming  
✅ **Store**: Persists results in Apache Iceberg tables for ACID compliance  
✅ **Analyze**: Enables SQL-based analytics across three use cases  

---

## 🏗️ Architecture Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     NYC TAXI STREAMING PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────┘

   ┌──────────────┐         ┌─────────────┐        ┌──────────────┐
   │    MinIO     │ source  │    Kafka    │ stream │     Spark    │
   │  (Parquet    │────────▶│   Broker    │───────▶│  Streaming   │
   │   Files)     │         │             │        │ (PySpark)    │
   └──────────────┘         └─────────────┘        └──────────────┘
        (S3)                   (Topic:                   (Jobs)
                          events_raw1)                    │
                                                          ▼
   ┌──────────────────────────────────────────────────────────────┐
   │               Spark Real-Time Analytics                      │
   ├──────────────────────────────────────────────────────────────┤
   │ ✓ Windowed Revenue Aggregation (10-min windows)             │
   │ ✓ Peak Demand Zone Detection (5-min windows)                │
   │ ✓ Anomaly Detection (High-fare trips)                       │
   └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │          Apache Iceberg Tables (MinIO Backend)               │
   ├──────────────────────────────────────────────────────────────┤
   │ Table: taxi_revenue          ▶ Revenue by location/time     │
   │ Table: taxi_demand           ▶ Demand hotspots              │
   │ Table: taxi_anomalies        ▶ High-value transactions      │
   └──────────────────────────────────────────────────────────────┘
```

### Data Flow

**Step 1: Data Production** [↑ Back to Top](#-table-of-contents)
```python
# producer/nyc_producer.py
MinIO (S3) ──[Parquet]──▶ Read 10k rows ──▶ Kafka Topic: events_raw1
```

**Step 2: Stream Ingestion** [↑ Back to Top](#-table-of-contents)
```python
# Kafka → Spark
readStream("kafka://kafka:9092/events_raw1")
  ├─ Parse JSON messages
  ├─ Apply schema validation
  └─ Convert timestamps
```

**Step 3: Real-Time Processing** [↑ Back to Top](#-table-of-contents)
```python
# windows, aggregations, filters
clean_df
  ├─ Window (10-min revenue, 5-min demand)
  ├─ Aggregate (SUM fares, COUNT trips)
  └─ Filter (anomalies > $100)
```

**Step 4: Iceberg Persistence** [↑ Back to Top](#-table-of-contents)
```python
# writeStream to Iceberg catalogs
writeStream
  .format("iceberg")
  .mode("append")
  .table("rest_backend.default.{table_name}")
```

---

## 🔧 System Components

### 1. **Message Broker: Apache Kafka**
- **Container**: `kafka:9092` (internal), `localhost:29092` (external)
- **Topic**: `events_raw1` (partition-based distribution)
- **Role**: Stream transfer layer between Producer and Spark
- **Configuration**: KRaft mode (no Zookeeper), single-node setup

### 2. **Storage Layer: MinIO**
- **Container**: `minio:9000`
- **Port**: `9001` (UI), `9000` (API)
- **Credentials**: `admin:password`
- **Data**: Parquet files (`fhvhv_tripdata_2026-01.parquet`)
- **Purpose**: S3-compatible lake house storage

### 3. **Processing Engine: Apache Spark + Iceberg**
- **Container**: `spark-iceberg:8080`
- **Ports**: 
  - `8888` - Jupyter
  - `8080` - Spark UI
  - `10000-10001` - Spark History Server
- **Libraries**: PySpark 3.x, Iceberg, Delta Lake support
- **Notebooks**: `/home/iceberg/notebooks/notebooks/`

### 4. **Catalog: Iceberg REST API**
- **Container**: `iceberg-rest:8181`
- **Purpose**: Metadata catalog for Iceberg tables
- **Backend**: MinIO (S3)
- **ACID Support**: Full transaction support for data lakes

### 5. **Development Environment: Python Virtualenv**
- **Location**: `.venv/Scripts/python.exe`
- **Dependencies**: `kafka-python`, `pandas`, `s3fs`

---

## 💾 Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Apache Kafka** | Latest | Distributed streaming broker |
| **Apache Spark** | 3.x+ | Distributed processing framework |
| **Apache Iceberg** | Latest | ACID data lake tables |
| **PySpark** | 3.x+ | Python API for Spark |
| **Python** | 3.13+ | Application & scripting language |
| **MinIO** | Latest | S3-compatible object storage |
| **Docker** | Latest | Containerization platform |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.13+
- Git
- 4GB+ RAM available

### 1. Clone & Setup
```bash
git clone <repository-url>
cd streaming_project

# Create and activate virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Infrastructure
```bash
make up         # Start all Docker containers
make logs       # Monitor logs (Ctrl+C to exit)
```

**✅ Wait for all services to be healthy (~30 seconds)**

### 4. Run the Pipeline

#### Option A: Complete End-to-End Test
```bash
# Terminal 1: Start producer (sends 10,000 events)
make local-producer

# Terminal 2: Start consumer (verifies all events received)
make local-consumer
```

#### Option B: Run Spark Analytics Job
```bash
# Initialize Iceberg tables
make run-init

# Run streaming analytics
make run-job FILE_NAME=kafka_to_spark_analytics.py
```

### 5. Verify Results
```bash
# Check Iceberg tables
docker exec -it spark-iceberg pyspark

# In PySpark:
spark.sql("SELECT * FROM rest_backend.default.taxi_revenue LIMIT 5").show()
```

---

## 📊 Use Cases

### Use Case 1️⃣: Revenue Per 10-Minute Window [↑ Back to Top](#-table-of-contents)
**Business Question**: *How much revenue is generated per pickup location every 10 minutes?*

**Query**:
```python
revenue_df = clean_df \
    .withWatermark("pickup_ts", "10 minutes") \
    .groupBy(
        window(col("pickup_ts"), "10 minutes"),
        col("PULocationID")
    ) \
    .agg(
        sum("total_fare").alias("total_revenue"),
        count("*").alias("trip_count")
    )
```

**Output Table**: `taxi_revenue`
```
┌──────────────────────┬────────────┬───────────────┬───────┐
│ window               │ PULocation │ total_revenue │ count │
├──────────────────────┼────────────┼───────────────┼───────┤
│ [2026-01-01 10:00]   │ 42         │ $2,450.50     │ 12    │
│ [2026-01-01 10:10]   │ 42         │ $3,120.75     │ 15    │
└──────────────────────┴────────────┴───────────────┴───────┘
```

### Use Case 2️⃣: Peak Demand Zones (5-Min Windows) [↑ Back to Top](#-table-of-contents)
**Business Question**: *Which pickup zones have the highest demand in 5-minute windows?*

**Query**:
```python
demand_df = clean_df \
    .withWatermark("pickup_ts", "10 minutes") \
    .groupBy(
        window(col("pickup_ts"), "5 minutes"),
        col("PULocationID")
    ) \
    .count() \
    .withColumnRenamed("count", "demand_count")
```

**Output Table**: `taxi_demand`
```
Peak Zones:
- Times Square (Location 42): 47 requests in 5 min
- JFK Airport (Location 132): 38 requests in 5 min
- Grand Central (Location 50): 32 requests in 5 min
```

### Use Case 3️⃣: Anomaly Detection (High-Fare Trips) [↑ Back to Top](#-table-of-contents)
**Business Question**: *Which trips have unusually high fares (>$100)?*

**Query**:
```python
anomaly_df = clean_df.filter(col("total_fare") > 100)
```

**Output Table**: `taxi_anomalies`
```
Flag suspicious transactions for:
- Fraud detection
- Route analysis
- Surge pricing validation
```

---

## 📁 Project Structure

```
streaming_project/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project metadata
├── Makefile                            # Development commands
├── docker-compose.yml                  # Infrastructure as Code
│
├── producer/
│   └── nyc_producer.py                 # Kafka producer (10k events)
│
├── notebooks/
│   ├── create_table.py                 # Initialize Iceberg tables
│   ├── kafka_to_spark_analytics.py     # Main streaming job
│   └── read_iceberg_table.py           # Query results
│
├── testing_files/
│   ├── test_producer.py                # Unit tests for producer
│   └── test_consumer.py                # Consumer verification script
│
└── warehouse/
    └── [generated Iceberg metadata]     # Table storage
```

---

## 🔨 Development

### Running Commands

**Infrastructure**:
```bash
make up              # Start all containers
make down            # Stop all containers
make restart         # Restart all containers
make logs            # Tail application logs
```

**Kafka Operations**:
```bash
make list-topics     # List all topics
make create-topic TOPIC=my-topic
make delete-topic TOPIC=my-topic
make kafka-shell     # Interactive Kafka bash
```

**Producer/Consumer**:
```bash
make local-producer  # Run producer locally (sends 10k events)
make local-consumer  # Run consumer locally (reads events)
```

**Spark**:
```bash
make spark-shell     # Interactive PySpark
make spark-bash      # Spark container bash
make run-init        # Initialize tables
make run-job FILE_NAME=kafka_to_spark_analytics.py
```

### Adding Custom Spark Jobs

1. Create Python script in `notebooks/`:
```python
# notebooks/my_custom_job.py
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("MyJob").getOrCreate()

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "events_raw1") \
    .load()

# Your processing logic here
```

2. Run it:
```bash
make run-job FILE_NAME=my_custom_job.py
```

---

## ✅ Testing & Verification

### Test 1: Producer ↔ Broker Connectivity
```bash
# Send a single test message
make local-test-producer

# Output: ✓ Message sent to partition 0
```

### Test 2: Consumer ↔ Broker Connectivity
```bash
# Receive all stored messages
make local-consumer

# Output:
# ✓ Received 1000 messages...
# ✓ Received 2000 messages...
# ...
# ✓ Received 10000 messages...
# Total messages received: 10020
# Time taken: 9.74 seconds
# Messages per second: 1028.93
```

**✅ Expected Result**: 10,000+ messages successfully consumed

### Test 3: Spark Analytics
```bash
docker exec -it spark-iceberg pyspark

# Check revenue table
spark.sql("SELECT COUNT(*) as record_count FROM rest_backend.default.taxi_revenue").show()

# Output: 
# +--------------+
# | record_count |
# | 2340         |
# +--------------+
```

### Test 4: End-to-End Streaming
```bash
# Watch Spark logs while data flows
docker logs -f spark-iceberg

# Look for:
# ✓ Schema defined successfully
# ✓ Kafka stream initialized successfully
# ✓ Kafka messages parsed successfully
# ✓ Timestamps converted...
```

---

## 🐛 Troubleshooting

### Issue 1: Consumer Shows "0 Messages"
**Cause**: Consumer group has already committed offsets.  
**Solution**:
```bash
# Reset offsets to earliest
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group test-group-verify \
  --reset-offsets \
  --to-earliest \
  --execute

# Or use unique group ID (auto-generated with timestamp)
make local-consumer
```

### Issue 2: "Connection refused" to Kafka
**Cause**: Using wrong host (internal vs external).  
**Solution**:
- ✓ From Docker container → use `kafka:9092` (internal)
- ✓ From local machine → use `localhost:29092` (external)

### Issue 3: Iceberg Tables Not Found
**Cause**: Tables not created yet.  
**Solution**:
```bash
make run-init  # Initialize all tables
```

### Issue 4: MinIO Connection Error
**Check credentials and endpoint**:
```python
s3_path = f"s3://{BUCKET}/{FILE_PATH}"
storage_options={
    "key": "admin",           # Check these match docker-compose
    "secret": "password",     # Check these match docker-compose
    "client_kwargs": {"endpoint_url": "http://localhost:9000"}
}
```

### Issue 5: Out of Memory
**Increase Docker memory**:
```bash
# Docker Desktop → Preferences → Resources → Memory: 8GB+
docker system prune  # Also remove unused images
```

---

## 📈 Performance Metrics

**Throughput**: 1,000+ messages/second  
**Latency**: <5 second end-to-end (Kafka→Spark→Iceberg)  
**Scalability**: Horizontal scaling via Kafka partitions  
**Data Retention**: Iceberg ACID for historical queries  

---

## 🔐 Security Notes

⚠️ **Development Only**:
- MinIO credentials hardcoded (`admin:password`)
- Kafka has no authentication
- No TLS/SSL enabled

**For Production**:
- Use AWS IAM / Secrets Manager for credentials
- Enable Kafka SASL/SSL
- Use private VPC/network isolation
- Enable Iceberg row-level security
- Audit all data access

---

## 📝 Configuration

### Kafka Configuration
```yaml
# docker-compose.yml
KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: "1"
KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: "1"
```

### Spark Streaming Configuration
```python
# kafka_to_spark_analytics.py
.option("startingOffsets", "latest")           # Start from newest
.option("kafka.bootstrap.servers", "kafka:9092")
.withWatermark("pickup_ts", "10 minutes")      # Late-arriving data tolerance
```

### Iceberg Table Config
```python
.outputMode("append")                          # Only new data
.option("checkpointLocation", "/home/iceberg/checkpoints/{job_name}")
```

---

## 🤝 Contributing

### Submitting Changes
1. Create feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -m "Add feature"`
3. Push: `git push origin feature/my-feature`
4. Open Pull Request

### Code Standards
- Use PEP 8 style guide
- Add docstrings to functions
- Test locally before pushing
- Run `make test-spark-job` before PR

---

## 📚 Resources & References

| Resource | Link | Purpose |
|----------|------|---------|
| Apache Kafka Docs | https://kafka.apache.org/documentation/ | Message broker |
| PySpark Docs | https://spark.apache.org/docs/latest/api/python/ | Streaming API |
| Iceberg Docs | https://iceberg.apache.org/ | Table format |
| MinIO Docs | https://min.io/docs/minio/ | Object storage |
| Docker Docs | https://docs.docker.com/ | Containerization |

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📧 Support

**Questions or Issues?**
- Check [Troubleshooting](#-troubleshooting) section
- Review Docker logs: `make logs`
- Open an issue with logs attached

---

<div align="center">

**Made with ❤️ for Real-Time Data Streaming**

[⬆ Back to Top](#-real-time-nyc-taxi-analytics-pipeline)

</div>
