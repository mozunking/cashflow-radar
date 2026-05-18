# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it via:

1. **Private email**: Send to maintainers directly
2. **GitHub Security Advisories**: Use the "Security" tab

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Security Requirements

### Authentication
- JWT with RS256 signature (15-minute expiry)
- Role-based access control (RBAC)

### Data Protection
- Sensitive fields encrypted with SM4-GCM
- Model files encrypted at rest
- TLS 1.3 for all communications

### Audit
- All write operations logged
- Logs immutable for 36 months
- Full traceability with trace_id

### Compliance
- 等保2.0 Level 3 certified
- 国密算法 compliant
