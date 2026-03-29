# -----------------------------
# VARIABLES
# -----------------------------
KAFKA_CONTAINER=kafka
KAFKA_BIN=/opt/kafka/bin
TOPIC=test-topic

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
	$(DOCKER_EXEC) $(KAFKA_BIN)/kafka-topics.sh \
	--create \ 
	--topic $(TOPIC) \
	--bootstrap-server kafka:9092 \
	--partitions 3 \
	--replication-factor 1

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