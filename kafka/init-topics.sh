#!/bin/bash
# ── IntelliTrace Kafka Topic Initializer ──────────────────────────────────────
# Runs once after Kafka broker is ready to create all required topics.

set -e

KAFKA_BIN=/opt/bitnami/kafka/bin
BROKER=kafka:9092

echo "[Kafka Init] Waiting for broker at $BROKER ..."
until $KAFKA_BIN/kafka-broker-api-versions.sh --bootstrap-server $BROKER > /dev/null 2>&1; do
  sleep 3
done
echo "[Kafka Init] Broker ready."

create_topic() {
  local NAME=$1
  local PARTITIONS=$2
  local RETENTION_MS=$3

  if $KAFKA_BIN/kafka-topics.sh --bootstrap-server $BROKER --list | grep -q "^${NAME}$"; then
    echo "[Kafka Init] Topic '${NAME}' already exists — skipping."
  else
    $KAFKA_BIN/kafka-topics.sh \
      --bootstrap-server $BROKER \
      --create \
      --topic "$NAME" \
      --partitions "$PARTITIONS" \
      --replication-factor 1 \
      --config retention.ms="$RETENTION_MS"
    echo "[Kafka Init] Created topic '${NAME}' (partitions=${PARTITIONS})"
  fi
}

# Raw transaction stream — high throughput, 7 day retention
create_topic "transactions.raw"    6  604800000

# Fraud alert events — 30 day retention
create_topic "fraud.alerts"        3  2592000000

# STR report triggers — 90 day retention (compliance)
create_topic "str.reports"         1  7776000000

# Dead-letter queue
create_topic "transactions.dlq"    2  604800000

echo "[Kafka Init] All topics ready."
