package com.shaktisafe.gateway.service;

import com.shaktisafe.gateway.model.FraudAlert;
import com.shaktisafe.gateway.model.Transaction;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * Core business logic:
 *  1. Stamp transaction with ingest time
 *  2. Publish to Kafka transactions.raw
 *  3. Proxy to ML Engine for synchronous risk score (optional fast path)
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TransactionService {

    private final KafkaTemplate<String, Transaction> kafkaTemplate;
    private final WebClient mlEngineWebClient;

    @Value("${kafka.topics.transactions}")
    private String transactionsTopic;

    @Value("${kafka.topics.alerts}")
    private String alertsTopic;

    // ── Ingest ─────────────────────────────────────────────────────────────────

    public Transaction ingest(Transaction tx) {
        // Stamp
        if (tx.getTransactionId() == null || tx.getTransactionId().isBlank()) {
            tx.setTransactionId("TXN-" + UUID.randomUUID());
        }
        if (tx.getTimestampMs() == null) {
            tx.setTimestampMs(System.currentTimeMillis());
        }
        tx.setIngestedAt(Instant.now());

        // Publish to Kafka (fire-and-forget)
        CompletableFuture<SendResult<String, Transaction>> future =
                kafkaTemplate.send(transactionsTopic, tx.getTransactionId(), tx).toCompletableFuture();

        future.whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("[Kafka] Failed to publish txn {}: {}", tx.getTransactionId(), ex.getMessage());
            } else {
                log.debug("[Kafka] Published txn {} to partition {}",
                        tx.getTransactionId(),
                        result.getRecordMetadata().partition());
            }
        });

        return tx;
    }

    // ── ML Engine proxy ────────────────────────────────────────────────────────

    /**
     * Synchronous risk score from the Python ML Engine.
     * Returns the raw JSON response as a Map. Times out gracefully.
     */
    public Mono<Map> scoreTransaction(Transaction tx) {
        return mlEngineWebClient.post()
                .uri("/analyze")
                .bodyValue(tx)
                .retrieve()
                .bodyToMono(Map.class)
                .onErrorResume(e -> {
                    log.warn("[ML] Score request failed for {}: {}", tx.getTransactionId(), e.getMessage());
                    return Mono.just(Map.of(
                            "transaction_id", tx.getTransactionId(),
                            "error", "ml_engine_unavailable",
                            "score", 0.0
                    ));
                });
    }

    // ── Stats proxy ────────────────────────────────────────────────────────────

    public Mono<Map> getStats() {
        return mlEngineWebClient.get()
                .uri("/stats")
                .retrieve()
                .bodyToMono(Map.class)
                .onErrorResume(e -> Mono.just(Map.of("error", "ml_engine_unavailable")));
    }

    public Mono<Map> getGraph() {
        return mlEngineWebClient.get()
                .uri("/graph")
                .retrieve()
                .bodyToMono(Map.class)
                .onErrorResume(e -> Mono.just(Map.of("error", "ml_engine_unavailable")));
    }

    public Mono<List> getAlerts() {
        return mlEngineWebClient.get()
                .uri("/alerts")
                .retrieve()
                .bodyToMono(List.class)
                .onErrorResume(e -> Mono.just(List.of()));
    }

    public Mono<List> getAccounts() {
        return mlEngineWebClient.get()
                .uri("/accounts")
                .retrieve()
                .bodyToMono(List.class)
                .onErrorResume(e -> Mono.just(List.of()));
    }
}
