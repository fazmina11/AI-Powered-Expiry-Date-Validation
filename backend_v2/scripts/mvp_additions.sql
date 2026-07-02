-- =============================================================
-- MVP ADDITIONS — New tables + column extensions
-- Safe to run multiple times (IF NOT EXISTS / ADD COLUMN IF NOT EXISTS)
-- =============================================================

-- ── 1. INGREDIENTS ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ingredients (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                  TEXT        NOT NULL UNIQUE,
    normalized_name       TEXT        NOT NULL,
    ingredient_type       TEXT,
    -- base | additive | preservative | flavoring | color | stabilizer
    description           TEXT,
    known_shelf_life_impact TEXT,
    -- extends | reduces | neutral | unknown
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ingredients_name            ON ingredients (normalized_name);
CREATE INDEX IF NOT EXISTS idx_ingredients_type            ON ingredients (ingredient_type);

-- ── 2. PRODUCT_INGREDIENTS ───────────────────────────────────
CREATE TABLE IF NOT EXISTS product_ingredients (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id        UUID        NOT NULL REFERENCES products(id)     ON DELETE CASCADE,
    ingredient_id     UUID        NOT NULL REFERENCES ingredients(id)  ON DELETE RESTRICT,
    ingredient_order  INT,
    percentage        NUMERIC(5,2),
    source            TEXT,
    -- manual | ocr | barcode_api | llm_extracted
    confidence        NUMERIC(5,2),
    raw_text          TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (product_id, ingredient_id)
);
CREATE INDEX IF NOT EXISTS idx_product_ingredients_product_id    ON product_ingredients (product_id);
CREATE INDEX IF NOT EXISTS idx_product_ingredients_ingredient_id ON product_ingredients (ingredient_id);

-- ── 3. PRESERVATIVES ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preservatives (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    ingredient_id     UUID        REFERENCES ingredients(id) ON DELETE SET NULL,
    name              TEXT        NOT NULL,
    code              TEXT,
    -- INS / E-number (e.g. E211, INS202)
    preservative_type TEXT,
    -- antimicrobial | antioxidant | acidity_regulator | stabilizer
    expected_effect   TEXT,
    -- extends_shelf_life | prevents_spoilage | slows_oxidation
    risk_notes        TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_preservatives_ingredient_id ON preservatives (ingredient_id);
CREATE INDEX IF NOT EXISTS idx_preservatives_type          ON preservatives (preservative_type);

-- ── 4. PRODUCT_PACKAGING ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS product_packaging (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id            UUID        NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    packaging_type        TEXT,
    -- plastic | glass | tetra_pack | can | pouch | paper
    seal_type             TEXT,
    -- vacuum_sealed | heat_sealed | screw_cap | open_pack
    is_resealable         BOOLEAN     NOT NULL DEFAULT false,
    light_exposure_level  TEXT,
    -- low | medium | high
    oxygen_barrier_level  TEXT,
    -- low | medium | high
    moisture_barrier_level TEXT,
    notes                 TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_product_packaging_product_id    ON product_packaging (product_id);
CREATE INDEX IF NOT EXISTS idx_product_packaging_type          ON product_packaging (packaging_type);

-- ── 5. SCAN_SESSIONS ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scan_sessions (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_item_id               UUID        REFERENCES inventory_items(id) ON DELETE SET NULL,
    session_status                  TEXT        NOT NULL DEFAULT 'in_progress',
    -- in_progress | completed | blocked | failed
    barcode_completed               BOOLEAN     NOT NULL DEFAULT false,
    ocr_completed                   BOOLEAN     NOT NULL DEFAULT false,
    mfg_date_completed              BOOLEAN     NOT NULL DEFAULT false,
    expiry_date_completed           BOOLEAN     NOT NULL DEFAULT false,
    product_description_completed   BOOLEAN     NOT NULL DEFAULT false,
    ingredients_completed           BOOLEAN     NOT NULL DEFAULT false,
    blocking_reason                 TEXT,
    started_at                      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at                    TIMESTAMPTZ,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_inventory_item_id ON scan_sessions (inventory_item_id);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_status            ON scan_sessions (session_status);

-- ── 6. DATA_QUALITY_ISSUES ───────────────────────────────────
CREATE TABLE IF NOT EXISTS data_quality_issues (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_item_id   UUID        REFERENCES inventory_items(id) ON DELETE CASCADE,
    related_table       TEXT,
    related_record_id   UUID,
    issue_type          TEXT        NOT NULL,
    -- missing_barcode | missing_expiry | low_ocr_confidence | invalid_date
    severity            TEXT        NOT NULL,
    -- low | medium | high | critical
    issue_message       TEXT        NOT NULL,
    resolution_status   TEXT        NOT NULL DEFAULT 'open',
    -- open | in_progress | resolved | ignored
    resolved_by         TEXT,
    resolved_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_inventory_item_id ON data_quality_issues (inventory_item_id);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_issue_type        ON data_quality_issues (issue_type);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_severity          ON data_quality_issues (severity);
CREATE INDEX IF NOT EXISTS idx_data_quality_issues_resolution        ON data_quality_issues (resolution_status);

-- ── 7. SHELF_LIFE_RULES ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS shelf_life_rules (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    category              TEXT        NOT NULL,
    storage_type          TEXT,
    -- ambient | refrigerated | frozen | controlled
    packaging_type        TEXT,
    ingredient_pattern    TEXT,
    -- regex or keyword pattern matched against ingredient list
    preservative_pattern  TEXT,
    estimated_min_days    INT,
    estimated_max_days    INT,
    confidence            NUMERIC(5,2),
    rule_source           TEXT,
    -- manual | dataset | llm_generated | validated
    notes                 TEXT,
    is_active             BOOLEAN     NOT NULL DEFAULT true,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_shelf_life_rules_category     ON shelf_life_rules (category);
CREATE INDEX IF NOT EXISTS idx_shelf_life_rules_storage_type ON shelf_life_rules (storage_type);
CREATE INDEX IF NOT EXISTS idx_shelf_life_rules_is_active    ON shelf_life_rules (is_active);

-- =============================================================
-- COLUMN ADDITIONS TO EXISTING TABLES
-- Using IF NOT EXISTS so re-runs are safe
-- =============================================================

-- ── products — new columns ────────────────────────────────────
ALTER TABLE products
    ADD COLUMN IF NOT EXISTS gtin                 TEXT,
    ADD COLUMN IF NOT EXISTS manufacturer_name    TEXT,
    ADD COLUMN IF NOT EXISTS country_of_origin    TEXT,
    ADD COLUMN IF NOT EXISTS net_quantity         TEXT,
    ADD COLUMN IF NOT EXISTS ingredients_raw_text TEXT,
    ADD COLUMN IF NOT EXISTS nutrition_raw_text   TEXT,
    ADD COLUMN IF NOT EXISTS allergen_info        TEXT,
    ADD COLUMN IF NOT EXISTS product_form         TEXT;
    -- powder | liquid | solid | frozen | semi-solid

-- ── inventory_items — new columns ────────────────────────────
ALTER TABLE inventory_items
    ADD COLUMN IF NOT EXISTS opened_at            TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS is_opened            BOOLEAN NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS observed_condition   TEXT,
    -- sealed | damaged | leaked | bloated | spoiled
    ADD COLUMN IF NOT EXISTS quality_score        NUMERIC(5,2);

-- ── ocr_results — new columns ────────────────────────────────
ALTER TABLE ocr_results
    ADD COLUMN IF NOT EXISTS detected_mfg_text          TEXT,
    ADD COLUMN IF NOT EXISTS detected_expiry_text        TEXT,
    ADD COLUMN IF NOT EXISTS detected_ingredients_text   TEXT,
    ADD COLUMN IF NOT EXISTS detected_nutrition_text     TEXT,
    ADD COLUMN IF NOT EXISTS date_parse_confidence       NUMERIC(5,2);
