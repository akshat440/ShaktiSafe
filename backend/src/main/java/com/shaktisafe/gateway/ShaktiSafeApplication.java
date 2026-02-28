package com.shaktisafe.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * IntelliTrace — Spring Boot API Gateway
 *
 * Responsibilities:
 *  - Accepts transaction ingestion via REST
 *  - Publishes to Kafka topic: transactions.raw
 *  - Proxies analysis requests to the Python ML Engine
 *  - Exposes /api/v1/** endpoints consumed by the Next.js dashboard
 */
@SpringBootApplication
@EnableAsync
@EnableScheduling
public class ShaktiSafeApplication {

    public static void main(String[] args) {
        SpringApplication.run(ShaktiSafeApplication.class, args);
    }
}
