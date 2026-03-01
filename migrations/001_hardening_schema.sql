CREATE TABLE IF NOT EXISTS idempotency_records (
    id INTEGER PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    idempotency_key VARCHAR(255) NOT NULL,
    request_hash VARCHAR(128) NOT NULL,
    response_payload JSON NOT NULL,
    status_code INTEGER NOT NULL,
    created_at DATETIME
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_endpoint_idempotency_key ON idempotency_records(endpoint, idempotency_key);
CREATE INDEX IF NOT EXISTS ix_idempotency_created_at ON idempotency_records(created_at);

ALTER TABLE ai_logs ADD COLUMN request_id VARCHAR(64);

CREATE INDEX IF NOT EXISTS ix_ai_logs_module_created ON ai_logs(module, created_at);
CREATE INDEX IF NOT EXISTS ix_ai_logs_request_id ON ai_logs(request_id);
CREATE INDEX IF NOT EXISTS ix_products_primary_category ON products(primary_category);
CREATE INDEX IF NOT EXISTS ix_products_created_at ON products(created_at);
CREATE INDEX IF NOT EXISTS ix_proposals_client_name ON proposals(client_name);
CREATE INDEX IF NOT EXISTS ix_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS ix_proposals_created_at ON proposals(created_at);
CREATE INDEX IF NOT EXISTS ix_orders_customer_name ON orders(customer_name);
CREATE INDEX IF NOT EXISTS ix_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders(created_at);
