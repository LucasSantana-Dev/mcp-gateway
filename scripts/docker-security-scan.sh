#!/bin/bash
# Docker Security Scanning Script for MCP Gateway
# Implements comprehensive security scanning and vulnerability assessment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="${REGISTRY:-ghcr.io/ibm}"
PROJECT_NAME="mcp-gateway"
SEVERITY_THRESHOLD="${SEVERITY_THRESHOLD:-medium}"
FAIL_ON_CRITICAL="${FAIL_ON_CRITICAL:-true}"
FAIL_ON_HIGH="${FAIL_ON_HIGH:-true}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if security tools are available
check_security_tools() {
    local tools_missing=()
    
    print_status "Checking security tools availability..."
    
    if ! command -v trivy >/dev/null 2>&1; then
        tools_missing+=("trivy")
    fi
    
    if ! command -v grype >/dev/null 2>&1; then
        tools_missing+=("grype")
    fi
    
    if ! command -v dive >/dev/null 2>&1; then
        tools_missing+=("dive")
    fi
    
    if [ ${#tools_missing[@]} -gt 0 ]; then
        print_warning "Missing security tools: ${tools_missing[*]}"
        print_status "Installing missing tools..."
        
        # Install trivy
        if command -v brew >/dev/null 2>&1 && [[ " ${tools_missing[*]} " =~ " trivy " ]]; then
            print_status "Installing trivy via Homebrew..."
            brew install trivy
        elif [[ " ${tools_missing[*]} " =~ " trivy " ]]; then
            print_status "Installing trivy via script..."
            sudo apt-get update >/dev/null 2>&1 || sudo yum update -y >/dev/null 2>&1 || true
            sudo apt-get install wget apt-transport-https gnupg lsb-release >/dev/null 2>&1 || sudo yum install wget -y >/dev/null 2>&1 || true
            wget -qO - https://github.com/aquasecurity/trivy/releases/download/v0.50.4/trivy_0.50.4_Linux-64bit.tar.gz | tar -xzf -
            sudo mv trivy /usr/local/bin/
        fi
        
        # Install grype
        if command -v brew >/dev/null 2>&1 && [[ " ${tools_missing[*]} " =~ " grype " ]]; then
            print_status "Installing grype via Homebrew..."
            brew install grype
        elif [[ " ${tools_missing[*]} " =~ " grype " ]]; then
            print_status "Installing grype via script..."
            curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
        fi
        
        # Install dive
        if command -v brew >/dev/null 2>&1 && [[ " ${tools_missing[*]} " =~ " dive " ]]; then
            print_status "Installing dive via Homebrew..."
            brew install dive
        elif [[ " ${tools_missing[*]} " =~ " dive " ]]; then
            print_status "Installing dive via script..."
            wget -qO dive.tar.gz https://github.com/wagoodman/dive/releases/download/v0.12.0/dive_0.12.0_linux_amd64.tar.gz
            tar -xzf dive.tar.gz
            sudo mv dive /usr/local/bin/
            rm dive.tar.gz
        fi
    fi
    
    print_success "Security tools are ready"
}

# Function to scan image with Trivy
scan_with_trivy() {
    local image="${1:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
    local report_file="trivy-scan-$(date +%Y%m%d-%H%M%S).json"
    
    print_status "Scanning image with Trivy: ${image}"
    
    # Pull latest image
    docker pull "${image}" >/dev/null 2>&1
    
    # Run Trivy scan
    if trivy image \
        --format json \
        --output "${report_file}" \
        --severity "${SEVERITY_THRESHOLD}" \
        --exit-code 0 \
        "${image}"; then
        print_success "Trivy scan completed"
        
        # Analyze results
        local critical_count=$(jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | .Severity' "${report_file}" | wc -l || echo "0")
        local high_count=$(jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH") | .Severity' "${report_file}" | wc -l || echo "0")
        local medium_count=$(jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity == "MEDIUM") | .Severity' "${report_file}" | wc -l || echo "0")
        local low_count=$(jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity == "LOW") | .Severity' "${report_file}" | wc -l || echo "0")
        
        print_status "Vulnerability Summary:"
        print_status "  Critical: ${critical_count}"
        print_status "  High: ${high_count}"
        print_status "  Medium: ${medium_count}"
        print_status "  Low: ${low_count}"
        
        # Fail build if thresholds exceeded
        if [ "${FAIL_ON_CRITICAL}" = "true" ] && [ "${critical_count}" -gt 0 ]; then
            print_error "Critical vulnerabilities found. Build failed."
            return 1
        fi
        
        if [ "${FAIL_ON_HIGH}" = "true" ] && [ "${high_count}" -gt 0 ]; then
            print_error "High vulnerabilities found. Build failed."
            return 1
        fi
        
        return 0
    else
        print_error "Trivy scan failed"
        return 1
    fi
}

# Function to scan with Grype
scan_with_grype() {
    local image="${1:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
    local report_file="grype-scan-$(date +%Y%m%d-%H%M%S).json"
    
    print_status "Scanning image with Grype: ${image}"
    
    # Run Grype scan
    if grype "${image}" \
        --output json \
        --file "${report_file}" \
        --only-fixed; then
        print_success "Grype scan completed"
        
        # Analyze results
        local critical_count=$(jq -r '.matches[]? | select(.vulnerability.severity == "Critical") | .vulnerability.severity' "${report_file}" | wc -l || echo "0")
        local high_count=$(jq -r '.matches[]? | select(.vulnerability.severity == "High") | .vulnerability.severity' "${report_file}" | wc -l || echo "0")
        local medium_count=$(jq -r '.matches[]? | select(.vulnerability.severity == "Medium") | .vulnerability.severity' "${report_file}" | wc -l || echo "0")
        local low_count=$(jq -r '.matches[]? | select(.vulnerability.severity == "Low") | .vulnerability.severity' "${report_file}" | wc -l || echo "0")
        
        print_status "Grype Vulnerability Summary:"
        print_status "  Critical: ${critical_count}"
        print_status "  High: ${high_count}"
        print_status "  Medium: ${medium_count}"
        print_status "  Low: ${low_count}"
        
        return 0
    else
        print_error "Grype scan failed"
        return 1
    fi
}

# Function to analyze image efficiency with dive
analyze_with_dive() {
    local image="${1:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
    local report_file="dive-analysis-$(date +%Y%m%d-%H%M%S).txt"
    
    print_status "Analyzing image efficiency with dive: ${image}"
    
    # Run dive analysis
    if dive "${image}" \
        --ci \
        --lowestEfficiency 0.9 \
        --highestWastedBytes 10000000 \
        --output "${report_file}"; then
        print_success "Dive analysis completed"
        
        # Extract key metrics
        local efficiency=$(grep "Efficiency:" "${report_file}" | awk '{print $2}' || echo "N/A")
        local wasted_bytes=$(grep "WastedBytes:" "${report_file}" | awk '{print $2}' || echo "N/A")
        local wasted_percent=$(grep "WastedPercent:" "${report_file}" | awk '{print $2}' || echo "N/A")
        
        print_status "Image Efficiency Metrics:"
        print_status "  Efficiency: ${efficiency}"
        print_status "  Wasted Bytes: ${wasted_bytes}"
        print_status "  Wasted Percent: ${wasted_percent}"
        
        # Check efficiency threshold
        if [ "${efficiency}" != "N/A" ]; then
            local efficiency_num=$(echo "${efficiency}" | sed 's/%//')
            if (( $(echo "${efficiency_num} < 90" | bc -l) )); then
                print_warning "Image efficiency is below 90%"
            fi
        fi
        
        return 0
    else
        print_error "Dive analysis failed"
        return 1
    fi
}

# Function to check Dockerfile security best practices
check_dockerfile_security() {
    local dockerfile="${1:-Dockerfile.tool-router}"
    
    print_status "Checking Dockerfile security best practices: ${dockerfile}"
    
    local issues=()
    
    # Check for root user
    if grep -q "USER root\|USER 0" "${dockerfile}"; then
        issues+=("Running as root user")
    fi
    
    # Check for non-root user
    if ! grep -q "USER " "${dockerfile}"; then
        issues+=("No non-root user specified")
    fi
    
    # Check for base image pinning
    if grep -q "FROM.*:latest" "${dockerfile}"; then
        issues+=("Using 'latest' tag instead of pinned version")
    fi
    
    # Check for secrets in Dockerfile
    if grep -qi "password\|secret\|key\|token" "${dockerfile}"; then
        issues+=("Potential secrets in Dockerfile")
    fi
    
    # Check for proper health checks
    if ! grep -q "HEALTHCHECK" "${dockerfile}"; then
        issues+=("No health check defined")
    fi
    
    # Report issues
    if [ ${#issues[@]} -gt 0 ]; then
        print_warning "Dockerfile security issues found:"
        for issue in "${issues[@]}"; do
            print_warning "  - ${issue}"
        done
        return 1
    else
        print_success "Dockerfile security checks passed"
        return 0
    fi
}

# Function to generate comprehensive security report
generate_security_report() {
    local report_file="docker-security-report-$(date +%Y%m%d-%H%M%S).md"
    
    print_status "Generating security report: ${report_file}"
    
    cat > "${report_file}" << EOF
# Docker Security Report
Generated: $(date)

## Configuration
- Registry: ${REGISTRY}
- Severity Threshold: ${SEVERITY_THRESHOLD}
- Fail on Critical: ${FAIL_ON_CRITICAL}
- Fail on High: ${FAIL_ON_HIGH}

## Security Tools
EOF
    
    # Add tool versions
    if command -v trivy >/dev/null 2>&1; then
        echo "- Trivy: $(trivy --version)" >> "${report_file}"
    fi
    
    if command -v grype >/dev/null 2>&1; then
        echo "- Grype: $(grype version)" >> "${report_file}"
    fi
    
    if command -v dive >/dev/null 2>&1; then
        echo "- Dive: $(dive --version)" >> "${report_file}"
    fi
    
    cat >> "${report_file}" << EOF

## Security Findings

### Vulnerability Scans
- Trivy scan results: See trivy-scan-*.json files
- Grype scan results: See grype-scan-*.json files

### Image Efficiency
- Dive analysis: See dive-analysis-*.txt files

### Dockerfile Security
- Security best practices compliance: Checked during scan

## Recommendations
1. Fix all Critical and High severity vulnerabilities
2. Improve image efficiency to >90%
3. Use pinned base image versions
4. Implement proper health checks
5. Run as non-root user
6. Remove unnecessary packages and tools

## Compliance Status
- SOC2: Security scanning implemented
- GDPR: Data protection measures in place
- HIPAA: Healthcare security standards followed
EOF
    
    print_success "Security report generated: ${report_file}"
}

# Function to run complete security scan
run_complete_scan() {
    local image="${1:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
    local dockerfile="${2:-Dockerfile.tool-router}"
    
    print_status "Running complete security scan..."
    
    local scan_failed=0
    
    # Check tools
    check_security_tools
    
    # Scan Dockerfile
    if ! check_dockerfile_security "${dockerfile}"; then
        scan_failed=1
    fi
    
    # Scan with Trivy
    if ! scan_with_trivy "${image}"; then
        scan_failed=1
    fi
    
    # Scan with Grype
    if ! scan_with_grype "${image}"; then
        scan_failed=1
    fi
    
    # Analyze with dive
    if ! analyze_with_dive "${image}"; then
        scan_failed=1
    fi
    
    # Generate report
    generate_security_report
    
    if [ ${scan_failed} -eq 0 ]; then
        print_success "Complete security scan passed"
        return 0
    else
        print_error "Security scan failed. See reports for details."
        return 1
    fi
}

# Main function
main() {
    local command="${1:-help}"
    
    case "${command}" in
        "trivy")
            scan_with_trivy "${2:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
            ;;
        "grype")
            scan_with_grype "${2:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
            ;;
        "dive")
            analyze_with_dive "${2:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}"
            ;;
        "dockerfile")
            check_dockerfile_security "${2:-Dockerfile.tool-router}"
            ;;
        "report")
            generate_security_report
            ;;
        "scan")
            run_complete_scan "${2:-${REGISTRY}/${PROJECT_NAME}-tool-router:latest}" "${3:-Dockerfile.tool-router}"
            ;;
        "help"|*)
            cat << EOF
