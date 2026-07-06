-- =====================================================================
-- verify_financials.sql — Verification script for Product Financial Master
--
-- Exposes stats detailing matching products and profiles.
-- =====================================================================

-- 1. Total count of registered products
SELECT COUNT(*) AS total_products 
FROM products;

-- 2. Total count of generated product financial profiles
SELECT COUNT(*) AS total_financial_profiles 
FROM product_financial_profiles;

-- 3. Total count of products missing a financial profile
SELECT COUNT(*) AS products_without_financial_profiles 
FROM products p 
LEFT JOIN product_financial_profiles pfp ON p.id = pfp.product_id 
WHERE pfp.product_id IS NULL;

-- 4. Detail list of products missing a financial profile (limit 50)
SELECT p.id, p.sku, p.name, p.category 
FROM products p 
LEFT JOIN product_financial_profiles pfp ON p.id = pfp.product_id 
WHERE pfp.product_id IS NULL
LIMIT 50;
