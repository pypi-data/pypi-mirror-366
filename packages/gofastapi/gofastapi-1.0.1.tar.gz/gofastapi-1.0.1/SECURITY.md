# Security Policy

## Supported Versions

We actively support the following versions of GoFastAPI with security updates:

| Version | Supported          | End of Life    |
| ------- | ------------------ | -------------- |
| 1.0.x   | ✅ Yes             | 2025-01-15     |
| 0.9.x   | 🔄 Critical only   | 2024-06-10     |
| 0.8.x   | ❌ No              | 2024-02-05     |
| < 0.8   | ❌ No              | Ended          |

## Reporting a Vulnerability

### 🚨 Security Contact

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities to:
- **Email**: security@gofastapi.dev
- **Subject**: [SECURITY] Brief description of the vulnerability
- **Encryption**: Use our PGP key (see below) for sensitive information

### 📋 What to Include

When reporting a security vulnerability, please include:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential impact and severity assessment
3. **Reproduction**: Step-by-step instructions to reproduce
4. **Environment**: 
   - GoFastAPI version
   - Python version
   - Operating system
   - Go version (if relevant)
5. **Proof of Concept**: Code or screenshots demonstrating the issue
6. **Suggested Fix**: If you have ideas for a fix (optional)

### 📧 Response Timeline

We are committed to responding to security reports promptly:

- **Initial Response**: Within 24 hours
- **Assessment**: Within 72 hours
- **Fix Development**: Within 7-14 days (depending on severity)
- **Release**: Within 7 days of fix completion
- **Public Disclosure**: 90 days after fix release (or coordinated disclosure)

### 🏆 Security Researcher Recognition

We believe in recognizing security researchers who help make GoFastAPI safer:

- **Hall of Fame**: Public recognition (with permission)
- **Credits**: Mentioned in release notes and security advisories
- **Swag**: GoFastAPI merchandise for significant findings
- **References**: Happy to provide references for responsible disclosure

## 🔒 Security Best Practices

### For Users

#### Installation Security
```bash
# Always verify package integrity
pip install gofastapi --trusted-host pypi.org

# Use virtual environments
python -m venv gofastapi-env
source gofastapi-env/bin/activate

# Keep dependencies updated
pip install --upgrade gofastapi
```

#### Runtime Security
```python
from gofastapi import GoFastAPI

app = GoFastAPI(
    # Disable debug in production
    debug=False,
    
    # Configure CORS properly
    cors_origins=["https://yourdomain.com"],
    
    # Set security headers
    security_headers=True,
    
    # Limit request size
    max_request_size="10MB"
)

# Use environment variables for secrets
import os
SECRET_KEY = os.getenv("SECRET_KEY")

# Validate all inputs
@app.post("/api/data")
def process_data(data: UserDataModel):  # Use Pydantic models
    # Validate and sanitize inputs
    return {"status": "processed"}
```

#### Deployment Security
```yaml
# docker-compose.yml
version: '3.8'
services:
  gofastapi:
    image: gofastapi:1.0.0
    environment:
      # Use secrets management
      - SECRET_KEY_FILE=/run/secrets/secret_key
    secrets:
      - secret_key
    # Run as non-root user
    user: "1000:1000"
    # Read-only filesystem
    read_only: true
    # Drop capabilities
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
```

### For Developers

#### Secure Coding Practices
```python
# Input validation
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    username: str
    email: str
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# SQL injection prevention
from sqlalchemy import text

# DON'T do this:
# query = f"SELECT * FROM users WHERE id = {user_id}"

# DO this instead:
query = text("SELECT * FROM users WHERE id = :user_id")
result = db.execute(query, user_id=user_id)

# XSS prevention
import html

def safe_render(user_content):
    return html.escape(user_content)
```

#### Dependency Security
```bash
# Scan for vulnerabilities
pip install safety
safety check

# Keep dependencies updated
pip-audit

# Use dependency pinning
pip freeze > requirements.txt
```

## 🛡️ Security Features

### Built-in Security

#### Request Validation
- **Input sanitization**: Automatic XSS prevention
- **Size limits**: Configurable request size limits
- **Rate limiting**: Built-in rate limiting support
- **Content-Type validation**: Strict content type checking

#### CORS Protection
```python
app = GoFastAPI(
    cors_origins=["https://trusted-domain.com"],
    cors_methods=["GET", "POST"],
    cors_headers=["Content-Type", "Authorization"],
    cors_credentials=False
)
```

#### Security Headers
```python
app = GoFastAPI(
    security_headers={
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'"
    }
)
```

