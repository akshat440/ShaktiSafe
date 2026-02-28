package com.shaktisafe.gateway.controller;

import com.shaktisafe.gateway.model.Transaction;
import com.shaktisafe.gateway.service.TransactionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;

/**
 * IntelliTrace REST API — all routes prefixed /api/v1
 *
 * POST /api/v1/transactions          Ingest a single transaction
 * POST /api/v1/transactions/batch    Ingest a batch (up to 500)
 * POST /api/v1/transactions/analyze  Ingest + synchronous ML score
 * GET  /api/v1/stats                 Dashboard stats
 * GET  /api/v1/graph                 Transaction graph for D3 viz
 * GET  /api/v1/alerts                Recent fraud alerts
 * GET  /api/v1/accounts              Account risk scores
 * GET  /api/v1/health                Liveness check
 */
@Slf4j
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService txService;

    // ── Ingest ─────────────────────────────────────────────────────────────────

    @PostMapping("/transactions")
    public ResponseEntity<Transaction> ingest(@Valid @RequestBody Transaction tx) {
        log.info("[Gateway] Ingesting txn {} ₹{}", tx.getTransactionId(), tx.getAmount());
        Transaction stamped = txService.ingest(tx);
        return ResponseEntity.accepted().body(stamped);
    }

    @PostMapping("/transactions/batch")
    public ResponseEntity<Map<String, Object>> ingestBatch(
            @RequestBody List<@Valid Transaction> transactions) {

        if (transactions.size() > 500) {
            return ResponseEntity.badRequest()
                    .body(Map.of("error", "Batch size cannot exceed 500"));
        }

        int ingested = 0;
        for (Transaction tx : transactions) {
            txService.ingest(tx);
            ingested++;
        }

        log.info("[Gateway] Batch ingested {} transactions", ingested);
        return ResponseEntity.accepted()
                .body(Map.of("ingested", ingested, "status", "queued"));
    }

    @PostMapping("/transactions/analyze")
    public Mono<ResponseEntity<Map>> analyzeTransaction(@Valid @RequestBody Transaction tx) {
        txService.ingest(tx);
        return txService.scoreTransaction(tx)
                .map(ResponseEntity::ok);
    }

    // ── Dashboard proxies ──────────────────────────────────────────────────────

    @GetMapping("/stats")
    public Mono<ResponseEntity<Map>> getStats() {
        return txService.getStats().map(ResponseEntity::ok);
    }

    @GetMapping("/graph")
    public Mono<ResponseEntity<Map>> getGraph() {
        return txService.getGraph().map(ResponseEntity::ok);
    }

    @GetMapping("/alerts")
    public Mono<ResponseEntity<List>> getAlerts() {
        return txService.getAlerts().map(ResponseEntity::ok);
    }

    @GetMapping("/accounts")
    public Mono<ResponseEntity<List>> getAccounts() {
        return txService.getAccounts().map(ResponseEntity::ok);
    }

    // ── Health ─────────────────────────────────────────────────────────────────

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "intellitrace-gateway"
        ));
    }
}
