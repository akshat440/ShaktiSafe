package com.shaktisafe.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Canonical transaction payload — matches the Python ML Engine schema exactly.
 * All 32 GNN feature fields are derived from this object.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {

    @NotBlank
    @JsonProperty("transaction_id")
    private String transactionId;

    @NotBlank
    @JsonProperty("sender_id")
    private String senderId;

    @NotBlank
    @JsonProperty("receiver_id")
    private String receiverId;

    @NotNull
    @Positive
    private Double amount;

    /** UPI, NEFT, RTGS, IMPS, WALLET, ATM */
    private String channel;

    /** ISO-4217 currency code, default INR */
    @Builder.Default
    private String currency = "INR";

    /** ISO-3166-1 alpha-2 */
    @JsonProperty("sender_country")
    @Builder.Default
    private String senderCountry = "IN";

    @JsonProperty("receiver_country")
    @Builder.Default
    private String receiverCountry = "IN";

    /** Unix epoch ms — defaults to now if omitted */
    @JsonProperty("timestamp_ms")
    private Long timestampMs;

    /** Optional device fingerprint hash */
    @JsonProperty("device_id")
    private String deviceId;

    /** Optional merchant category code */
    private String mcc;

    /** Populated by the gateway on ingest */
    @JsonProperty("ingested_at")
    private Instant ingestedAt;
}
