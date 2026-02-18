#!/bin/bash

# Advanced Docker Monitoring Dashboard for MCP Gateway
# Provides comprehensive monitoring, alerting, and performance analysis

set -euo pipefail

# Configuration
SCRIPT_NAME="$(basename "$0")"
LOG_FILE="/tmp/mcp-gateway-dashboard.log"
DATA_DIR="/tmp/mcp-gateway-monitoring"
COMPOSE_FILE="docker-compose.yml"
HISTORY_FILE="$DATA_DIR/resource_history.csv"
ALERT_LOG="$DATA_DIR/alerts.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Alert thresholds
CPU_WARNING_THRESHOLD=70
CPU_CRITICAL_THRESHOLD=85
MEMORY_WARNING_THRESHOLD=75
MEMORY_CRITICAL_THRESHOLD=90
DISK_WARNING_THRESHOLD=80
DISK_CRITICAL_THRESHOLD=90

# Create data directory
mkdir -p "$DATA_DIR"

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
    clear
    print_status "$CYAN" "🚀 MCP Gateway Docker Monitoring Dashboard"
    echo "=================================================="
    print_status "$BLUE" "Last Updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

# Get container stats
get_container_stats() {
    local container_name=$1
    local stats
    stats=$(docker stats --no-stream --format "table {{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}}" "$container_name" 2>/dev/null | tail -n +2 || echo "N/A,N/A,N/A,N/A,N/A")
    echo "$stats"
}

# Parse stats values
parse_stat() {
    local line=$1
    local field=$2
    case $field in
        cpu) echo "$line" | cut -d',' -f1 | sed 's/%//' ;;
        mem_usage) echo "$line" | cut -d',' -f2 ;;
        mem_percent) echo "$line" | cut -d',' -f3 | sed 's/%//' ;;
        net_io) echo "$line" | cut -d',' -f4 ;;
        block_io) echo "$line" | cut -d',' -f5 ;;
        *) echo "N/A" ;;
    esac
}

# Check alert thresholds
check_alerts() {
    local container=$1
    local cpu=$2
    local mem_percent=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local alert_triggered=false

    # CPU alerts
    if (( $(echo "$cpu >= $CPU_CRITICAL_THRESHOLD" | bc -l) )); then
        echo "[$timestamp] CRITICAL: $container CPU usage at ${cpu}% (threshold: $CPU_CRITICAL_THRESHOLD%)" >> "$ALERT_LOG"
        print_status "$RED" "🚨 CRITICAL: $container CPU usage at ${cpu}%"
        alert_triggered=true
    elif (( $(echo "$cpu >= $CPU_WARNING_THRESHOLD" | bc -l) )); then
        echo "[$timestamp] WARNING: $container CPU usage at ${cpu}% (threshold: $CPU_WARNING_THRESHOLD%)" >> "$ALERT_LOG"
        print_status "$YELLOW" "⚠️  WARNING: $container CPU usage at ${cpu}%"
        alert_triggered=true
    fi

    # Memory alerts
    if (( $(echo "$mem_percent >= $MEMORY_CRITICAL_THRESHOLD" | bc -l) )); then
        echo "[$timestamp] CRITICAL: $container Memory usage at ${mem_percent}% (threshold: $MEMORY_CRITICAL_THRESHOLD%)" >> "$ALERT_LOG"
        print_status "$RED" "🚨 CRITICAL: $container Memory usage at ${mem_percent}%"
        alert_triggered=true
    elif (( $(echo "$mem_percent >= $MEMORY_WARNING_THRESHOLD" | bc -l) )); then
        echo "[$timestamp] WARNING: $container Memory usage at ${mem_percent}% (threshold: $MEMORY_WARNING_THRESHOLD%)" >> "$ALERT_LOG"
        print_status "$YELLOW" "⚠️  WARNING: $container Memory usage at ${mem_percent}%"
        alert_triggered=true
    fi

    return $([[ "$alert_triggered" == "true" ]] && echo 0 || echo 1)
}

