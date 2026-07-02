--
-- PostgreSQL database dump
--

\restrict IgNhiHC509mTrl9pwgW36CugVifYXEfXdBO82iEQ0ubB5a5XmhznXXfipmZsumh

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type character varying(100) NOT NULL,
    entity_type character varying(100),
    entity_id character varying(100),
    action character varying(100),
    message text,
    metadata_json jsonb,
    actor_id character varying(200),
    actor_name character varying(150),
    actor_type character varying(50),
    before_state json,
    after_state json,
    change_summary text,
    ip_address character varying(50),
    user_agent character varying(500),
    request_id character varying(100),
    occurred_at timestamp with time zone DEFAULT now() NOT NULL
);

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

--
-- Name: barcode_scans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.barcode_scans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid,
    scan_session_id uuid,
    raw_barcode character varying(255) NOT NULL,
    barcode_type character varying(20),
    scan_source character varying(100),
    scan_status character varying(20) DEFAULT 'unresolved'::character varying NOT NULL,
    notes text,
    scanned_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


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
);

--
-- Name: external_product_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.external_product_cache (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    query_value character varying(255) NOT NULL,
    query_type character varying(50) NOT NULL,
    external_source character varying(100) DEFAULT 'OPEN_FOOD_FACTS'::character varying NOT NULL,
    external_product_id character varying(255),
    external_source_url text,
    barcode character varying(100),
    product_name character varying(255),
    brand character varying(150),
    category character varying(150),
    description text,
    ingredients text,
    nutrition_info jsonb,
    storage_instruction text,
    image_url text,
    raw_response jsonb,
    cache_status character varying(50) DEFAULT 'ACTIVE'::character varying,
    fetched_at timestamp without time zone DEFAULT now(),
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


--
-- Name: external_product_enrichment_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.external_product_enrichment_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid,
    barcode_value character varying(150) NOT NULL,
    provider character varying(100) NOT NULL,
    request_url text,
    response_status character varying(50) NOT NULL,
    response_json jsonb,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: inventory_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    barcode_scan_id uuid,
    scan_session_id uuid,
    ocr_result_id uuid,
    supplier_id uuid,
    warehouse_id uuid,
    storage_location_id uuid,
    batch_number character varying(100),
    manufacturing_date date,
    expiry_date date,
    packed_date date,
    pipeline_status character varying(30) DEFAULT 'PENDING_OCR'::character varying NOT NULL,
    status_reason text,
    intake_source character varying(50) DEFAULT 'OCR_SCAN'::character varying NOT NULL,
    intake_status character varying(50) DEFAULT 'DATA_INCOMPLETE'::character varying NOT NULL,
    operator_decision character varying(100),
    quantity integer DEFAULT 1,
    unit character varying(20),
    intake_notes text,
    notes text,
    intake_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: inventory_movements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_movements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    inventory_item_id uuid NOT NULL,
    from_location_id uuid,
    to_location_id uuid,
    movement_type character varying(50) NOT NULL,
    quantity integer NOT NULL,
    reason text,
    moved_by character varying(100),
    moved_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: manual_reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.manual_reviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    scan_session_id uuid,
    inventory_item_id uuid,
    ocr_result_id uuid,
    review_type character varying(50) DEFAULT 'OCR_CORRECTION'::character varying NOT NULL,
    original_mfg_date date,
    original_expiry_date date,
    corrected_mfg_date date,
    corrected_expiry_date date,
    corrected_batch_number character varying(100),
    corrected_description text,
    reviewer_id character varying(200),
    reviewer_name character varying(150),
    reviewer_role character varying(100),
    reviewer_note text,
    human_decision character varying(30),
    review_notes text,
    escalation_reason text,
    review_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: ml_predictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ml_predictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    inventory_item_id uuid NOT NULL,
    model_name character varying(200),
    model_version character varying(50),
    predicted_mfg_date date,
    predicted_expiry_date date,
    predicted_remaining_days integer,
    predicted_decision character varying(30),
    decision_confidence double precision,
    decision_reason text,
    raw_prediction_payload text,
    prediction_status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    failure_reason text,
    predicted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: ocr_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ocr_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_image_id uuid NOT NULL,
    product_id uuid,
    scan_session_id uuid,
    inventory_item_id uuid,
    raw_text text,
    ocr_engine character varying(100),
    ocr_engine_version character varying(50),
    extracted_text_blocks json,
    overall_confidence double precision,
    ocr_confidence numeric(5,4),
    extracted_product_name character varying(255),
    extracted_brand character varying(150),
    extracted_description text,
    extracted_ingredients_text text,
    extracted_nutrition_text text,
    candidate_mfg_date date,
    candidate_expiry_date date,
    candidate_packed_date date,
    best_before_text character varying(255),
    batch_number_detected character varying(100),
    mrp_detected numeric(10,2),
    date_parse_confidence numeric(5,4),
    response_json jsonb,
    ocr_status character varying(30) DEFAULT 'PENDING'::character varying NOT NULL,
    failure_reason text,
    processed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: product_allergens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_allergens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    allergen_name character varying(150) NOT NULL,
    allergen_type character varying(100),
    contains boolean NOT NULL,
    may_contain boolean NOT NULL,
    source_text text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: product_identifiers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_identifiers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    identifier_value character varying(150) NOT NULL,
    identifier_type character varying(50) NOT NULL,
    is_primary boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    source character varying(50) DEFAULT 'LOCAL_DATABASE'::character varying
);


