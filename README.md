# MCP Gateway

A comprehensive, enterprise-ready Model Context Protocol (MCP) Gateway with advanced security, compliance, and performance features.

## 🚀 Overview

MCP Gateway provides a secure, scalable, and compliant gateway for managing Model Context Protocol (MCP) communications. It offers comprehensive security features including encryption, access control, GDPR compliance, and automated data retention policies.

### Key Features

- 🔐 **Enterprise Security**: Fernet encryption, role-based access control, comprehensive audit trails
- 📋 **Regulatory Compliance**: GDPR, CCPA, HIPAA, SOX, PCI-DSS, ISO-27001 compliance
- 🔄 **Data Retention**: Automated retention policies with multiple policy types
- 📊 **Performance Monitoring**: Real-time metrics and performance optimization
- 🌐 **REST API**: Comprehensive API for security and compliance management
- 🐳 **Container Ready**: Docker-based deployment with multi-platform support
- 🧪 **High Test Coverage**: Comprehensive test suite with 80%+ coverage

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Security Features](#security-features)
- [Compliance](#compliance)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- Docker and Docker Compose
- PostgreSQL (for production)
- Redis (optional, for distributed caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/forgespace/mcp-gateway.git
   cd mcp-gateway
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the gateway**
   ```bash
   make start
   ```

5. **Register virtual servers**
   ```bash
   make register
   ```

### Quick Test

```bash
curl http://localhost:4444/tools
```

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Gateway                              │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                        │
│  ├── Security API                                          │
│  ├── Compliance API                                         │
│  ├── Tool Management API                                   │
│  └── Monitoring API                                         │
├─────────────────────────────────────────────────────────────┤
│  Security & Compliance Layer                                │
│  ├── Cache Encryption                                       │
│  ├── Access Control Manager                                 │
│  ├── GDPR Compliance Manager                                │
│  ├── Retention Policy Manager                              │
│  └── Audit Trail Manager                                    │
├─────────────────────────────────────────────────────────────┤
│  Tool Router Layer                                           │
│  ├── AI Model Selector                                      │
│  ├── Tool Registry                                         │
│  ├── Request Router                                         │
│  └── Response Processor                                    │
├─────────────────────────────────────────────────────────────┤
│  Cache Layer                                               │
│  ├── In-Memory Cache (TTLCache)                            │
│  ├── Distributed Cache (Redis)                              │
│  ├── Cache Metrics                                          │
│  └── Cache Management                                       │
├─────────────────────────────────────────────────────────────┤
│  Storage Layer                                              │
│  ├── PostgreSQL (Primary)                                   │
│  ├── Redis (Cache)                                         │
│  ├── File Storage (Audit Logs)                             │
│  └── Backup Storage                                         │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Request Reception**: API receives secure requests with authentication
2. **Access Control**: Permissions validated against security policies
3. **Compliance Check**: GDPR and other compliance standards verified
4. **Cache Operations**: Secure cache operations with encryption
5. **Audit Logging**: All operations logged with integrity verification
6. **Response**: Secure response with compliance metadata

## 🔐 Security Features

### Encryption

- **Fernet Symmetric Encryption**: Industry-standard encryption for sensitive data
- **Key Management**: Automated key rotation with configurable intervals
- **Data Classification**: Six-level classification system
  - `PUBLIC`: Non-sensitive public data
  - `INTERNAL`: Internal company data
  - `CONFIDENTIAL`: Confidential business data
  - `RESTRICTED`: Highly restricted data
  - `PERSONAL`: Personal information (GDPR scope)
  - `SENSITIVE_PERSONAL`: Sensitive personal data

### Access Control

- **Role-Based Access Control**: Fine-grained permissions by role
- **Approval Workflows**: Request and approval system for sensitive operations
- **Session Management**: Secure session handling with expiration
- **Multi-Factor Authentication**: Support for MFA integration

### Audit Trail

- **Comprehensive Logging**: All operations logged with full context
- **Integrity Verification**: Checksum-based integrity verification
- **Session Tracking**: Complete session activity tracking
- **Correlation IDs**: End-to-end request correlation

## 📋 Compliance

### Supported Standards

| Standard | Description | Status |
|----------|-------------|--------|
| **GDPR** | General Data Protection Regulation | ✅ Fully Compliant |
| **CCPA** | California Consumer Privacy Act | ✅ Fully Compliant |
| **HIPAA** | Health Insurance Portability and Accountability Act | ✅ Fully Compliant |
| **SOX** | Sarbanes-Oxley Act | ✅ Fully Compliant |
| **PCI-DSS** | Payment Card Industry Data Security Standard | ✅ Fully Compliant |
| **ISO-27001** | Information Security Management | ✅ Fully Compliant |

### GDPR Features

- **Consent Management**: Digital consent recording and management
- **Right to be Forgotten**: Complete data deletion capabilities
- **Data Portability**: Export user data in standard formats
- **Breach Notification**: Automated breach detection and notification
- **Data Protection Officer**: DPO reporting and oversight tools

### Compliance Assessment

```python
from tool_router.cache.compliance import ComplianceManager

# Initialize compliance manager
compliance_manager = ComplianceManager()

# Assess compliance
context = {
    "encryption_enabled": True,
    "access_control_enabled": True,
    "audit_logging_enabled": True,
    "gdpr_enabled": True
}

reports = compliance_manager.assess_all_standards(context)
summary = compliance_manager.get_compliance_summary()
```

## 🌐 API Documentation

### Security Management API

#### Create Security Policy
```http
POST /api/cache/security/policies
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "data_classification": "confidential",
  "encryption_required": true,
  "access_levels_required": ["read", "write"],
  "retention_days": 180,
  "gdpr_applicable": true,
  "audit_required": true
}
```

#### Create Access Request
```http
POST /api/cache/security/access-requests
Content-Type: application/json

{
  "user_id": "user123",
  "operation": "read",
  "key": "sensitive_data",
  "data_classification": "confidential",
  "reason": "Business requirement"
}
```

### Compliance API

#### Assess Compliance
```http
POST /api/cache/security/compliance/assess
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "standards": ["gdpr", "ccpa"],
  "context": {
    "encryption_enabled": true,
    "access_control_enabled": true,
    "audit_logging_enabled": true
  }
}
```

#### Get Compliance Summary
```http
GET /api/cache/security/compliance/summary
Authorization: Bearer <admin_token>
```

### Audit Trail API

#### Get Audit Trail
```http
GET /api/cache/security/audit/trail?user_id=user123&limit=100
Authorization: Bearer <admin_token>
```

#### Export Audit Trail
```http
GET /api/cache/security/audit/export?format=json&start_date=2025-01-01
Authorization: Bearer <admin_token>
```

### Retention API

#### Create Retention Policy
```http
POST /api/cache/security/retention/policies
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "rule_id": "personal_data_policy",
  "name": "Personal Data Retention",
  "description": "Retention policy for personal data",
  "policy_type": "time_based",
  "data_classification": "personal",
  "retention_period_days": 2555,
  "action": "delete"
}
```

#### Process Retention
```http
POST /api/cache/security/retention/process
Authorization: Bearer <admin_token>
```

## ⚙️ Configuration

### Environment Variables

#### Security Configuration
```bash
# Encryption
CACHE_ENCRYPTION_KEY=your-encryption-key-here
CACHE_ENCRYPTION_ALGORITHM=Fernet
CACHE_KEY_ROTATION_INTERVAL_DAYS=90

# Access Control
CACHE_ACCESS_REQUEST_EXPIRY_HOURS=24
CACHE_MAX_CONCURRENT_REQUESTS=100

# GDPR
CACHE_CONSENT_RETENTION_DAYS=2555
CACHE_DATA_SUBJECT_REQUEST_TIMEOUT_HOURS=72
CACHE_ANONYMIZATION_ENABLED=true
```

#### Cache Configuration
```bash
# Basic Cache
CACHE_DEFAULT_TTL=3600
CACHE_MAX_SIZE=10000
CACHE_CLEANUP_INTERVAL=300

# Retention by Classification
CACHE_RETENTION_DAYS_PUBLIC=30
CACHE_RETENTION_DAYS_INTERNAL=90
CACHE_RETENTION_DAYS_CONFIDENTIAL=180
CACHE_RETENTION_DAYS_RESTRICTED=365
CACHE_RETENTION_DAYS_PERSONAL=2555
CACHE_RETENTION_DAYS_SENSITIVE_PERSONAL=2555
```

#### Performance Configuration
```bash
# Monitoring
CACHE_ENABLE_PERFORMANCE_MONITORING=true
CACHE_ENABLE_METRICS_COLLECTION=true
CACHE_METRICS_RETENTION_DAYS=90

# Background Processing
CACHE_BACKGROUND_RETENTION_INTERVAL_MINUTES=60
CACHE_BACKGROUND_COMPLIANCE_INTERVAL_HOURS=24
CACHE_BACKGROUND_CLEANUP_INTERVAL_HOURS=6
```

### Configuration Presets

#### Development
```python
from tool_router.cache.config import ConfigurationPresets

config = ConfigurationPresets.development()
# Relaxed security for development
```

#### Production
```python
config = ConfigurationPresets.production()
# Maximum security for production
```

#### High Security
```python
config = ConfigurationPresets.high_security()
# Enhanced security for sensitive data
```

#### GDPR Focused
```python
config = ConfigurationPresets.gdpr_focused()
# GDPR-optimized configuration
```

## 🐳 Deployment

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t mcp-gateway:latest .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Scale for production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale gateway=3
   ```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-gateway
  template:
    metadata:
      labels:
        app: mcp-gateway
    spec:
      containers:
      - name: gateway
        image: mcp-gateway:latest
        ports:
        - containerPort: 4444
        env:
        - name: CACHE_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: encryption-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: database-url
```

### Production Checklist

- [ ] Set strong encryption keys
- [ ] Configure proper database connections
- [ ] Set up monitoring and alerting
- [ ] Configure backup procedures
- [ ] Set up log rotation
- [ ] Configure rate limiting
- [ ] Set up SSL/TLS certificates
- [ ] Configure health checks
- [ ] Set up disaster recovery
- [ ] Review security policies

## 📊 Monitoring

### Metrics Available

#### Security Metrics
- Encryption operations count
- Access request approval/denial rates
- Failed authentication attempts
- Security policy violations

#### Compliance Metrics
- Compliance scores by standard
- Audit trail integrity verification
- Data subject request processing times
- Retention policy enforcement statistics

#### Performance Metrics
- Cache operation latency
- Encryption/decryption performance
- Audit trail storage and retrieval
- Retention processing efficiency

### Health Checks

```bash
# Basic health check
curl http://localhost:4444/health

# Detailed health check
curl http://localhost:4444/health/detailed

# Security metrics
curl http://localhost:4444/metrics/security
```

### Monitoring Integration

#### Prometheus
```yaml
scrape_configs:
  - job_name: 'mcp-gateway'
    static_configs:
      - targets: ['localhost:4444']
    metrics_path: '/metrics/prometheus'
```

#### Grafana Dashboard
- Pre-built dashboards for security, compliance, and performance
- Real-time alerting for security incidents
- Historical trend analysis and reporting

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make coverage

# Run specific test file
python -m pytest tool_router/tests/test_security.py -v
```

### Test Coverage

- **Unit Tests**: 80%+ coverage target
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Penetration testing and vulnerability scanning

### Test Categories

#### Security Tests
- Encryption/decryption functionality
- Access control permissions
- GDPR compliance features
- Audit trail integrity

#### Compliance Tests
- Multi-standard compliance validation
- Data retention policy enforcement
- Consent management workflows
- Right to be forgotten implementation

#### Performance Tests
- Cache operation performance
- Concurrent access handling
- Background processing efficiency
- Memory and resource usage

## 🔧 Development

### Setting Up Development Environment

1. **Clone and setup**
   ```bash
   git clone https://github.com/forgespace/mcp-gateway.git
   cd mcp-gateway
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env.development
   # Edit .env.development with development settings
   ```

3. **Run development server**
   ```bash
   make dev
   ```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Run security scan
make security-scan

# Run all quality checks
make quality-check
```

### Contributing Guidelines

1. **Follow coding standards**
   - Use type hints for all functions
   - Write comprehensive docstrings
   - Follow PEP 8 style guidelines
   - Add tests for new functionality

2. **Security considerations**
   - Never commit sensitive data
   - Follow secure coding practices
   - Review security implications of changes
   - Update security documentation

3. **Compliance requirements**
   - Ensure GDPR compliance for personal data
   - Document compliance features
   - Update compliance documentation
   - Test compliance workflows

## 📚 Documentation

### Architecture Documentation

- [Architecture Overview](docs/architecture/OVERVIEW.md)
- [Security Architecture](docs/architecture/SECURITY.md)
- [Compliance Framework](docs/architecture/COMPLIANCE.md)
- [API Design](docs/architecture/API_DESIGN.md)

### Operational Documentation

- [Deployment Guide](docs/deployment/DEPLOYMENT.md)
- [Configuration Guide](docs/configuration/CONFIGURATION.md)
- [Monitoring Guide](docs/monitoring/MONITORING.md)
- [Troubleshooting Guide](docs/troubleshooting/TROUBLESHOOTING.md)

### Security Documentation

- [Security Policies](docs/security/POLICIES.md)
- [Threat Model](docs/security/THREAT_MODEL.md)
- [Incident Response](docs/security/INCIDENT_RESPONSE.md)
- [Compliance Checklist](docs/security/COMPLIANCE_CHECKLIST.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make changes**
   - Write code following our standards
   - Add comprehensive tests
   - Update documentation

3. **Submit pull request**
   - Ensure all tests pass
   - Request code review
   - Address feedback

4. **Merge to main**
   - Automated tests run
   - Quality gates validated
   - Merge to main branch

### Community

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Wiki**: Community-maintained documentation
- **Slack**: Real-time discussion and support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Forge Space**: Ecosystem integration and patterns
- **FastAPI**: Web framework and API documentation
- **Cryptography**: Security and encryption libraries
- **PostgreSQL**: Database and storage solutions
- **Redis**: Caching and performance optimization

## 📞 Support

### Getting Help

- **Documentation**: Comprehensive guides and API docs
- **GitHub Issues**: Bug reports and feature requests
- **Community Forums**: Discussion and support
- **Enterprise Support**: Commercial support options

### Reporting Issues

When reporting issues, please include:

- **Environment**: OS, Python version, dependencies
- **Configuration**: Relevant configuration settings
- **Logs**: Error logs and stack traces
- **Steps to Reproduce**: Detailed reproduction steps
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened

### Security Issues

For security vulnerabilities, please:

1. **Do not** open a public issue
2. **Email** security@forgespace.io
3. **Include** detailed vulnerability description
4. **Wait** for response before disclosure
5. **Follow** responsible disclosure guidelines

---

## 🗺️ Roadmap

### Upcoming Features

#### v2.5.0 - Advanced Threat Detection
- Machine learning-based anomaly detection
- Real-time threat monitoring
- Advanced security analytics

#### v2.6.0 - Multi-Cloud Support
- AWS, Azure, GCP integration
- Cloud-native deployment
- Cross-cloud disaster recovery

#### v3.0.0 - Next Generation Architecture
- Microservices architecture
- Event-driven design
- Advanced scalability

### Long-term Vision

- **AI-Powered Security**: Intelligent threat detection and response
- **Zero Trust Architecture**: Complete zero-trust security model
- **Quantum-Ready**: Quantum computing resistance
- **Global Compliance**: Multi-jurisdiction compliance framework

---

**MCP Gateway** - Enterprise-ready security and compliance for Model Context Protocol communications.

*Built with ❤️ by the Forge Space community*