# Store historical data
store_history() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local containers=$(docker-compose ps -q 2>/dev/null || echo "")

    # Create CSV header if file doesn't exist
    if [[ ! -f "$HISTORY_FILE" ]]; then
        echo "timestamp,container,cpu_percent,memory_usage,memory_percent,net_io,block_io" > "$HISTORY_FILE"
    fi

    # Store stats for each container
    while IFS= read -r container_id; do
        if [[ -n "$container_id" ]]; then
            local container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}" 2>/dev/null || echo "unknown")
            local stats=$(get_container_stats "$container_id")

            if [[ "$stats" != "N/A,N/A,N/A,N/A,N/A" ]]; then
                local cpu=$(parse_stat "$stats" "cpu")
                local mem_usage=$(parse_stat "$stats" "mem_usage")
                local mem_percent=$(parse_stat "$stats" "mem_percent")
                local net_io=$(parse_stat "$stats" "net_io")
                local block_io=$(parse_stat "$stats" "block_io")

                echo "$timestamp,$container_name,$cpu,$mem_usage,$mem_percent,$net_io,$block_io" >> "$HISTORY_FILE"
            fi
        fi
    done <<< "$containers"
}

# Display container status
display_container_status() {
    print_status "$BLUE" "📦 Container Status"
    echo "----------------------------------------"

    local containers=$(docker-compose ps --services 2>/dev/null || echo "")

    while IFS= read -r service; do
        if [[ -n "$service" ]]; then
            local container_id=$(docker-compose ps -q "$service" 2>/dev/null || echo "")
            if [[ -n "$container_id" ]]; then
                local status=$(docker ps --filter "id=$container_id" --format "{{.Status}}" 2>/dev/null || echo "Unknown")
                local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "no-healthcheck")
                local stats=$(get_container_stats "$container_id")

                if [[ "$stats" != "N/A,N/A,N/A,N/A,N/A" ]]; then
                    local cpu=$(parse_stat "$stats" "cpu")
                    local mem_usage=$(parse_stat "$stats" "mem_usage")
                    local mem_percent=$(parse_stat "$stats" "mem_percent")

                    # Health status color
                    local health_color="$GREEN"
                    if [[ "$health" == "unhealthy" ]]; then
                        health_color="$RED"
                    elif [[ "$health" == "starting" ]]; then
                        health_color="$YELLOW"
                    fi

                    printf "%-20s %-12s %-10s %-8s %-15s %-10s\n" \
                        "$service" \
                        "${status%% *}" \
                        "$(echo "$health" | head -c 8)" \
                        "${cpu}%" \
                        "$mem_usage" \
                        "${mem_percent}%"

                    # Check alerts
                    check_alerts "$service" "$cpu" "$mem_percent"
                else
                    printf "%-20s %-12s %-10s %-8s %-15s %-10s\n" \
                        "$service" \
                        "${status%% *}" \
                        "N/A" \
                        "N/A" \
                        "N/A" \
                        "N/A"
                fi
            fi
        fi
    done <<< "$containers"
    echo ""
}

# Display system resources
display_system_resources() {
    print_status "$BLUE" "🖥️  System Resources"
    echo "----------------------------------------"

    # Docker system info
    local docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "Unknown")
    local containers_total=$(docker ps -q | wc -l 2>/dev/null || echo "0")
    local containers_running=$(docker ps --filter "status=running" -q | wc -l 2>/dev/null || echo "0")

    echo "Docker Version: $docker_version"
    echo "Containers: $containers_running running / $containers_total total"

    # Disk usage
    local docker_usage=$(docker system df --format "{{.Type}}: {{.Size}}" 2>/dev/null | head -5 || echo "N/A")
    echo "Docker Disk Usage:"
    echo "$docker_usage" | while IFS= read -r line; do
        echo "  $line"
    done

    # Host system info (if available)
    if command -v free >/dev/null 2>&1; then
        local mem_info=$(free -h | awk 'NR==2{printf "System Memory: %s / %s (%s used)", $3, $2, $3*100/$2}')
        echo "$mem_info"
    fi

    if command -v df >/dev/null 2>&1; then
        local disk_usage=$(df -h / | awk 'NR==2{printf "Disk Usage: %s / %s (%s used)", $3, $2, $5}')
        echo "$disk_usage"
    fi

    echo ""
}

