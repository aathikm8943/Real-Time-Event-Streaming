# Kafka Producer-Consumer Issue - Resolution Guide

## Problem Statement

The Kafka consumer was not receiving any data despite the producer successfully sending messages to the `events_raw` topic. Messages were confirmed as sent (visible in logs with partition and offset info), but the consumer would hang indefinitely when attempting to read from the topic.

### Symptoms
- ✗ Producer sends messages successfully with confirmed partition/offset
- ✗ Consumer hangs or times out when trying to read messages
- ✗ No errors in consumer logs — just silent failure
- ✗ Kafka broker logs show repeated warnings about topic creation failures

---

## Root Cause Analysis

### The Core Issue
The Kafka broker was attempting to create the `__consumer_offsets` internal topic with a **replication factor of 3**, but only **1 broker** was running in the single-node cluster.

### Why This Breaks Consumers
1. Consumer groups require the `__consumer_offsets` system topic to track consumption progress
2. When this topic fails to create, consumer groups cannot be initialized
3. Consumers attempting to join a group hang indefinitely waiting for the group coordinator
4. The broker logs show this failure repeatedly:

```
WARN Auto topic creation failed for __consumer_offsets with error 'INVALID_REPLICATION_FACTOR': 
Unable to replicate the partition 3 time(s): The target replication factor of 3 cannot be 
reached because only 1 broker(s) are registered.
```

### Related Configurations
The issue also affected transaction state topics:
- `__transaction_state` topic also tried to use replication-factor 3

---

## Solution Applied

### Changes Made to `docker-compose.yml`

Added the following environment variables to the Kafka service to configure replication for single-node clusters:

```yaml
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: "1"
KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS: "1"
KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: "1"
KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: "1"
```

### What Each Setting Does

| Variable | Purpose |
|----------|---------|
| `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR` | Sets replication factor for `__consumer_offsets` system topic |
| `KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS` | Number of partitions for consumer offsets topic |
| `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR` | Minimum in-sync replicas for transaction state logs |
| `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR` | Replication factor for `__transaction_state` topic |

### Container Restart Required
Because the configuration is read at broker startup, containers must be completely rebuilt:

```bash
docker-compose down
docker-compose up -d
```

---

## Verification & Testing

### Test Files Created

#### 1. `test_producer.py` - Simple Test Producer
Sends 5 test messages to the `events_raw` topic without external dependencies.

**Run:**
```bash
python test_producer.py
```

**Expected Output:**
```
Test Producer Started...
Sending 5 test messages to events_raw topic...

Sending: {'id': 0, 'message': 'Test message 1', 'timestamp': 1774852433.47, 'value': 100}
✓ Sent to partition: 0, offset: 0
...
All messages sent!
```

#### 2. `test_consumer.py` - Simple Test Consumer
Reads messages from the `events_raw` topic in a consumer group.

**Run:**
```bash
python test_consumer.py
```

**Expected Output:**
```
Kafka Consumer Started...
Listening for messages on events_raw topic...

✓ Message 1:
  Partition: 0, Offset: 0
  Data: {'id': 0, 'message': 'Test message 1', 'timestamp': 1774852433.47, 'value': 100}
...
Total messages received: 5
```

### Test Results

✅ **Before Fix:**
- Producer: ✓ Works (messages confirmed sent)
- Consumer: ✗ Hangs indefinitely
- Broker logs: `__consumer_offsets` creation repeatedly fails

✅ **After Fix:**
- Producer: ✓ Works (messages confirmed)
- Consumer: ✓ Successfully receives all messages
- Broker logs: No replication errors

---

## Key Configuration Points

### For Single-Node Clusters
Always set replication factors to 1:

```yaml
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: "1"
KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: "1"
```

### For Multi-Node Clusters
You can use higher replication factors (e.g., 3):

```yaml
KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: "3"
KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: "3"
```

### Related Bootstrap Settings
The original configuration uses two listeners for flexibility:

| Listener | Use Case | Address |
|----------|----------|---------|
| INTERNAL | Container-to-container (Kafka-to-Spark) | `kafka:9092` |
| EXTERNAL | Host machine (Python producer/consumer) | `localhost:29092` |

Both work correctly after this fix; the issue was never about listener configuration.

---

## Files Modified

- **[docker-compose.yml](./docker-compose.yml)** 
  - Added 4 new replication factor environment variables to Kafka service
  - Ensures `__consumer_offsets` and `__transaction_state` topics use replication factor 1

## Files Created (for Testing)

- **[test_producer.py](./test_producer.py)**
  - Simple test producer without external data dependencies
  - Sends 5 JSON messages to `events_raw` topic

- **[test_consumer.py](./test_consumer.py)**
  - Simple test consumer with consumer group
  - Reads 5 messages from beginning of topic

---

## Lessons Learned

1. **System Topic Failures Are Silent** - Consumer group creation failures don't always produce obvious errors; consumers just hang
2. **Replication Factor Must Match Broker Count** - Single-node clusters cannot replicate topics across 3+ brokers
3. **Kafka Configuration Changes Require Restart** - YAML changes only apply when containers are rebuilt
4. **Check Broker Logs First** - `docker logs kafka` shows replication warnings that explain the root cause

---

## Troubleshooting Guide

### Consumer Still Hangs After Fix

1. **Verify container restart:**
   ```bash
   docker-compose down && docker-compose up -d
   ```

2. **Check the environment variables:** 
   ```bash
   docker inspect kafka | grep -i "REPLICATION_FACTOR"
   ```

3. **Check broker logs:**
   ```bash
   docker logs kafka | grep -i "replication\|offsets"
   ```

### Producer Fails to Connect

1. **Verify Kafka is running:**
   ```bash
   docker ps | grep kafka
   ```

2. **Check port binding:**
   ```bash
   docker port kafka
   # Should show: 29092/tcp -> 0.0.0.0:29092
   ```

3. **Verify bootstrap server address:**
   - For host machine: `localhost:29092` (EXTERNAL listener)
   - For containers: `kafka:9092` (INTERNAL listener)

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Producer | ✓ Works | ✓ Works |
| Consumer | ✗ Hangs | ✓ Works |
| `__consumer_offsets` | ✗ Creation fails | ✓ Created successfully |
| Root Cause | Replication factor mismatch | Fixed with factor=1 |
| Messages Stored | ✓ Yes (but unretrievable) | ✓ Yes (retrievable) |

The issue is now resolved. Both producer and consumer work seamlessly with the updated Kafka configuration.
