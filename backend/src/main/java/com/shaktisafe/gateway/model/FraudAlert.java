package com.shaktisafe.gateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * Fraud alert emitted by the ML Engine and forwarded on the fraud.alerts topic.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FraudAlert {

    @JsonProperty("alert_id")
    private String alertId;

    /** MULE_RING | STRUCTURING | JURISDICTION | SANCTIONS | LAYERING */
    private String type;

    /** 0.0 – 1.0 */
    private Double score;

    /** LOW | MEDIUM | HIGH | CRITICAL */
    private String severity;

    @JsonProperty("transaction_ids")
    private List<String> transactionIds;

    @JsonProperty("account_ids")
    private List<String> accountIds;

    private String description;

    private Map<String, Object> metadata;

    @JsonProperty("created_at")
    private Instant createdAt;

    /** Whether an STR has been auto-filed with FIU-IND */
    @JsonProperty("str_filed")
    @Builder.Default
    private Boolean strFiled = false;
}
