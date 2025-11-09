# User, Roles & Permissions Management System

## Overview

This document provides comprehensive guidance on the User, Roles & Permissions Management system implemented in the LIMS-QMS Platform. The system provides enterprise-grade authentication, authorization, and access control.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [User Management](#user-management)
4. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
5. [Permission System](#permission-system)
6. [Multi-Factor Authentication (MFA)](#multi-factor-authentication-mfa)
7. [Session Management](#session-management)
8. [API Key Authentication](#api-key-authentication)
9. [Security Features](#security-features)
10. [Audit Logging](#audit-logging)
11. [Competency Management](#competency-management)
12. [Delegation & Substitution](#delegation--substitution)
13. [API Documentation](#api-documentation)

---

## Features

### 1. User Management

- **User Registration & Profiles**
  - Username, email, full name, employee ID
  - Department and designation tracking
  - Profile images and preferences
  - Multi-language support with timezone settings

- **Password Security**
  - Strong password policies
  - Password expiration (90 days default)
  - Password history (prevent reuse of last 5 passwords)
  - Forced password change on first login
  - Account lockout after 5 failed attempts

- **Account Status**
  - Active/inactive status
  - Email and phone verification
  - Date joined and termination tracking
  - Manager hierarchy

### 2. Role-Based Access Control (RBAC)

#### Predefined Roles

1. **Admin** - Full system access
2. **Quality Manager** - QMS oversight, audit management
3. **Lab Manager** - Laboratory operations, equipment, training
4. **Technician** - Test execution, data entry
5. **Checker** - Review and verification
6. **Approver** - Final approvals and sign-offs
7. **Auditor** - Read-only audit access with export
8. **Customer** - Limited external access to orders and tickets
9. **HR Manager** - Human resources management
10. **Finance Manager** - Financial operations and reporting

#### Role Features

- **Hierarchy Support** - Parent-child role relationships
- **Custom Roles** - Create organization-specific roles
- **Role Inheritance** - Child roles inherit parent permissions
- **User Limits** - Restrict maximum users per role
- **System Roles** - Protected roles that cannot be deleted

### 3. Permission System

#### Permission Structure

Permissions follow the format: `resource:action`

**Resources:**
- Core: `user`, `role`, `permission`, `session`, `api_key`
- Documents: `document`, `form`, `form_template`, `form_record`
- Projects: `project`, `task`, `milestone`
- HR: `employee`, `recruitment`, `training`, `leave`, `attendance`, `performance`
- Procurement: `vendor`, `rfq`, `purchase_order`, `equipment`, `calibration`
- Financial: `expense`, `invoice`, `payment`, `revenue`
- CRM: `lead`, `customer`, `order`, `support_ticket`
- Quality: `non_conformance`, `audit`, `capa`, `risk_assessment`
- Analytics: `report`, `analytics`, `kpi`, `dashboard`
- Workflow: `workflow`, `approval`
- Competency: `competency`, `certification`
- Delegation: `delegation`

**Actions:**
- `create` - Create new resources
- `read` - View resources
- `update` - Modify existing resources
- `delete` - Remove resources
- `approve` - Approve pending items
- `review` - Review and verify
- `export` - Export data

#### Permission Scopes

- **all** - Access to all resources
- **own** - Access only to own resources
- **department** - Access to department resources
- **team** - Access to team resources

### 4. Multi-Factor Authentication (MFA)

- **TOTP Support** - Google Authenticator, Authy, etc.
- **Backup Codes** - 10 one-time recovery codes
- **QR Code Generation** - Easy setup via QR code scan
- **Optional MFA** - Can be enabled per user
- **MFA Token Verification** - 30-second time window

### 5. Session Management

- **JWT Tokens** - Secure access tokens
- **Refresh Tokens** - 30-day expiry
- **Session Tracking** - Track all active sessions
- **Device Information** - IP address, user agent, location
- **Session Termination** - Logout from all devices
- **Concurrent Session Limits** - Configurable per user (default: 5)
- **Session Expiry** - Automatic expiration after 7 days
- **Activity Tracking** - Last activity timestamp

### 6. API Key Authentication

- **Programmatic Access** - Alternative to user credentials
- **Scoped Permissions** - Limit API key capabilities
- **IP Whitelisting** - Restrict usage to specific IPs
- **Expiration** - Optional expiry dates
- **Usage Tracking** - Monitor last used and usage count
- **Key Prefix** - First 8 characters for identification

### 7. Security Features

#### Password Policy

```python
MIN_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGIT = True
REQUIRE_SPECIAL = True
MIN_UNIQUE_CHARS = 5
PREVENT_REUSE_COUNT = 5
MAX_AGE_DAYS = 90
```

#### Account Protection

- Failed login tracking
- Automatic account lockout (5 attempts)
- 30-minute lockout duration
- Password expiration warnings
- Suspicious activity detection

#### Encryption

- **Password Hashing** - bcrypt with salt
- **MFA Secrets** - Encrypted storage
- **API Keys** - Hashed storage
- **Sensitive Data** - Fernet symmetric encryption

### 8. Audit Logging

Every action is logged with:
- User ID and username
- Activity type and action
- Resource type and ID
- IP address and user agent
- Request method and path
- Before/after changes
- Risk score calculation
- Timestamp

#### Activity Types

- `LOGIN` / `LOGOUT` / `LOGIN_FAILED`
- `PASSWORD_CHANGE` / `PASSWORD_RESET`
- `MFA_ENABLED` / `MFA_DISABLED`
- `PROFILE_UPDATE`
- `PERMISSION_CHANGE`
- `ROLE_ASSIGNED` / `ROLE_REMOVED`
- `API_KEY_CREATED` / `API_KEY_REVOKED`
- `SUSPICIOUS_ACTIVITY`

### 9. Competency Management

- **Certification Tracking** - Professional certifications
- **Training Records** - Completed training courses
- **Equipment Authorization** - Equipment operation approval
- **Test Method Competency** - Authorized test methods
- **Approval Levels** - 1-5 scale authority
- **Expiry Alerts** - Automatic notifications before expiry
- **Verification** - Verified by authorized personnel

### 10. Delegation & Substitution

- **Temporary Role Delegation** - Assign roles during leave
- **Time-Bound** - Start and end dates
- **Approval Required** - Optional approval workflow
- **Scope Control** - Full role or specific permissions
- **Auto-Routing** - Automatic approval chain substitution
- **Active Status Tracking** - Monitor current delegations

---

## Architecture

### Database Models

```
User
├── UserSession (1:many)
├── LoginHistory (1:many)
├── UserAPIKey (1:many)
├── UserActivity (1:many)
├── PasswordHistory (1:many)
├── UserCompetency (1:many)
├── RoleDelegation (1:many) - as delegator
└── RoleDelegation (1:many) - as delegate

Role
├── User (many:many)
└── Permission (many:many)

Permission
└── Role (many:many)
```

### Service Layer

- **AuthorizationService** - Permission checking logic
- **ActivityService** - Audit logging
- **UserService** - User management operations
- **RoleService** - Role management
- **PermissionService** - Permission management

### API Endpoints Structure

```
/api/v1/auth/
  - POST /login
  - POST /register
  - POST /logout
  - POST /refresh-token
  - POST /password-change
  - POST /password-reset
  - POST /mfa/setup
  - POST /mfa/verify
  - POST /mfa/disable

/api/v1/users/
  - GET /me
  - GET /
  - GET /{id}
  - PUT /{id}
  - POST /
  - DELETE /{id}
  - POST /{id}/roles
  - GET /{id}/permissions
  - GET /{id}/activities
  - GET /{id}/sessions

/api/v1/roles/
  - GET /
  - GET /{id}
  - POST /
  - PUT /{id}
  - DELETE /{id}
  - POST /{id}/permissions

/api/v1/permissions/
  - GET /
  - GET /{id}
  - POST /
  - PUT /{id}
  - DELETE /{id}
```

---

## Usage Examples

### 1. Permission Checking in Endpoints

```python
from fastapi import Depends
from backend.api.dependencies.permissions import require_permission

@router.get("/documents/")
async def get_documents(
    current_user: User = Depends(require_permission("document", "read"))
):
    # User has been checked for document:read permission
    return documents
```

### 2. Multiple Permission Check

```python
from backend.api.dependencies.permissions import require_any_permission

@router.get("/reports/")
async def get_reports(
    current_user: User = Depends(require_any_permission([
        ("report", "read"),
        ("analytics", "view")
    ]))
):
    return reports
```

### 3. Role-Based Access

```python
from backend.api.dependencies.permissions import require_role

@router.post("/admin/settings")
async def update_settings(
    settings: dict,
    current_user: User = Depends(require_role("admin"))
):
    # Only users with 'admin' role can access
    return updated_settings
```

### 4. Programmatic Permission Check

```python
from backend.services.auth_service import AuthorizationService

if AuthorizationService.has_permission(user, "document", "approve", db):
    # User can approve documents
    approve_document()
```

### 5. Activity Logging

```python
from backend.services.activity_service import ActivityService

ActivityService.log_activity(
    db=db,
    user=current_user,
    activity_type=ActivityType.PROFILE_UPDATE,
    action="update",
    resource_type="user",
    resource_id=str(user.id),
    request=request,
    changes={"email": {"old": old_email, "new": new_email}}
)
```

---

## Configuration

### Environment Variables

```bash
# Authentication
SECRET_KEY=your-secret-key-here  # Change in production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# Encryption
ENCRYPTION_KEY=your-encryption-key-here  # For MFA secrets

# Redis (for sessions)
REDIS_URL=redis://localhost:6379/0

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
```

### Password Policy Customization

Edit `backend/core/security.py`:

```python
class PasswordPolicy:
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    MIN_UNIQUE_CHARS = 5
    PREVENT_REUSE_COUNT = 5
    MAX_AGE_DAYS = 90
```

---

## Security Best Practices

1. **Change Default Credentials** - Immediately after installation
2. **Use Strong SECRET_KEY** - Generate using `openssl rand -hex 32`
3. **Enable HTTPS** - Always use TLS in production
4. **Configure CORS** - Restrict allowed origins
5. **Set Up Redis** - For proper session management
6. **Regular Audits** - Review user activity logs
7. **Monitor Failed Logins** - Watch for brute force attacks
8. **Backup Codes** - Store MFA backup codes securely
9. **API Key Rotation** - Rotate API keys periodically
10. **Review Permissions** - Audit role permissions regularly

---

## Testing

### Run Database Initialization

```bash
cd /home/user/lims-qms-platform
python database/init_db.py
```

### Test Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin@123"
```

### Test Permission Check

```bash
# Get access token from login response
TOKEN="your-access-token"

curl -X GET http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Common Issues

**1. Account Locked**
- Wait 30 minutes or contact administrator
- Reset failed login attempts via admin

**2. MFA Setup Issues**
- Ensure time synchronization on device
- Use backup codes if TOTP fails

**3. Session Expired**
- Login again or use refresh token
- Check token expiration settings

**4. Permission Denied**
- Verify user has required role
- Check permission assignments
- Review audit logs for details

---

## Future Enhancements

- SSO Integration (OAuth2, SAML)
- Biometric Authentication
- Hardware Token Support (YubiKey)
- Advanced Risk Scoring
- Behavioral Analytics
- Compliance Reporting (GDPR, SOC 2)

---

## Support

For questions or issues:
- Check audit logs: `/api/v1/activities/`
- Review user permissions: `/api/v1/users/{id}/permissions`
- Contact system administrator

---

## Version History

- **v1.0.0** - Initial implementation with comprehensive RBAC
  - User management
  - 10 predefined roles
  - 200+ permissions
  - MFA support
  - Session management
  - API key authentication
  - Competency tracking
  - Delegation system
  - Complete audit logging