--
-- Name: product_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_images (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    scan_session_id uuid,
    file_path character varying(500) NOT NULL,
    file_url character varying(500),
    file_size_bytes integer,
    mime_type character varying(100),
    image_type character varying(50),
    processing_status character varying(30) DEFAULT 'uploaded'::character varying NOT NULL,
    notes text,
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: product_ingredients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_ingredients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    ingredient_name character varying(255) NOT NULL,
    ingredient_order integer,
    percentage numeric(5,2),
    is_additive boolean NOT NULL,
    additive_code character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: product_lookup_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_lookup_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    query_value character varying(255) NOT NULL,
    query_type character varying(50) NOT NULL,
    result_status character varying(50) NOT NULL,
    result_source character varying(100),
    product_id uuid,
    external_cache_id uuid,
    requested_by character varying(150),
    request_source character varying(100) DEFAULT 'BACKEND_API'::character varying,
    telegram_chat_id character varying(150),
    telegram_user_id character varying(150),
    n8n_execution_id character varying(150),
    response_payload jsonb,
    error_message text,
    lookup_duration_ms integer,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT chk_product_lookup_query_type CHECK (((query_type)::text = ANY ((ARRAY['PRODUCT_ID'::character varying, 'BARCODE'::character varying, 'PRODUCT_NAME'::character varying, 'UNKNOWN'::character varying])::text[]))),
    CONSTRAINT chk_product_lookup_result_source CHECK (((result_source)::text = ANY ((ARRAY['LOCAL_DATABASE'::character varying, 'OPEN_FOOD_FACTS'::character varying, 'CACHE'::character varying, 'NONE'::character varying])::text[]))),
    CONSTRAINT chk_product_lookup_result_status CHECK (((result_status)::text = ANY ((ARRAY['FOUND'::character varying, 'NOT_FOUND'::character varying, 'INVALID_QUERY'::character varying, 'EXTERNAL_API_FAILED'::character varying, 'ERROR'::character varying])::text[])))
);


--
-- Name: product_nutrition; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_nutrition (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    serving_size character varying(100),
    calories numeric(10,2),
    protein_g numeric(10,2),
    carbohydrates_g numeric(10,2),
    sugar_g numeric(10,2),
    fat_g numeric(10,2),
    saturated_fat_g numeric(10,2),
    sodium_mg numeric(10,2),
    fiber_g numeric(10,2),
    raw_nutrition_text text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: product_question_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_question_logs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    question text NOT NULL,
    detected_intent character varying(100),
    extracted_entity character varying(255),
    result_status character varying(50),
    result_source character varying(100),
    product_id uuid,
    inventory_item_id uuid,
    request_source character varying(100) DEFAULT 'BACKEND_API'::character varying,
    requested_by character varying(150),
    telegram_chat_id character varying(150),
    telegram_user_id character varying(150),
    n8n_execution_id character varying(150),
    response_payload jsonb,
    error_message text,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT chk_product_question_result_source CHECK (((result_source)::text = ANY ((ARRAY['LOCAL_DATABASE'::character varying, 'NONE'::character varying])::text[]))),
    CONSTRAINT chk_product_question_result_status CHECK (((result_status)::text = ANY ((ARRAY['ANSWERED'::character varying, 'NOT_FOUND'::character varying, 'UNSUPPORTED_INTENT'::character varying, 'INVALID_QUESTION'::character varying, 'ERROR'::character varying])::text[])))
);


