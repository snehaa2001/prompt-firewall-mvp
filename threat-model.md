# Prompt Firewall - Threat Model

**Date**: November 10, 2025
**Methodology**: STRIDE
**Version**: 1.0

## Assets

| Asset | Sensitivity | Location |
|-------|-------------|----------|
| API Keys (OpenAI) | Critical | GCP Secret Manager |
| Admin Credentials | High | Firebase Authentication |
| User Logs | Medium | Firestore (PII-redacted) |
| Policies | Medium | Firestore |

## Entry Points

| Entry Point | Authentication | Exposure |
|-------------|----------------|----------|
| POST /v1/query | Optional | Public |
| GET /v1/policy | Firebase Auth | Admin only |
| POST /v1/policy | Firebase Auth | Admin only |
| PUT /v1/policy/{id} | Firebase Auth | Admin only |
| DELETE /v1/policy/{id} | Firebase Auth | Admin only |
| GET /v1/logs | Firebase Auth | Admin only |
| POST /admin/cleanup-logs | Firebase Auth | Admin only |
| POST /v1/admin/create-admin-user | Admin Secret | One-time setup |

## STRIDE Analysis

### Spoofing
| Threat | Likelihood | Impact | Risk | Mitigation |
|--------|------------|--------|------|------------|
| Admin impersonation | Medium | Critical | HIGH | Firebase Auth, token expiry |
| API key theft | Low | Critical | MEDIUM | Secret Manager, Workload Identity |

### Tampering
| Threat | Likelihood | Impact | Risk | Mitigation |
|--------|------------|--------|------|------------|
| Policy manipulation | Low | Critical | MEDIUM | Admin-only endpoints, role checks |
| Log injection | Medium | Medium | MEDIUM | Structured logging, validation |

### Repudiation
| Threat | Likelihood | Impact | Risk | Mitigation |
|--------|------------|--------|------|------------|
| Admin denies actions | Medium | Medium | MEDIUM | TODO: Add audit log |

### Information Disclosure
| Threat | Likelihood | Impact | Risk | Mitigation |
|--------|------------|--------|------|------------|
| PII in logs | High | Critical | CRITICAL | PII redaction, 90-day retention |
| Unauthorized log access | Medium | High | MEDIUM | Firebase Auth, role checks |

### Denial of Service
| Threat | Likelihood | Impact | Risk | Mitigation |
|--------|------------|--------|------|------------|
| High-volume requests | High | High | HIGH | TODO: Rate limiting |
| Large payloads | Medium | Medium | MEDIUM | Request size limits |

### Elevation of Privilege
| Threat | Likelihood | Impact | Risk | Mitigation |
|--------|------------|--------|------|------------|
| User to admin escalation | Low | Critical | MEDIUM | Firebase custom claims |

## Risk Matrix

| Risk Level | Count |
|------------|-------|
| CRITICAL | 1 |
| HIGH | 3 |
| MEDIUM | 6 |
| LOW | 0 |

## Compliance

| Regulation | Status |
|------------|--------|
| GDPR | ✅ Implemented (PII redaction, retention) |
| CCPA | ✅ Implemented |


