ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS ml_status VARCHAR DEFAULT 'PENDING';
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS ml_decision VARCHAR;
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS ml_confidence FLOAT;
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS adjusted_remaining FLOAT;
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS arrhenius_remaining FLOAT;
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS ml_processed_at TIMESTAMP;