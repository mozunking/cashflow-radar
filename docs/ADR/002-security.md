# ADR-002: Security Architecture for CAD Financial Risk Control System

**Status:** Proposed
**Date:** 2026-05-18
**Deciders:** Security Team, Architecture Team

---

## Context

CAD (Capital Anomaly Detection) is a financial risk control system processing sensitive transaction data requiring:
- 国密 SM2/SM3/SM4 cryptographic compliance
- 等保2.0 Level 3 certification
- 36-month tamper-proof audit retention
- JWT/HMAC authentication for Java system integration

### Current Security Posture

Code review reveals **CRITICAL vulnerabilities** requiring immediate remediation:

| Severity | Issue | Location |
|----------|-------|----------|
| CRITICAL | JWT authentication stub - always returns `dev_user:admin` | `src/cad-service/auth.py:52` |
| CRITICAL | Hardcoded database password `cad123` | `docker/compose.dev.yml:11,38` |
| CRITICAL | MinIO default credentials `minioadmin:minioadmin` | `docker/compose.dev.yml:71-72` |
| HIGH | No input validation on `transaction_id` path parameter | `src/cad-service/api.py:49` |
| HIGH | Rate limiter defined but not applied to endpoints | `src/cad-service/main.py:34` |
| MEDIUM | Grafana default admin password | `docker/compose.dev.yml:93` |
| MEDIUM | No TLS configuration in docker-compose | `docker/compose.dev.yml` |

---

## Decision: Security Architecture

### 1. STRIDE Threat Model

| Threat Category | Attack Vector | Mitigation |
|-----------------|---------------|------------|
| **Spoofing** | JWT token forgery, credential theft | SM2 digital signatures, certificate pinning |
| **Tampering** | Transaction data manipulation, log injection | SM4-GCM authenticated encryption, input validation |
| **Repudiation** | User denies action, audit log manipulation | Immutable append-only audit logs, SM3 hash chains |
| **Information Disclosure** | Data exfiltration, credential exposure | SM4 encryption at rest, TLS 1.3 in transit |
| **Denial of Service** | API flooding, resource exhaustion | Rate limiting per client, circuit breakers |
| **Elevation of Privilege** | Role bypass, privilege escalation | RBAC enforcement, principle of least privilege |

### 2. Authentication & Authorization

#### 2.1 JWT Implementation (Production)

```python
# src/cad-service/auth.py - REQUIRED IMPLEMENTATION
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from gmssl import sm2, sm3, sm4

class JWTConfig:
    """JWT configuration - MUST be loaded from environment"""
    SM2_PRIVATE_KEY_FILE: str = os.getenv("JWT_SM2_PRIVATE_KEY_FILE", "/secrets/jwt-private.key")
    SM2_PUBLIC_KEY_FILE: str = os.getenv("JWT_SM2_PUBLIC_KEY_FILE", "/secrets/jwt-public.key")
    JWT_EXPIRY_MINUTES: int = int(os.getenv("JWT_EXPIRY_MINUTES", "15"))
    ISSUER: str = "cad-service"

class TokenData(BaseModel):
    user_id: str
    role: str
    exp: datetime
    iat: datetime
    iss: str

def _load_sm2_key(key_file: str) -> bytes:
    """Load SM2 key from file with proper permissions (0o400)"""
    if not os.path.exists(key_file):
        raise FileNotFoundError(f"SM2 key file not found: {key_file}")
    with open(key_file, 'rb') as f:
        return f.read()

def verify_jwt(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]) -> TokenData:
    """
    Verify JWT token using SM2 algorithm.

    Production requirements:
    1. Load SM2 public key from secure file storage
    2. Verify SM2 signature on token
    3. Check expiration (exp claim)
    4. Validate issuer (iss claim)
    5. Extract and return user_id and role
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # Split JWT: header.payload.signature (base64url encoded)
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        header_b64, payload_b64, signature_b64 = parts

        # Decode payload
        payload = json.loads(base64url_decode(payload_b64))

        # Check expiration
        exp = datetime.fromtimestamp(payload.get('exp', 0))
        if datetime.now() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate issuer
        if payload.get('iss') != JWTConfig.ISSUER:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
            )

        # Verify SM2 signature
        message = f"{header_b64}.{payload_b64}".encode()
        signature = base64url_decode(signature_b64)

        sm2_public_key = _load_sm2_key(JWTConfig.SM2_PUBLIC_KEY_FILE)
        sm2_verify = sm2.CryptSM2(sm2_public_key, None)

        # SM2 sign = SM3 hash + SM2 encrypt (simplified)
        msg_hash = sm3.sm3_hash(message)
        if not sm2_verify.verify(msg_hash.encode(), signature):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
            )

        return TokenData(
            user_id=payload['user_id'],
            role=payload['role'],
            exp=exp,
            iat=datetime.fromtimestamp(payload.get('iat', 0)),
            iss=payload.get('iss', ''),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )
```

