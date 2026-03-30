from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("TaxiStreamingAnalytics") \
    .getOrCreate()

# -----------------------------
# Schema
# -----------------------------
schema = StructType() \
    .add("hvfhs_license_num", StringType()) \
    .add("dispatching_base_num", StringType()) \
    .add("originating_base_num", StringType()) \
    .add("request_datetime", StringType()) \
    .add("on_scene_datetime", StringType()) \
    .add("pickup_datetime", StringType()) \
    .add("dropoff_datetime", StringType()) \
    .add("PULocationID", IntegerType()) \
    .add("DOLocationID", IntegerType()) \
    .add("trip_miles", DoubleType()) \
    .add("trip_time", IntegerType()) \
    .add("base_passenger_fare", DoubleType()) \
    .add("tolls", DoubleType()) \
    .add("bcf", DoubleType()) \
    .add("sales_tax", DoubleType()) \
    .add("congestion_surcharge", DoubleType()) \
    .add("airport_fee", DoubleType()) \
    .add("tips", DoubleType()) \
    .add("driver_pay", DoubleType()) \
    .add("cbd_congestion_fee", DoubleType()) \
    .add("shared_request_flag", StringType()) \
    .add("shared_match_flag", StringType()) \
    .add("access_a_ride_flag", StringType()) \
    .add("wav_request_flag", StringType()) \
    .add("wav_match_flag", StringType())
    
print("✅ Schema defined successfully")

# -----------------------------
# Read from Kafka
# -----------------------------
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "events_raw1") \
    .option("startingOffsets", "latest") \
    .load()

print("✅ Kafka stream initialized successfully")
# -----------------------------
# Parse JSON
# -----------------------------
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

print("✅ Kafka messages parsed successfully")

print("-" * 100)
print(df.writeStream \
  .format("console") \
  .start())
print("-" * 100)
# -----------------------------
# Convert timestamps
# -----------------------------
clean_df = parsed_df \
    .withColumn("pickup_ts", to_timestamp("pickup_datetime")) \
    .withColumn("dropoff_ts", to_timestamp("dropoff_datetime")) \
    .withColumn("total_fare",
        col("base_passenger_fare") +
        col("tolls") +
        col("bcf") +
        col("sales_tax") +
        col("tips")
    )
print("✅ Timestamps converted and total fare calculated successfully")

# =========================================================
# 🚕 USE CASE 1 — Revenue per 10 min window
# =========================================================
print("Starting streaming queries for analytics...")
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

revenue_query = revenue_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "/home/iceberg/checkpoints/revenue") \
    .toTable("rest_backend.default.taxi_revenue")

# =========================================================
# 🚦 USE CASE 2 — Peak demand zones
# =========================================================
demand_df = clean_df \
    .withWatermark("pickup_ts", "10 minutes") \
    .groupBy(
        window(col("pickup_ts"), "5 minutes"),
        col("PULocationID")
    ) \
    .count() \
    .withColumnRenamed("count", "demand_count")

demand_query = demand_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "/home/iceberg/checkpoints/demand") \
    .toTable("rest_backend.default.taxi_demand")

# =========================================================
# ⚠️ USE CASE 3 — Anomaly detection (high fare trips)
# =========================================================
anomaly_df = clean_df \
    .filter(col("total_fare") > 100)

anomaly_query = anomaly_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .option("checkpointLocation", "/home/iceberg/checkpoints/anomaly") \
    .toTable("rest_backend.default.taxi_anomalies")

# =========================================================
# Debug (optional)
# =========================================================
console_query = clean_df.writeStream \
    .format("console") \
    .option("truncate", False) \
    .start()

spark.streams.awaitAnyTermination()