# Display recent alerts
display_recent_alerts() {
    print_status "$BLUE" "🚨 Recent Alerts (Last 10)"
    echo "----------------------------------------"

    if [[ -f "$ALERT_LOG" ]] && [[ -s "$ALERT_LOG" ]]; then
        tail -n 10 "$ALERT_LOG" | while IFS= read -r alert; do
            if [[ "$alert" == *"CRITICAL"* ]]; then
                print_status "$RED" "$alert"
            elif [[ "$alert" == *"WARNING"* ]]; then
                print_status "$YELLOW" "$alert"
            else
                echo "$alert"
            fi
        done
    else
        print_status "$GREEN" "✅ No recent alerts"
    fi
    echo ""
}

# Display performance trends
display_performance_trends() {
    print_status "$BLUE" "📈 Performance Trends (Last Hour)"
    echo "----------------------------------------"

    if [[ -f "$HISTORY_FILE" ]] && [[ -s "$HISTORY_FILE" ]]; then
        local one_hour_ago=$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v-1H '+%Y-%m-%d %H:%M:%S')

        # Calculate averages for each container
        tail -n +2 "$HISTORY_FILE" | while IFS=',' read -r timestamp container cpu mem_usage mem_percent net_io block_io; do
            if [[ "$timestamp" > "$one_hour_ago" ]]; then
                echo "$container,$cpu,$mem_percent"
            fi
        done | sort | awk -F',' '
        {
            cpu_sum[$1] += $2; mem_sum[$1] += $3; count[$1]++
        }
        END {
            for (container in count) {
                avg_cpu = cpu_sum[container] / count[container]
                avg_mem = mem_sum[container] / count[container]
                printf "%-20s Avg CPU: %6.2f%% Avg Mem: %6.2f%%\n", container, avg_cpu, avg_mem
            }
        }'
    else
        print_status "$YELLOW" "⚠️  No historical data available yet"
    fi
    echo ""
}

# Display optimization recommendations
display_recommendations() {
    print_status "$BLUE" "💡 Optimization Recommendations"
    echo "----------------------------------------"

    local containers=$(docker-compose ps -q 2>/dev/null || echo "")
    local recommendations=()

    while IFS= read -r container_id; do
        if [[ -n "$container_id" ]]; then
            local container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}" 2>/dev/null || echo "unknown")
            local stats=$(get_container_stats "$container_id")

            if [[ "$stats" != "N/A,N/A,N/A,N/A,N/A" ]]; then
                local cpu=$(parse_stat "$stats" "cpu")
                local mem_percent=$(parse_stat "$stats" "mem_percent")

                # CPU recommendations
                if (( $(echo "$cpu > 80" | bc -l) )); then
                    recommendations+=("Consider increasing CPU limit for $container_name (current: ${cpu}%)")
                elif (( $(echo "$cpu < 10" | bc -l) )); then
                    recommendations+=("Consider reducing CPU reservation for $container_name (current: ${cpu}%)")
                fi

                # Memory recommendations
                if (( $(echo "$mem_percent > 85" | bc -l) )); then
                    recommendations+=("Consider increasing memory limit for $container_name (current: ${mem_percent}%)")
                elif (( $(echo "$mem_percent < 20" | bc -l) )); then
                    recommendations+=("Consider reducing memory limit for $container_name (current: ${mem_percent}%)")
                fi
            fi
        fi
    done <<< "$containers"

    if [[ ${#recommendations[@]} -gt 0 ]]; then
        for rec in "${recommendations[@]}"; do
            print_status "$YELLOW" "• $rec"
        done
    else
        print_status "$GREEN" "✅ Resource usage looks optimal"
    fi
    echo ""
}

# Interactive menu
show_menu() {
    echo "Options:"
    echo "1. Refresh dashboard"
    echo "2. View detailed container logs"
    echo "3. Run performance test"
    echo "4. Export monitoring data"
    echo "5. Clear alert history"
    echo "6. Exit"
    echo ""
    read -p "Select option [1-6]: " choice

    case $choice in
        1) return 0 ;;
        2) show_detailed_logs ;;
        3) run_performance_test ;;
        4) export_data ;;
        5) clear_alerts ;;
        6) exit 0 ;;
        *) print_status "$RED" "Invalid option" && sleep 2 ;;
    esac
}

# Show detailed logs
show_detailed_logs() {
    local containers=$(docker-compose ps --services 2>/dev/null || echo "")
    echo "Available containers:"
    echo "$containers" | nl
    echo ""
    read -p "Select container number: " container_num

    local service=$(echo "$containers" | sed -n "${container_num}p")
    if [[ -n "$service" ]]; then
        print_status "$BLUE" "Showing logs for $service (press Ctrl+C to exit)..."
        docker-compose logs -f "$service"
    fi
}