--
-- Name: product_storage_requirements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product_storage_requirements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    product_id uuid NOT NULL,
    storage_type character varying(50) NOT NULL,
    min_temperature_c numeric(5,2),
    max_temperature_c numeric(5,2),
    humidity_notes text,
    handling_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    brand character varying(255),
    manufacturer character varying(255),
    sku character varying(100) NOT NULL,
    barcode character varying(100) NOT NULL,
    barcode_type character varying(20) DEFAULT 'EAN13'::character varying NOT NULL,
    category character varying(100),
    sub_category character varying(100),
    description text,
    net_quantity character varying(100),
    unit character varying(50),
    mrp numeric(10,2),
    currency character varying(10) DEFAULT 'INR'::character varying NOT NULL,
    country_of_origin character varying(100),
    product_type character varying(100),
    default_storage_type character varying(50),
    shelf_life_label character varying(255),
    image_url character varying(500),
    product_image_url character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    is_perishable boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    ingredients text,
    nutrition_info jsonb,
    storage_instruction text,
    product_source character varying(50) DEFAULT 'LOCAL_DATABASE'::character varying,
    external_source character varying(100),
    external_source_url text
);


--
-- Name: scan_alerts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scan_alerts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    scan_session_id uuid,
    inventory_item_id uuid,
    alert_type character varying(100) NOT NULL,
    severity character varying(50) DEFAULT 'WARNING'::character varying NOT NULL,
    field_name character varying(100),
    message text NOT NULL,
    is_resolved boolean DEFAULT false NOT NULL,
    resolved_by character varying(150),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_at timestamp with time zone
);


