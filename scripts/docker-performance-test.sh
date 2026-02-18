#!/bin/bash

# Docker Performance Testing Suite for MCP Gateway
# Automated performance benchmarking and regression testing

set -euo pipefail

# Configuration
SCRIPT_NAME="$(basename "$0")"
LOG_FILE="/tmp/mcp-gateway-perf-test.log"
RESULTS_DIR="/tmp/mcp-gateway-perf-results"
BASELINE_FILE="$RESULTS_DIR/performance_baseline.json"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test configuration
TEST_DURATION=300  # 5 minutes
SAMPLE_INTERVAL=10  # 10 seconds
WARMUP_TIME=30     # 30 seconds warmup

# Performance thresholds
MAX_CPU_AVG=50     # Maximum average CPU percentage
MAX_MEMORY_AVG=70  # Maximum average memory percentage
MAX_STARTUP_TIME=60 # Maximum startup time in seconds
MAX_RESPONSE_TIME=2000 # Maximum response time in milliseconds

# Create results directory
mkdir -p "$RESULTS_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print header
print_header() {
    print_status "$CYAN" "🧪 Docker Performance Testing Suite"
    echo "=========================================="
    print_status "$BLUE" "Test Started: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

# Get container startup time
get_startup_time() {
    local container_name=$1
    local service_name=$2

    # Stop and start the service
    docker-compose stop "$service_name" >/dev/null 2>&1
    local start_time=$(date +%s.%N)

    docker-compose start "$service_name" >/dev/null 2>&1

    # Wait for container to be healthy
    local timeout=0
    while [[ $timeout -lt $MAX_STARTUP_TIME ]]; do
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-healthcheck")
        if [[ "$health" == "healthy" ]]; then
            local end_time=$(date +%s.%N)
            echo "$end_time - $start_time" | bc -l
            return 0
        fi
        sleep 2
        timeout=$((timeout + 2))
    done

    echo "$MAX_STARTUP_TIME"  # Return max time if not healthy
}

# Measure response time
measure_response_time() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}

    # Try different methods to measure response time
    local response_time=0

    # Method 1: curl if available
    if command -v curl >/dev/null 2>&1; then
        response_time=$(curl -o /dev/null -s -w '%{time_total}' --max-time 10 "http://localhost:$port$endpoint" 2>/dev/null || echo "10000")
    # Method 2: wget if available
    elif command -v wget >/dev/null 2>&1; then
        response_time=$(wget -O /dev/null --timeout=10 --tries=1 "http://localhost:$port$endpoint" 2>&1 | grep -o 'real.*m' | sed 's/real.*m[[:space:]]*//' | sed 's/s//' || echo "10000")
    # Method 3: nc (netcat) basic connectivity
    elif command -v nc >/dev/null 2>&1; then
        local start_time=$(date +%s.%N)
        if nc -z localhost "$port" 2>/dev/null; then
            local end_time=$(date +%s.%N)
            response_time=$(echo "$end_time - $start_time" | bc -l)
        else
            response_time="10000"
        fi
    else
        response_time="10000"  # Default high value if no tools available
    fi

    # Convert to milliseconds
    echo "$response_time * 1000 / 1" | bc -l 2>/dev/null || echo "10000"
}