#### 2.2 Role-Based Access Control (RBAC)

```python
# Role hierarchy for CAD system
CAD_ROLES = {
    "admin": ["detect:write", "detect:read", "feedback:write", "feedback:read",
              "model:read", "explain:read", "config:write", "audit:read"],
    "supervisor": ["detect:read", "feedback:write", "feedback:read",
                   "model:read", "explain:read", "audit:read"],
    "analyst": ["detect:read", "feedback:write", "feedback:read", "explain:read"],
    "auditor": ["detect:read", "audit:read"],  # Read-only for compliance
    "java_system": ["detect:write", "detect:read", "feedback:read"],  # API integration
}

def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control."""
    def role_checker(
        token_data: Annotated[TokenData, Depends(verify_jwt)]
    ) -> AuthenticatedUser:
        if token_data.role not in allowed_roles:
            # Log failed authorization attempt
            log_security_event(
                event_type="AUTHORIZATION_FAILURE",
                user_id=token_data.user_id,
                required_roles=list(allowed_roles),
                user_role=token_data.role,
                endpoint=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return AuthenticatedUser(user_id=token_data.user_id, role=token_data.role)
    return role_checker
```

### 3. Data Protection - 国密 Implementation

#### 3.1 SM4-GCM Encryption for Sensitive Fields

```python
# src/cad-service/crypto.py
from gmssl import sm4
import os
from typing import Any

class SM4Encryption:
    """SM4-GCM authenticated encryption for sensitive data fields"""

    def __init__(self, key: bytes | None = None):
        """
        Initialize with 256-bit SM4 key from secure storage.

        Key derivation: Master Key (SM2 encrypted) -> Data Encryption Key
        """
        if key is None:
            key = self._load_dek_from_mek()
        if len(key) != 32:
            raise ValueError("SM4 key must be 256 bits (32 bytes)")
        self._crypt_sm4 = sm4.CryptSM4()
        self._key = key

    def encrypt(self, plaintext: str | bytes, aad: str = "") -> dict[str, Any]:
        """
        Encrypt using SM4-GCM mode.

        Returns:
            {
                "ciphertext": base64_encoded,
                "iv": base64_encoded,
                "tag": base64_encoded_16_bytes,
                "algorithm": "SM4-GCM"
            }
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        if isinstance(aad, str):
            aad = aad.encode('utf-8')

        iv = os.urandom(12)  # 96-bit IV for GCM
        self._crypt_sm4.set_key(self._key, sm4.SM4_ENCRYPT)
        self._crypt_sm4.gcm_set_iv(iv)

        if aad:
            self._crypt_sm4.gcm_add_aad(aad)

        ciphertext = self._crypt_sm4.gcm_encrypt(plaintext)
        tag = self._crypt_sm4.gcm_get_tag()

        return {
            "ciphertext": base64.b64encode(ciphertext).decode('ascii'),
            "iv": base64.b64encode(iv).decode('ascii'),
            "tag": base64.b64encode(tag).decode('ascii'),
            "algorithm": "SM4-GCM",
        }

    def decrypt(self, encrypted: dict[str, Any], aad: str = "") -> bytes:
        """Decrypt SM4-GCM ciphertext"""
        ciphertext = base64.b64decode(encrypted['ciphertext'])
        iv = base64.b64decode(encrypted['iv'])
        tag = base64.b64decode(encrypted['tag'])

        self._crypt_sm4.set_key(self._key, sm4.SM4_DECRYPT)
        self._crypt_sm4.gcm_set_iv(iv)
        self._crypt_sm4.gcm_set_tag(tag)

        if aad:
            self._crypt_sm4.gcm_add_aad(aad.encode('utf-8'))

        return self._crypt_sm4.gcm_decrypt(ciphertext)

# Fields requiring encryption
ENCRYPTED_FIELDS = [
    "account_id",      # 账户ID
    "transaction_id", # 交易流水号 (if containing sensitive patterns)
    "amount",          # 交易金额 (for certain transaction types)
    "review_comment",  # 复核意见 (may contain sensitive info)
]

def encrypt_transaction_record(record: dict, crypto: SM4Encryption) -> dict:
    """Encrypt sensitive fields in transaction record"""
    encrypted = record.copy()
    for field in ENCRYPTED_FIELDS:
        if field in encrypted and encrypted[field] is not None:
            encrypted[field] = crypto.encrypt(
                str(encrypted[field]),
                aad=f"txn:{record.get('transaction_id', '')}"  # AAD for integrity
            )
    return encrypted
```

