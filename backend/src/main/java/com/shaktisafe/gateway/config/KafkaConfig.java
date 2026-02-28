package com.shaktisafe.gateway.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

/**
 * Kafka topic definitions — auto-created on startup.
 */
@Configuration
public class KafkaConfig {

    @Value("${kafka.topics.transactions}")
    private String transactionsTopic;

    @Value("${kafka.topics.alerts}")
    private String alertsTopic;

    @Value("${kafka.topics.str-reports}")
    private String strReportsTopic;

    @Bean
    public NewTopic transactionsRawTopic() {
        return TopicBuilder.name(transactionsTopic)
                .partitions(6)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic fraudAlertsTopic() {
        return TopicBuilder.name(alertsTopic)
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic strReportsTopic() {
        return TopicBuilder.name(strReportsTopic)
                .partitions(1)
                .replicas(1)
                .build();
    }
}