# Collect performance metrics
collect_metrics() {
    local duration=$1
    local output_file=$2
    local sample_interval=$3

    print_status "$BLUE" "📊 Collecting performance metrics for ${duration}s..."

    local end_time=$(($(date +%s) + duration))
    local sample_count=0

    # Create CSV header
    echo "timestamp,container,cpu_percent,memory_usage,memory_percent,net_io,block_io" > "$output_file"

    while [[ $(date +%s) -lt $end_time ]]; do
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local containers=$(docker-compose ps -q 2>/dev/null || echo "")

        while IFS= read -r container_id; do
            if [[ -n "$container_id" ]]; then
                local container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}" 2>/dev/null || echo "unknown")
                local stats=$(docker stats --no-stream --format "table {{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" "$container_id" 2>/dev/null | tail -n +2 || echo "N/A,N/A,N/A,N/A,N/A")

                if [[ "$stats" != "N/A,N/A,N/A,N/A,N/A" ]]; then
                    # Parse stats
                    local cpu=$(echo "$stats" | cut -d',' -f1 | sed 's/%//')
                    local mem_usage=$(echo "$stats" | cut -d',' -f2)
                    local mem_percent=$(echo "$stats" | cut -d',' -f3 | sed 's/%//')
                    local net_io=$(echo "$stats" | cut -d',' -f4)
                    local block_io=$(echo "$stats" | cut -d',' -f5)

                    echo "$timestamp,$container_name,$cpu,$mem_usage,$mem_percent,$net_io,$block_io" >> "$output_file"
                    sample_count=$((sample_count + 1))
                fi
            fi
        done <<< "$containers"

        sleep "$sample_interval"
    done

    print_status "$GREEN" "✅ Collected $sample_count samples"
    return $sample_count
}

# Analyze performance data
analyze_data() {
    local data_file=$1
    local results_file=$2

    print_status "$BLUE" "📈 Analyzing performance data..."

    # Create analysis results
    {
        echo "{"
        echo "  \"analysis_timestamp\": \"$(date -Iseconds)\","
        echo "  \"test_duration\": \"$TEST_DURATION\","
        echo "  \"sample_interval\": \"$SAMPLE_INTERVAL\","
        echo "  \"containers\": {"

        # Get unique container names
        local containers=$(tail -n +2 "$data_file" | cut -d',' -f2 | sort -u)

        local first_container=true
        while IFS= read -r container; do
            if [[ -n "$container" ]]; then
                if [[ "$first_container" == "false" ]]; then
                    echo ","
                fi
                first_container=false

                echo "    \"$container\": {"

                # Calculate statistics for this container
                local container_data=$(tail -n +2 "$data_file" | grep "^.*,${container},")
                local cpu_avg=$(echo "$container_data" | cut -d',' -f3 | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 0}')
                local mem_avg=$(echo "$container_data" | cut -d',' -f5 | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 0}')
                local cpu_max=$(echo "$container_data" | cut -d',' -f3 | sort -nr | head -1)
                local mem_max=$(echo "$container_data" | cut -d',' -f5 | sort -nr | head -1)
                local sample_count=$(echo "$container_data" | wc -l)

                echo "      \"sample_count\": $sample_count,"
                echo "      \"cpu\": {"
                echo "        \"average\": $cpu_avg,"
                echo "        \"maximum\": $cpu_max"
                echo "      },"
                echo "      \"memory\": {"
                echo "        \"average\": $mem_avg,"
                echo "        \"maximum\": $mem_max"
                echo "      }"
                echo -n "    }"
            fi
        done <<< "$containers"

        echo ""
        echo "  }"
        echo "}"
    } > "$results_file"

    print_status "$GREEN" "✅ Analysis completed"
}

# Run startup performance test
run_startup_test() {
    print_status "$BLUE" "🚀 Running startup performance test..."

    local startup_results="$RESULTS_DIR/startup_test_$(date +%Y%m%d_%H%M%S).json"

    {
        echo "{"
        echo "  \"test_timestamp\": \"$(date -Iseconds)\","
        echo "  \"startup_times\": {"

        local services=$(docker-compose ps --services 2>/dev/null || echo "")
        local first_service=true

        while IFS= read -r service; do
            if [[ -n "$service" ]]; then
                local container_id=$(docker-compose ps -q "$service" 2>/dev/null || echo "")
                if [[ -n "$container_id" ]]; then
                    local container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}" 2>/dev/null || echo "unknown")

                    if [[ "$first_service" == "false" ]]; then
                        echo ","
                    fi
                    first_service=false

                    local startup_time=$(get_startup_time "$container_name" "$service")

                    echo "    \"$service\": {"
                    echo "      \"container_name\": \"$container_name\","
                    echo "      \"startup_time_seconds\": $startup_time,"
                    echo "      \"within_threshold\": $(echo "$startup_time <= $MAX_STARTUP_TIME" | bc -l)"
                    echo "    }"
                fi
            fi
        done <<< "$services"

        echo ""
        echo "  }"
        echo "}"
    } > "$startup_results"

    print_status "$GREEN" "✅ Startup test completed: $startup_results"
}

