-- =============================================================
-- Phase 2 — Seed Script: 20 Mock Products
-- =============================================================
-- Idempotent: uses INSERT ... ON CONFLICT DO NOTHING
-- so duplicate barcodes and SKUs are silently skipped.
-- Run with:
--   docker exec -i expiry_postgres psql -U expiry_user -d expiry_db < scripts/seed_products.sql

INSERT INTO products (name, brand, sku, barcode, barcode_type, category, description, default_storage_type)
VALUES
-- ── Dairy (4 products) ─────────────────────────────────────
(
    'Full Cream Milk 1L',
    'Amul',
    'AMUL-MILK-1L',
    '8901058000027',
    'EAN13',
    'Dairy',
    'Pasteurised full cream milk in a 1-litre tetra pack.',
    'refrigerated'
),
(
    'Low Fat Yogurt 400g',
    'Nestle',
    'NESTLE-YOG-400G',
    '8901030789010',
    'EAN13',
    'Dairy',
    'Low-fat plain yogurt with live cultures, 400g tub.',
    'refrigerated'
),
(
    'Processed Cheese Slices 200g',
    'Britannia',
    'BRIT-CHEESE-200G',
    '8901063150245',
    'EAN13',
    'Dairy',
    'Individually wrapped processed cheese slices, 200g pack.',
    'refrigerated'
),
(
    'Salted Butter 100g',
    'Mother Dairy',
    'MDAIRY-BUT-100G',
    '8904117100018',
    'EAN13',
    'Dairy',
    'Creamy salted butter, 100g block.',
    'refrigerated'
),

-- ── Beverages (4 products) ────────────────────────────────
(
    'Mango Fruit Drink 200ml',
    'Frooti',
    'FROOTI-MANGO-200ML',
    '8901088100015',
    'EAN13',
    'Beverages',
    'Mango flavoured fruit drink, 200ml tetra pack.',
    'ambient'
),
(
    'Orange Juice 1L',
    'Tropicana',
    'TROP-OJ-1L',
    '0012000001086',
    'EAN13',
    'Beverages',
    '100% pure pressed orange juice, 1-litre carton.',
    'refrigerated'
),
(
    'Green Tea 25 Bags',
    'Tetley',
    'TETLEY-GT-25',
    '0055100150002',
    'EAN13',
    'Beverages',
    'Green tea bags, pack of 25. Store in cool dry place.',
    'ambient'
),
(
    'Sparkling Mineral Water 500ml',
    'Perrier',
    'PERRIER-500ML',
    '0074780300018',
    'EAN13',
    'Beverages',
    'Naturally sparkling mineral water, 500ml glass bottle.',
    'ambient'
),

-- ── Snacks (3 products) ───────────────────────────────────
(
    'Classic Salted Chips 100g',
    'Lays',
    'LAYS-SALT-100G',
    '0028400589758',
    'EAN13',
    'Snacks',
    'Classic salted potato chips, 100g bag.',
    'ambient'
),
(
    'Dark Chocolate Bar 80g',
    'Cadbury Bournville',
    'CAD-BORN-80G',
    '7622300441937',
    'EAN13',
    'Snacks',
    'Rich dark chocolate 70% cocoa, 80g bar.',
    'ambient'
),
(
    'Roasted Mixed Nuts 150g',
    'Happilo',
    'HAPPI-MNUTS-150G',
    '8906017260093',
    'EAN13',
    'Snacks',
    'Dry roasted mixed nuts — almonds, cashews, walnuts, 150g.',
    'ambient'
),

-- ── Bakery (3 products) ───────────────────────────────────
(
    'Whole Wheat Bread 400g',
    'Harvest Gold',
    'HG-WWBREAD-400G',
    '8906068110018',
    'EAN13',
    'Bakery',
    'Whole wheat sandwich bread, 400g loaf (18 slices).',
    'ambient'
),
(
    'Butter Croissant 6-Pack',
    'Monginis',
    'MONG-CROIS-6PK',
    '8904265100012',
    'EAN13',
    'Bakery',
    'Freshly baked all-butter croissants, pack of 6.',
    'ambient'
),
(
    'Digestive Biscuits 400g',
    'McVitie''s',
    'MCVIT-DIG-400G',
    '5000168003009',
    'EAN13',
    'Bakery',
    'Original digestive wheat biscuits, 400g pack.',
    'ambient'
),

-- ── Personal Care (3 products) ────────────────────────────
(
    'Moisturising Shampoo 340ml',
    'Dove',
    'DOVE-SHAMP-340ML',
    '0011111019220',
    'EAN13',
    'Personal Care',
    'Intensive moisture repair shampoo for dry hair, 340ml.',
    'ambient'
),
(
    'Sunscreen SPF 50 100ml',
    'Lotus Herbals',
    'LOTUS-SPF50-100ML',
    '8901176011339',
    'EAN13',
    'Personal Care',
    'Broad spectrum SPF 50 sunscreen, 100ml tube.',
    'ambient'
),
(
    'Toothpaste Whitening 150g',
    'Colgate',
    'COLG-WHITE-150G',
    '0035000138637',
    'EAN13',
    'Personal Care',
    'Advanced whitening toothpaste with fluoride, 150g.',
    'ambient'
),

-- ── Packaged Foods (3 products) ───────────────────────────
(
    'Basmati Rice 5kg',
    'India Gate',
    'IGATE-BASMATI-5KG',
    '8906000940019',
    'EAN13',
    'Packaged Foods',
    'Premium aged basmati rice, 5kg vacuum-sealed bag.',
    'ambient'
),
(
    'Masala Instant Noodles 70g',
    'Maggi',
    'MAGGI-MASALA-70G',
    '8901058504121',
    'EAN13',
    'Packaged Foods',
    'Instant noodles with masala tastemaker, 70g single serving.',
    'ambient'
),
(
    'Frozen Peas 500g',
    'McCain',
    'MCCAIN-PEAS-500G',
    '0065251000188',
    'EAN13',
    'Packaged Foods',
    'Garden fresh frozen green peas, 500g resealable bag.',
    'frozen'
)
ON CONFLICT (barcode) DO NOTHING;
-- Rows with duplicate barcode are silently skipped (idempotent).
-- SKU uniqueness is enforced by the UNIQUE constraint on the column.