#### 3.2 SM3 Hash Chain for Audit Logs

```python
# src/cad-service/audit.py
from gmssl import sm3
from datetime import datetime
from typing import Any
import json

class AuditLogEntry:
    """Immutable audit log entry with SM3 hash chain"""

    def __init__(
        self,
        sequence: int,
        timestamp: datetime,
        user_id: str,
        action: str,
        resource: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
        previous_hash: str = "GENESIS",
    ):
        self.sequence = sequence
        self.timestamp = timestamp
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.resource_id = resource_id
        self.details = details or {}
        self.previous_hash = previous_hash
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SM3 hash of this entry including previous hash (chain)"""
        data = {
            "seq": self.sequence,
            "ts": self.timestamp.isoformat(),
            "user": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "details": self.details,
            "prev": self.previous_hash,
        }
        message = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return sm3.sm3_hash(message.encode('utf-8'))

    def to_dict(self) -> dict:
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    @classmethod
    def verify_chain(cls, entries: list[dict]) -> bool:
        """Verify integrity of audit log chain"""
        prev_hash = "GENESIS"
        for entry in entries:
            if entry['previous_hash'] != prev_hash:
                return False
            # Recompute and verify hash
            computed = cls._recompute_hash(entry)
            if computed != entry['hash']:
                return False
            prev_hash = entry['hash']
        return True

AUDIT_ACTIONS = [
    "LOGIN", "LOGOUT",                    # Authentication events
    "DETECT_BATCH",                       # Batch detection
    "FEEDBACK_SUBMIT", "FEEDBACK_UPDATE", # Feedback operations
    "MODEL_ACCESS",                       # Model queries
    "CONFIG_CHANGE",                      # Configuration changes
    "DATA_EXPORT",                        # Data export (compliance)
]
```

### 4. API Security

#### 4.1 Rate Limiting Configuration

```python
# src/cad-service/main.py - Required additions
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Rate limiting configuration
RATE_LIMITS = {
    # Authenticated endpoints
    "/api/v1/detect/batch": "100/minute",      # Batch detection
    "/api/v1/feedback": "50/minute",           # Feedback submission
    "/api/v1/explain/{transaction_id}": "200/minute",  # Explanations

    # Public/read endpoints
    "/health": "1000/minute",                  # Health check
    "/health/degradation": "100/minute",       # Degradation status

    # Strict limits for sensitive operations
    "/api/v1/admin/*": "10/minute",            # Admin operations
}

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="redis://redis:6379/1",  # Separate Redis DB for rate limits
)

app = FastAPI(...)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Apply rate limits to routes
@router.post("/detect/batch")
@limiter.limit("100/minute")
async def batch_detect(...):
    ...

# For distributed rate limiting, use Redis-backed storage
# This prevents bypass via multiple service instances
```

#### 4.2 Input Validation

```python
# src/cad-service/models.py - Enhanced validation
from pydantic import BaseModel, Field, field_validator, constr
import re

class BatchDetectRequest(BaseModel):
    data_date: constr(min_length=10, max_length=10) = Field(..., description="数据日期 YYYY-MM-DD")
    feature_version: constr(max_length=64) | None = Field(default=None)

    @field_validator("data_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        # Strict date validation
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError("data_date must be YYYY-MM-DD format")
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("data_date is not a valid date")
        # Prevent future dates (configurable)
        if datetime.strptime(v, "%Y-%m-%d").date() > datetime.now().date():
            raise ValueError("data_date cannot be in the future")
        return v

class FeedbackRequest(BaseModel):
    transaction_id: constr(min_length=8, max_length=64) = Field(...)
    review_result: Literal["确认", "排除", "存疑"]
    review_comment: constr(max_length=1000)  # Limit comment length
    anomaly_type: constr(max_length=64) | None = None

    @field_validator("transaction_id")
    @classmethod
    def validate_transaction_id(cls, v: str) -> str:
        # Alphanumeric + hyphens only, no SQL injection patterns
        if not re.match(r'^[A-Za-z0-9_-]+$', v):
            raise ValueError("transaction_id contains invalid characters")
        # Length check to prevent DoS
        if len(v) > 64:
            raise ValueError("transaction_id too long")
        return v

class ExplainTransactionParams(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=64)

    @field_validator("transaction_id")
    @classmethod
    def sanitize_transaction_id(cls, v: str) -> str:
        # Remove any potentially dangerous characters
        sanitized = re.sub(r'[^A-Za-z0-9_-]', '', v)
        if len(sanitized) < len(v):
            raise ValueError("transaction_id contains invalid characters")
        return sanitized
```

