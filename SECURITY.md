# SECURITY

## Authentication and Authorization

- Bearer token authentication is enforced by middleware.
- Token map comes from `AUTH_TOKEN_MAP` environment variable.
- RBAC roles: `admin`, `support`, `user`.
- Unauthorized and forbidden requests return standardized secure errors.

## Secret Management

- `SECRET_KEY` and API keys are environment-only.
- App fails fast in staging/production when `SECRET_KEY` is missing.
- Webhook secret is loaded from `WEBHOOK_SECRET`.

## Rate Limiting

- AI-triggering endpoints use middleware rate limiting.
- Global default limit controlled by `RATE_LIMIT_PER_MINUTE`.
- High-volume webhook route has separate limit.

## Webhook Verification

- Signature headers required:
  - `X-Webhook-Signature`
  - `X-Webhook-Timestamp`
  - `X-Webhook-Event-Id`
- HMAC SHA-256 verification uses `WEBHOOK_SECRET`.
- Replay protection:
  - timestamp validation window
  - duplicate event-id cache rejection

## Request Safety

- Content type and JSON payload schema are validated.
- Request size is constrained globally and per endpoint.
- Free-text message length limits are enforced.
- Invalid JSON and invalid schemas return secure validation errors.

## AI Safety and Resilience

- AI calls use timeout and retry with exponential backoff.
- AI parsing uses robust JSON extraction to avoid nested-brace parsing issues.
- AI outputs are validated against strict schemas before DB writes.
- Fallback behavior exists when AI call/parsing fails.

## Logging and Traceability

- Request correlation ID is generated/provided and returned in response headers.
- Correlation ID is persisted in AI logs for auditability.
- Error responses include request ID for trace investigations.
