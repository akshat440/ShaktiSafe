package com.shaktisafe.gateway.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;

@Configuration
public class WebClientConfig {

    @Value("${ml.engine.base-url}")
    private String mlEngineBaseUrl;

    @Value("${ml.engine.timeout-seconds:30}")
    private int timeoutSeconds;

    @Bean
    public WebClient mlEngineWebClient() {
        return WebClient.builder()
                .baseUrl(mlEngineBaseUrl)
                .defaultHeader("Content-Type", "application/json")
                .codecs(c -> c.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
    }
}
