package com.learnia.gateway.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.List;

@Component
public class ApiKeyGlobalFilter implements GlobalFilter, Ordered {

    private static final Logger log = LoggerFactory.getLogger(ApiKeyGlobalFilter.class);
    private static final String API_KEY_HEADER = "X-API-Key";

    // Paths that bypass API key enforcement
    private static final List<String> EXCLUDED_PREFIXES = List.of(
            "/api/v1/auth/",
            "/actuator/",
            "/eureka/"
    );

    private final WebClient authClient;

    public ApiKeyGlobalFilter(WebClient.Builder webClientBuilder,
                              @Value("${auth.service.url:http://auth-service:8081}") String authServiceUrl) {
        this.authClient = webClientBuilder
                .baseUrl(authServiceUrl)
                .build();
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getPath().value();

        if (EXCLUDED_PREFIXES.stream().anyMatch(path::startsWith)) {
            return chain.filter(exchange);
        }

        String apiKey = exchange.getRequest().getHeaders().getFirst(API_KEY_HEADER);

        if (apiKey == null || apiKey.isBlank()) {
            log.debug("Rejected request to {} — missing X-API-Key", path);
            return reject(exchange, "Missing X-API-Key header");
        }

        return authClient.get()
                .uri("/api/v1/auth/validate")
                .header(API_KEY_HEADER, apiKey)
                .exchangeToMono(response -> {
                    if (response.statusCode().is2xxSuccessful()) {
                        return chain.filter(exchange);
                    }
                    log.debug("Rejected request to {} — invalid API key", path);
                    return reject(exchange, "Invalid or inactive API key");
                })
                .onErrorResume(ex -> {
                    log.warn("Auth service unavailable: {}", ex.getMessage());
                    return reject(exchange, "Authentication service unavailable");
                });
    }

    private Mono<Void> reject(ServerWebExchange exchange, String message) {
        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);
        byte[] body = ("{\"error\":\"" + message + "\"}").getBytes(StandardCharsets.UTF_8);
        DataBuffer buffer = exchange.getResponse().bufferFactory().wrap(body);
        return exchange.getResponse().writeWith(Mono.just(buffer));
    }

    @Override
    public int getOrder() {
        return -100;
    }
}