### 5. Audit Logging Architecture

#### 5.1 Tamper-Proof Audit System

```python
# src/cad-service/audit.py - Audit logging with 36-month retention

from sqlalchemy import Column, String, Integer, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
import boto3
from datetime import datetime, timedelta

class AuditLogModel(Base):
    """PostgreSQL table for audit logs - append-only"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sequence = Column(Integer, unique=True, nullable=False)  # Monotonic sequence
    timestamp = Column(DateTime, nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    action = Column(String(32), nullable=False, index=True)
    resource = Column(String(64), nullable=False)
    resource_id = Column(String(128), nullable=False)
    details = Column(JSONB, nullable=True)  # Encrypted sensitive fields
    previous_hash = Column(String(64), nullable=False)
    hash = Column(String(64), nullable=False, unique=True)  # SM3 chain

    __table_args__ = (
        Index('ix_audit_logs_timestamp_hash', 'timestamp', 'hash'),  # Range queries
        Index('ix_audit_logs_user_action', 'user_id', 'action'),  # User activity queries
    )

# S3 Archive Configuration for 36-month retention
AUDIT_ARCHIVE_CONFIG = {
    "bucket": "cad-audit-logs",
    "prefix": "audit/",
    "retention_days": 365 * 3,  # 36 months
    "glacier_transition_days": 90,  # Move to Glacier after 90 days
    "format": "parquet",  # Columnar format for efficient queries
}

def archive_old_audit_logs(session, cutoff_date: datetime):
    """
    Archive audit logs older than cutoff_date to S3/Glacier.

    Requirements:
    - 36-month minimum retention per 等保2.0
    - Encrypted at rest with SM4
    - Integrity verified via SM3 hash chain
    """
    old_logs = session.query(AuditLogModel).filter(
        AuditLogModel.timestamp < cutoff_date
    ).all()

    if not old_logs:
        return

    # Export to encrypted Parquet
    records = [log.to_dict() for log in old_logs]

    s3_client = boto3.client('s3')
    partition_key = cutoff_date.strftime("%Y/%m")

    # Write encrypted parquet
    buffer = pa.BufferOutputStream()
    with pa.ipc.new_file(buffer, schema) as writer:
        writer.write_table(pyarrow.Table.from_pylist(records))
    encrypted_data = sm4_encrypt(buffer.getvalue())

    s3_client.put_object(
        Bucket=AUDIT_ARCHIVE_CONFIG["bucket"],
        Key=f"{AUDIT_ARCHIVE_CONFIG['prefix']}{partition_key}/audit_{cutoff_date.date()}.parquet.enc",
        Body=encrypted_data,
        Metadata={'encryption': 'SM4-GCM', 'retention': '36months'}
    )

    # Verify integrity before deletion
    assert verify_sm3_chain([log.hash for log in old_logs])

    # Delete from PostgreSQL after successful archive
    for log in old_logs:
        session.delete(log)
    session.commit()
```

### 6. Compliance Checklist

#### 6.1 等保2.0 Level 3 Mapping

| Control | Requirement | Implementation | Status |
|---------|-------------|----------------|--------|
| **网络安全** | | | |
| 7.1.1 | 身份鉴别 | JWT with SM2 signatures, 15-min expiry | REQUIRED |
| 7.1.2 | 访问控制 | RBAC with 5 roles, principle of least privilege | PARTIAL |
| 7.1.3 | 审计追溯 | SM3 hash chain, 36-month retention | REQUIRED |
| **数据安全** | | | |
| 8.1.1 | 敏感数据保护 | SM4-GCM encryption at rest | REQUIRED |
| 8.1.2 | 传输加密 | TLS 1.3 (infrastructure config) | REQUIRED |
| 8.1.3 | 密钥管理 | SM2 key lifecycle, hardware backup | REQUIRED |
| **应用安全** | | | |
| 9.1.1 | 输入验证 | Pydantic validation, sanitization | PARTIAL |
| 9.1.2 | 抗抵赖 | Digital signatures, audit logs | REQUIRED |
| 9.1.3 | 代码安全 | No hardcoded secrets, dependency scanning | REQUIRED |

