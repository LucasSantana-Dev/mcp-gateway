# Docker Security Report
Generated: Sat Feb 21 00:35:18 -03 2026

## Configuration
- Registry: ghcr.io/ibm
- Severity Threshold: medium
- Fail on Critical: true
- Fail on High: true

## Security Tools
- Trivy: Version: 0.69.1
- Grype: Application:         grype
Version:             0.109.0
BuildDate:           2026-02-18T21:40:23Z
GitCommit:           Homebrew
GitDescription:      [not provided]
Platform:            darwin/arm64
GoVersion:           go1.26.0
Compiler:            gc
Syft Version:        v1.42.1
Supported DB Schema: 6
- Dive: dive 0.13.1

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