--
-- Name: scan_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scan_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    session_status character varying(50) DEFAULT 'IN_PROGRESS'::character varying NOT NULL,
    operator_name character varying(150),
    device_id character varying(150),
    notes text,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storage_contexts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storage_contexts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    inventory_item_id uuid NOT NULL,
    warehouse_id character varying(100),
    zone character varying(100),
    aisle character varying(50),
    shelf character varying(50),
    bin_location character varying(100),
    storage_type character varying(50),
    temperature_celsius double precision,
    humidity_percent double precision,
    notes text,
    recorded_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: storage_locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storage_locations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    warehouse_id uuid NOT NULL,
    location_code character varying(100) NOT NULL,
    zone character varying(100),
    aisle character varying(50),
    rack character varying(50),
    shelf character varying(50),
    bin character varying(50),
    storage_type character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suppliers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    contact_name character varying(150),
    phone character varying(50),
    email character varying(255),
    address text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: unknown_product_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.unknown_product_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    query_value character varying(255) NOT NULL,
    query_type character varying(50) NOT NULL,
    barcode character varying(100),
    product_name character varying(255),
    request_source character varying(100) DEFAULT 'BACKEND_API'::character varying,
    requested_by character varying(150),
    telegram_chat_id character varying(150),
    telegram_user_id character varying(150),
    n8n_execution_id character varying(150),
    status character varying(50) DEFAULT 'PENDING'::character varying,
    admin_notes text,
    resolved_product_id uuid,
    created_at timestamp without time zone DEFAULT now(),
    resolved_at timestamp without time zone,
    CONSTRAINT chk_unknown_product_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'CREATED'::character varying, 'IGNORED'::character varying, 'DUPLICATE'::character varying, 'RESOLVED'::character varying])::text[])))
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(255),
    hashed_password text NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.warehouses (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(100),
    address text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: barcode_scans barcode_scans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.barcode_scans
    ADD CONSTRAINT barcode_scans_pkey PRIMARY KEY (id);


--
-- Name: external_product_cache external_product_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_product_cache
    ADD CONSTRAINT external_product_cache_pkey PRIMARY KEY (id);


--
-- Name: external_product_enrichment_logs external_product_enrichment_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_product_enrichment_logs
    ADD CONSTRAINT external_product_enrichment_logs_pkey PRIMARY KEY (id);


--
-- Name: inventory_items inventory_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_pkey PRIMARY KEY (id);


--
-- Name: inventory_movements inventory_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_pkey PRIMARY KEY (id);


--
-- Name: manual_reviews manual_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manual_reviews
    ADD CONSTRAINT manual_reviews_pkey PRIMARY KEY (id);


--
-- Name: ml_predictions ml_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_predictions
    ADD CONSTRAINT ml_predictions_pkey PRIMARY KEY (id);


--
-- Name: ocr_results ocr_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocr_results
    ADD CONSTRAINT ocr_results_pkey PRIMARY KEY (id);


--
-- Name: product_allergens product_allergens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_allergens
    ADD CONSTRAINT product_allergens_pkey PRIMARY KEY (id);


--
-- Name: product_identifiers product_identifiers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_identifiers
    ADD CONSTRAINT product_identifiers_pkey PRIMARY KEY (id);


--
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (id);


--
-- Name: product_ingredients product_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_ingredients
    ADD CONSTRAINT product_ingredients_pkey PRIMARY KEY (id);


--
-- Name: product_lookup_logs product_lookup_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_lookup_logs
    ADD CONSTRAINT product_lookup_logs_pkey PRIMARY KEY (id);


--
-- Name: product_nutrition product_nutrition_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_nutrition
    ADD CONSTRAINT product_nutrition_pkey PRIMARY KEY (id);


--
-- Name: product_question_logs product_question_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_question_logs
    ADD CONSTRAINT product_question_logs_pkey PRIMARY KEY (id);


--
-- Name: product_storage_requirements product_storage_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_storage_requirements
    ADD CONSTRAINT product_storage_requirements_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: scan_alerts scan_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scan_alerts
    ADD CONSTRAINT scan_alerts_pkey PRIMARY KEY (id);


--
-- Name: scan_sessions scan_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scan_sessions
    ADD CONSTRAINT scan_sessions_pkey PRIMARY KEY (id);


--
-- Name: storage_contexts storage_contexts_inventory_item_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_contexts
    ADD CONSTRAINT storage_contexts_inventory_item_id_key UNIQUE (inventory_item_id);


--
-- Name: storage_contexts storage_contexts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_contexts
    ADD CONSTRAINT storage_contexts_pkey PRIMARY KEY (id);


--
-- Name: storage_locations storage_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_locations
    ADD CONSTRAINT storage_locations_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: unknown_product_requests unknown_product_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unknown_product_requests
    ADD CONSTRAINT unknown_product_requests_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: warehouses warehouses_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_code_key UNIQUE (code);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: idx_external_product_cache_barcode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_product_cache_barcode ON public.external_product_cache USING btree (barcode);


--
-- Name: idx_external_product_cache_product_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_product_cache_product_name ON public.external_product_cache USING btree (product_name);


--
-- Name: idx_external_product_cache_query; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_product_cache_query ON public.external_product_cache USING btree (query_type, query_value);


--
-- Name: idx_external_product_cache_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_external_product_cache_source ON public.external_product_cache USING btree (external_source);


--
-- Name: idx_product_identifiers_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_identifiers_product_id ON public.product_identifiers USING btree (product_id);


--
-- Name: idx_product_identifiers_unique_value; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_product_identifiers_unique_value ON public.product_identifiers USING btree (identifier_type, identifier_value);


--
-- Name: idx_product_identifiers_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_identifiers_value ON public.product_identifiers USING btree (identifier_value);


--
-- Name: idx_product_lookup_logs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_lookup_logs_created_at ON public.product_lookup_logs USING btree (created_at);


--
-- Name: idx_product_lookup_logs_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_lookup_logs_product_id ON public.product_lookup_logs USING btree (product_id);


--
-- Name: idx_product_lookup_logs_query; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_lookup_logs_query ON public.product_lookup_logs USING btree (query_type, query_value);


--
-- Name: idx_product_lookup_logs_result_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_lookup_logs_result_status ON public.product_lookup_logs USING btree (result_status);


--
-- Name: idx_product_question_logs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_question_logs_created_at ON public.product_question_logs USING btree (created_at);


--
-- Name: idx_product_question_logs_intent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_question_logs_intent ON public.product_question_logs USING btree (detected_intent);


--
-- Name: idx_product_question_logs_inventory_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_question_logs_inventory_item_id ON public.product_question_logs USING btree (inventory_item_id);


--
-- Name: idx_product_question_logs_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_product_question_logs_product_id ON public.product_question_logs USING btree (product_id);


--
-- Name: idx_products_brand; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_products_brand ON public.products USING btree (brand);


--
-- Name: idx_products_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_products_category ON public.products USING btree (category);


--
-- Name: idx_products_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_products_name ON public.products USING btree (name);


--
-- Name: idx_unknown_product_requests_barcode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_unknown_product_requests_barcode ON public.unknown_product_requests USING btree (barcode);


--
-- Name: idx_unknown_product_requests_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_unknown_product_requests_created_at ON public.unknown_product_requests USING btree (created_at);


--
-- Name: idx_unknown_product_requests_query; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_unknown_product_requests_query ON public.unknown_product_requests USING btree (query_type, query_value);


--
-- Name: idx_unknown_product_requests_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_unknown_product_requests_status ON public.unknown_product_requests USING btree (status);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_entity_id ON public.audit_logs USING btree (entity_id);


--
-- Name: ix_audit_logs_event_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_event_type ON public.audit_logs USING btree (event_type);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_audit_logs_occurred_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_occurred_at ON public.audit_logs USING btree (occurred_at);


--
-- Name: ix_barcode_scans_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_barcode_scans_id ON public.barcode_scans USING btree (id);


--
-- Name: ix_barcode_scans_scan_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_barcode_scans_scan_session_id ON public.barcode_scans USING btree (scan_session_id);


--
-- Name: ix_external_product_cache_barcode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_cache_barcode ON public.external_product_cache USING btree (barcode);


--
-- Name: ix_external_product_cache_external_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_cache_external_source ON public.external_product_cache USING btree (external_source);


--
-- Name: ix_external_product_cache_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_cache_id ON public.external_product_cache USING btree (id);


--
-- Name: ix_external_product_cache_product_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_cache_product_name ON public.external_product_cache USING btree (product_name);


--
-- Name: ix_external_product_cache_query_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_cache_query_type ON public.external_product_cache USING btree (query_type);


--
-- Name: ix_external_product_cache_query_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_cache_query_value ON public.external_product_cache USING btree (query_value);


--
-- Name: ix_external_product_enrichment_logs_barcode_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_enrichment_logs_barcode_value ON public.external_product_enrichment_logs USING btree (barcode_value);


--
-- Name: ix_external_product_enrichment_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_enrichment_logs_id ON public.external_product_enrichment_logs USING btree (id);


--
-- Name: ix_external_product_enrichment_logs_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_enrichment_logs_product_id ON public.external_product_enrichment_logs USING btree (product_id);


--
-- Name: ix_external_product_enrichment_logs_response_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_external_product_enrichment_logs_response_status ON public.external_product_enrichment_logs USING btree (response_status);


--
-- Name: ix_inventory_items_batch_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_batch_number ON public.inventory_items USING btree (batch_number);


--
-- Name: ix_inventory_items_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_id ON public.inventory_items USING btree (id);


--
-- Name: ix_inventory_items_intake_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_intake_status ON public.inventory_items USING btree (intake_status);


--
-- Name: ix_inventory_items_ocr_result_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_ocr_result_id ON public.inventory_items USING btree (ocr_result_id);


--
-- Name: ix_inventory_items_pipeline_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_pipeline_status ON public.inventory_items USING btree (pipeline_status);


--
-- Name: ix_inventory_items_scan_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_scan_session_id ON public.inventory_items USING btree (scan_session_id);


--
-- Name: ix_inventory_items_storage_location_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_storage_location_id ON public.inventory_items USING btree (storage_location_id);


--
-- Name: ix_inventory_items_supplier_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_supplier_id ON public.inventory_items USING btree (supplier_id);


--
-- Name: ix_inventory_items_warehouse_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_items_warehouse_id ON public.inventory_items USING btree (warehouse_id);


--
-- Name: ix_inventory_movements_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_movements_id ON public.inventory_movements USING btree (id);


--
-- Name: ix_inventory_movements_inventory_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_movements_inventory_item_id ON public.inventory_movements USING btree (inventory_item_id);


--
-- Name: ix_inventory_movements_movement_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_movements_movement_type ON public.inventory_movements USING btree (movement_type);


--
-- Name: ix_manual_reviews_human_decision; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_manual_reviews_human_decision ON public.manual_reviews USING btree (human_decision);


--
-- Name: ix_manual_reviews_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_manual_reviews_id ON public.manual_reviews USING btree (id);


--
-- Name: ix_manual_reviews_inventory_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_manual_reviews_inventory_item_id ON public.manual_reviews USING btree (inventory_item_id);


--
-- Name: ix_manual_reviews_ocr_result_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_manual_reviews_ocr_result_id ON public.manual_reviews USING btree (ocr_result_id);


--
-- Name: ix_manual_reviews_review_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_manual_reviews_review_status ON public.manual_reviews USING btree (review_status);


--
-- Name: ix_manual_reviews_scan_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_manual_reviews_scan_session_id ON public.manual_reviews USING btree (scan_session_id);


--
-- Name: ix_ml_predictions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ml_predictions_id ON public.ml_predictions USING btree (id);


--
-- Name: ix_ml_predictions_inventory_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ml_predictions_inventory_item_id ON public.ml_predictions USING btree (inventory_item_id);


--
-- Name: ix_ml_predictions_predicted_decision; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ml_predictions_predicted_decision ON public.ml_predictions USING btree (predicted_decision);


--
-- Name: ix_ocr_results_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ocr_results_id ON public.ocr_results USING btree (id);


--
-- Name: ix_ocr_results_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ocr_results_product_id ON public.ocr_results USING btree (product_id);


--
-- Name: ix_ocr_results_scan_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ocr_results_scan_session_id ON public.ocr_results USING btree (scan_session_id);


--
-- Name: ix_product_allergens_allergen_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_allergens_allergen_name ON public.product_allergens USING btree (allergen_name);


--
-- Name: ix_product_allergens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_allergens_id ON public.product_allergens USING btree (id);


--
-- Name: ix_product_allergens_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_allergens_product_id ON public.product_allergens USING btree (product_id);


--
-- Name: ix_product_identifiers_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_identifiers_id ON public.product_identifiers USING btree (id);


--
-- Name: ix_product_identifiers_identifier_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_identifiers_identifier_value ON public.product_identifiers USING btree (identifier_value);


--
-- Name: ix_product_identifiers_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_identifiers_product_id ON public.product_identifiers USING btree (product_id);


--
-- Name: ix_product_images_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_images_id ON public.product_images USING btree (id);


--
-- Name: ix_product_images_scan_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_images_scan_session_id ON public.product_images USING btree (scan_session_id);


--
-- Name: ix_product_ingredients_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_ingredients_id ON public.product_ingredients USING btree (id);


--
-- Name: ix_product_ingredients_ingredient_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_ingredients_ingredient_name ON public.product_ingredients USING btree (ingredient_name);


--
-- Name: ix_product_ingredients_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_ingredients_product_id ON public.product_ingredients USING btree (product_id);


--
-- Name: ix_product_lookup_logs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_lookup_logs_created_at ON public.product_lookup_logs USING btree (created_at);


--
-- Name: ix_product_lookup_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_lookup_logs_id ON public.product_lookup_logs USING btree (id);


--
-- Name: ix_product_lookup_logs_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_lookup_logs_product_id ON public.product_lookup_logs USING btree (product_id);


--
-- Name: ix_product_lookup_logs_query_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_lookup_logs_query_type ON public.product_lookup_logs USING btree (query_type);


--
-- Name: ix_product_lookup_logs_query_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_lookup_logs_query_value ON public.product_lookup_logs USING btree (query_value);


--
-- Name: ix_product_lookup_logs_result_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_lookup_logs_result_status ON public.product_lookup_logs USING btree (result_status);


--
-- Name: ix_product_nutrition_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_nutrition_id ON public.product_nutrition USING btree (id);


--
-- Name: ix_product_nutrition_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_product_nutrition_product_id ON public.product_nutrition USING btree (product_id);


--
-- Name: ix_product_storage_requirements_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_storage_requirements_id ON public.product_storage_requirements USING btree (id);


--
-- Name: ix_product_storage_requirements_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_product_storage_requirements_product_id ON public.product_storage_requirements USING btree (product_id);


--
-- Name: ix_products_barcode; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_products_barcode ON public.products USING btree (barcode);


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- Name: ix_products_sku; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_products_sku ON public.products USING btree (sku);


--
-- Name: ix_scan_alerts_alert_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_alerts_alert_type ON public.scan_alerts USING btree (alert_type);


--
-- Name: ix_scan_alerts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_alerts_id ON public.scan_alerts USING btree (id);


--
-- Name: ix_scan_alerts_inventory_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_alerts_inventory_item_id ON public.scan_alerts USING btree (inventory_item_id);


--
-- Name: ix_scan_alerts_is_resolved; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_alerts_is_resolved ON public.scan_alerts USING btree (is_resolved);


--
-- Name: ix_scan_alerts_scan_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_alerts_scan_session_id ON public.scan_alerts USING btree (scan_session_id);


--
-- Name: ix_scan_alerts_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_alerts_severity ON public.scan_alerts USING btree (severity);


--
-- Name: ix_scan_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_sessions_id ON public.scan_sessions USING btree (id);


--
-- Name: ix_scan_sessions_session_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_scan_sessions_session_status ON public.scan_sessions USING btree (session_status);


--
-- Name: ix_storage_contexts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_storage_contexts_id ON public.storage_contexts USING btree (id);


--
-- Name: ix_storage_locations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_storage_locations_id ON public.storage_locations USING btree (id);


--
-- Name: ix_storage_locations_location_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_storage_locations_location_code ON public.storage_locations USING btree (location_code);


--
-- Name: ix_storage_locations_warehouse_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_storage_locations_warehouse_id ON public.storage_locations USING btree (warehouse_id);


--
-- Name: ix_suppliers_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_suppliers_id ON public.suppliers USING btree (id);


--
-- Name: ix_unknown_product_requests_barcode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_unknown_product_requests_barcode ON public.unknown_product_requests USING btree (barcode);


--
-- Name: ix_unknown_product_requests_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_unknown_product_requests_created_at ON public.unknown_product_requests USING btree (created_at);


--
-- Name: ix_unknown_product_requests_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_unknown_product_requests_id ON public.unknown_product_requests USING btree (id);


--
-- Name: ix_unknown_product_requests_query_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_unknown_product_requests_query_type ON public.unknown_product_requests USING btree (query_type);


--
-- Name: ix_unknown_product_requests_query_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_unknown_product_requests_query_value ON public.unknown_product_requests USING btree (query_value);


--
-- Name: ix_unknown_product_requests_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_unknown_product_requests_status ON public.unknown_product_requests USING btree (status);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_warehouses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_warehouses_id ON public.warehouses USING btree (id);


--
-- Name: barcode_scans barcode_scans_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.barcode_scans
    ADD CONSTRAINT barcode_scans_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: barcode_scans barcode_scans_scan_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.barcode_scans
    ADD CONSTRAINT barcode_scans_scan_session_id_fkey FOREIGN KEY (scan_session_id) REFERENCES public.scan_sessions(id) ON DELETE SET NULL;


--
-- Name: external_product_enrichment_logs external_product_enrichment_logs_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.external_product_enrichment_logs
    ADD CONSTRAINT external_product_enrichment_logs_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: inventory_items fk_inventory_items_ocr_result_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT fk_inventory_items_ocr_result_id FOREIGN KEY (ocr_result_id) REFERENCES public.ocr_results(id) ON DELETE SET NULL;


--
-- Name: inventory_items inventory_items_barcode_scan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_barcode_scan_id_fkey FOREIGN KEY (barcode_scan_id) REFERENCES public.barcode_scans(id) ON DELETE SET NULL;


--
-- Name: inventory_items inventory_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE RESTRICT;


--
-- Name: inventory_items inventory_items_scan_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_scan_session_id_fkey FOREIGN KEY (scan_session_id) REFERENCES public.scan_sessions(id) ON DELETE SET NULL;


--
-- Name: inventory_items inventory_items_storage_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_storage_location_id_fkey FOREIGN KEY (storage_location_id) REFERENCES public.storage_locations(id) ON DELETE SET NULL;


--
-- Name: inventory_items inventory_items_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id) ON DELETE SET NULL;


