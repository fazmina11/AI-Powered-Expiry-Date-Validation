-- AUTO-GENERATED: seed_all_tables.sql
-- Idempotent: safe to run multiple times

-- ═══════════════════════════════════════════
-- 1. PRODUCTS (20)
-- ═══════════════════════════════════════════
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('6bf38777-8241-442b-b443-8ed648f7ee8b','Amul Taaza Milk 500ml','Amul','AMUL-TAAZA-500ML','8901262010011','EAN13','Dairy','Pasteurised toned milk pouch.','refrigerated',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('d9d497a6-d070-43eb-a1a1-692a2977f4fa','Nestle Everyday Whitener 400g','Nestle','NESTLE-EW-400G','8901058850123','EAN13','Dairy','Dairy whitener powder for tea and coffee.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('0ca02492-67f1-43cb-979e-db3f38ba9dfc','Mother Dairy Classic Curd 400g','Mother Dairy','MD-CURD-400G','8901648004321','EAN13','Dairy','Fresh curd requiring cold storage.','refrigerated',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('1069962a-5fe1-4d05-8fce-cd0ed1d93ee7','Amul Salted Butter 100g','Amul','AMUL-BUTTER-100G','8901262030019','EAN13','Dairy','Salted butter block, 100g.','refrigerated',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('8c9a25a7-71ec-4d1c-b613-5e20d1bcf839','Britannia Good Day Cookies 200g','Britannia','BRIT-GD-200G','8901063160012','EAN13','Snacks','Cashew cookies packed for retail.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('12c9f1f0-5fc1-49c3-8f44-b05bc6e6eea7','Parle-G Glucose Biscuits 250g','Parle','PARLE-G-250G','8901719101015','EAN13','Snacks','Classic glucose biscuits.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('0ac0fa33-97f3-49d6-85a0-deb66cfe55f8','Lay''''s Classic Salted Chips 52g','Lay''s','LAYS-CLASSIC-52G','8901491100226','EAN13','Snacks','Classic salted potato chips.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('7207edd4-f970-4405-a801-bd7ad8c9f942','Kurkure Masala Munch 90g','Kurkure','KURKURE-MASALA-90G','8901491501221','EAN13','Snacks','Spicy crunchy corn snack.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('497607f1-92b2-43be-94c2-76823be5855a','Coca-Cola Original 750ml','Coca-Cola','COKE-750ML','8901764012342','EAN13','Beverages','Carbonated soft drink bottle.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('bb457039-0100-4e72-973a-f44d04d88826','Real Mixed Fruit Juice 1L','Real','REAL-MIXED-1L','8901207011123','EAN13','Beverages','Packaged mixed fruit juice carton.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('f5cbd3a0-6057-4c6a-8f22-e81546d59e3f','Tropicana Orange Delight 1L','Tropicana','TROP-ORANGE-1L','8901491200452','EAN13','Beverages','Packaged orange fruit beverage.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('e9efa9a4-d2e9-42a3-997a-73347fc47c60','Bisleri Mineral Water 1L','Bisleri','BISLERI-1L','8901207040017','EAN13','Beverages','Packaged drinking water 1-litre.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('b430351b-5c73-4dcf-8dd5-1dd23f0b0cef','Harvest Gold White Bread 400g','Harvest Gold','HG-WHITE-BREAD-400G','8901725180089','EAN13','Bakery','Packaged white bread loaf.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('3a8590ba-0daa-4477-967d-6b0cf8adcc3b','Britannia Brown Bread 400g','Britannia','BRIT-BROWN-BREAD-400G','8901063019870','EAN13','Bakery','Packaged brown bread loaf.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('786dfc39-b6ce-45dc-a8d9-e62396feae91','Maggi Masala Noodles 70g','Maggi','MAGGI-MASALA-70G','8901058840018','EAN13','Packaged Foods','Instant noodles with masala tastemaker.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('4706f11d-5ffe-4916-ba15-3328089a331c','Aashirvaad Wheat Atta 1kg','Aashirvaad','AASHIRVAAD-ATTA-1KG','8901725123456','EAN13','Packaged Foods','Whole wheat flour pack.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('d955e05a-113a-42cf-9fb1-e9fc2ad21194','Tata Salt Iodized 1kg','Tata','TATA-SALT-1KG','8904043901017','EAN13','Packaged Foods','Iodized salt packet.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('6791233c-112c-41fc-bd6f-ebf97e36a3ef','Fortune Sunflower Oil 1L','Fortune','FORTUNE-SFO-1L','8906007280012','EAN13','Packaged Foods','Refined sunflower cooking oil.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('835ab1c9-5fcc-4681-9a02-44dd4b4b48a4','Dove Cream Beauty Bar 100g','Dove','DOVE-BAR-100G','8901030865432','EAN13','Personal Care','Moisturizing bathing soap bar.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;
INSERT INTO products (id,name,brand,sku,barcode,barcode_type,category,description,default_storage_type,is_active,created_at,updated_at)
VALUES ('d9660bec-3569-4ca4-9ef7-645ca44fcefe','Dettol Antiseptic Liquid 250ml','Dettol','DETTOL-250ML','8901396389012','EAN13','Personal Care','Antiseptic disinfectant liquid.','ambient',TRUE,NOW(),NOW())
ON CONFLICT (barcode) DO NOTHING;

-- ═══════════════════════════════════════════
-- 2. BARCODE SCANS (25)
-- ═══════════════════════════════════════════
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('f2177ce0-8334-4156-ab59-88b6d37534ed','6bf38777-8241-442b-b443-8ed648f7ee8b','8901262010011','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('14f6ffd0-2784-4b39-a3b6-710d814eef26','d9d497a6-d070-43eb-a1a1-692a2977f4fa','8901058850123','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('8fdf2930-5836-47b8-b013-be7f9f96c11a','0ca02492-67f1-43cb-979e-db3f38ba9dfc','8901648004321','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('40fb3a06-b1d5-40a4-aefb-10e8a4f52d41','1069962a-5fe1-4d05-8fce-cd0ed1d93ee7','8901262030019','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('7b403c4e-5766-4220-923e-6999e1abc5a9','8c9a25a7-71ec-4d1c-b613-5e20d1bcf839','8901063160012','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('5bf33666-ea73-403b-87df-89ce291c968c','12c9f1f0-5fc1-49c3-8f44-b05bc6e6eea7','8901719101015','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('2f3ffe6f-205c-4732-ace3-281ff6c58082','0ac0fa33-97f3-49d6-85a0-deb66cfe55f8','8901491100226','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('a4bedee3-ce4c-4159-8294-5b3f3f1f1189','7207edd4-f970-4405-a801-bd7ad8c9f942','8901491501221','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('5ffbdf9f-d63c-4e95-a8f4-6dcbea7d39a7','497607f1-92b2-43be-94c2-76823be5855a','8901764012342','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('cbfefd07-c288-4067-8e2b-60e52885eece','bb457039-0100-4e72-973a-f44d04d88826','8901207011123','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('fcdb5ff3-093a-44bc-a33c-8ee1623bbd68','f5cbd3a0-6057-4c6a-8f22-e81546d59e3f','8901491200452','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('1b2d8850-f1fe-4b25-9c99-c787d7038a87','e9efa9a4-d2e9-42a3-997a-73347fc47c60','8901207040017','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('ccc49a39-5422-4751-9766-d5c408bbbef4','b430351b-5c73-4dcf-8dd5-1dd23f0b0cef','8901725180089','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('fe4f0535-2e73-44cc-8cea-3e9632e4cff8','3a8590ba-0daa-4477-967d-6b0cf8adcc3b','8901063019870','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('01f766eb-a3fe-4114-b49c-42ae5d5aa163','786dfc39-b6ce-45dc-a8d9-e62396feae91','8901058840018','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('bc50fe05-4b8e-47b5-9a4e-dfcbd38492f8','4706f11d-5ffe-4916-ba15-3328089a331c','8901725123456','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('3c9c858e-d12d-4485-90d8-79dd198bc9d5','d955e05a-113a-42cf-9fb1-e9fc2ad21194','8904043901017','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('48f23555-d1eb-4c2a-9b26-cb5d064e6b6d','6791233c-112c-41fc-bd6f-ebf97e36a3ef','8906007280012','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('5af1ff80-c3fe-4a20-bcec-66f1dea56118','835ab1c9-5fcc-4681-9a02-44dd4b4b48a4','8901030865432','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,scanned_at,created_at)
VALUES ('07c85e3b-e90d-453e-a748-4339a1681dc5','d9660bec-3569-4ca4-9ef7-645ca44fcefe','8901396389012','EAN13','handheld_scanner','resolved',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at)
VALUES ('a1f1405d-a184-41a5-acd2-2e0f85c3cf6d',NULL,'9990000000001','EAN13','mobile_app','unresolved','Barcode not found in catalogue',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at)
VALUES ('75c17280-5c9f-4e87-80b6-17062bca3341',NULL,'9990000000002','EAN13','mobile_app','unresolved','Barcode not found in catalogue',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at)
VALUES ('f4d9882e-c1ec-449f-8baf-d476c840d652',NULL,'9990000000003','EAN13','mobile_app','unresolved','Barcode not found in catalogue',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at)
VALUES ('3a0cd11e-59ff-438b-b829-82e0bbae950c',NULL,'9990000000004','EAN13','mobile_app','unresolved','Barcode not found in catalogue',NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO barcode_scans (id,product_id,raw_barcode,barcode_type,scan_source,scan_status,notes,scanned_at,created_at)
VALUES ('0d96ec94-6a6a-4d94-8353-ab6845965573',NULL,'9990000000005','EAN13','mobile_app','unresolved','Barcode not found in catalogue',NOW(),NOW())
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════
-- 3. INVENTORY ITEMS (25)
-- ═══════════════════════════════════════════
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('b1d79f1e-b549-49a6-b88e-474a9e582e62','6bf38777-8241-442b-b443-8ed648f7ee8b','f2177ce0-8334-4156-ab59-88b6d37534ed','BATCH-2026001','2026-03-28','2026-06-19','PENDING_OCR',18,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','d9d497a6-d070-43eb-a1a1-692a2977f4fa','14f6ffd0-2784-4b39-a3b6-710d814eef26','BATCH-2026002','2026-02-08','2026-07-09','OCR_COMPLETED',26,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('72ac683e-2e41-435a-adc2-272c07144541','0ca02492-67f1-43cb-979e-db3f38ba9dfc','8fdf2930-5836-47b8-b013-be7f9f96c11a','BATCH-2026003','2026-01-27','2026-08-08','PENDING_ML_REVIEW',30,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('04b2ecb8-4baf-4cbf-a9fa-3c354306b12e','1069962a-5fe1-4d05-8fce-cd0ed1d93ee7','40fb3a06-b1d5-40a4-aefb-10e8a4f52d41','BATCH-2026004','2026-01-14','2026-10-22','ML_COMPLETED',28,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('84da942f-3099-4fca-9dd8-d419ecb47e1f','8c9a25a7-71ec-4d1c-b613-5e20d1bcf839','7b403c4e-5766-4220-923e-6999e1abc5a9','BATCH-2026005','2026-04-18',NULL,'MANUAL_REVIEW',22,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('4ff66496-1a5f-48a1-8ed8-cef0aba666fa','12c9f1f0-5fc1-49c3-8f44-b05bc6e6eea7','5bf33666-ea73-403b-87df-89ce291c968c','BATCH-2026006','2026-01-08','2026-06-19','PENDING_OCR',22,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('e5c2a776-8a2c-4c08-b30f-bef5415c9d51','0ac0fa33-97f3-49d6-85a0-deb66cfe55f8','2f3ffe6f-205c-4732-ace3-281ff6c58082','BATCH-2026007','2026-01-12','2026-07-09','OCR_COMPLETED',47,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('87fa595e-3532-48d6-9bd0-34a27257cf5f','7207edd4-f970-4405-a801-bd7ad8c9f942','a4bedee3-ce4c-4159-8294-5b3f3f1f1189','BATCH-2026008','2026-04-20','2026-08-08','PENDING_ML_REVIEW',26,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('001f1a1d-daa0-4414-bb6a-312768bd7ef3','497607f1-92b2-43be-94c2-76823be5855a','5ffbdf9f-d63c-4e95-a8f4-6dcbea7d39a7','BATCH-2026009','2025-12-31','2026-10-22','ML_COMPLETED',20,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('7b815279-b5e0-46ac-a0fd-d30d853e9573','bb457039-0100-4e72-973a-f44d04d88826','cbfefd07-c288-4067-8e2b-60e52885eece','BATCH-2026010','2026-01-07',NULL,'MANUAL_REVIEW',47,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('785a3771-47c9-47ad-8832-5dcef7d65eac','f5cbd3a0-6057-4c6a-8f22-e81546d59e3f','fcdb5ff3-093a-44bc-a33c-8ee1623bbd68','BATCH-2026011','2026-02-06','2026-06-19','PENDING_OCR',48,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('f910442a-43ba-4734-8162-3022363bee47','e9efa9a4-d2e9-42a3-997a-73347fc47c60','1b2d8850-f1fe-4b25-9c99-c787d7038a87','BATCH-2026012','2026-03-11','2026-07-09','OCR_COMPLETED',40,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('5b8055e4-1113-4660-bfb7-b794dfa35e4c','b430351b-5c73-4dcf-8dd5-1dd23f0b0cef','ccc49a39-5422-4751-9766-d5c408bbbef4','BATCH-2026013','2026-04-01','2026-08-08','PENDING_ML_REVIEW',39,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('1091fc23-0cbd-4522-b45b-999481193061','3a8590ba-0daa-4477-967d-6b0cf8adcc3b','fe4f0535-2e73-44cc-8cea-3e9632e4cff8','BATCH-2026014','2026-04-12','2026-10-22','ML_COMPLETED',46,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('2f5d6bf1-fdfc-44d0-b05b-2b270f8886d2','786dfc39-b6ce-45dc-a8d9-e62396feae91','01f766eb-a3fe-4114-b49c-42ae5d5aa163','BATCH-2026015','2026-03-22',NULL,'MANUAL_REVIEW',47,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('cf0e4b36-01db-4118-a3a4-5ba93c8ad80d','4706f11d-5ffe-4916-ba15-3328089a331c','bc50fe05-4b8e-47b5-9a4e-dfcbd38492f8','BATCH-2026016','2025-12-29','2026-06-19','PENDING_OCR',14,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('90836731-ca74-4cc0-9ba0-586cbaa6e231','d955e05a-113a-42cf-9fb1-e9fc2ad21194','3c9c858e-d12d-4485-90d8-79dd198bc9d5','BATCH-2026017','2026-03-07','2026-07-09','OCR_COMPLETED',7,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('91465d53-29c8-42fe-8e9f-b3c09439d891','6791233c-112c-41fc-bd6f-ebf97e36a3ef','48f23555-d1eb-4c2a-9b26-cb5d064e6b6d','BATCH-2026018','2026-04-16','2026-08-08','PENDING_ML_REVIEW',3,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('e9eaa4b2-56cf-4fa0-8001-30bd56a910ba','835ab1c9-5fcc-4681-9a02-44dd4b4b48a4','5af1ff80-c3fe-4a20-bcec-66f1dea56118','BATCH-2026019','2026-03-12','2026-10-22','ML_COMPLETED',12,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('f643b03b-7436-4300-9868-72f0148667f3','d9660bec-3569-4ca4-9ef7-645ca44fcefe','07c85e3b-e90d-453e-a748-4339a1681dc5','BATCH-2026020','2026-04-14',NULL,'MANUAL_REVIEW',25,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('422f517d-ec7f-4857-aed5-a0d0d73f15e7','6bf38777-8241-442b-b443-8ed648f7ee8b','f2177ce0-8334-4156-ab59-88b6d37534ed','BATCH-2026021','2026-05-24','2026-06-19','PENDING_OCR',8,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('0e64e0e2-9d86-49b2-8075-9386e80cf21c','d9d497a6-d070-43eb-a1a1-692a2977f4fa','14f6ffd0-2784-4b39-a3b6-710d814eef26','BATCH-2026022','2026-01-29','2026-07-09','OCR_COMPLETED',36,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('f95afaa0-c93b-45ff-b280-6722cd1c724d','0ca02492-67f1-43cb-979e-db3f38ba9dfc','8fdf2930-5836-47b8-b013-be7f9f96c11a','BATCH-2026023','2026-01-23','2026-08-08','PENDING_ML_REVIEW',23,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('4b7c5b68-4bee-44fc-9a81-ba30dd8e876d','1069962a-5fe1-4d05-8fce-cd0ed1d93ee7','40fb3a06-b1d5-40a4-aefb-10e8a4f52d41','BATCH-2026024','2026-03-23','2026-10-22','ML_COMPLETED',19,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO inventory_items (id,product_id,barcode_scan_id,batch_number,manufacturing_date,expiry_date,pipeline_status,quantity,unit,intake_at,created_at,updated_at)
VALUES ('64488bf3-4d52-41e7-9bd4-c6de6231caff','8c9a25a7-71ec-4d1c-b613-5e20d1bcf839','7b403c4e-5766-4220-923e-6999e1abc5a9','BATCH-2026025','2026-04-14',NULL,'MANUAL_REVIEW',39,'units',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════
-- 4. PRODUCT IMAGES (30)
-- ═══════════════════════════════════════════
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('1d7a938a-23c9-4762-bc7a-422fe70ea538','6bf38777-8241-442b-b443-8ed648f7ee8b','/uploads/8901262010011_0.jpg','https://cdn.expiry.io/8901262010011_0.jpg',328762,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('e1e2dcc7-7e43-4ac2-a6fa-97e83e912dfa','d9d497a6-d070-43eb-a1a1-692a2977f4fa','/uploads/8901058850123_1.jpg','https://cdn.expiry.io/8901058850123_1.jpg',138588,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('f5c5516b-c7fb-4e51-bab3-b6321337cfa3','0ca02492-67f1-43cb-979e-db3f38ba9dfc','/uploads/8901648004321_2.jpg','https://cdn.expiry.io/8901648004321_2.jpg',207103,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('d72be797-dc25-4cce-97e6-66f21a3e75e5','1069962a-5fe1-4d05-8fce-cd0ed1d93ee7','/uploads/8901262030019_3.jpg','https://cdn.expiry.io/8901262030019_3.jpg',59027,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('2d74ecd4-cab0-433b-af91-7f1e41b90da1','8c9a25a7-71ec-4d1c-b613-5e20d1bcf839','/uploads/8901063160012_4.jpg','https://cdn.expiry.io/8901063160012_4.jpg',438531,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('9ae59bdb-26ce-4f9a-8715-9665eeafd55d','12c9f1f0-5fc1-49c3-8f44-b05bc6e6eea7','/uploads/8901719101015_5.jpg','https://cdn.expiry.io/8901719101015_5.jpg',236804,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('471e5967-9088-43af-bfe2-807096588f68','0ac0fa33-97f3-49d6-85a0-deb66cfe55f8','/uploads/8901491100226_6.jpg','https://cdn.expiry.io/8901491100226_6.jpg',208530,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('75fb6e6c-f93d-47ea-a855-52220cc25d90','7207edd4-f970-4405-a801-bd7ad8c9f942','/uploads/8901491501221_7.jpg','https://cdn.expiry.io/8901491501221_7.jpg',398608,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('6e20853b-250b-497f-8773-4c72c99551b0','497607f1-92b2-43be-94c2-76823be5855a','/uploads/8901764012342_8.jpg','https://cdn.expiry.io/8901764012342_8.jpg',183604,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('52576b9d-f0b8-476b-9717-7729ebb3e603','bb457039-0100-4e72-973a-f44d04d88826','/uploads/8901207011123_9.jpg','https://cdn.expiry.io/8901207011123_9.jpg',309730,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('02aa98b5-6d3a-4412-89d5-0af64e29459b','f5cbd3a0-6057-4c6a-8f22-e81546d59e3f','/uploads/8901491200452_10.jpg','https://cdn.expiry.io/8901491200452_10.jpg',165020,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('848e4cda-fd67-4e30-a6bd-c842561470cf','e9efa9a4-d2e9-42a3-997a-73347fc47c60','/uploads/8901207040017_11.jpg','https://cdn.expiry.io/8901207040017_11.jpg',267684,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('ec843c28-fb18-42f0-9a52-bd893686b30c','b430351b-5c73-4dcf-8dd5-1dd23f0b0cef','/uploads/8901725180089_12.jpg','https://cdn.expiry.io/8901725180089_12.jpg',193067,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('ce97e598-d347-4a36-886b-adaa7f664a28','3a8590ba-0daa-4477-967d-6b0cf8adcc3b','/uploads/8901063019870_13.jpg','https://cdn.expiry.io/8901063019870_13.jpg',475606,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('926adc8f-b17e-40bd-94a9-d463491d6a6b','786dfc39-b6ce-45dc-a8d9-e62396feae91','/uploads/8901058840018_14.jpg','https://cdn.expiry.io/8901058840018_14.jpg',440103,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('9998ec8d-33da-4959-af3e-461f45a4613a','4706f11d-5ffe-4916-ba15-3328089a331c','/uploads/8901725123456_15.jpg','https://cdn.expiry.io/8901725123456_15.jpg',349639,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('929baf10-1ef0-4661-91bb-2952886b10c4','d955e05a-113a-42cf-9fb1-e9fc2ad21194','/uploads/8904043901017_16.jpg','https://cdn.expiry.io/8904043901017_16.jpg',157911,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('2cb877ef-01a5-42a8-8437-83dd9e945d13','6791233c-112c-41fc-bd6f-ebf97e36a3ef','/uploads/8906007280012_17.jpg','https://cdn.expiry.io/8906007280012_17.jpg',87705,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('79102a33-e969-4702-bf24-7571563b9268','835ab1c9-5fcc-4681-9a02-44dd4b4b48a4','/uploads/8901030865432_18.jpg','https://cdn.expiry.io/8901030865432_18.jpg',273683,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('87f7dc52-24d4-437d-b014-3272110dbf59','d9660bec-3569-4ca4-9ef7-645ca44fcefe','/uploads/8901396389012_19.jpg','https://cdn.expiry.io/8901396389012_19.jpg',338556,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('38fd88cd-d743-4824-8978-430602a05385','6bf38777-8241-442b-b443-8ed648f7ee8b','/uploads/8901262010011_20.jpg','https://cdn.expiry.io/8901262010011_20.jpg',242622,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('4cfcbd0a-ff53-43e7-9841-18c263f27852','d9d497a6-d070-43eb-a1a1-692a2977f4fa','/uploads/8901058850123_21.jpg','https://cdn.expiry.io/8901058850123_21.jpg',371654,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('84c4995c-82dd-4d86-8bad-eb7161baafe7','0ca02492-67f1-43cb-979e-db3f38ba9dfc','/uploads/8901648004321_22.jpg','https://cdn.expiry.io/8901648004321_22.jpg',133990,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('435bf16a-6e9a-47a8-b042-d33263e6e4c6','1069962a-5fe1-4d05-8fce-cd0ed1d93ee7','/uploads/8901262030019_23.jpg','https://cdn.expiry.io/8901262030019_23.jpg',138858,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('089dace1-de1b-4f29-a8fe-7ba65377e834','8c9a25a7-71ec-4d1c-b613-5e20d1bcf839','/uploads/8901063160012_24.jpg','https://cdn.expiry.io/8901063160012_24.jpg',169890,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('54bc505b-25fa-4a58-9dc4-a2da76c4f75d','12c9f1f0-5fc1-49c3-8f44-b05bc6e6eea7','/uploads/8901719101015_25.jpg','https://cdn.expiry.io/8901719101015_25.jpg',206588,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('b341bf88-2bb7-44e4-828a-e1a4da809f0e','0ac0fa33-97f3-49d6-85a0-deb66cfe55f8','/uploads/8901491100226_26.jpg','https://cdn.expiry.io/8901491100226_26.jpg',391498,'image/jpeg','barcode_close_up','ocr_completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('71fa2e59-207b-4551-80c6-0dfbe3836504','7207edd4-f970-4405-a801-bd7ad8c9f942','/uploads/8901491501221_27.jpg','https://cdn.expiry.io/8901491501221_27.jpg',295933,'image/jpeg','product_photo','failed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('60fda319-1b57-4912-b6af-a19f9678ae82','497607f1-92b2-43be-94c2-76823be5855a','/uploads/8901764012342_28.jpg','https://cdn.expiry.io/8901764012342_28.jpg',362001,'image/jpeg','front_label','uploaded',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO product_images (id,product_id,file_path,file_url,file_size_bytes,mime_type,image_type,processing_status,uploaded_at,created_at,updated_at)
VALUES ('31d57334-89a6-43c8-9756-6986b18ebb35','bb457039-0100-4e72-973a-f44d04d88826','/uploads/8901207011123_29.jpg','https://cdn.expiry.io/8901207011123_29.jpg',315002,'image/jpeg','back_label','ocr_pending',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════
-- 5. OCR RESULTS (28)
-- ═══════════════════════════════════════════
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('20dd5182-33d8-4e38-a64d-7d8178bb0286','1d7a938a-23c9-4762-bc7a-422fe70ea538','b1d79f1e-b549-49a6-b88e-474a9e582e62','MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A','tesseract-5.3','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',NULL,'pending',NULL,NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('2ea8b6f2-e707-4fea-9d42-e6874f4db4e6','e1e2dcc7-7e43-4ac2-a6fa-97e83e912dfa','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','Manufacturing Date: March 2026  Best Before: Sep 2026','google-vision-v1','1.0','[{"label":"Best Before","value":"Sep 2026"}]',0.8371,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('3c3da521-1d6b-45d4-8431-7391aee56d77','f5c5516b-c7fb-4e51-bab3-b6321337cfa3','72ac683e-2e41-435a-adc2-272c07144541','Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421','aws-textract-v2','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',0.839,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('7e4675bb-2f2e-43e7-a2ac-1f013f37b9d1','d72be797-dc25-4cce-97e6-66f21a3e75e5','04b2ecb8-4baf-4cbf-a9fa-3c354306b12e','PROD DATE: 20/04/26  EXP DATE: 20/10/26  MRP Rs.45','tesseract-5.3','1.0','[]',0.708,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('a4f13fa0-ff29-4008-902b-346241ca1d62','2d74ecd4-cab0-433b-af91-7f1e41b90da1','84da942f-3099-4fca-9dd8-d419ecb47e1f','Label torn -- partial: ...exp 06/2026...','google-vision-v1','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',NULL,'failed','OCR engine timeout',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('7152701f-e4c3-4253-8f8a-13ba0e03f281','9ae59bdb-26ce-4f9a-8715-9665eeafd55d','4ff66496-1a5f-48a1-8ed8-cef0aba666fa','MFG 2026-01-10  EXP 2026-07-10  LOT 9921B','aws-textract-v2','1.0','[{"label":"Best Before","value":"Sep 2026"}]',NULL,'pending',NULL,NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('27075ff7-3615-4b01-bec1-71af791ad47e','471e5967-9088-43af-bfe2-807096588f68','e5c2a776-8a2c-4c08-b30f-bef5415c9d51','Manufactured: Feb 2026  Expiry: Aug 2026  Batch: F221','tesseract-5.3','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',0.5726,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('e9c54cc7-31b2-482c-8eee-4eaf54178d81','75fb6e6c-f93d-47ea-a855-52220cc25d90','87fa595e-3532-48d6-9bd0-34a27257cf5f','MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A','google-vision-v1','1.0','[]',0.8386,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('2a94df59-2d98-4b37-abf4-bea2364d6092','6e20853b-250b-497f-8773-4c72c99551b0','001f1a1d-daa0-4414-bb6a-312768bd7ef3','Manufacturing Date: March 2026  Best Before: Sep 2026','aws-textract-v2','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',0.7578,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('8fc02c7f-8537-4f44-a53c-f44e43753548','52576b9d-f0b8-476b-9717-7729ebb3e603','7b815279-b5e0-46ac-a0fd-d30d853e9573','Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421','tesseract-5.3','1.0','[{"label":"Best Before","value":"Sep 2026"}]',NULL,'failed','OCR engine timeout',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('00956f7b-fafd-4062-9fb0-12a55fa29af6','02aa98b5-6d3a-4412-89d5-0af64e29459b','785a3771-47c9-47ad-8832-5dcef7d65eac','PROD DATE: 20/04/26  EXP DATE: 20/10/26  MRP Rs.45','google-vision-v1','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',NULL,'pending',NULL,NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('f4096c83-be1f-47a5-a437-9b81ef00b2b2','848e4cda-fd67-4e30-a6bd-c842561470cf','f910442a-43ba-4734-8162-3022363bee47','Label torn -- partial: ...exp 06/2026...','aws-textract-v2','1.0','[]',0.9687,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('7d4b237c-99bc-43e2-bca4-bfb8eeadcc74','ec843c28-fb18-42f0-9a52-bd893686b30c','5b8055e4-1113-4660-bfb7-b794dfa35e4c','MFG 2026-01-10  EXP 2026-07-10  LOT 9921B','tesseract-5.3','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',0.8846,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('6d019115-27b9-458b-9797-4b0724fd7cf7','ce97e598-d347-4a36-886b-adaa7f664a28','1091fc23-0cbd-4522-b45b-999481193061','Manufactured: Feb 2026  Expiry: Aug 2026  Batch: F221','google-vision-v1','1.0','[{"label":"Best Before","value":"Sep 2026"}]',0.5935,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('ef011f47-543b-48d8-a438-a0c34fa0254a','926adc8f-b17e-40bd-94a9-d463491d6a6b','2f5d6bf1-fdfc-44d0-b05b-2b270f8886d2','MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A','aws-textract-v2','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',NULL,'failed','OCR engine timeout',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('912c2db4-6aae-4395-9b9c-0205165d6360','9998ec8d-33da-4959-af3e-461f45a4613a','cf0e4b36-01db-4118-a3a4-5ba93c8ad80d','Manufacturing Date: March 2026  Best Before: Sep 2026','tesseract-5.3','1.0','[]',NULL,'pending',NULL,NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('f399805b-a484-461e-b4fa-91b7ed04e491','929baf10-1ef0-4661-91bb-2952886b10c4','90836731-ca74-4cc0-9ba0-586cbaa6e231','Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421','google-vision-v1','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',0.8251,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('f3cbff9b-23d2-424b-bc2f-e3209724f287','2cb877ef-01a5-42a8-8437-83dd9e945d13','91465d53-29c8-42fe-8e9f-b3c09439d891','PROD DATE: 20/04/26  EXP DATE: 20/10/26  MRP Rs.45','aws-textract-v2','1.0','[{"label":"Best Before","value":"Sep 2026"}]',0.9492,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('80426ab5-c98b-4bab-8a07-4c80d07795fc','79102a33-e969-4702-bf24-7571563b9268','e9eaa4b2-56cf-4fa0-8001-30bd56a910ba','Label torn -- partial: ...exp 06/2026...','tesseract-5.3','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',0.6497,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('337d2e53-e051-4e9f-876c-2af89458b869','87f7dc52-24d4-437d-b014-3272110dbf59','f643b03b-7436-4300-9868-72f0148667f3','MFG 2026-01-10  EXP 2026-07-10  LOT 9921B','google-vision-v1','1.0','[]',NULL,'failed','OCR engine timeout',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('614e17d5-84a6-4b12-8170-1a16f55fd4b7','38fd88cd-d743-4824-8978-430602a05385','422f517d-ec7f-4857-aed5-a0d0d73f15e7','Manufactured: Feb 2026  Expiry: Aug 2026  Batch: F221','aws-textract-v2','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',NULL,'pending',NULL,NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('d49592cc-c187-4ddb-8b23-556b8585342d','4cfcbd0a-ff53-43e7-9841-18c263f27852','0e64e0e2-9d86-49b2-8075-9386e80cf21c','MFG: 01/03/2026  EXP: 01/09/2026  BATCH: LOT-221A','tesseract-5.3','1.0','[{"label":"Best Before","value":"Sep 2026"}]',0.8206,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('93ba3e86-ad9b-4167-8c7b-0d5c30062f29','84c4995c-82dd-4d86-8bad-eb7161baafe7','f95afaa0-c93b-45ff-b280-6722cd1c724d','Manufacturing Date: March 2026  Best Before: Sep 2026','google-vision-v1','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',0.5771,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('f6dbee2b-b68f-4b7c-aa96-e7812071251a','435bf16a-6e9a-47a8-b042-d33263e6e4c6','4b7c5b68-4bee-44fc-9a81-ba30dd8e876d','Mfd: 15.02.2026  Use by: 15.08.2026  Batch No: B4421','aws-textract-v2','1.0','[]',0.5619,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('51804342-511b-4ac1-a277-c83066fb9a8f','089dace1-de1b-4f29-a8fe-7ba65377e834','64488bf3-4d52-41e7-9bd4-c6de6231caff','PROD DATE: 20/04/26  EXP DATE: 20/10/26  MRP Rs.45','tesseract-5.3','1.0','[{"label":"MFG","value":"01/03/2026"},{"label":"EXP","value":"01/09/2026"}]',NULL,'failed','OCR engine timeout',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('fb1810c0-2866-41d9-81bd-1aab50f3d778','54bc505b-25fa-4a58-9dc4-a2da76c4f75d','b1d79f1e-b549-49a6-b88e-474a9e582e62','Label torn -- partial: ...exp 06/2026...','google-vision-v1','1.0','[{"label":"Best Before","value":"Sep 2026"}]',NULL,'pending',NULL,NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('b4e5c46e-333a-4c2d-95c0-4168bb68d912','b341bf88-2bb7-44e4-828a-e1a4da809f0e','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','MFG 2026-01-10  EXP 2026-07-10  LOT 9921B','aws-textract-v2','1.0','[{"label":"Mfd","value":"15.02.2026"},{"label":"Use by","value":"15.08.2026"}]',0.945,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ocr_results (id,product_image_id,inventory_item_id,raw_text,ocr_engine,ocr_engine_version,extracted_text_blocks,overall_confidence,ocr_status,failure_reason,processed_at,created_at,updated_at)
VALUES ('78d9bc5b-8d82-4517-9db0-dcb52540d0c7','71fa2e59-207b-4551-80c6-0dfbe3836504','72ac683e-2e41-435a-adc2-272c07144541','Manufactured: Feb 2026  Expiry: Aug 2026  Batch: F221','tesseract-5.3','1.0','[]',0.732,'completed',NULL,NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════
-- 6. STORAGE CONTEXTS (25)
-- ═══════════════════════════════════════════
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('69a5ef80-e29b-472d-8323-1ce555e42f2d','b1d79f1e-b549-49a6-b88e-474a9e582e62','WH-DELHI-01','Zone-A','A1','S1','BIN-100','refrigerated',3.59,49.57,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('589c5dbd-00ee-4107-89b9-75b7fdb99b11','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','WH-MUMBAI-02','Zone-B','A2','S2','BIN-101','ambient',18.1,51.19,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('366727ad-4bac-4078-ab5c-0cbab2eec0bd','72ac683e-2e41-435a-adc2-272c07144541','WH-BANGALORE-03','Cold-Room-1','A3','S3','BIN-102','refrigerated',7.47,52.68,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('2ba76401-96ae-4555-8225-515df2e1a320','04b2ecb8-4baf-4cbf-a9fa-3c354306b12e','WH-DELHI-01','Cold-Room-2','A4','S4','BIN-103','refrigerated',6.59,52.56,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('06eba890-3f69-4fe0-81b4-4ce807017466','84da942f-3099-4fca-9dd8-d419ecb47e1f','WH-MUMBAI-02','Frozen-Bay','A5','S1','BIN-104','ambient',25.85,52.11,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('37f3f7e8-da52-48f8-9ce7-3ccb18ab27cd','4ff66496-1a5f-48a1-8ed8-cef0aba666fa','WH-BANGALORE-03','Ambient-Rack-3','A1','S2','BIN-105','ambient',22.04,40.85,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('265b1dd9-e564-4305-96a1-fab4bfe3b130','e5c2a776-8a2c-4c08-b30f-bef5415c9d51','WH-DELHI-01','Zone-A','A2','S3','BIN-106','ambient',27.51,40.33,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('c9c501d7-70d6-463a-b6e5-6478fb0baacf','87fa595e-3532-48d6-9bd0-34a27257cf5f','WH-MUMBAI-02','Zone-B','A3','S4','BIN-107','ambient',25.59,62.05,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('ddf3d5db-320f-484e-9475-f53ff21b3200','001f1a1d-daa0-4414-bb6a-312768bd7ef3','WH-BANGALORE-03','Cold-Room-1','A4','S1','BIN-108','ambient',27.17,53.97,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('29c2025f-ae97-4e23-846f-98b87843d63f','7b815279-b5e0-46ac-a0fd-d30d853e9573','WH-DELHI-01','Cold-Room-2','A5','S2','BIN-109','ambient',27.11,68.59,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('d26e1cbd-f1e8-48de-970c-bee402719b21','785a3771-47c9-47ad-8832-5dcef7d65eac','WH-MUMBAI-02','Frozen-Bay','A1','S3','BIN-110','ambient',21.82,50.43,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('5fe9b718-997b-41b4-8f7a-e623dadeebe1','f910442a-43ba-4734-8162-3022363bee47','WH-BANGALORE-03','Ambient-Rack-3','A2','S4','BIN-111','ambient',25.44,42.45,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('9d4cd9f7-f076-4e20-b4cf-538e54b04861','5b8055e4-1113-4660-bfb7-b794dfa35e4c','WH-DELHI-01','Zone-A','A3','S1','BIN-112','ambient',21.73,40.6,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('a3f320f1-da9e-409a-a611-0f6cbda568e0','1091fc23-0cbd-4522-b45b-999481193061','WH-MUMBAI-02','Zone-B','A4','S2','BIN-113','ambient',25.15,67.42,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('584a3e49-e1f4-44d8-b60d-d9811281ea5f','2f5d6bf1-fdfc-44d0-b05b-2b270f8886d2','WH-BANGALORE-03','Cold-Room-1','A5','S3','BIN-114','ambient',23.4,69.77,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('46dea939-40c8-46a0-8d32-165e250770f6','cf0e4b36-01db-4118-a3a4-5ba93c8ad80d','WH-DELHI-01','Cold-Room-2','A1','S4','BIN-115','ambient',26.16,46.58,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('4b5ee6c4-c5ff-4814-9871-1694267770b4','90836731-ca74-4cc0-9ba0-586cbaa6e231','WH-MUMBAI-02','Frozen-Bay','A2','S1','BIN-116','ambient',18.96,65.68,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('d49cb916-2cb0-4c11-b65a-2d750e99a7dd','91465d53-29c8-42fe-8e9f-b3c09439d891','WH-BANGALORE-03','Ambient-Rack-3','A3','S2','BIN-117','ambient',23.81,46.01,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('271fba8f-0210-4982-b9e0-5955aac70237','e9eaa4b2-56cf-4fa0-8001-30bd56a910ba','WH-DELHI-01','Zone-A','A4','S3','BIN-118','ambient',21.18,40.16,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('e332a502-dccc-430e-b0cc-8c3072822f96','f643b03b-7436-4300-9868-72f0148667f3','WH-MUMBAI-02','Zone-B','A5','S4','BIN-119','ambient',22.13,61.82,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('f0939b0a-1d13-4101-ba6d-be33a983f17f','422f517d-ec7f-4857-aed5-a0d0d73f15e7','WH-BANGALORE-03','Cold-Room-1','A1','S1','BIN-120','refrigerated',7.43,59.71,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('3ecbdbea-0cc6-4a86-921d-cf7d6230dd09','0e64e0e2-9d86-49b2-8075-9386e80cf21c','WH-DELHI-01','Cold-Room-2','A2','S2','BIN-121','ambient',27.86,57.2,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('361004cb-0f3f-496c-892c-1de23e2110b8','f95afaa0-c93b-45ff-b280-6722cd1c724d','WH-MUMBAI-02','Frozen-Bay','A3','S3','BIN-122','refrigerated',5.63,68.99,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('40620fb7-7e80-4743-b0e6-d7f5056f7e1c','4b7c5b68-4bee-44fc-9a81-ba30dd8e876d','WH-BANGALORE-03','Ambient-Rack-3','A4','S4','BIN-123','refrigerated',2.11,45.0,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;
INSERT INTO storage_contexts (id,inventory_item_id,warehouse_id,zone,aisle,shelf,bin_location,storage_type,temperature_celsius,humidity_percent,notes,recorded_at,created_at,updated_at)
VALUES ('4c8ead50-d019-4cb2-ab3d-1a64bc94907e','64488bf3-4d52-41e7-9bd4-c6de6231caff','WH-DELHI-01','Zone-A','A5','S1','BIN-124','ambient',23.18,56.29,'Auto-recorded on intake.',NOW(),NOW(),NOW())
ON CONFLICT (inventory_item_id) DO NOTHING;

-- ═══════════════════════════════════════════
-- 7. ML PREDICTIONS (20)
-- ═══════════════════════════════════════════
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('5a7ecd4c-b8b8-462f-b5c7-bd26a01f2b1a','b1d79f1e-b549-49a6-b88e-474a9e582e62','expiry-shelf-v2.1','2.1.0','2026-06-19',-5,'ACCEPTED',0.824,'Product has sufficient shelf life remaining.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('9f6a0965-e26a-4588-aeb7-39d35e7d4e56','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','expiry-shelf-v2.1','2.1.0','2026-07-09',15,'PRIORITY_SALE',0.9608,'Nearing expiry -- prioritize for immediate sale.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('2d60549c-bb38-483c-a740-b5838dc71131','72ac683e-2e41-435a-adc2-272c07144541','expiry-shelf-v2.1','2.1.0','2026-08-08',45,'REJECTED',0.9539,'Product is already expired. Do not sell.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('2f3efdde-62fd-478e-8aca-55e93ba8f344','04b2ecb8-4baf-4cbf-a9fa-3c354306b12e','expiry-shelf-v2.1','2.1.0','2026-10-22',120,'REJECTED',0.9303,'Remaining shelf life below minimum threshold.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('c35338bd-44aa-4396-a690-f91375263ef4','84da942f-3099-4fca-9dd8-d419ecb47e1f','expiry-shelf-v2.1','2.1.0',NULL,NULL,'REQUIRES_REVIEW',0.7678,'Confidence too low -- requires human review.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('bb90654a-5a88-4950-b0cd-bfb85d90b9ad','4ff66496-1a5f-48a1-8ed8-cef0aba666fa','expiry-shelf-v2.1','2.1.0','2026-06-19',-5,'ACCEPTED',0.8252,'Product has sufficient shelf life remaining.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('eb05d808-1934-416c-9113-1f25fc6f4bbe','e5c2a776-8a2c-4c08-b30f-bef5415c9d51','expiry-shelf-v2.1','2.1.0','2026-07-09',15,'PRIORITY_SALE',0.8382,'Nearing expiry -- prioritize for immediate sale.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('bd165fa7-6be7-44f7-88f1-0f53211d5be0','87fa595e-3532-48d6-9bd0-34a27257cf5f','expiry-shelf-v2.1','2.1.0','2026-08-08',45,'REJECTED',0.7873,'Product is already expired. Do not sell.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('5ea533ec-9900-4321-aadb-80e293b48359','001f1a1d-daa0-4414-bb6a-312768bd7ef3','expiry-shelf-v2.1','2.1.0','2026-10-22',120,'REJECTED',0.8486,'Remaining shelf life below minimum threshold.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('b01f29d2-a675-48e8-bea4-c9efe729f7a6','7b815279-b5e0-46ac-a0fd-d30d853e9573','expiry-shelf-v2.1','2.1.0',NULL,NULL,'REQUIRES_REVIEW',0.7447,'Confidence too low -- requires human review.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('9bd2afbd-705a-4284-8d64-b619f91823a7','785a3771-47c9-47ad-8832-5dcef7d65eac','expiry-shelf-v2.1','2.1.0','2026-06-19',-5,'ACCEPTED',0.8212,'Product has sufficient shelf life remaining.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('0edf9dc0-5b8e-4c7f-aa26-4395ebbd3dbb','f910442a-43ba-4734-8162-3022363bee47','expiry-shelf-v2.1','2.1.0','2026-07-09',15,'PRIORITY_SALE',0.8975,'Nearing expiry -- prioritize for immediate sale.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('f9f3cea4-3f8b-43bf-a005-9a637b56e328','5b8055e4-1113-4660-bfb7-b794dfa35e4c','expiry-shelf-v2.1','2.1.0','2026-08-08',45,'REJECTED',0.7293,'Product is already expired. Do not sell.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('a82c7de1-8b41-40b6-8a4b-0aa2a8e774ff','1091fc23-0cbd-4522-b45b-999481193061','expiry-shelf-v2.1','2.1.0','2026-10-22',120,'REJECTED',0.8756,'Remaining shelf life below minimum threshold.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('88622edc-0f4f-4401-872d-7b357373db61','2f5d6bf1-fdfc-44d0-b05b-2b270f8886d2','expiry-shelf-v2.1','2.1.0',NULL,NULL,'REQUIRES_REVIEW',0.8138,'Confidence too low -- requires human review.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('da445377-6d8e-4db3-a4d9-2be0465afa9a','cf0e4b36-01db-4118-a3a4-5ba93c8ad80d','expiry-shelf-v2.1','2.1.0','2026-06-19',-5,'ACCEPTED',0.8802,'Product has sufficient shelf life remaining.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('eb2be191-9a5a-4f2a-8d2a-6257d768f796','90836731-ca74-4cc0-9ba0-586cbaa6e231','expiry-shelf-v2.1','2.1.0','2026-07-09',15,'PRIORITY_SALE',0.8268,'Nearing expiry -- prioritize for immediate sale.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('e926bbd2-3eda-4042-9b29-43e057c13e52','91465d53-29c8-42fe-8e9f-b3c09439d891','expiry-shelf-v2.1','2.1.0','2026-08-08',45,'REJECTED',0.9512,'Product is already expired. Do not sell.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('dc2b82ef-0d59-4443-b60f-779dc553ffcf','e9eaa4b2-56cf-4fa0-8001-30bd56a910ba','expiry-shelf-v2.1','2.1.0','2026-10-22',120,'REJECTED',0.9605,'Remaining shelf life below minimum threshold.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO ml_predictions (id,inventory_item_id,model_name,model_version,predicted_expiry_date,predicted_remaining_days,predicted_decision,decision_confidence,decision_reason,prediction_status,predicted_at,created_at,updated_at)
VALUES ('24d9a7f1-9468-40d4-ba99-621235dd4e01','f643b03b-7436-4300-9868-72f0148667f3','expiry-shelf-v2.1','2.1.0',NULL,NULL,'REQUIRES_REVIEW',0.8352,'Confidence too low -- requires human review.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════
-- 8. MANUAL REVIEWS (10)
-- ═══════════════════════════════════════════
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('08a6aea5-9633-47c4-932c-6d5b0d8cfaeb','b1d79f1e-b549-49a6-b88e-474a9e582e62','USR-1000','warehouse_staff','2026-06-21','ACCEPTED','Manually verified batch. Corrected expiry date confirmed.','OCR failed -- label was torn.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('3e0c2d49-4c2f-4c9b-9a30-6e5b4d64e9d8','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','USR-1001','supervisor','2026-07-11','REJECTED','Manually verified batch. Corrected expiry date confirmed.','ML confidence below threshold.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('d7967f45-e057-4918-8946-103287b5d31c','72ac683e-2e41-435a-adc2-272c07144541','USR-1002','qa','2026-08-10','PRIORITY_SALE','Manually verified batch. Corrected expiry date confirmed.','Conflicting dates found on packaging.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('b05470b2-f8b8-4381-84fe-0b28fc44f1dc','04b2ecb8-4baf-4cbf-a9fa-3c354306b12e','USR-1003','warehouse_staff','2026-10-24','ESCALATE_TO_QA','Manually verified batch. Corrected expiry date confirmed.','Batch close to expiry -- supervisor review required.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('aa9cd9f3-68db-4c49-aaa0-944cccd57ae3','84da942f-3099-4fca-9dd8-d419ecb47e1f','USR-1004','supervisor','2026-07-26','ACCEPTED','Manually verified batch. Corrected expiry date confirmed.','Batch number missing from label.','completed',NOW(),NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('0d88f30a-4800-46b5-8e73-48749bf67ccd','4ff66496-1a5f-48a1-8ed8-cef0aba666fa','USR-1005','qa','2026-06-21','REJECTED','Manually verified batch. Corrected expiry date confirmed.','OCR failed -- label was torn.','pending',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('73cebdca-b307-48d1-ab2f-7b92f4eebb4a','e5c2a776-8a2c-4c08-b30f-bef5415c9d51','USR-1006','warehouse_staff','2026-07-11','PRIORITY_SALE','Manually verified batch. Corrected expiry date confirmed.','ML confidence below threshold.','pending',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('8d1641f2-6412-4bed-af77-63bfefa74edc','87fa595e-3532-48d6-9bd0-34a27257cf5f','USR-1007','supervisor','2026-08-10','ESCALATE_TO_QA','Manually verified batch. Corrected expiry date confirmed.','Conflicting dates found on packaging.','pending',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('ca40ba17-28d0-46b9-ae8b-94220e30edf7','001f1a1d-daa0-4414-bb6a-312768bd7ef3','USR-1008','qa','2026-10-24','ACCEPTED','Manually verified batch. Corrected expiry date confirmed.','Batch close to expiry -- supervisor review required.','pending',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;
INSERT INTO manual_reviews (id,inventory_item_id,reviewer_id,reviewer_role,corrected_expiry_date,human_decision,review_notes,escalation_reason,review_status,reviewed_at,created_at,updated_at)
VALUES ('c753d04d-f994-4c08-9004-5f6b8923640b','7b815279-b5e0-46ac-a0fd-d30d853e9573','USR-1009','warehouse_staff','2026-07-26','REJECTED','Manually verified batch. Corrected expiry date confirmed.','Batch number missing from label.','pending',NULL,NOW(),NOW())
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════
-- 9. AUDIT LOGS (40)
-- ═══════════════════════════════════════════
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('ca9fe9b8-8a92-4c1b-93fa-23cf86bdedbd','product.created','product','6bf38777-8241-442b-b443-8ed648f7ee8b','actor-1000','system',NULL,NULL,'Product registered in catalogue.','10.0.1.1','req-b3061c7b',NOW() - INTERVAL '0 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('e10e264d-ffba-4ac9-9b80-f12470885bb3','inventory.intake','inventory_item','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','actor-1001','service',NULL,NULL,'Batch received at warehouse intake.','10.0.2.2','req-44bf3059',NOW() - INTERVAL '120 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('71b4b71b-362f-4e46-8b95-f69a82f2da74','ocr.completed','ocr_result','3c3da521-1d6b-45d4-8431-7391aee56d77','actor-1002','service',NULL,NULL,'OCR extraction completed successfully.','10.0.3.3','req-ff0176ac',NOW() - INTERVAL '240 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('701b766b-0c48-41ed-9672-2a2d8172a39b','ocr.failed','ocr_result','7e4675bb-2f2e-43e7-a2ac-1f013f37b9d1','actor-1003','service',NULL,NULL,'OCR extraction failed due to engine timeout.','10.0.4.4','req-40d43f01',NOW() - INTERVAL '360 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('b95bb385-f6a7-48b2-9106-fc13d88b95f9','ml.prediction_received','inventory_item','84da942f-3099-4fca-9dd8-d419ecb47e1f','actor-1004','ml_team',NULL,NULL,'ML prediction returned with decision.','10.0.1.5','req-4da14f14',NOW() - INTERVAL '480 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('d90053aa-14f2-4e9f-b6b6-faf90646fe0c','manual_review.completed','inventory_item','4ff66496-1a5f-48a1-8ed8-cef0aba666fa','actor-1005','user',NULL,NULL,'Manual review completed by warehouse staff.','10.0.2.6','req-5d300db1',NOW() - INTERVAL '600 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('4325336a-3290-4b22-95d4-5a4cb607091c','status.changed','inventory_item','e5c2a776-8a2c-4c08-b30f-bef5415c9d51','actor-1006','system','{"status":"PENDING_OCR"}','{"status":"OCR_COMPLETED"}','Pipeline status updated to next stage.','10.0.3.7','req-149a6b6d',NOW() - INTERVAL '720 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('2c3fc4f8-0f1e-4153-9e2d-f584df05bce5','barcode.scanned','barcode_scan','a6d4df42-add0-4d46-812a-184bb58f40ab','actor-1007','service',NULL,NULL,'Barcode scanned via handheld scanner.','10.0.4.8','req-0e224df0',NOW() - INTERVAL '840 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('b0027416-1b8b-4429-8911-eaf42a75294e','product.updated','product','497607f1-92b2-43be-94c2-76823be5855a','actor-1008','user',NULL,NULL,'Product details updated by staff.','10.0.1.9','req-19b9f5b1',NOW() - INTERVAL '960 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('b23d76a0-b6b5-4c77-8ceb-5c71738f93a2','inventory.flagged_for_review','inventory_item','7b815279-b5e0-46ac-a0fd-d30d853e9573','actor-1009','system',NULL,NULL,'Item flagged for manual review due to low confidence.','10.0.2.10','req-7ddfaaaa',NOW() - INTERVAL '1080 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('e0973a5a-66b3-4884-a9b1-8a9696422f9e','product.created','product','f5cbd3a0-6057-4c6a-8f22-e81546d59e3f','actor-1000','system',NULL,NULL,'Product registered in catalogue.','10.0.3.11','req-bca9ef9e',NOW() - INTERVAL '1200 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('f8a44d25-b622-4554-87cb-e017bd939679','inventory.intake','inventory_item','f910442a-43ba-4734-8162-3022363bee47','actor-1001','service',NULL,NULL,'Batch received at warehouse intake.','10.0.4.12','req-271ecfcf',NOW() - INTERVAL '1320 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('99e624eb-3848-47be-88ae-88836eace884','ocr.completed','ocr_result','7d4b237c-99bc-43e2-bca4-bfb8eeadcc74','actor-1002','service',NULL,NULL,'OCR extraction completed successfully.','10.0.1.13','req-cd7fd4b4',NOW() - INTERVAL '1440 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('9a01d678-089f-45f2-8c2b-094aaa50fed8','ocr.failed','ocr_result','6d019115-27b9-458b-9797-4b0724fd7cf7','actor-1003','service',NULL,NULL,'OCR extraction failed due to engine timeout.','10.0.2.14','req-5fa1286c',NOW() - INTERVAL '1560 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('5f1d772f-1938-4416-9a73-5fa40975c904','ml.prediction_received','inventory_item','2f5d6bf1-fdfc-44d0-b05b-2b270f8886d2','actor-1004','ml_team',NULL,NULL,'ML prediction returned with decision.','10.0.3.15','req-1eae3894',NOW() - INTERVAL '1680 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('d4beca48-438c-415b-8fad-51e57b450cff','manual_review.completed','inventory_item','cf0e4b36-01db-4118-a3a4-5ba93c8ad80d','actor-1005','user',NULL,NULL,'Manual review completed by warehouse staff.','10.0.4.16','req-3ca511f5',NOW() - INTERVAL '1800 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('bd27fbd4-dc86-462a-bc2a-40cd7edbde0c','status.changed','inventory_item','90836731-ca74-4cc0-9ba0-586cbaa6e231','actor-1006','system','{"status":"PENDING_OCR"}','{"status":"OCR_COMPLETED"}','Pipeline status updated to next stage.','10.0.1.17','req-7bf28884',NOW() - INTERVAL '1920 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('3ad77317-ccc3-49cf-abbc-2494195ee28f','barcode.scanned','barcode_scan','44c5f582-d6eb-4557-be8c-20cdd443e902','actor-1007','service',NULL,NULL,'Barcode scanned via handheld scanner.','10.0.2.18','req-63de9f72',NOW() - INTERVAL '2040 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('651461e3-f016-427f-b91c-177e704626cb','product.updated','product','835ab1c9-5fcc-4681-9a02-44dd4b4b48a4','actor-1008','user',NULL,NULL,'Product details updated by staff.','10.0.3.19','req-c46f55e9',NOW() - INTERVAL '2160 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('63621b90-3430-43b8-a9b1-e4eeb5f0fc1c','inventory.flagged_for_review','inventory_item','f643b03b-7436-4300-9868-72f0148667f3','actor-1009','system',NULL,NULL,'Item flagged for manual review due to low confidence.','10.0.4.20','req-3fab3695',NOW() - INTERVAL '2280 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('ebca3cec-9370-494a-ac59-8f0abcefbaf3','product.created','product','6bf38777-8241-442b-b443-8ed648f7ee8b','actor-1000','system',NULL,NULL,'Product registered in catalogue.','10.0.1.1','req-441413fa',NOW() - INTERVAL '2400 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('9cb344d5-0dc4-4a87-b4fd-2e41fa0ddece','inventory.intake','inventory_item','0e64e0e2-9d86-49b2-8075-9386e80cf21c','actor-1001','service',NULL,NULL,'Batch received at warehouse intake.','10.0.2.2','req-d6c22681',NOW() - INTERVAL '2520 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('128f96e6-33ff-4d14-a7d1-ced49289effc','ocr.completed','ocr_result','93ba3e86-ad9b-4167-8c7b-0d5c30062f29','actor-1002','service',NULL,NULL,'OCR extraction completed successfully.','10.0.3.3','req-4b35da7d',NOW() - INTERVAL '2640 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('ab516782-1663-4c17-be2e-3b9ee1fdf6f8','ocr.failed','ocr_result','f6dbee2b-b68f-4b7c-aa96-e7812071251a','actor-1003','service',NULL,NULL,'OCR extraction failed due to engine timeout.','10.0.4.4','req-846be1d4',NOW() - INTERVAL '2760 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('75b65d1d-a820-4e1a-a197-067f1c5a8bf4','ml.prediction_received','inventory_item','64488bf3-4d52-41e7-9bd4-c6de6231caff','actor-1004','ml_team',NULL,NULL,'ML prediction returned with decision.','10.0.1.5','req-b9f8fcd7',NOW() - INTERVAL '2880 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('9175051f-94f5-461e-9991-3a5b41c94533','manual_review.completed','inventory_item','b1d79f1e-b549-49a6-b88e-474a9e582e62','actor-1005','user',NULL,NULL,'Manual review completed by warehouse staff.','10.0.2.6','req-0349e588',NOW() - INTERVAL '3000 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('a2895a68-540f-402c-ac76-347c6aa157ea','status.changed','inventory_item','876c3ed6-e32d-4e28-8b5b-ca44b1d2ec9e','actor-1006','system','{"status":"PENDING_OCR"}','{"status":"OCR_COMPLETED"}','Pipeline status updated to next stage.','10.0.3.7','req-7d2914fc',NOW() - INTERVAL '3120 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('5bbe4f5b-cdd7-4fcc-9636-cd169f5c39d0','barcode.scanned','barcode_scan','9c187b0b-adb5-4cef-8dc2-beb8cfe55552','actor-1007','service',NULL,NULL,'Barcode scanned via handheld scanner.','10.0.4.8','req-4b6cb52f',NOW() - INTERVAL '3240 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('ca64128c-fd7a-4093-b5fd-42516b70f292','product.updated','product','497607f1-92b2-43be-94c2-76823be5855a','actor-1008','user',NULL,NULL,'Product details updated by staff.','10.0.1.9','req-fd3417f8',NOW() - INTERVAL '3360 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('8bdeef53-6cf6-47d4-9d9d-6c15777d2081','inventory.flagged_for_review','inventory_item','84da942f-3099-4fca-9dd8-d419ecb47e1f','actor-1009','system',NULL,NULL,'Item flagged for manual review due to low confidence.','10.0.2.10','req-ec55fa14',NOW() - INTERVAL '3480 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('9bf8e66c-0359-4ebf-8f48-fe585e7b2639','product.created','product','f5cbd3a0-6057-4c6a-8f22-e81546d59e3f','actor-1000','system',NULL,NULL,'Product registered in catalogue.','10.0.3.11','req-2bc1859b',NOW() - INTERVAL '3600 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('3c1e98a5-0634-4ded-86c3-36e3657bee0d','inventory.intake','inventory_item','e5c2a776-8a2c-4c08-b30f-bef5415c9d51','actor-1001','service',NULL,NULL,'Batch received at warehouse intake.','10.0.4.12','req-2f403c9b',NOW() - INTERVAL '3720 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('0f76a9c2-ed26-405c-b6a9-22c199a89548','ocr.completed','ocr_result','a4f13fa0-ff29-4008-902b-346241ca1d62','actor-1002','service',NULL,NULL,'OCR extraction completed successfully.','10.0.1.13','req-a5baa052',NOW() - INTERVAL '3840 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('cbe9aa20-b0b6-47de-8c03-ea4496c22aeb','ocr.failed','ocr_result','7152701f-e4c3-4253-8f8a-13ba0e03f281','actor-1003','service',NULL,NULL,'OCR extraction failed due to engine timeout.','10.0.2.14','req-0729ff79',NOW() - INTERVAL '3960 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('1c8a9095-3eda-431d-8fd1-0159cfe7d310','ml.prediction_received','inventory_item','7b815279-b5e0-46ac-a0fd-d30d853e9573','actor-1004','ml_team',NULL,NULL,'ML prediction returned with decision.','10.0.3.15','req-1e63b22d',NOW() - INTERVAL '4080 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('21f74068-90c2-4d87-9b96-698315f73600','manual_review.completed','inventory_item','785a3771-47c9-47ad-8832-5dcef7d65eac','actor-1005','user',NULL,NULL,'Manual review completed by warehouse staff.','10.0.4.16','req-820ba07d',NOW() - INTERVAL '4200 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('a87c442e-f591-40d1-a343-d0ae60c18025','status.changed','inventory_item','f910442a-43ba-4734-8162-3022363bee47','actor-1006','system','{"status":"PENDING_OCR"}','{"status":"OCR_COMPLETED"}','Pipeline status updated to next stage.','10.0.1.17','req-e7386d1d',NOW() - INTERVAL '4320 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('56ff7e59-8383-4b21-9c6a-5ffa8b6ff815','barcode.scanned','barcode_scan','6ea387c4-bb6a-47f8-8ed7-07812a2c1110','actor-1007','service',NULL,NULL,'Barcode scanned via handheld scanner.','10.0.2.18','req-eb34e1ab',NOW() - INTERVAL '4440 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('d7d18731-0feb-4a4a-9f86-c134c92da60f','product.updated','product','835ab1c9-5fcc-4681-9a02-44dd4b4b48a4','actor-1008','user',NULL,NULL,'Product details updated by staff.','10.0.3.19','req-a33986a6',NOW() - INTERVAL '4560 seconds')
ON CONFLICT DO NOTHING;
INSERT INTO audit_logs (id,event_type,entity_type,entity_id,actor_id,actor_type,before_state,after_state,change_summary,ip_address,request_id,occurred_at)
VALUES ('a34f3060-ac53-4052-85f1-6f743d3b39fb','inventory.flagged_for_review','inventory_item','2f5d6bf1-fdfc-44d0-b05b-2b270f8886d2','actor-1009','system',NULL,NULL,'Item flagged for manual review due to low confidence.','10.0.4.20','req-a391d89e',NOW() - INTERVAL '4680 seconds')
ON CONFLICT DO NOTHING;
