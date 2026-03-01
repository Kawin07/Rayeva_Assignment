# ARCHITECTURE

## Request Flow

1. Request enters Flask app.
2. `before_request` assigns or propagates `request_id`.
3. Route validates auth and RBAC via middleware.
4. Route validates/sanitizes JSON via shared utility.
5. Route delegates to service layer.
6. Service executes business flow and orchestration.
7. AI task goes through queue abstraction.
8. AI client performs resilient provider calls with timeout/retry.
9. Service validates AI output schema before persistence.
10. Service writes model data and AI logs.
11. Response returns with `X-Request-Id`.

## Layered Design

- `app/routes`: HTTP and transport concerns only.
- `app/services`: business orchestration, transactions, idempotency.
- `app/tasks`: queue-ready task execution abstraction.
- `app/modules`: AI module logic and prompts.
- `app/modules/ai_client.py`: provider API adapter and resilience.
- `app/models`: persistence models and indexes.
- `app/security`: auth, RBAC, rate limiting, webhook verification.
- `app/errors.py`: centralized API error envelope.

## AI Orchestration

- AI-triggering routes call service methods.
- Services call module generators through `queue.submit(...)` for queue migration readiness.
- Modules generate prompts and transform domain data.
- `AIClient` enforces timeout, retry, exponential backoff, and robust JSON extraction.
- Service layer performs strict schema validation before DB writes.

## Logging System

- Request correlation uses `X-Request-Id`.
- Correlation ID stored on `ai_logs.request_id`.
- AI prompt/response logging goes through `log_ai_interaction`.
- Webhook verification logs metadata (event id, timestamp, path) without body leakage.

## Error Handling

- Centralized handlers produce one secure response shape:

```json
{
  "success": false,
  "error": {
    "code": "...",
    "message": "...",
    "request_id": "..."
  }
}
```

- Runtime exceptions map to generic internal errors.
- Validation and HTTP exceptions map to stable API error codes.

## Security Design

- Token-based auth with role validation.
- RBAC guards on products/proposals/orders routes.
- Payload size limits with `MAX_CONTENT_LENGTH` and per-route checks.
- Schema validation for all JSON input.
- Webhook signature verification and replay window checks.
- No API secrets in code; environment-only configuration.

## Scalability Strategy

- Queue abstraction allows swapping synchronous execution for Celery/RQ.
- Idempotency records protect against duplicate order/proposal creation.
- DB indexes added for query-heavy fields.
- AI call retries and timeouts reduce cascading failures.