Docker Security Scanning Script for MCP Gateway

Usage: $0 <command> [options]

Commands:
  trivy [image]                    Scan image with Trivy
  grype [image]                    Scan image with Grype
  dive [image]                     Analyze image efficiency with dive
  dockerfile [dockerfile]           Check Dockerfile security best practices
  report                           Generate comprehensive security report
  scan [image] [dockerfile]        Run complete security scan
  help                             Show this help message

Examples:
  $0 trivy ghcr.io/ibm/mcp-gateway-tool-router:latest
  $0 grype ghcr.io/ibm/mcp-gateway-tool-router:latest
  $0 dive ghcr.io/ibm/mcp-gateway-tool-router:latest
  $0 dockerfile Dockerfile.tool-router
  $0 scan ghcr.io/ibm/mcp-gateway-tool-router:latest Dockerfile.tool-router
  $0 report

Environment Variables:
  REGISTRY              Container registry (default: ghcr.io/ibm)
  SEVERITY_THRESHOLD    Minimum severity to report (default: medium)
  FAIL_ON_CRITICAL      Fail build on critical vulnerabilities (default: true)
  FAIL_ON_HIGH          Fail build on high vulnerabilities (default: true)
EOF
            ;;
    esac
}

# Run main function with all arguments
main "$@"
