"""
Cache Security API Module

This module provides FastAPI endpoints for cache security and compliance management:
- Security management endpoints
- Compliance management endpoints
- Audit trail endpoints
- Retention management endpoints
- Configuration management endpoints

Key Components:
- CacheSecurityAPI: Main FastAPI application
- SecurityEndpoints: Security management endpoints
- ComplianceEndpoints: Compliance management endpoints
- AuditEndpoints: Audit trail endpoints
- RetentionEndpoints: Retention management endpoints
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, Depends, Query, Body, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

from .security import CacheSecurityManager
from .compliance import ComplianceManager
from .retention import RetentionPolicyManager, LifecycleManager, RetentionScheduler, RetentionAuditor
from .config import CacheConfig
from .types import (
    DataClassification, AccessLevel, ComplianceStandard, SecurityPolicy,
    AccessRequest, ConsentRecord, AuditEntry, CacheEntryMetadata, SecurityMetrics,
    CacheOperationResult, CacheSecurityError, EncryptionError,
    AccessControlError, ComplianceError, RetentionError, AuditError
)


# Pydantic models for API requests/responses
class EncryptionRequest(BaseModel):
    """Encryption request model."""
    data: str = Field(..., description="Data to encrypt")
    classification: DataClassification = Field(..., description="Data classification")


class EncryptionResponse(BaseModel):
    """Encryption response model."""
    encrypted_data: str = Field(..., description="Encrypted data")
    encryption_id: str = Field(..., description="Encryption operation ID")
    timestamp: datetime = Field(..., description="Encryption timestamp")


class DecryptionRequest(BaseModel):
    """Decryption request model."""
    encrypted_data: str = Field(..., description="Encrypted data to decrypt")
    encryption_id: str = Field(..., description="Encryption operation ID")


class DecryptionResponse(BaseModel):
    """Decryption response model."""
    decrypted_data: str = Field(..., description="Decrypted data")
    timestamp: datetime = Field(..., description="Decryption timestamp")


class AccessControlRequest(BaseModel):
    """Access control request model."""
    user_id: str = Field(..., description="User ID")
    resource_id: str = Field(..., description="Resource ID")
    required_level: AccessLevel = Field(..., description="Required access level")
    context: Dict[str, Any] = Field(default_factory=dict, description="Access context")


class AccessControlResponse(BaseModel):
    """Access control response model."""
    granted: bool = Field(..., description="Access granted status")
    reason: str = Field(..., description="Access decision reason")
    timestamp: datetime = Field(..., description="Access check timestamp")


class ConsentRequest(BaseModel):
    """Consent request model."""
    subject_id: str = Field(..., description="Data subject ID")
    data_types: List[str] = Field(..., description="Data types for consent")
    purposes: List[str] = Field(..., description="Purposes for data processing")
    legal_basis: str = Field(default="consent", description="Legal basis for processing")


class ConsentResponse(BaseModel):
    """Consent response model."""
    consent_id: str = Field(..., description="Consent record ID")
    granted: bool = Field(..., description="Consent granted status")
    timestamp: datetime = Field(..., description="Consent timestamp")


class DataSubjectRequestModel(BaseModel):
    """Data subject request model."""
    request_type: str = Field(..., description="Request type")
    subject_id: str = Field(..., description="Data subject ID")
    subject_contact: str = Field(..., description="Subject contact information")
    description: str = Field(..., description="Request description")


class RetentionPolicyRequest(BaseModel):
    """Retention policy request model."""
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    data_classification: DataClassification = Field(..., description="Data classification")
    retention_days: int = Field(..., description="Retention period in days")
    action: str = Field(..., description="Retention action")


class AuditQueryRequest(BaseModel):
    """Audit query request model."""
    event_type: Optional[str] = Field(None, description="Event type filter")
    user_id: Optional[str] = Field(None, description="User ID filter")
    resource_id: Optional[str] = Field(None, description="Resource ID filter")
    start_time: Optional[datetime] = Field(None, description="Start time filter")
    end_time: Optional[datetime] = Field(None, description="End time filter")
    limit: int = Field(default=100, description="Result limit")


class SecurityConfigRequest(BaseModel):
    """Security configuration request model."""
    encryption_enabled: bool = Field(default=True, description="Enable encryption")
    audit_enabled: bool = Field(default=True, description="Enable audit logging")
    retention_days: Dict[str, int] = Field(default_factory=dict, description="Retention periods")


# Security dependency
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user from JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # In a real implementation, you would validate the JWT token
    # For now, we'll extract the user ID from the token
    try:
        # This is a placeholder for actual JWT validation
        user_id = "admin"  # Default user for demo
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


class CacheSecurityAPI:
    """Main FastAPI application for cache security."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize the API."""
        self.config = config or CacheConfig()
        self.app = FastAPI(
            title="Cache Security API",
            description="Security and compliance management for MCP Gateway cache",
            version="2.4.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Initialize managers
        self.security_manager = CacheSecurityManager(self.config)
        self.compliance_manager = ComplianceManager(self.config)
        self.retention_manager = RetentionPolicyManager(self.config)
        self.lifecycle_manager = LifecycleManager(self.config)
        self.retention_scheduler = RetentionScheduler(self.retention_manager, self.config)
        self.retention_auditor = RetentionAuditor(self.retention_manager, self.config)
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Start retention scheduler
        self.retention_scheduler.start()
    
    def _setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.4.0"
            }
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Get security metrics."""
            try:
                security_metrics = self.security_manager.get_metrics()
                compliance_metrics = self.compliance_manager.get_metrics()
                retention_metrics = self.retention_manager.get_metrics()
                
                return {
                    "security": asdict(security_metrics),
                    "compliance": asdict(compliance_metrics),
                    "retention": asdict(retention_metrics),
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")
        
        # Encryption endpoints
        @self.app.post("/security/encrypt", response_model=EncryptionResponse)
        async def encrypt_data(request: EncryptionRequest, user_id: str = Depends(get_current_user)):
            """Encrypt data."""
            try:
                result = self.security_manager.encrypt_data(request.data, request.classification)
                
                return EncryptionResponse(
                    encrypted_data=result.encrypted_data,
                    encryption_id=result.operation_id,
                    timestamp=result.timestamp
                )
            except EncryptionError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")
        
        @self.app.post("/security/decrypt", response_model=DecryptionResponse)
        async def decrypt_data(request: DecryptionRequest, user_id: str = Depends(get_current_user)):
            """Decrypt data."""
            try:
                result = self.security_manager.decrypt_data(request.encrypted_data, request.encryption_id)
                
                return DecryptionResponse(
                    decrypted_data=result.decrypted_data,
                    timestamp=result.timestamp
                )
            except EncryptionError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
        
        # Access control endpoints
        @self.app.post("/security/access-check", response_model=AccessControlResponse)
        async def check_access(request: AccessControlRequest, user_id: str = Depends(get_current_user)):
            """Check access permissions."""
            try:
                result = self.security_manager.check_access(
                    request.user_id,
                    request.resource_id,
                    request.required_level,
                    request.context
                )
                
                return AccessControlResponse(
                    granted=result.access_granted,
                    reason=result.reason,
                    timestamp=result.timestamp
                )
            except AccessControlError as e:
                raise HTTPException(status_code=403, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Access check failed: {str(e)}")
        
        # Compliance endpoints
        @self.app.post("/compliance/consent", response_model=ConsentResponse)
        async def record_consent(request: ConsentRequest, user_id: str = Depends(get_current_user)):
            """Record consent for data processing."""
            try:
                consent_data = {
                    'data_types': request.data_types,
                    'purposes': request.purposes,
                    'legal_basis': request.legal_basis
                }
                
                consent_id = self.compliance_manager.record_consent(request.subject_id, consent_data)
                
                return ConsentResponse(
                    consent_id=consent_id,
                    granted=True,
                    timestamp=datetime.utcnow()
                )
            except ComplianceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Consent recording failed: {str(e)}")
        
        @self.app.get("/compliance/consent/{subject_id}")
        async def check_consent(subject_id: str, data_type: str = Query(...), purpose: str = Query(...)):
            """Check consent for data processing."""
            try:
                has_consent = self.compliance_manager.check_consent(subject_id, data_type, purpose)
                
                return {
                    "subject_id": subject_id,
                    "data_type": data_type,
                    "purpose": purpose,
                    "has_consent": has_consent,
                    "timestamp": datetime.utcnow()
                }
            except ComplianceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Consent check failed: {str(e)}")
        
        @self.app.post("/compliance/data-subject-request")
        async def create_data_subject_request(request: DataSubjectRequestModel, user_id: str = Depends(get_current_user)):
            """Create a data subject request."""
            try:
                request_data = asdict(request)
                request_id = self.compliance_manager.create_data_subject_request(request_data)
                
                return {
                    "request_id": request_id,
                    "status": "pending",
                    "timestamp": datetime.utcnow()
                }
            except ComplianceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Request creation failed: {str(e)}")
        
        @self.app.get("/compliance/data-subject-requests")
        async def get_data_subject_requests(subject_id: Optional[str] = Query(None)):
            """Get data subject requests."""
            try:
                requests = self.compliance_manager.get_data_subject_requests(subject_id)
                
                return {
                    "requests": [asdict(req) for req in requests],
                    "count": len(requests),
                    "timestamp": datetime.utcnow()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get requests: {str(e)}")
        
        @self.app.post("/compliance/right-to-be-forgotten/{subject_id}")
        async def process_right_to_be_forgotten(subject_id: str, user_id: str = Depends(get_current_user)):
            """Process GDPR right to be forgotten."""
            try:
                result = self.compliance_manager.process_right_to_be_forgotten(subject_id)
                
                return {
                    "subject_id": subject_id,
                    "result": result,
                    "timestamp": datetime.utcnow()
                }
            except ComplianceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Right to be forgotten failed: {str(e)}")
        
        @self.app.get("/compliance/assessment/{standard}")
        async def assess_compliance(standard: str, user_id: str = Depends(get_current_user)):
            """Assess compliance for a standard."""
            try:
                compliance_standard = ComplianceStandard(standard)
                assessment = self.compliance_manager.assess_compliance(compliance_standard)
                
                return asdict(assessment)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid compliance standard: {standard}")
            except ComplianceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Compliance assessment failed: {str(e)}")
        
        @self.app.get("/compliance/report")
        async def generate_compliance_report(standards: Optional[List[str]] = Query(None)):
            """Generate compliance report."""
            try:
                if standards:
                    compliance_standards = [ComplianceStandard(s) for s in standards]
                else:
                    compliance_standards = [ComplianceStandard.GDPR]
                
                report = self.compliance_manager.generate_compliance_report(compliance_standards)
                
                return asdict(report)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid compliance standard: {str(e)}")
            except ComplianceError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
        
        # Retention endpoints
        @self.app.get("/retention/rules")
        async def get_retention_rules(classification: Optional[str] = Query(None)):
            """Get retention rules."""
            try:
                if classification:
                    data_classification = DataClassification(classification)
                    rules = self.retention_manager.get_rules(data_classification)
                else:
                    rules = self.retention_manager.get_rules()
                
                return {
                    "rules": [asdict(rule) for rule in rules],
                    "count": len(rules),
                    "timestamp": datetime.utcnow()
                }
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid data classification: {classification}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get retention rules: {str(e)}")
        
        @self.app.post("/retention/rules")
        async def create_retention_rule(request: RetentionPolicyRequest, user_id: str = Depends(get_current_user)):
            """Create a new retention rule."""
            try:
                from .retention import RetentionRule, RetentionAction, RetentionTrigger
                
                rule = RetentionRule(
                    rule_id=f"rule_{int(time.time())}",
                    name=request.name,
                    description=request.description,
                    data_classification=request.data_classification,
                    trigger=RetentionTrigger.TIME_BASED,
                    action=RetentionAction(request.action),
                    retention_days=request.retention_days
                )
                
                rule_id = self.retention_manager.add_rule(rule)
                
                return {
                    "rule_id": rule_id,
                    "status": "created",
                    "timestamp": datetime.utcnow()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create retention rule: {str(e)}")
        
        @self.app.get("/retention/audit")
        async def audit_retention_compliance(user_id: str = Depends(get_current_user)):
            """Audit retention compliance."""
            try:
                audit_results = self.retention_auditor.audit_retention_compliance()
                
                return audit_results
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Retention audit failed: {str(e)}")
        
        @self.app.post("/retention/cleanup")
        async def trigger_retention_cleanup(background_tasks: BackgroundTasks, user_id: str = Depends(get_current_user)):
            """Trigger retention cleanup."""
            try:
                background_tasks.add_task(self.retention_scheduler.trigger_cleanup_now)
                
                return {
                    "status": "cleanup_triggered",
                    "timestamp": datetime.utcnow()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to trigger cleanup: {str(e)}")
        
        # Configuration endpoints
        @self.app.get("/config")
        async def get_configuration():
            """Get current security configuration."""
            try:
                return asdict(self.config)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")
        
        @self.app.put("/config")
        async def update_configuration(request: SecurityConfigRequest, user_id: str = Depends(get_current_user)):
            """Update security configuration."""
            try:
                # Update configuration
                self.config.encryption_enabled = request.encryption_enabled
                self.config.audit_enabled = request.audit_enabled
                
                if request.retention_days:
                    for classification_str, days in request.retention_days.items():
                        classification = DataClassification(classification_str)
                        self.config.retention_days[classification] = days
                
                return {
                    "status": "updated",
                    "timestamp": datetime.utcnow()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application."""
        return self.app
    
    def shutdown(self) -> None:
        """Shutdown the API."""
        self.retention_scheduler.stop()


# Create global API instance
api_instance = None


def create_cache_security_api(config: Optional[CacheConfig] = None) -> FastAPI:
    """Create and configure the cache security API."""
    global api_instance
    api_instance = CacheSecurityAPI(config)
    return api_instance.get_app()


def get_cache_security_api() -> Optional[CacheSecurityAPI]:
    """Get the global API instance."""
    return api_instance


def shutdown_cache_security_api() -> None:
    """Shutdown the global API instance."""
    global api_instance
    if api_instance:
        api_instance.shutdown()
        api_instance = None