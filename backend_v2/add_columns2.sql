ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS adjusted_remaining FLOAT;
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS arrhenius_remaining FLOAT;