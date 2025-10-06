#!/bin/bash
# Performance benchmarking script for BWARM Dashboard
# 
# Usage: ./tests/performance/benchmark.sh [test_type]
#   test_type: light | medium | heavy | stress (default: medium)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default configuration
TEST_TYPE=${1:-medium}
HOST="http://localhost:8000"
RESULTS_DIR="tests/performance/results"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}BWARM Dashboard Performance Benchmark${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Test configurations
case "$TEST_TYPE" in
    light)
        USERS=50
        SPAWN_RATE=10
        RUN_TIME="60s"
        echo -e "${GREEN}Test Type: Light Load${NC}"
        echo -e "Users: $USERS | Spawn Rate: $SPAWN_RATE/s | Duration: $RUN_TIME"
        ;;
    medium)
        USERS=100
        SPAWN_RATE=20
        RUN_TIME="120s"
        echo -e "${YELLOW}Test Type: Medium Load${NC}"
        echo -e "Users: $USERS | Spawn Rate: $SPAWN_RATE/s | Duration: $RUN_TIME"
        ;;
    heavy)
        USERS=500
        SPAWN_RATE=50
        RUN_TIME="300s"
        echo -e "${YELLOW}Test Type: Heavy Load${NC}"
        echo -e "Users: $USERS | Spawn Rate: $SPAWN_RATE/s | Duration: $RUN_TIME"
        ;;
    stress)
        USERS=1000
        SPAWN_RATE=100
        RUN_TIME="600s"
        echo -e "${RED}Test Type: Stress Test${NC}"
        echo -e "Users: $USERS | Spawn Rate: $SPAWN_RATE/s | Duration: $RUN_TIME"
        ;;
    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        echo "Valid types: light | medium | heavy | stress"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Target: $HOST${NC}"
echo ""

# Check if backend is running
if ! curl -s "$HOST/health" > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Backend not running at $HOST${NC}"
    echo "Please start the backend with: uvicorn main:app --reload"
    exit 1
fi

echo -e "${GREEN}✓ Backend is running${NC}"
echo ""

# Run locust test
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$RESULTS_DIR/${TEST_TYPE}_${TIMESTAMP}"

echo -e "${BLUE}Running load test...${NC}"
echo ""

locust -f tests/performance/locustfile.py \
    --host="$HOST" \
    --users "$USERS" \
    --spawn-rate "$SPAWN_RATE" \
    --run-time "$RUN_TIME" \
    --headless \
    --csv="$OUTPUT_FILE" \
    --html="$OUTPUT_FILE.html"

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Test Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "Results saved to:"
echo -e "  - CSV: ${OUTPUT_FILE}_stats.csv"
echo -e "  - HTML Report: ${OUTPUT_FILE}.html"
echo ""
echo -e "${BLUE}Open HTML report:${NC} open ${OUTPUT_FILE}.html"
echo ""