--
-- Name: inventory_items inventory_items_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_items
    ADD CONSTRAINT inventory_items_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE SET NULL;


--
-- Name: inventory_movements inventory_movements_from_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_from_location_id_fkey FOREIGN KEY (from_location_id) REFERENCES public.storage_locations(id) ON DELETE SET NULL;


--
-- Name: inventory_movements inventory_movements_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE CASCADE;


--
-- Name: inventory_movements inventory_movements_to_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_to_location_id_fkey FOREIGN KEY (to_location_id) REFERENCES public.storage_locations(id) ON DELETE SET NULL;


--
-- Name: manual_reviews manual_reviews_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manual_reviews
    ADD CONSTRAINT manual_reviews_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE CASCADE;


--
-- Name: manual_reviews manual_reviews_ocr_result_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manual_reviews
    ADD CONSTRAINT manual_reviews_ocr_result_id_fkey FOREIGN KEY (ocr_result_id) REFERENCES public.ocr_results(id) ON DELETE SET NULL;


--
-- Name: manual_reviews manual_reviews_scan_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manual_reviews
    ADD CONSTRAINT manual_reviews_scan_session_id_fkey FOREIGN KEY (scan_session_id) REFERENCES public.scan_sessions(id) ON DELETE SET NULL;


--
-- Name: ml_predictions ml_predictions_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ml_predictions
    ADD CONSTRAINT ml_predictions_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE CASCADE;