# Run response time test
run_response_time_test() {
    print_status "$BLUE" "⚡ Running response time test..."

    local response_results="$RESULTS_DIR/response_test_$(date +%Y%m%d_%H%M%S).json"

    {
        echo "{"
        echo "  \"test_timestamp\": \"$(date -Iseconds)\","
        echo "  \"response_times\": {"

        # Test known services
        local services=(
            "gateway:4444:/health"
            "service-manager:9000:/health"
            "tool-router:8030:/health"
            "translate:8000:/health"
        )

        local first_service=true
        for service_config in "${services[@]}"; do
            IFS=':' read -r service port endpoint <<< "$service_config"

            if [[ "$first_service" == "false" ]]; then
                echo ","
            fi
            first_service=false

            local response_time=$(measure_response_time "$service" "$port" "$endpoint")
            local within_threshold=$(echo "$response_time <= $MAX_RESPONSE_TIME" | bc -l)

            echo "    \"$service\": {"
            echo "      \"port\": $port,"
            echo "      \"endpoint\": \"$endpoint\","
            echo "      \"response_time_ms\": $response_time,"
            echo "      "within_threshold": $within_threshold"
            echo "    }"
        done

        echo ""
        echo "  }"
        echo "}"
    } > "$response_results"

    print_status "$GREEN" "✅ Response time test completed: $response_results"
}

# Compare with baseline
compare_with_baseline() {
    local current_results=$1

    if [[ ! -f "$BASELINE_FILE" ]]; then
        print_status "$YELLOW" "⚠️  No baseline file found - creating baseline"
        cp "$current_results" "$BASELINE_FILE"
        return 0
    fi

    print_status "$BLUE" "📊 Comparing with baseline..."

    # Simple comparison logic (could be enhanced with jq)
    local baseline_cpu=$(grep -o '"average": [0-9.]*' "$BASELINE_FILE" | head -1 | cut -d' ' -f3)
    local current_cpu=$(grep -o '"average": [0-9.]*' "$current_results" | head -1 | cut -d' ' -f3)

    if [[ -n "$baseline_cpu" ]] && [[ -n "$current_cpu" ]]; then
        local cpu_diff=$(echo "$current_cpu - $baseline_cpu" | bc -l)
        local cpu_change=$(echo "scale=2; $cpu_diff / $baseline_cpu * 100" | bc -l)

        if (( $(echo "$cpu_change > 10" | bc -l) )); then
            print_status "$RED" "🚨 CPU usage increased by ${cpu_change}% compared to baseline"
        elif (( $(echo "$cpu_change < -10" | bc -l) )); then
            print_status "$GREEN" "✅ CPU usage decreased by ${cpu_change#-}% compared to baseline"
        else
            print_status "$BLUE" "ℹ️  CPU usage changed by ${cpu_change#-}% compared to baseline"
        fi
    fi
}