### Authentication & Authorization
```python
from gofastapi.security import HTTPBearer, JWTBearer

# HTTP Bearer token authentication
security = HTTPBearer()

@app.get("/protected")
def protected_endpoint(token: str = Depends(security)):
    # Validate token
    user = validate_token(token)
    return {"user": user}

# JWT authentication
jwt_security = JWTBearer(secret_key="your-secret-key")

@app.get("/jwt-protected")
def jwt_protected(token: dict = Depends(jwt_security)):
    return {"user_id": token["user_id"]}
```

## 🚨 Known Security Considerations

### Go-Python Bridge
- **Memory safety**: Shared memory between Go and Python
- **Type safety**: Ensure proper type conversion
- **Resource limits**: Monitor memory and CPU usage

### Subinterpreter Security
- **Isolation**: Subinterpreters share some global state
- **Resource leaks**: Monitor for memory leaks
- **Import security**: Control module imports in subinterpreters

### Hot-Reload Security
- **File watching**: Potential directory traversal
- **Code injection**: Validate reloaded code
- **Production use**: Disable hot-reload in production

## 📊 Security Monitoring

### Logging Security Events
```python
import logging

security_logger = logging.getLogger("gofastapi.security")

@app.middleware("request")
async def security_middleware(request, call_next):
    # Log suspicious requests
    if len(request.url.query) > 1000:
        security_logger.warning(
            "Suspicious long query string",
            extra={"ip": request.client.host, "query_length": len(request.url.query)}
        )
    
    response = await call_next(request)
    return response
```

### Metrics and Alerting
```python
from gofastapi.monitoring import SecurityMetrics

security_metrics = SecurityMetrics()

# Track security events
security_metrics.increment("failed_auth_attempts")
security_metrics.increment("sql_injection_attempts")
security_metrics.increment("xss_attempts")
```

## 🔐 Cryptographic Standards

### Encryption
- **TLS**: Minimum TLS 1.2, prefer TLS 1.3
- **Cipher suites**: Strong cipher suites only
- **Key exchange**: ECDHE for perfect forward secrecy

### Hashing
- **Passwords**: bcrypt, scrypt, or Argon2
- **General purpose**: SHA-256 or SHA-3
- **HMAC**: For message authentication

### Random Number Generation
```python
import secrets

# Use cryptographically secure random numbers
token = secrets.token_urlsafe(32)
api_key = secrets.token_hex(16)
```

## 📝 Security Checklist

### Development
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection for state-changing operations
- [ ] Secure error handling (no sensitive info in errors)
- [ ] Dependency vulnerability scanning
- [ ] Static code analysis

### Deployment
- [ ] TLS/SSL configuration
- [ ] Security headers
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] Monitoring and alerting
- [ ] Regular security updates
- [ ] Backup and disaster recovery

### Operations
- [ ] Log monitoring
- [ ] Incident response plan
- [ ] Regular security assessments
- [ ] Employee security training
- [ ] Third-party security audits

## 🔍 Security Testing

### Automated Testing
```python
# Security test example
def test_sql_injection_protection():
    client = TestClient(app)
    
    # Test SQL injection attempt
    malicious_input = "'; DROP TABLE users; --"
    response = client.get(f"/users/{malicious_input}")
    
    # Should not succeed
    assert response.status_code in [400, 422]
    
    # Database should still exist
    assert check_database_integrity()
```

### Manual Testing
- **Penetration testing**: Regular pen tests
- **Code review**: Security-focused code reviews
- **Dependency audits**: Regular dependency security audits

## 📞 Emergency Response

### Incident Response Plan
1. **Detection**: Identify the security incident
2. **Assessment**: Evaluate impact and severity
3. **Containment**: Immediate actions to limit damage
4. **Notification**: Alert stakeholders and users
5. **Investigation**: Detailed forensic analysis
6. **Recovery**: Restore normal operations
7. **Lessons Learned**: Post-incident review

### Emergency Contacts
- **Security Team**: security@gofastapi.dev
- **On-call Engineer**: +1-XXX-XXX-XXXX
- **Legal Team**: legal@gofastapi.dev

## 🔑 PGP Key

For sensitive security reports, use our PGP key:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
[PGP Key would be inserted here in a real implementation]
-----END PGP PUBLIC KEY BLOCK-----
```

Key ID: [Key ID would be here]
Fingerprint: [Fingerprint would be here]

---

**Remember**: Security is everyone's responsibility. When in doubt, err on the side of caution and reach out to our security team.