--
-- Name: ocr_results ocr_results_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocr_results
    ADD CONSTRAINT ocr_results_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE SET NULL;


--
-- Name: ocr_results ocr_results_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocr_results
    ADD CONSTRAINT ocr_results_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: ocr_results ocr_results_product_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocr_results
    ADD CONSTRAINT ocr_results_product_image_id_fkey FOREIGN KEY (product_image_id) REFERENCES public.product_images(id) ON DELETE CASCADE;


--
-- Name: ocr_results ocr_results_scan_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ocr_results
    ADD CONSTRAINT ocr_results_scan_session_id_fkey FOREIGN KEY (scan_session_id) REFERENCES public.scan_sessions(id) ON DELETE SET NULL;


--
-- Name: product_allergens product_allergens_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_allergens
    ADD CONSTRAINT product_allergens_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: product_identifiers product_identifiers_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_identifiers
    ADD CONSTRAINT product_identifiers_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: product_images product_images_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: product_images product_images_scan_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_scan_session_id_fkey FOREIGN KEY (scan_session_id) REFERENCES public.scan_sessions(id) ON DELETE SET NULL;


--
-- Name: product_ingredients product_ingredients_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_ingredients
    ADD CONSTRAINT product_ingredients_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: product_lookup_logs product_lookup_logs_external_cache_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_lookup_logs
    ADD CONSTRAINT product_lookup_logs_external_cache_id_fkey FOREIGN KEY (external_cache_id) REFERENCES public.external_product_cache(id) ON DELETE SET NULL;