#### 6.2 数据安全法 Compliance

| Requirement | Implementation |
|-------------|-----------------|
| 数据分类分级 | Sensitive fields marked for SM4 encryption |
| 数据溯源 | SM3 hash chain enables full traceability |
| 数据保护影响评估 | Required before production deployment |
| 应急响应 | 4-hour incident response SLA documented |

### 7. Security Configuration (Docker)

```yaml
# docker/compose.prod.yml - Production security configuration
services:
  cad-service:
    environment:
      # Authentication
      - JWT_SM2_PRIVATE_KEY_FILE=/secrets/jwt-private.key
      - JWT_SM2_PUBLIC_KEY_FILE=/secrets/jwt-public.key
      - JWT_EXPIRY_MINUTES=15

      # Database
      - DATABASE_URL=postgresql://${CAD_DB_USER}:${CAD_DB_PASSWORD}@postgres:5432/cad
      - POSTGRES_SSL_MODE=require

      # Redis with AUTH
      - REDIS_URL=rediss://:${REDIS_PASSWORD}@redis:6379/0

      # Encryption
      - SM4_DEK=${SM4_DATA_ENCRYPTION_KEY}

    secrets:
      - jwt-private-key
      - jwt-public-key
      - db-password
      - redis-password
      - sm4-dek

  postgres:
    environment:
      - POSTGRES_USER=${CAD_DB_USER}
      - POSTGRES_PASSWORD=${CAD_DB_PASSWORD}
      - POSTGRES_DB=cad
    command: postgres -c ssl=on -c ssl_cert_file=/var/lib/postgresql/server.crt -c ssl_key_file=/var/lib/postgresql/server.key
    volumes:
      - ./certs:/var/lib/postgresql:cached

  redis:
    command: redis-server --requirepass ${REDIS_PASSWORD} --tls-port 6379 --port 0 --tls-cert-file /certs/redis.crt --tls-key-file /certs/redis.key

secrets:
  jwt-private-key:
    file: ./secrets/jwt-private.key  # 0o400 permissions
  jwt-public-key:
    file: ./secrets/jwt-public.key
  db-password:
    file: ./secrets/db-password
  redis-password:
    file: ./secrets/redis-password
  sm4-dek:
    file: ./secrets/sm4-dek  # 256-bit key, SM2 encrypted master key

networks:
  cad-network:
    driver: overlay
    attachable: true
```

### 8. Security Event Monitoring

```python
# src/cad-service/security_events.py
from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class SecurityEventType(str, Enum):
    AUTHENTICATION_SUCCESS = "AUTH_SUCCESS"
    AUTHENTICATION_FAILURE = "AUTH_FAILURE"
    AUTHORIZATION_FAILURE = "AUTHZ_FAILURE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT"
    SUSPICIOUS_INPUT = "SUSPICIOUS_INPUT"
    DATA_EXPORT = "DATA_EXPORT"
    CONFIG_CHANGE = "CONFIG_CHANGE"

class SecurityEvent(BaseModel):
    event_type: SecurityEventType
    timestamp: datetime
    user_id: str | None
    ip_address: str
    endpoint: str
    details: dict
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL

# Alert thresholds
SECURITY_ALERT_THRESHOLDS = {
    "AUTH_FAILURE_PER_MINUTE": 5,
    "RATE_LIMIT_PER_MINUTE": 100,
    "DATA_EXPORT_PER_DAY": 10,
}

def should_alert(event: SecurityEvent) -> bool:
    """Determine if event should trigger alert"""
    if event.risk_level in ("HIGH", "CRITICAL"):
        return True
    # Check thresholds
    if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
        return check_rate_threshold(event.ip_address, "AUTH_FAILURE_PER_MINUTE", 5)
    return False
```

---

## Consequences

### Positive
- Compliant with 等保2.0 Level 3 requirements
- 国密 algorithm support for Chinese financial regulations
- Tamper-proof audit trail with 36-month retention
- Defense against OWASP Top 10 attacks

### Negative
- Increased latency from SM2/SM4 cryptographic operations
- Key management complexity
- Additional infrastructure for secrets management

### Risks
- Key rotation requires JWT re-issuance (15-min window)
- SM2 performance under high load (mitigate with hardware acceleration)

---

## References

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [等保2.0 三级要求](https://www.dcjsj.gov.cn/)
- [国密SSL/TLS协议 specification](http://www.gmbz.org.cn/)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
