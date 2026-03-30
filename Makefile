# -----------------------------
# VARIABLES
# -----------------------------
KAFKA_CONTAINER=kafka
KAFKA_BIN=/opt/kafka/bin
TOPIC=test-topic
PYTHON_BIN=.venv/Scripts/python.exe

# Disable Git Bash path conversion
DOCKER_EXEC=MSYS_NO_PATHCONV=1 docker exec -it $(KAFKA_CONTAINER)

# -----------------------------
# KAFKA COMMANDS
# -----------------------------
kafka-shell:
	$(DOCKER_EXEC) bash

list-topics:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-topics.sh \
	--list \
	--bootstrap-server kafka:9092

create-topic:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-topics.sh --create --topic $(TOPIC) --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1

delete-topic:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-topics.sh \
	--delete \
	--topic $(TOPIC) \
	--bootstrap-server kafka:9092

produce:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-console-producer.sh \
	--topic $(TOPIC) \
	--bootstrap-server kafka:9092

consume:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-console-consumer.sh \
	--topic $(TOPIC) \
	--from-beginning \
	--bootstrap-server kafka:9092

consume-live:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-console-consumer.sh \
	--topic $(TOPIC) \
	--bootstrap-server kafka:9092

local-consume-live:
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-console-consumer.sh \
	--topic $(TOPIC) \
	--bootstrap-server localhost:29092
# -----------------------------
# DOCKER
# -----------------------------
up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

# -----------------------------
# SPARK
# -----------------------------
spark-shell:
	docker exec -it $(SPARK_CONTAINER) pyspark

spark-bash:
	docker exec -it $(SPARK_CONTAINER) bash

run-job:
	docker exec -it $(SPARK_CONTAINER) spark-submit /home/iceberg/jobs/kafka_to_iceberg.py

# -----------------------------
# PRODUCER (LOCAL PYTHON)
# -----------------------------
run-producer:
	python producer/producer.py

# LOCAL EXECUTION (Host Machine)
# Connects to Kafka via localhost:29092 (EXTERNAL listener)
# Useful for testing producer/consumer locally
# -----------------------------
local-producer:
	$(PYTHON_BIN) producer/nyc_producer.py

local-consumer:
	$(PYTHON_BIN) testing_files/test_consumer.py

local-test-producer:
	$(PYTHON_BIN) testing_files/test_producer.py

local-test-consumer:
	$(PYTHON_BIN) testing_files/test_consumer.py

# CONTAINER EXECUTION (Inside Docker)
# Runs producer/consumer from within Kafka container
# Connects to Kafka via kafka:9092 (INTERNAL listener)
# Useful for production-like scenarios
# -----------------------------
container-producer:
	docker run --network streaming_project_iceberg_net -v $(PWD)/producer:/app/producer python:3.13 bash -c "pip install kafka-python pandas s3fs -q && python /app/producer/nyc_producer.py"

container-consumer:
	docker run --network streaming_project_iceberg_net python:3.13 bash -c "pip install kafka-python -q && python -c \"from kafka import KafkaConsumer; import json; c = KafkaConsumer('events_raw', bootstrap_servers=['kafka:9092'], auto_offset_reset='earliest', value_deserializer=lambda m: json.loads(m.decode('utf-8')), group_id='container-group'); [print(f'Message: {msg.value}') for i, msg in enumerate(c) if i < 5]; c.close()\""

container-test-producer:
	docker run --network streaming_project_iceberg_net -v $(PWD):/app python:3.13 bash -c "pip install kafka-python -q && python /app/test_producer.py"

container-test-consumer:
	docker run --network streaming_project_iceberg_net -v $(PWD):/app python:3.13 bash -c "pip install kafka-python -q && python /app/test_consumer.py"

# -----------------------------
# DEBUG
# -----------------------------
check-kafka:
	docker exec -it $(KAFKA_CONTAINER) bash

check-spark:
	docker exec -it $(SPARK_CONTAINER) bash

network:
	docker network ls

ps:
	docker ps

# QUICK REFERENCE
# =====================================================
# LOCAL EXECUTION (Host Machine via localhost:29092)
#   make local-producer          - Run NYC producer locally
#   make local-consumer          - Run consumer locally
#   make local-test-producer     - Send 5 test messages
#   make local-test-consumer     - Receive 5 test messages
#
# CONTAINER EXECUTION (Inside Docker via kafka:9092)
#   make container-producer      - Run NYC producer in container
#   make container-consumer      - Run consumer in container
#   make container-test-producer - Run test producer in container
#   make container-test-consumer - Run test consumer in container
#
# KAFKA OPERATIONS
#   make list-topics             - List all topics
#   make create-topic            - Create topic
#   make consume-live TOPIC=xxx  - Consume messages (docker)
# =====================================================