# Generate performance report
generate_report() {
    local test_dir=$1
    local report_file="$test_dir/performance_report_$(date +%Y%m%d_%H%M%S).md"

    print_status "$BLUE" "📝 Generating performance report..."

    {
        echo "# Docker Performance Test Report"
        echo ""
        echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**Test Duration:** ${TEST_DURATION}s"
        echo "**Sample Interval:** ${SAMPLE_INTERVAL}s"
        echo ""
        echo "## Test Results Summary"
        echo ""

        # Include results from all test files
        for json_file in "$test_dir"/*.json; do
            if [[ -f "$json_file" ]]; then
                local filename=$(basename "$json_file")
                echo "### $filename"
                echo '```json'
                cat "$json_file"
                echo '```'
                echo ""
            fi
        done

        echo "## Performance Thresholds"
        echo ""
        echo "- Max Average CPU: ${MAX_CPU_AVG}%"
        echo "- Max Average Memory: ${MAX_MEMORY_AVG}%"
        echo "- Max Startup Time: ${MAX_STARTUP_TIME}s"
        echo "- Max Response Time: ${MAX_RESPONSE_TIME}ms"
        echo ""
        echo "## Recommendations"
        echo ""
        echo "*Review the detailed results above and consider the following:*"
        echo ""
        echo "- Containers consistently above CPU thresholds may need more CPU allocation"
        echo "- High memory usage may indicate memory leaks or insufficient limits"
        echo "- Slow startup times may need optimization or resource adjustments"
        echo "- High response times may indicate performance bottlenecks"
        echo ""
    } > "$report_file"

    print_status "$GREEN" "✅ Report generated: $report_file"
}

# Run full performance test suite
run_full_test_suite() {
    local test_timestamp=$(date +%Y%m%d_%H%M%S)
    local test_dir="$RESULTS_DIR/test_$test_timestamp"
    mkdir -p "$test_dir"

    print_header

    # 1. Warmup period
    print_status "$BLUE" "🔥 Warming up containers for ${WARMUP_TIME}s..."
    sleep "$WARMUP_TIME"

    # 2. Startup performance test
    run_startup_test

    # 3. Response time test
    run_response_time_test

    # 4. Load test with metrics collection
    local metrics_file="$test_dir/metrics_$test_timestamp.csv"
    collect_metrics "$TEST_DURATION" "$metrics_file" "$SAMPLE_INTERVAL"

    # 5. Analyze collected data
    local analysis_file="$test_dir/analysis_$test_timestamp.json"
    analyze_data "$metrics_file" "$analysis_file"

    # 6. Compare with baseline
    compare_with_baseline "$analysis_file"

    # 7. Generate report
    generate_report "$test_dir"

    print_status "$GREEN" "✅ Full performance test suite completed!"
    print_status "$BLUE" "Results directory: $test_dir"

    # Check for any threshold violations
    local violations=false

    # Check CPU averages
    local cpu_violations=$(grep -o '"average": [0-9.]*' "$analysis_file" | awk '{if($2 > '"$MAX_CPU_AVG"') print $2}' | wc -l)
    if [[ $cpu_violations -gt 0 ]]; then
        print_status "$RED" "🚨 $cpu_violations container(s) exceeded CPU threshold of ${MAX_CPU_AVG}%"
        violations=true
    fi

    # Check memory averages
    local mem_violations=$(grep -o '"average": [0-9.]*' "$analysis_file" | awk '{if(NR%2==0 && $2 > '"$MAX_MEMORY_AVG"') print $2}' | wc -l)
    if [[ $mem_violations -gt 0 ]]; then
        print_status "$RED" "🚨 $mem_violations container(s) exceeded memory threshold of ${MAX_MEMORY_AVG}%"
        violations=true
    fi

    if [[ "$violations" == "false" ]]; then
        print_status "$GREEN" "✅ All performance thresholds met!"
    fi

    return $([[ "$violations" == "true" ]] && echo 1 || echo 0)
}

# Help function
show_help() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Docker Performance Testing Suite for MCP Gateway

OPTIONS:
    -h, --help              Show this help message
    -s, --startup          Run startup performance test only
    -r, --response         Run response time test only
    -l, --load             Run load test with metrics collection only
    -c, --compare          Compare with baseline only
    -d, --duration N       Test duration in seconds (default: 300)
    -i, --interval N       Sample interval in seconds (default: 10)
    -w, --warmup N         Warmup time in seconds (default: 30)
    --set-baseline         Set current results as baseline
    --report-only          Generate report from existing results

EXAMPLES:
    $SCRIPT_NAME                           # Run full test suite
    $SCRIPT_NAME -s                        # Startup test only
    $SCRIPT_NAME -d 600 -i 5              # 10-minute test with 5s intervals
    $SCRIPT_NAME --set-baseline            # Set current performance as baseline

THRESHOLDS:
    Max Average CPU: ${MAX_CPU_AVG}%
    Max Average Memory: ${MAX_MEMORY_AVG}%
    Max Startup Time: ${MAX_STARTUP_TIME}s
    Max Response Time: ${MAX_RESPONSE_TIME}ms

EOF
}

# Parse command line arguments
STARTUP_ONLY=false
RESPONSE_ONLY=false
LOAD_ONLY=false
COMPARE_ONLY=false
SET_BASELINE=false
REPORT_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--startup)
            STARTUP_ONLY=true
            shift
            ;;
        -r|--response)
            RESPONSE_ONLY=true
            shift
            ;;
        -l|--load)
            LOAD_ONLY=true
            shift
            ;;
        -c|--compare)
            COMPARE_ONLY=true
            shift
            ;;
        -d|--duration)
            TEST_DURATION="$2"
            shift 2
            ;;
        -i|--interval)
            SAMPLE_INTERVAL="$2"
            shift 2
            ;;
        -w|--warmup)
            WARMUP_TIME="$2"
            shift 2
            ;;
        --set-baseline)
            SET_BASELINE=true
            shift
            ;;
        --report-only)
            REPORT_ONLY=true
            shift
            ;;
        *)
            print_status "$RED" "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check dependencies
if ! command -v docker >/dev/null 2>&1; then
    print_status "$RED" "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
    print_status "$RED" "❌ Docker Compose is not installed or not in PATH"
    exit 1
fi

if ! command -v bc >/dev/null 2>&1; then
    print_status "$RED" "❌ 'bc' calculator is required but not found"
    exit 1
fi

# Main execution
log "Starting Docker performance testing"

if [[ "$REPORT_ONLY" == "true" ]]; then
    generate_report "$RESULTS_DIR"
elif [[ "$STARTUP_ONLY" == "true" ]]; then
    print_header
    run_startup_test
elif [[ "$RESPONSE_ONLY" == "true" ]]; then
    print_header
    run_response_time_test
elif [[ "$LOAD_ONLY" == "true" ]]; then
    print_header
    test_timestamp=$(date +%Y%m%d_%H%M%S)
    metrics_file="$RESULTS_DIR/load_test_$test_timestamp.csv"
    collect_metrics "$TEST_DURATION" "$metrics_file" "$SAMPLE_INTERVAL"

    analysis_file="$RESULTS_DIR/load_analysis_$test_timestamp.json"
    analyze_data "$metrics_file" "$analysis_file"

    if [[ "$SET_BASELINE" == "true" ]]; then
        cp "$analysis_file" "$BASELINE_FILE"
        print_status "$GREEN" "✅ Baseline updated"
    fi
elif [[ "$COMPARE_ONLY" == "true" ]]; then
    if [[ ! -f "$BASELINE_FILE" ]]; then
        print_status "$RED" "❌ No baseline file found"
        exit 1
    fi

    # Find most recent analysis file
    latest_analysis=$(ls -t "$RESULTS_DIR"/*analysis*.json 2>/dev/null | head -1)
    if [[ -n "$latest_analysis" ]]; then
        compare_with_baseline "$latest_analysis"
    else
        print_status "$RED" "❌ No analysis files found"
        exit 1
    fi
else
    # Run full test suite
    run_full_test_suite
    exit_code=$?

    if [[ "$SET_BASELINE" == "true" ]]; then
        latest_analysis=$(ls -t "$RESULTS_DIR"/*analysis*.json 2>/dev/null | head -1)
        if [[ -n "$latest_analysis" ]]; then
            cp "$latest_analysis" "$BASELINE_FILE"
            print_status "$GREEN" "✅ Baseline updated with latest results"
        fi
    fi

    exit $exit_code
fi

log "Performance testing completed"
