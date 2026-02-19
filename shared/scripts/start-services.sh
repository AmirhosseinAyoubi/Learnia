#!/bin/bash

docker-compose up -d


sleep 10

cd spring-boot-services


echo "Starting Eureka Server..."
mvn spring-boot:run -pl learnia-eureka-server > /tmp/eureka.log 2>&1 &
EUREKA_PID=$!

sleep 5

echo "Starting Config Server..."
mvn spring-boot:run -pl learnia-config-server > /tmp/config.log 2>&1 &
CONFIG_PID=$!

sleep 5

echo "Starting API Gateway..."
mvn spring-boot:run -pl learnia-gateway > /tmp/gateway.log 2>&1 &
GATEWAY_PID=$!

sleep 5

echo "Starting Auth Service..."
mvn spring-boot:run -pl learnia-auth-service > /tmp/auth.log 2>&1 &
AUTH_PID=$!

echo "Starting User Service..."
mvn spring-boot:run -pl learnia-user-service > /tmp/user.log 2>&1 &
USER_PID=$!

echo "Starting Course Service..."
mvn spring-boot:run -pl learnia-course-service > /tmp/course.log 2>&1 &
COURSE_PID=$!

echo "Starting Document Service..."
mvn spring-boot:run -pl learnia-document-service > /tmp/document.log 2>&1 &
DOCUMENT_PID=$!

