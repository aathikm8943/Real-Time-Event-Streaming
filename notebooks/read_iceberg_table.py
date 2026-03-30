from pyspark.sql import SparkSession

# ----------------------------------------
# 1. Create Spark Session with Iceberg config
# ----------------------------------------
spark = SparkSession.builder \
    .appName("ReadIcebergTable") \
    .config("spark.sql.catalog.rest_backend", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.rest_backend.type", "rest") \
    .config("spark.sql.catalog.rest_backend.uri", "http://localhost:8181") \
    .config("spark.sql.catalog.rest_backend.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
    .getOrCreate()

# ----------------------------------------
# 2. Check catalogs
# ----------------------------------------
print("=== Available Catalogs ===")
spark.sql("SHOW CATALOGS").show(truncate=False)

# ----------------------------------------
# 3. Check namespaces (databases)
# ----------------------------------------
print("=== Namespaces ===")
spark.sql("SHOW NAMESPACES IN rest_backend").show(truncate=False)

# ----------------------------------------
# 4. Check tables
# ----------------------------------------
print("=== Tables ===")
spark.sql("SHOW TABLES IN rest_backend.default").show(truncate=False)

# ----------------------------------------
# 5. Read full table (BATCH)
# ----------------------------------------
print("=== Sample Data ===")
df = spark.sql("SELECT * FROM rest_backend.default.taxi_trips")
df.show(10, truncate=False)

# ----------------------------------------
# 6. Count records
# ----------------------------------------
print("=== Row Count ===")
spark.sql("SELECT COUNT(*) FROM rest_backend.default.taxi_trips").show()

# ----------------------------------------
# 7. Show schema
# ----------------------------------------
print("=== Schema ===")
df.printSchema()

# ----------------------------------------
# 8. Optional: Filtered query
# ----------------------------------------
print("=== Filtered Data (example) ===")
spark.sql("""
SELECT *
FROM rest_backend.default.taxi_trips
WHERE trip_distance > 5
LIMIT 10
""").show()

# ----------------------------------------
# 9. Optional: Iceberg metadata
# ----------------------------------------
print("=== Snapshots ===")
spark.sql("SELECT * FROM rest_backend.default.taxi_trips.snapshots").show(truncate=False)

# ----------------------------------------
# Stop Spark
# ----------------------------------------
spark.stop()