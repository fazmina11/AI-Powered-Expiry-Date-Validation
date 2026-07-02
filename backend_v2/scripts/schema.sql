-- Full Expiry Validation PostgreSQL schema dump
-- Generated from backend_v2 SQLAlchemy models.
-- Restore with: psql -U expiry_user -d expiry_db -f full_expiry_db_dump.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE audit_logs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	event_type VARCHAR(100) NOT NULL, 
	entity_type VARCHAR(100), 
	entity_id VARCHAR(100), 
	action VARCHAR(100), 
	message TEXT, 
	metadata_json JSONB, 
	actor_id VARCHAR(200), 
	actor_name VARCHAR(150), 
	actor_type VARCHAR(50), 
	before_state JSON, 
	after_state JSON, 
	change_summary TEXT, 
	ip_address VARCHAR(50), 
	user_agent VARCHAR(500), 
	request_id VARCHAR(100), 
	occurred_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

<<<<<<< HEAD
CREATE INDEX IF NOT EXISTS idx_products_sku      ON products (sku);
CREATE INDEX IF NOT EXISTS idx_products_barcode  ON products (barcode);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_brand    ON products (brand);

-- =============================================================
-- 0. users
-- Application users for authentication
-- =============================================================
CREATE TABLE IF NOT EXISTS users (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    name          VARCHAR(255),
    hashed_password TEXT       NOT NULL,
    is_active     BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- =============================================================
-- 2. barcode_scans
-- Records every barcode scanning event.
-- A scan may or may not resolve to a known product.
-- =============================================================
CREATE TABLE IF NOT EXISTS barcode_scans (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID        REFERENCES products (id) ON DELETE SET NULL,
    -- NULL when barcode is not yet registered in the catalogue
    raw_barcode     VARCHAR(255) NOT NULL,
    barcode_type    VARCHAR(20),
    scan_source     VARCHAR(100),
    -- device_id, session_id, api_client
    scan_status     VARCHAR(20)  NOT NULL DEFAULT 'unresolved',
    -- resolved | unresolved
    notes           TEXT,
    scanned_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
=======
CREATE TABLE products (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	brand VARCHAR(255), 
	manufacturer VARCHAR(255), 
	sku VARCHAR(100) NOT NULL, 
	barcode VARCHAR(100) NOT NULL, 
	barcode_type VARCHAR(20) DEFAULT 'EAN13' NOT NULL, 
	category VARCHAR(100), 
	sub_category VARCHAR(100), 
	description TEXT, 
	net_quantity VARCHAR(100), 
	unit VARCHAR(50), 
	mrp NUMERIC(10, 2), 
	currency VARCHAR(10) DEFAULT 'INR' NOT NULL, 
	country_of_origin VARCHAR(100), 
	product_type VARCHAR(100), 
	default_storage_type VARCHAR(50), 
	shelf_life_label VARCHAR(255), 
	image_url VARCHAR(500), 
	product_image_url VARCHAR(500), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	is_perishable BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
>>>>>>> 0f02161 (Update project for Harish branch)
);

CREATE TABLE scan_sessions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	session_status VARCHAR(50) DEFAULT 'IN_PROGRESS' NOT NULL, 
	operator_name VARCHAR(150), 
	device_id VARCHAR(150), 
	notes TEXT, 
	started_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE suppliers (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	contact_name VARCHAR(150), 
	phone VARCHAR(50), 
	email VARCHAR(255), 
	address TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE warehouses (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	code VARCHAR(100), 
	address TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (code)
);

CREATE TABLE barcode_scans (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID, 
	scan_session_id UUID, 
	raw_barcode VARCHAR(255) NOT NULL, 
	barcode_type VARCHAR(20), 
	scan_source VARCHAR(100), 
	scan_status VARCHAR(20) DEFAULT 'unresolved' NOT NULL, 
	notes TEXT, 
	scanned_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE SET NULL, 
	FOREIGN KEY(scan_session_id) REFERENCES scan_sessions (id) ON DELETE SET NULL
);

CREATE TABLE external_product_enrichment_logs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID, 
	barcode_value VARCHAR(150) NOT NULL, 
	provider VARCHAR(100) NOT NULL, 
	request_url TEXT, 
	response_status VARCHAR(50) NOT NULL, 
	response_json JSONB, 
	error_message TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE SET NULL
);

CREATE TABLE product_allergens (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	allergen_name VARCHAR(150) NOT NULL, 
	allergen_type VARCHAR(100), 
	contains BOOLEAN NOT NULL, 
	may_contain BOOLEAN NOT NULL, 
	source_text TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE product_identifiers (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	identifier_value VARCHAR(150) NOT NULL, 
	identifier_type VARCHAR(50) NOT NULL, 
	is_primary BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE product_images (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	scan_session_id UUID, 
	file_path VARCHAR(500) NOT NULL, 
	file_url VARCHAR(500), 
	file_size_bytes INTEGER, 
	mime_type VARCHAR(100), 
	image_type VARCHAR(50), 
	processing_status VARCHAR(30) DEFAULT 'uploaded' NOT NULL, 
	notes TEXT, 
	uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE, 
	FOREIGN KEY(scan_session_id) REFERENCES scan_sessions (id) ON DELETE SET NULL
);

CREATE TABLE product_ingredients (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	ingredient_name VARCHAR(255) NOT NULL, 
	ingredient_order INTEGER, 
	percentage NUMERIC(5, 2), 
	is_additive BOOLEAN NOT NULL, 
	additive_code VARCHAR(50), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE product_nutrition (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	serving_size VARCHAR(100), 
	calories NUMERIC(10, 2), 
	protein_g NUMERIC(10, 2), 
	carbohydrates_g NUMERIC(10, 2), 
	sugar_g NUMERIC(10, 2), 
	fat_g NUMERIC(10, 2), 
	saturated_fat_g NUMERIC(10, 2), 
	sodium_mg NUMERIC(10, 2), 
	fiber_g NUMERIC(10, 2), 
	raw_nutrition_text TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE product_storage_requirements (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	storage_type VARCHAR(50) NOT NULL, 
	min_temperature_c NUMERIC(5, 2), 
	max_temperature_c NUMERIC(5, 2), 
	humidity_notes TEXT, 
	handling_notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE storage_locations (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	warehouse_id UUID NOT NULL, 
	location_code VARCHAR(100) NOT NULL, 
	zone VARCHAR(100), 
	aisle VARCHAR(50), 
	rack VARCHAR(50), 
	shelf VARCHAR(50), 
	bin VARCHAR(50), 
	storage_type VARCHAR(50), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE CASCADE
);

CREATE TABLE inventory_items (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_id UUID NOT NULL, 
	barcode_scan_id UUID, 
	scan_session_id UUID, 
	ocr_result_id UUID, 
	supplier_id UUID, 
	warehouse_id UUID, 
	storage_location_id UUID, 
	batch_number VARCHAR(100), 
	manufacturing_date DATE, 
	expiry_date DATE, 
	packed_date DATE, 
	pipeline_status VARCHAR(30) DEFAULT 'PENDING_OCR' NOT NULL, 
	status_reason TEXT, 
	intake_source VARCHAR(50) DEFAULT 'OCR_SCAN' NOT NULL, 
	intake_status VARCHAR(50) DEFAULT 'DATA_INCOMPLETE' NOT NULL, 
	operator_decision VARCHAR(100), 
	quantity INTEGER DEFAULT 1, 
	unit VARCHAR(20), 
	intake_notes TEXT, 
	notes TEXT, 
	intake_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE RESTRICT, 
	FOREIGN KEY(barcode_scan_id) REFERENCES barcode_scans (id) ON DELETE SET NULL, 
	FOREIGN KEY(scan_session_id) REFERENCES scan_sessions (id) ON DELETE SET NULL, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL, 
	FOREIGN KEY(warehouse_id) REFERENCES warehouses (id) ON DELETE SET NULL, 
	FOREIGN KEY(storage_location_id) REFERENCES storage_locations (id) ON DELETE SET NULL
);

CREATE TABLE inventory_movements (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	inventory_item_id UUID NOT NULL, 
	from_location_id UUID, 
	to_location_id UUID, 
	movement_type VARCHAR(50) NOT NULL, 
	quantity INTEGER NOT NULL, 
	reason TEXT, 
	moved_by VARCHAR(100), 
	moved_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(inventory_item_id) REFERENCES inventory_items (id) ON DELETE CASCADE, 
	FOREIGN KEY(from_location_id) REFERENCES storage_locations (id) ON DELETE SET NULL, 
	FOREIGN KEY(to_location_id) REFERENCES storage_locations (id) ON DELETE SET NULL
);

CREATE TABLE ml_predictions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	inventory_item_id UUID NOT NULL, 
	model_name VARCHAR(200), 
	model_version VARCHAR(50), 
	predicted_mfg_date DATE, 
	predicted_expiry_date DATE, 
	predicted_remaining_days INTEGER, 
	predicted_decision VARCHAR(30), 
	decision_confidence FLOAT, 
	decision_reason TEXT, 
	raw_prediction_payload TEXT, 
	prediction_status VARCHAR(20) DEFAULT 'pending' NOT NULL, 
	failure_reason TEXT, 
	predicted_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(inventory_item_id) REFERENCES inventory_items (id) ON DELETE CASCADE
);

CREATE TABLE ocr_results (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	product_image_id UUID NOT NULL, 
	product_id UUID, 
	scan_session_id UUID, 
	inventory_item_id UUID, 
	raw_text TEXT, 
	ocr_engine VARCHAR(100), 
	ocr_engine_version VARCHAR(50), 
	extracted_text_blocks JSON, 
	overall_confidence FLOAT, 
	ocr_confidence NUMERIC(5, 4), 
	extracted_product_name VARCHAR(255), 
	extracted_brand VARCHAR(150), 
	extracted_description TEXT, 
	extracted_ingredients_text TEXT, 
	extracted_nutrition_text TEXT, 
	candidate_mfg_date DATE, 
	candidate_expiry_date DATE, 
	candidate_packed_date DATE, 
	best_before_text VARCHAR(255), 
	batch_number_detected VARCHAR(100), 
	mrp_detected NUMERIC(10, 2), 
	date_parse_confidence NUMERIC(5, 4), 
	response_json JSONB, 
	ocr_status VARCHAR(30) DEFAULT 'PENDING' NOT NULL, 
	failure_reason TEXT, 
	processed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_image_id) REFERENCES product_images (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE SET NULL, 
	FOREIGN KEY(scan_session_id) REFERENCES scan_sessions (id) ON DELETE SET NULL, 
	FOREIGN KEY(inventory_item_id) REFERENCES inventory_items (id) ON DELETE SET NULL
);

CREATE TABLE scan_alerts (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	scan_session_id UUID, 
	inventory_item_id UUID, 
	alert_type VARCHAR(100) NOT NULL, 
	severity VARCHAR(50) DEFAULT 'WARNING' NOT NULL, 
	field_name VARCHAR(100), 
	message TEXT NOT NULL, 
	is_resolved BOOLEAN DEFAULT false NOT NULL, 
	resolved_by VARCHAR(150), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	resolved_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(scan_session_id) REFERENCES scan_sessions (id) ON DELETE SET NULL, 
	FOREIGN KEY(inventory_item_id) REFERENCES inventory_items (id) ON DELETE SET NULL
);

CREATE TABLE storage_contexts (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	inventory_item_id UUID NOT NULL, 
	warehouse_id VARCHAR(100), 
	zone VARCHAR(100), 
	aisle VARCHAR(50), 
	shelf VARCHAR(50), 
	bin_location VARCHAR(100), 
	storage_type VARCHAR(50), 
	temperature_celsius FLOAT, 
	humidity_percent FLOAT, 
	notes TEXT, 
	recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (inventory_item_id), 
	FOREIGN KEY(inventory_item_id) REFERENCES inventory_items (id) ON DELETE CASCADE
);

CREATE TABLE manual_reviews (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	scan_session_id UUID, 
	inventory_item_id UUID, 
	ocr_result_id UUID, 
	review_type VARCHAR(50) DEFAULT 'OCR_CORRECTION' NOT NULL, 
	original_mfg_date DATE, 
	original_expiry_date DATE, 
	corrected_mfg_date DATE, 
	corrected_expiry_date DATE, 
	corrected_batch_number VARCHAR(100), 
	corrected_description TEXT, 
	reviewer_id VARCHAR(200), 
	reviewer_name VARCHAR(150), 
	reviewer_role VARCHAR(100), 
	reviewer_note TEXT, 
	human_decision VARCHAR(30), 
	review_notes TEXT, 
	escalation_reason TEXT, 
	review_status VARCHAR(20) DEFAULT 'PENDING' NOT NULL, 
	reviewed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(scan_session_id) REFERENCES scan_sessions (id) ON DELETE SET NULL, 
	FOREIGN KEY(inventory_item_id) REFERENCES inventory_items (id) ON DELETE CASCADE, 
	FOREIGN KEY(ocr_result_id) REFERENCES ocr_results (id) ON DELETE SET NULL
);

CREATE INDEX ix_audit_logs_action ON audit_logs (action);
CREATE INDEX ix_audit_logs_entity_id ON audit_logs (entity_id);
CREATE INDEX ix_audit_logs_event_type ON audit_logs (event_type);
CREATE INDEX ix_audit_logs_id ON audit_logs (id);
CREATE INDEX ix_audit_logs_occurred_at ON audit_logs (occurred_at);

CREATE UNIQUE INDEX ix_products_barcode ON products (barcode);
CREATE INDEX ix_products_id ON products (id);
CREATE UNIQUE INDEX ix_products_sku ON products (sku);

CREATE INDEX ix_scan_sessions_id ON scan_sessions (id);
CREATE INDEX ix_scan_sessions_session_status ON scan_sessions (session_status);

CREATE INDEX ix_suppliers_id ON suppliers (id);

CREATE INDEX ix_warehouses_id ON warehouses (id);

CREATE INDEX ix_barcode_scans_id ON barcode_scans (id);
CREATE INDEX ix_barcode_scans_scan_session_id ON barcode_scans (scan_session_id);

CREATE INDEX ix_external_product_enrichment_logs_barcode_value ON external_product_enrichment_logs (barcode_value);
CREATE INDEX ix_external_product_enrichment_logs_id ON external_product_enrichment_logs (id);
CREATE INDEX ix_external_product_enrichment_logs_product_id ON external_product_enrichment_logs (product_id);
CREATE INDEX ix_external_product_enrichment_logs_response_status ON external_product_enrichment_logs (response_status);

CREATE INDEX ix_product_allergens_allergen_name ON product_allergens (allergen_name);
CREATE INDEX ix_product_allergens_id ON product_allergens (id);
CREATE INDEX ix_product_allergens_product_id ON product_allergens (product_id);

CREATE INDEX ix_product_identifiers_id ON product_identifiers (id);
CREATE INDEX ix_product_identifiers_identifier_value ON product_identifiers (identifier_value);
CREATE INDEX ix_product_identifiers_product_id ON product_identifiers (product_id);

CREATE INDEX ix_product_images_id ON product_images (id);
CREATE INDEX ix_product_images_scan_session_id ON product_images (scan_session_id);

CREATE INDEX ix_product_ingredients_id ON product_ingredients (id);
CREATE INDEX ix_product_ingredients_ingredient_name ON product_ingredients (ingredient_name);
CREATE INDEX ix_product_ingredients_product_id ON product_ingredients (product_id);

CREATE INDEX ix_product_nutrition_id ON product_nutrition (id);
CREATE UNIQUE INDEX ix_product_nutrition_product_id ON product_nutrition (product_id);

CREATE INDEX ix_product_storage_requirements_id ON product_storage_requirements (id);
CREATE INDEX ix_product_storage_requirements_product_id ON product_storage_requirements (product_id);

CREATE INDEX ix_storage_locations_id ON storage_locations (id);
CREATE INDEX ix_storage_locations_location_code ON storage_locations (location_code);
CREATE INDEX ix_storage_locations_warehouse_id ON storage_locations (warehouse_id);

ALTER TABLE inventory_items ADD CONSTRAINT fk_inventory_items_ocr_result_id FOREIGN KEY(ocr_result_id) REFERENCES ocr_results (id) ON DELETE SET NULL;
CREATE INDEX ix_inventory_items_batch_number ON inventory_items (batch_number);
CREATE INDEX ix_inventory_items_id ON inventory_items (id);
CREATE INDEX ix_inventory_items_intake_status ON inventory_items (intake_status);
CREATE INDEX ix_inventory_items_ocr_result_id ON inventory_items (ocr_result_id);
CREATE INDEX ix_inventory_items_pipeline_status ON inventory_items (pipeline_status);
CREATE INDEX ix_inventory_items_scan_session_id ON inventory_items (scan_session_id);
CREATE INDEX ix_inventory_items_storage_location_id ON inventory_items (storage_location_id);
CREATE INDEX ix_inventory_items_supplier_id ON inventory_items (supplier_id);
CREATE INDEX ix_inventory_items_warehouse_id ON inventory_items (warehouse_id);

CREATE INDEX ix_inventory_movements_id ON inventory_movements (id);
CREATE INDEX ix_inventory_movements_inventory_item_id ON inventory_movements (inventory_item_id);
CREATE INDEX ix_inventory_movements_movement_type ON inventory_movements (movement_type);

CREATE INDEX ix_ml_predictions_id ON ml_predictions (id);
CREATE INDEX ix_ml_predictions_inventory_item_id ON ml_predictions (inventory_item_id);
CREATE INDEX ix_ml_predictions_predicted_decision ON ml_predictions (predicted_decision);

CREATE INDEX ix_ocr_results_id ON ocr_results (id);
CREATE INDEX ix_ocr_results_product_id ON ocr_results (product_id);
CREATE INDEX ix_ocr_results_scan_session_id ON ocr_results (scan_session_id);

CREATE INDEX ix_scan_alerts_alert_type ON scan_alerts (alert_type);
CREATE INDEX ix_scan_alerts_id ON scan_alerts (id);
CREATE INDEX ix_scan_alerts_inventory_item_id ON scan_alerts (inventory_item_id);
CREATE INDEX ix_scan_alerts_is_resolved ON scan_alerts (is_resolved);
CREATE INDEX ix_scan_alerts_scan_session_id ON scan_alerts (scan_session_id);
CREATE INDEX ix_scan_alerts_severity ON scan_alerts (severity);

CREATE INDEX ix_storage_contexts_id ON storage_contexts (id);

CREATE INDEX ix_manual_reviews_human_decision ON manual_reviews (human_decision);
CREATE INDEX ix_manual_reviews_id ON manual_reviews (id);
CREATE INDEX ix_manual_reviews_inventory_item_id ON manual_reviews (inventory_item_id);
CREATE INDEX ix_manual_reviews_ocr_result_id ON manual_reviews (ocr_result_id);
CREATE INDEX ix_manual_reviews_review_status ON manual_reviews (review_status);
CREATE INDEX ix_manual_reviews_scan_session_id ON manual_reviews (scan_session_id);

