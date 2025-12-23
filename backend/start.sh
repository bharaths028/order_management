#!/bin/bash

# Production Start Script
# Runs Airflow and related services in background processes
# Runs FastAPI as the main foreground service with web server gateway

set -e

# Configuration
AIRFLOW_HOME="${AIRFLOW_HOME:-/opt/airflow}"
PYTHONPATH="${PYTHONPATH:-/opt/airflow/backend}"
LOG_DIR="${LOG_DIR:-$AIRFLOW_HOME/logs}"
PID_DIR="${PID_DIR:-$AIRFLOW_HOME/pids}"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Database configuration
if [ "$ENVIRONMENT" = "production" ]; then
    # Production: Use AWS Aurora PostgreSQL
    export DATABASE_URL="${AWS_DATABASE_URL:-postgresql://admin:password@order-management.c7jxyz.us-east-1.rds.amazonaws.com:5432/order_management}"
else
    # Development: Use local Docker PostgreSQL
    export DATABASE_URL="${DATABASE_URL:-postgresql://admin:admin123@postgres:5432/order_management}"
fi

echo "Starting Order Management System..."
echo "Environment: ${ENVIRONMENT:-development}"
echo "Database: $DATABASE_URL"
echo "Airflow Home: $AIRFLOW_HOME"
echo "Log Directory: $LOG_DIR"

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db init

# Create Airflow admin user if it doesn't exist
echo "Setting up Airflow admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin \
    2>/dev/null || echo "Admin user already exists"

# Start Airflow scheduler in background
echo "Starting Airflow scheduler..."
airflow scheduler \
    --log-file "$LOG_DIR/airflow-scheduler.log" \
    --pid "$PID_DIR/airflow-scheduler.pid" \
    &
SCHEDULER_PID=$!
echo "Airflow scheduler started (PID: $SCHEDULER_PID)"

# Start Airflow webserver in background
echo "Starting Airflow webserver..."
airflow webserver \
    --port 8080 \
    --log-file "$LOG_DIR/airflow-webserver.log" \
    --pid "$PID_DIR/airflow-webserver.pid" \
    &
WEBSERVER_PID=$!
echo "Airflow webserver started (PID: $WEBSERVER_PID)"

# Wait for Airflow to be ready
echo "Waiting for Airflow to be ready..."
sleep 10

# Function to cleanup background processes on exit
cleanup() {
    echo "Shutting down background services..."
    
    if [ -n "$SCHEDULER_PID" ] && kill -0 "$SCHEDULER_PID" 2>/dev/null; then
        echo "Stopping Airflow scheduler (PID: $SCHEDULER_PID)..."
        kill "$SCHEDULER_PID" 2>/dev/null || true
        wait "$SCHEDULER_PID" 2>/dev/null || true
    fi
    
    if [ -n "$WEBSERVER_PID" ] && kill -0 "$WEBSERVER_PID" 2>/dev/null; then
        echo "Stopping Airflow webserver (PID: $WEBSERVER_PID)..."
        kill "$WEBSERVER_PID" 2>/dev/null || true
        wait "$WEBSERVER_PID" 2>/dev/null || true
    fi
    
    echo "All background services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT SIGTERM SIGINT

# Start FastAPI application with Uvicorn as the main foreground process
echo "Starting FastAPI application..."
echo "FastAPI is now running. Visit http://localhost:8000/docs for API documentation"
echo ""

# Export environment variables for FastAPI app
export PYTHONPATH="$PYTHONPATH"
export DATABASE_URL="$DATABASE_URL"

# Run FastAPI with Uvicorn in foreground (this will be the main process)
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info

# If FastAPI exits, cleanup will be triggered by the trap
