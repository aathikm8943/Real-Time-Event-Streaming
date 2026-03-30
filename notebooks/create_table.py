from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CreateIcebergTable") \
    .getOrCreate()
    
spark.sql("CREATE NAMESPACE IF NOT EXISTS rest_backend.default")

spark.sql("""
CREATE TABLE IF NOT EXISTS rest_backend.default.taxi_trips (
    hvfhs_license_num STRING,
    dispatching_base_num STRING,
    originating_base_num STRING,

    request_datetime STRING,
    on_scene_datetime STRING,
    pickup_datetime STRING,
    dropoff_datetime STRING,

    PULocationID INT,
    DOLocationID INT,

    trip_miles DOUBLE,
    trip_time INT,

    base_passenger_fare DOUBLE,
    tolls DOUBLE,
    bcf DOUBLE,
    sales_tax DOUBLE,
    congestion_surcharge DOUBLE,
    airport_fee DOUBLE,
    tips DOUBLE,
    driver_pay DOUBLE,
    cbd_congestion_fee DOUBLE,

    shared_request_flag STRING,
    shared_match_flag STRING,
    access_a_ride_flag STRING,
    wav_request_flag STRING,
    wav_match_flag STRING
)
USING iceberg
""")

print("✅ Iceberg table created successfully")

spark.stop()