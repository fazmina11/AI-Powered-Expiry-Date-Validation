-- =====================================================================
-- verify_inventory_financials.sql — Verification script for Phase 2
--
-- Exposes stats detailing matching inventory financials, snapshots,
-- validation check metrics, and total valuations.
-- =====================================================================

-- 1. Count of inventory items missing purchase_price
SELECT COUNT(*) AS items_missing_purchase_price 
FROM inventory_items 
WHERE purchase_price IS NULL;

-- 2. Count of inventory items missing mrp
SELECT COUNT(*) AS items_missing_mrp 
FROM inventory_items 
WHERE mrp IS NULL;

-- 3. Count of inventory items missing financial_profile_snapshot
SELECT COUNT(*) AS items_missing_snapshot 
FROM inventory_items 
WHERE financial_profile_snapshot IS NULL;

-- 4. Count of inventory items with invalid pricing (mrp < purchase_price)
SELECT COUNT(*) AS items_with_invalid_pricing 
FROM inventory_items 
WHERE mrp < purchase_price;

-- 5. Count of inventory items with supplier_return_percent outside valid range (0 - 100)
SELECT COUNT(*) AS items_with_invalid_return_percent 
FROM inventory_items 
WHERE supplier_return_percent < 0.00 OR supplier_return_percent > 100.00;

-- 6. Total inventory valuation across the entire warehouse
SELECT SUM(inventory_cost) AS total_inventory_valuation 
FROM inventory_items;