# Run performance test
run_performance_test() {
    print_status "$BLUE" "🧪 Running Performance Test..."

    local test_duration=30
    local test_results="$DATA_DIR/performance_test_$(date +%Y%m%d_%H%M%S).log"

    echo "Running performance test for ${test_duration} seconds..."
    echo "Results will be saved to: $test_results"

    local start_time=$(date +%s)
    local end_time=$((start_time + test_duration))

    {
        echo "Performance Test Results - $(date)"
        echo "Duration: ${test_duration} seconds"
        echo "=========================================="

        while [[ $(date +%s) -lt $end_time ]]; do
            local timestamp=$(date '+%H:%M:%S')
            local containers=$(docker-compose ps -q 2>/dev/null || echo "")

            echo "[$timestamp] Container Stats:"
            while IFS= read -r container_id; do
                if [[ -n "$container_id" ]]; then
                    local container_name=$(docker ps --filter "id=$container_id" --format "{{.Names}}" 2>/dev/null || echo "unknown")
                    local stats=$(get_container_stats "$container_id")

                    if [[ "$stats" != "N/A,N/A,N/A,N/A,N/A" ]]; then
                        local cpu=$(parse_stat "$stats" "cpu")
                        local mem_percent=$(parse_stat "$stats" "mem_percent")
                        echo "  $container_name: CPU=${cpu}%, Memory=${mem_percent}%"
                    fi
                fi
            done <<< "$containers"
            echo ""
            sleep 5
        done

        echo "Test completed at $(date)"
    } > "$test_results"

    print_status "$GREEN" "✅ Performance test completed"
    print_status "$BLUE" "Results saved to: $test_results"
    sleep 3
}

# Export monitoring data
export_data() {
    local export_file="$DATA_DIR/mcp_gateway_monitoring_$(date +%Y%m%d_%H%M%S).tar.gz"

    print_status "$BLUE" "📦 Exporting monitoring data..."

    tar -czf "$export_file" -C "$DATA_DIR" . 2>/dev/null || {
        print_status "$RED" "❌ Failed to export data"
        return 1
    }

    print_status "$GREEN" "✅ Data exported to: $export_file"
    sleep 2
}

# Clear alert history
clear_alerts() {
    if [[ -f "$ALERT_LOG" ]]; then
        > "$ALERT_LOG"
        print_status "$GREEN" "✅ Alert history cleared"
    else
        print_status "$YELLOW" "⚠️  No alert history to clear"
    fi
    sleep 2
}

# Main dashboard loop
main_dashboard() {
    while true; do
        print_header
        display_container_status
        display_system_resources
        display_recent_alerts
        display_performance_trends
        display_recommendations

        show_menu
    done
}

# Help function
show_help() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Advanced Docker Monitoring Dashboard for MCP Gateway

OPTIONS:
    -h, --help          Show this help message
    -s, --single        Run single check and exit
    -d, --duration N    Run for N seconds then exit
    --export-data       Export monitoring data and exit

EXAMPLES:
    $SCRIPT_NAME                    # Interactive dashboard
    $SCRIPT_NAME -s                  # Single check
    $SCRIPT_NAME -d 300             # Run for 5 minutes

FEATURES:
    - Real-time container monitoring
    - Automated alerting
    - Historical data tracking
    - Performance analysis
    - Optimization recommendations
    - Interactive troubleshooting

EOF
}

# Parse command line arguments
SINGLE_MODE=false
DURATION=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--single)
            SINGLE_MODE=true
            shift
            ;;
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        --export-data)
            export_data
            exit 0
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
    print_status "$YELLOW" "⚠️  'bc' calculator not found - some features may not work"
fi

# Main execution
log "Starting Docker monitoring dashboard"

if [[ "$SINGLE_MODE" == "true" ]]; then
    print_header
    display_container_status
    display_system_resources
    display_recent_alerts
    display_performance_trends
    display_recommendations
elif [[ "$DURATION" -gt 0 ]]; then
    end_time=$(($(date +%s) + DURATION))
    while [[ $(date +%s) -lt $end_time ]]; do
        print_header
        display_container_status
        display_system_resources
        store_history
        sleep 10
    done
else
    main_dashboard
fi

log "Monitoring dashboard session ended"