--
-- Name: product_lookup_logs product_lookup_logs_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_lookup_logs
    ADD CONSTRAINT product_lookup_logs_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: product_nutrition product_nutrition_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_nutrition
    ADD CONSTRAINT product_nutrition_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: product_question_logs product_question_logs_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_question_logs
    ADD CONSTRAINT product_question_logs_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE SET NULL;


--
-- Name: product_question_logs product_question_logs_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_question_logs
    ADD CONSTRAINT product_question_logs_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: product_storage_requirements product_storage_requirements_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product_storage_requirements
    ADD CONSTRAINT product_storage_requirements_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: scan_alerts scan_alerts_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scan_alerts
    ADD CONSTRAINT scan_alerts_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE SET NULL;


--
-- Name: scan_alerts scan_alerts_scan_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scan_alerts
    ADD CONSTRAINT scan_alerts_scan_session_id_fkey FOREIGN KEY (scan_session_id) REFERENCES public.scan_sessions(id) ON DELETE SET NULL;


--
-- Name: storage_contexts storage_contexts_inventory_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_contexts
    ADD CONSTRAINT storage_contexts_inventory_item_id_fkey FOREIGN KEY (inventory_item_id) REFERENCES public.inventory_items(id) ON DELETE CASCADE;


--
-- Name: storage_locations storage_locations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_locations
    ADD CONSTRAINT storage_locations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id) ON DELETE CASCADE;


--
-- Name: unknown_product_requests unknown_product_requests_resolved_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unknown_product_requests
    ADD CONSTRAINT unknown_product_requests_resolved_product_id_fkey FOREIGN KEY (resolved_product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict IgNhiHC509mTrl9pwgW36CugVifYXEfXdBO82iEQ0ubB5a5XmhznXXfipmZsumh

