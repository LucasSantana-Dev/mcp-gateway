#!/bin/bash
# Advanced Monitoring and Alerting for Scalable MCP Gateway
# Comprehensive monitoring with intelligent alerting and automated responses

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SERVICE_MANAGER_URL="http://localhost:9000"
GATEWAY_URL="http://localhost:4444"
TOOL_ROUTER_URL="http://localhost:8030"
MONITORING_INTERVAL=60  # 1 minute
ALERT_LOG="logs/monitoring/alerts.log"
METRICS_LOG="logs/monitoring/metrics.log"
HEALTH_LOG="logs/monitoring/health.log"
PERFORMANCE_LOG="logs/monitoring/performance.log"

# Alert thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
WAKE_TIME_THRESHOLD=500
RESPONSE_TIME_THRESHOLD=1000
COST_SAVINGS_THRESHOLD=40

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_alert() {
    echo -e "${MAGENTA}[ALERT]${NC} $1"
}

# Initialize monitoring directories
init_monitoring() {
    log "Initializing monitoring directories..."

    mkdir -p logs/monitoring/{alerts,metrics,health,performance}
    mkdir -p monitoring/{dashboards,reports,alerts}

    # Create log rotation configuration
    cat > logs/monitoring/logrotate.conf << EOF
logs/monitoring/*.log {
    hourly
    missingok
    rotate 24
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

    log_success "Monitoring directories initialized"
}

# Collect System Metrics
collect_system_metrics() {
    local timestamp=$(date -Iseconds)

    # System resources
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

    # Docker resources
    local docker_containers=$(docker ps -q | wc -l)
    local docker_images=$(docker images -q | wc -l)
    local docker_volumes=$(docker volume ls -q | wc -l)

    # Network metrics
    local network_connections=$(netstat -an | grep ESTABLISHED | wc -l)
    local listening_ports=$(netstat -an | grep LISTEN | wc -l)

    # Log metrics
    echo "$timestamp,system,cpu,$cpu_usage" >> "$METRICS_LOG"
    echo "$timestamp,system,memory,$memory_usage" >> "$METRICS_LOG"
    echo "$timestamp,system,disk,$disk_usage" >> "$METRICS_LOG"
    echo "$timestamp,system,containers,$docker_containers" >> "$METRICS_LOG"
    echo "$timestamp,system,images,$docker_images" >> "$METRICS_LOG"
    echo "$timestamp,system,volumes,$docker_volumes" >> "$METRICS_LOG"
    echo "$timestamp,system,connections,$network_connections" >> "$METRICS_LOG"
    echo "$timestamp,system,ports,$listening_ports" >> "$METRICS_LOG"
}

# Collect Service Metrics
collect_service_metrics() {
    local timestamp=$(date -Iseconds)

    # Get service status
    local services_status=$(curl -s "$SERVICE_MANAGER_URL/services/status" 2>/dev/null || echo "{}")

    if [[ "$services_status" != "{}" ]]; then
        # Process each service
        echo "$services_status" | jq -r 'to_entries[] | "\(.key),\(.value.state),\(.value.last_activity // "never")"' 2>/dev/null | while IFS=',' read -r service state last_activity; do
            if [[ -n "$service" ]]; then
                echo "$timestamp,service,$service,state,$state" >> "$METRICS_LOG"
                echo "$timestamp,service,$service,last_activity,$last_activity" >> "$METRICS_LOG"

                # Get service-specific metrics
                local service_metrics=$(curl -s "$SERVICE_MANAGER_URL/services/$service/metrics" 2>/dev/null || echo "{}")

                if [[ "$service_metrics" != "{}" ]]; then
                    local cpu_usage=$(echo "$service_metrics" | jq -r '.cpu_usage // 0' 2>/dev/null || echo "0")
                    local memory_usage=$(echo "$service_metrics" | jq -r '.memory_usage // 0' 2>/dev/null || echo "0")
                    local wake_time=$(echo "$service_metrics" | jq -r '.wake_time // 0' 2>/dev/null || echo "0")
                    local response_time=$(echo "$service_metrics" | jq -r '.response_time // 0' 2>/dev/null || echo "0")

                    echo "$timestamp,service,$service,cpu,$cpu_usage" >> "$METRICS_LOG"
                    echo "$timestamp,service,$service,memory,$memory_usage" >> "$METRICS_LOG"
                    echo "$timestamp,service,$service,wake_time,$wake_time" >> "$METRICS_LOG"
                    echo "$timestamp,service,$service,response_time,$response_time" >> "$METRICS_LOG"
                fi
            fi
        done
    fi

    # Get performance metrics
    local performance_metrics=$(curl -s "$SERVICE_MANAGER_URL/metrics/performance" 2>/dev/null || echo "{}")

    if [[ "$performance_metrics" != "{}" ]]; then
        local avg_wake_time=$(echo "$performance_metrics" | jq -r '.average_wake_time // 0' 2>/dev/null || echo "0")
        local total_requests=$(echo "$performance_metrics" | jq -r '.total_requests // 0' 2>/dev/null || echo "0")
        local success_rate=$(echo "$performance_metrics" | jq -r '.success_rate // 0' 2>/dev/null || echo "0")

        echo "$timestamp,performance,average_wake_time,$avg_wake_time" >> "$PERFORMANCE_LOG"
        echo "$timestamp,performance,total_requests,$total_requests" >> "$PERFORMANCE_LOG"
        echo "$timestamp,performance,success_rate,$success_rate" >> "$PERFORMANCE_LOG"
    fi

    # Get resource metrics
    local resource_metrics=$(curl -s "$SERVICE_MANAGER_URL/metrics/resources" 2>/dev/null || echo "{}")

    if [[ "$resource_metrics" != "{}" ]]; then
        local total_cpu=$(echo "$resource_metrics" | jq -r '.total_cpu // 0' 2>/dev/null || echo "0")
        local total_memory=$(echo "$resource_metrics" | jq -r '.total_memory // 0' 2>/dev/null || echo "0")
        local cost_savings=$(echo "$resource_metrics" | jq -r '.cost_savings // 0' 2>/dev/null || echo "0")

        echo "$timestamp,resource,total_cpu,$total_cpu" >> "$METRICS_LOG"
        echo "$timestamp,resource,total_memory,$total_memory" >> "$METRICS_LOG"
        echo "$timestamp,resource,cost_savings,$cost_savings" >> "$METRICS_LOG"
    fi
}

# Perform Health Checks
perform_health_checks() {
    local timestamp=$(date -Iseconds)
    local all_healthy=true

    # Check core services
    local core_services=(
        "gateway:$GATEWAY_URL/health"
        "service-manager:$SERVICE_MANAGER_URL/health"
        "tool-router:$TOOL_ROUTER_URL/health"
    )

    for service_info in "${core_services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d':' -f1)
        local service_url=$(echo "$service_info" | cut -d':' -f2-)

        local start_time=$(date +%s%N)
        local health_status="unhealthy"
        local response_time=0

        if curl -f -s "$service_url" > /dev/null 2>&1; then
            local end_time=$(date +%s%N)
            response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
            health_status="healthy"
        fi

        echo "$timestamp,health,$service_name,$health_status,$response_time" >> "$HEALTH_LOG"

        if [[ "$health_status" != "healthy" ]]; then
            log_alert "Health check failed for $service_name"
            all_healthy=false
        fi
    done

    # Check Service Manager API
    local sm_api_start=$(date +%s%N)
    if curl -f -s "$SERVICE_MANAGER_URL/services/status" > /dev/null 2>&1; then
        local sm_api_end=$(date +%s%N)
        local sm_api_response_time=$(( (sm_api_end - sm_api_start) / 1000000 ))
        echo "$timestamp,health,service_manager_api,healthy,$sm_api_response_time" >> "$HEALTH_LOG"
    else
        echo "$timestamp,health,service_manager_api,unhealthy,0" >> "$HEALTH_LOG"
        log_alert "Service Manager API health check failed"
        all_healthy=false
    fi

    # Check Docker daemon
    if docker info &> /dev/null; then
        echo "$timestamp,health,docker,healthy,0" >> "$HEALTH_LOG"
    else
        echo "$timestamp,health,docker,unhealthy,0" >> "$HEALTH_LOG"
        log_alert "Docker daemon health check failed"
        all_healthy=false
    fi

    # Check disk space
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -lt 90 ]]; then
        echo "$timestamp,health,disk_space,healthy,$disk_usage" >> "$HEALTH_LOG"
    else
        echo "$timestamp,health,disk_space,unhealthy,$disk_usage" >> "$HEALTH_LOG"
        log_alert "Disk space critically low: ${disk_usage}%"
        all_healthy=false
    fi

    return $([[ "$all_healthy" == "true" ]] && echo 0 || echo 1)
}

# Check for Alerts
check_alerts() {
    local timestamp=$(date -Iseconds)
    local alerts_triggered=false

    # Check CPU usage alerts
    local cpu_usage=$(tail -10 "$METRICS_LOG" | grep ",system,cpu," | tail -1 | cut -d',' -f4 | sed 's/%//' || echo "0")
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        log_alert "High CPU usage: ${cpu_usage}% (threshold: ${CPU_THRESHOLD}%)"
        echo "$timestamp,alert,high_cpu,${cpu_usage}" >> "$ALERT_LOG"
        alerts_triggered=true
    fi

    # Check memory usage alerts
    local memory_usage=$(tail -10 "$METRICS_LOG" | grep ",system,memory," | tail -1 | cut -d',' -f4 | sed 's/%//' || echo "0")
    if (( $(echo "$memory_usage > $MEMORY_THRESHOLD" | bc -l) )); then
        log_alert "High memory usage: ${memory_usage}% (threshold: ${MEMORY_THRESHOLD}%)"
        echo "$timestamp,alert,high_memory,${memory_usage}" >> "$ALERT_LOG"
        alerts_triggered=true
    fi

    # Check wake time alerts
    local wake_times=$(tail -10 "$METRICS_LOG" | grep ",service.*,wake_time," | tail -5 | cut -d',' -f4)
    for wake_time in $wake_times; do
        if [[ $wake_time -gt $WAKE_TIME_THRESHOLD ]]; then
            log_alert "Slow wake time: ${wake_time}ms (threshold: ${WAKE_TIME_THRESHOLD}ms)"
            echo "$timestamp,alert,slow_wake_time,${wake_time}" >> "$ALERT_LOG"
            alerts_triggered=true
        fi
    done

    # Check response time alerts
    local response_times=$(tail -10 "$METRICS_LOG" | grep ",service.*,response_time," | tail -5 | cut -d',' -f4)
    for response_time in $response_times; do
        if [[ $response_time -gt $RESPONSE_TIME_THRESHOLD ]]; then
            log_alert "Slow response time: ${response_time}ms (threshold: ${RESPONSE_TIME_THRESHOLD}ms)"
            echo "$timestamp,alert,slow_response_time,${response_time}" >> "$ALERT_LOG"
            alerts_triggered=true
        fi
    done

    # Check cost savings alerts
    local cost_savings=$(tail -10 "$METRICS_LOG" | grep ",resource,cost_savings," | tail -1 | cut -d',' -f4 | sed 's/%//' || echo "0")
    if (( $(echo "$cost_savings < $COST_SAVINGS_THRESHOLD" | bc -l) )); then
        log_alert "Low cost savings: ${cost_savings}% (threshold: ${COST_SAVINGS_THRESHOLD}%)"
        echo "$timestamp,alert,low_cost_savings,${cost_savings}" >> "$ALERT_LOG"
        alerts_triggered=true
    fi

    # Check service health alerts
    local unhealthy_services=$(tail -10 "$HEALTH_LOG" | grep ",unhealthy," | cut -d',' -f3 | sort -u)
    for service in $unhealthy_services; do
        log_alert "Unhealthy service: $service"
        echo "$timestamp,alert,unhealthy_service,$service" >> "$ALERT_LOG"
        alerts_triggered=true
    done

    return $([[ "$alerts_triggered" == "true" ]] && echo 1 || echo 0)
}

# Automated Response to Alerts
automated_response() {
    local timestamp=$(date -Iseconds)

    # Get recent alerts
    local recent_alerts=$(tail -20 "$ALERT_LOG" | grep "$(date -Iseconds | cut -d'T' -f1)")

    if [[ -n "$recent_alerts" ]]; then
        log "Processing automated responses for alerts..."

        # High CPU usage response
        local high_cpu_alerts=$(echo "$recent_alerts" | grep ",alert,high_cpu,")
        if [[ -n "$high_cpu_alerts" ]]; then
            log "Automated response: High CPU usage detected, sleeping low-priority services"

            # Sleep low-priority services
            local low_priority_services=$(curl -s "$SERVICE_MANAGER_URL/services/status" | jq -r 'to_entries[] | select(.value.sleep_policy.priority == "low" and .value.state == "running") | .key' 2>/dev/null || echo "")

            for service in $low_priority_services; do
                curl -X POST "$SERVICE_MANAGER_URL/services/$service/sleep" -s > /dev/null || log_warning "Failed to sleep $service"
                echo "$timestamp,response,sleep_low_priority,$service" >> "$ALERT_LOG"
            done
        fi

        # High memory usage response
        local high_memory_alerts=$(echo "$recent_alerts" | grep ",alert,high_memory,")
        if [[ -n "$high_memory_alerts" ]]; then
            log "Automated response: High memory usage detected, optimizing memory"

            # Reduce memory reservations for sleeping services
            local sleeping_services=$(curl -s "$SERVICE_MANAGER_URL/services/status" | jq -r 'to_entries[] | select(.value.state == "sleeping") | .key' 2>/dev/null || echo "")

            for service in $sleeping_services; do
                curl -X PUT "$SERVICE_MANAGER_URL/services/$service/sleep-policy" \
                     -H "Content-Type: application/json" \
                     -d '{"memory_reservation": "32MB"}' \
                     -s > /dev/null || log_warning "Failed to optimize memory for $service"
                echo "$timestamp,response,optimize_memory,$service" >> "$ALERT_LOG"
            done
        fi

        # Unhealthy service response
        local unhealthy_service_alerts=$(echo "$recent_alerts" | grep ",alert,unhealthy_service,")
        if [[ -n "$unhealthy_service_alerts" ]]; then
            log "Automated response: Unhealthy services detected, attempting recovery"

            echo "$unhealthy_service_alerts" | while IFS=',' read -r timestamp alert_type service; do
                if [[ -n "$service" ]]; then
                    log "Attempting to restart unhealthy service: $service"

                    # Try to restart the service
                    if [[ "$service" == "gateway" || "$service" == "service-manager" || "$service" == "tool-router" ]]; then
                        docker-compose -f docker-compose.scalable.yml restart "$service" || log_warning "Failed to restart $service"
                    else
                        curl -X POST "$SERVICE_MANAGER_URL/services/$service/restart" -s > /dev/null || log_warning "Failed to restart $service"
                    fi

                    echo "$timestamp,response,restart_service,$service" >> "$ALERT_LOG"
                fi
            done
        fi

        # Low cost savings response
        local low_cost_alerts=$(echo "$recent_alerts" | grep ",alert,low_cost_savings,")
        if [[ -n "$low_cost_alerts" ]]; then
            log "Automated response: Low cost savings detected, applying aggressive optimization"

            # Apply aggressive sleep policies
            curl -X POST "$SERVICE_MANAGER_URL/optimization/aggressive" -s > /dev/null || log_warning "Failed to apply aggressive optimization"
            echo "$timestamp,response,aggressive_optimization,enabled" >> "$ALERT_LOG"
        fi
    fi
}

# Generate Monitoring Dashboard
generate_dashboard() {
    local dashboard_file="monitoring/dashboards/dashboard-$(date +%Y%m%d-%H%M%S).html"

    cat > "$dashboard_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>MCP Gateway Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #333; }
        .metric { font-size: 2em; font-weight: bold; color: #2196F3; }
        .status { padding: 5px 10px; border-radius: 4px; color: white; font-size: 0.8em; }
        .status.healthy { background: #4CAF50; }
        .status.unhealthy { background: #f44336; }
        .status.warning { background: #ff9800; }
        .chart-container { position: relative; height: 200px; }
        .alert { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .alert.error { background: #f8d7da; border-color: #f5c6cb; }
    </style>
</head>
<body>
    <h1>MCP Gateway Monitoring Dashboard</h1>
    <div class="dashboard">
        <div class="card">
            <h3>System Status</h3>
            <div class="metric" id="system-status">Loading...</div>
            <div id="service-status"></div>
        </div>
        <div class="card">
            <h3>Resource Usage</h3>
            <div class="chart-container">
                <canvas id="resource-chart"></canvas>
            </div>
        </div>
        <div class="card">
            <h3>Performance Metrics</h3>
            <div class="chart-container">
                <canvas id="performance-chart"></canvas>
            </div>
        </div>
        <div class="card">
            <h3>Recent Alerts</h3>
            <div id="alerts"></div>
        </div>
    </div>

    <script>
        // This would be populated with real data from the monitoring system
        function updateDashboard() {
            // Update system status
            document.getElementById('system-status').innerHTML = 'Operational';

            // Update resource chart
            const resourceCtx = document.getElementById('resource-chart').getContext('2d');
            new Chart(resourceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['CPU', 'Memory', 'Disk'],
                    datasets: [{
                        data: [45, 62, 38],
                        backgroundColor: ['#2196F3', '#4CAF50', '#ff9800']
                    }]
                }
            });

            // Update performance chart
            const performanceCtx = document.getElementById('performance-chart').getContext('2d');
            new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['1m ago', '2m ago', '3m ago', '4m ago', '5m ago'],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [120, 115, 130, 125, 118],
                        borderColor: '#2196F3',
                        tension: 0.4
                    }]
                }
            });
        }

        updateDashboard();
        setInterval(updateDashboard, 60000); // Update every minute
    </script>
</body>
</html>
EOF

    log_success "Monitoring dashboard generated: $dashboard_file"
}

# Send Notifications
send_notifications() {
    local timestamp=$(date -Iseconds)

    # Get recent alerts
    local recent_alerts=$(tail -10 "$ALERT_LOG" | grep "$(date -Iseconds | cut -d'T' -f1)")

    if [[ -n "$recent_alerts" ]]; then
        log "Sending notifications for recent alerts..."

        # This would integrate with notification systems like:
        # - Email notifications
        # - Slack/webhook notifications
        # - SMS notifications
        # - Push notifications

        # For now, just log the notification
        echo "$timestamp,notification,alerts_sent,$(echo "$recent_alerts" | wc -l)" >> "$ALERT_LOG"
    fi
}

# Generate Monitoring Report
generate_monitoring_report() {
    local timestamp=$(date -Iseconds)
    local report_file="monitoring/reports/monitoring-report-$(date +%Y%m%d-%H%M%S).json"

    mkdir -p monitoring/reports

    # Collect metrics for the report
    local total_alerts=$(wc -l < "$ALERT_LOG" 2>/dev/null || echo "0")
    local critical_alerts=$(grep -c "alert,high_" "$ALERT_LOG" 2>/dev/null || echo "0")
    local warning_alerts=$(grep -c "alert,slow_" "$ALERT_LOG" 2>/dev/null || echo "0")

    local total_services=$(curl -s "$SERVICE_MANAGER_URL/services/status" | jq 'keys | length' 2>/dev/null || echo "0")
    local running_services=$(curl -s "$SERVICE_MANAGER_URL/services/status" | jq '[.[] | select(.state == "running")] | length' 2>/dev/null || echo "0")
    local sleeping_services=$(curl -s "$SERVICE_MANAGER_URL/services/status" | jq '[.[] | select(.state == "sleeping")] | length' 2>/dev/null || echo "0")

    # Generate report
    cat > "$report_file" << EOF
{
  "report": {
    "timestamp": "$timestamp",
    "type": "monitoring_summary",
    "version": "1.0.0"
  },
  "summary": {
    "total_alerts": $total_alerts,
    "critical_alerts": $critical_alerts,
    "warning_alerts": $warning_alerts,
    "total_services": $total_services,
    "running_services": $running_services,
    "sleeping_services": $sleeping_services,
    "uptime_percentage": $(( running_services * 100 / total_services ))
  },
  "alerts": [
EOF

    # Add recent alerts to report
    tail -20 "$ALERT_LOG" | while IFS=',' read -r timestamp alert_type alert_value; do
        echo "    {"
        echo "      \"timestamp\": \"$timestamp\","
        echo "      \"type\": \"$alert_type\","
        echo "      \"value\": \"$alert_value\""
        echo "    },"
    done | sed '$ s/,$//' >> "$report_file"

    cat >> "$report_file" << EOF
  ],
  "recommendations": [
EOF

    # Add recommendations based on alerts
    local recommendations=()

    if [[ $critical_alerts -gt 0 ]]; then
        recommendations+=("Address critical alerts immediately")
    fi

    if [[ $warning_alerts -gt 5 ]]; then
        recommendations+=("Review and optimize warning conditions")
    fi

    if [[ $running_services -lt $((total_services / 2)) ]]; then
        recommendations+=("Consider waking more services for better availability")
    fi

    local i=0
    for recommendation in "${recommendations[@]}"; do
        if [[ $i -gt 0 ]]; then
            echo "," >> "$report_file"
        fi
        echo "    \"$recommendation\"" >> "$report_file"
        ((i++))
    done

    cat >> "$report_file" << EOF
  ]
}
EOF

    log_success "Monitoring report generated: $report_file"
}

# Main Monitoring Loop
main() {
    local action=${1:-monitor}

    case $action in
        "init")
            init_monitoring
            ;;
        "monitor")
            log "Starting advanced monitoring..."

            while true; do
                # Collect metrics
                collect_system_metrics
                collect_service_metrics

                # Perform health checks
                perform_health_checks

                # Check for alerts
                check_alerts

                # Send notifications
                send_notifications

                log "Monitoring cycle completed. Next cycle in ${MONITORING_INTERVAL} seconds..."
                sleep $MONITORING_INTERVAL
            done
            ;;
        "check")
            perform_health_checks
            check_alerts
            ;;
        "alerts")
            check_alerts
            automated_response
            ;;
        "dashboard")
            generate_dashboard
            ;;
        "report")
            generate_monitoring_report
            ;;
        "response")
            automated_response
            ;;
        "notify")
            send_notifications
            ;;
        "all")
            init_monitoring
            collect_system_metrics
            collect_service_metrics
            perform_health_checks
            check_alerts
            automated_response
            generate_dashboard
            generate_monitoring_report
            ;;
        *)
            echo "Usage: $0 {init|monitor|check|alerts|dashboard|report|response|notify|all}"
            echo ""
            echo "Actions:"
            echo "  init      - Initialize monitoring directories"
            echo "  monitor   - Start continuous monitoring loop"
            echo "  check     - Perform health checks and alert detection"
            echo "  alerts    - Check alerts and trigger automated responses"
            echo "  dashboard - Generate monitoring dashboard"
            echo "  report    - Generate monitoring report"
            echo "  response  - Execute automated responses to alerts"
            echo "  notify    - Send notifications for alerts"
            echo "  all       - Run all monitoring functions once"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
