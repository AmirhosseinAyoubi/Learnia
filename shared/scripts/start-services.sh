#!/bin/bash

# Script to start all Learnia services
# This is a helper script for local development

echo "Starting Learnia services..."

# Start infrastructure
echo "Starting infrastructure services (Docker Compose)..."
docker-compose up -d

# Wait for infrastructure to be ready
echo "Waiting for infrastructure to be ready..."
sleep 10

# Start Spring Boot services
echo "Starting Spring Boot services..."
cd spring-boot-services

# Start Eureka Server
echo "Starting Eureka Server..."
mvn spring-boot:run -pl learnia-eureka-server > /tmp/eureka.log 2>&1 &
EUREKA_PID=$!

sleep 5

# Start Config Server
echo "Starting Config Server..."
mvn spring-boot:run -pl learnia-config-server > /tmp/config.log 2>&1 &
CONFIG_PID=$!

sleep 5

# Start Gateway
echo "Starting API Gateway..."
mvn spring-boot:run -pl learnia-gateway > /tmp/gateway.log 2>&1 &
GATEWAY_PID=$!

sleep 5

# Start other services
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

echo "Spring Boot services started!"
echo "PIDs: Eureka=$EUREKA_PID, Config=$CONFIG_PID, Gateway=$GATEWAY_PID"
echo "      Auth=$AUTH_PID, User=$USER_PID, Course=$COURSE_PID, Document=$DOCUMENT_PID"

echo ""
echo "To start Python services, run:"
echo "  cd python-services/processing-service && uvicorn src.main:app --port 8001"
echo "  cd python-services/content-service && uvicorn src.main:app --port 8002"
echo "  cd python-services/ai-service && uvicorn src.main:app --port 8003"
echo "  cd python-services/question-service && uvicorn src.main:app --port 8004"
echo "  cd python-services/quiz-service && uvicorn src.main:app --port 8005"
