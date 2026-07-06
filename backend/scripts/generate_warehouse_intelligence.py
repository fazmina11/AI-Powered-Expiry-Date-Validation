#!/usr/bin/env python
"""
scripts/generate_warehouse_intelligence.py — Synthetic Data Generator for Phase 4.
Generates:
  - Transport cost configuration row
  - 10 warehouses and configs (stable identities)
  - Demand profiles for all category combinations (with average_sell_through_days)
  - 90 directional transfer matrix routes (using dynamic transport cost configurations)
  - Realistic supplier return policies (with min/max return quantity limits)

Uses a fixed random seed (42) to guarantee repeatability.
"""

from decimal import Decimal
import os
import random
import sys
from datetime import datetime

# Add parent directory to path to enable imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product
from app.models.warehouse import (
    Warehouse,
    TransportCostConfiguration,
    WarehouseConfiguration,
    WarehouseDemandProfile,
    WarehouseTransferMatrix,
    SupplierReturnPolicy,
    OptimizationConfiguration,
)



def main():
    db = SessionLocal()
    try:
        print("Starting warehouse intelligence data generation...")

        # 1. Clean existing warehouse tables to enable fresh insertion
        db.query(WarehouseTransferMatrix).delete()
        db.query(WarehouseDemandProfile).delete()
        db.query(WarehouseConfiguration).delete()
        db.query(SupplierReturnPolicy).delete()
        db.query(TransportCostConfiguration).delete()
        db.query(OptimizationConfiguration).delete()
        db.query(Warehouse).delete()
        db.commit()
        print("Existing warehouse intelligence records purged.")

        # 2. Insert dynamic TransportCostConfiguration
        config = TransportCostConfiguration(
            id="default",
            fuel_cost_per_km=Decimal("15.00"),
            labour_cost_per_hour=Decimal("150.00"),
            good_handling_cost=Decimal("500.00"),
            moderate_handling_cost=Decimal("1000.00"),
            poor_handling_cost=Decimal("2000.00"),
        )
        db.add(config)
        
        opt_config = OptimizationConfiguration(
            id="default",
            financial_weight=Decimal("30.00"),
            demand_weight=Decimal("25.00"),
            compatibility_weight=Decimal("25.00"),
            transport_weight=Decimal("30.00"),
            shelf_life_weight=Decimal("20.00"),
            supplier_weight=Decimal("30.00"),
        )
        db.add(opt_config)
        db.flush()
        print("Dynamic transport and optimization configurations registered.")


        # 3. Create 10 Warehouses with stable identities
        warehouses_data = [
            ("WH-BLR", "Warehouse Bangalore", 10000, "08:00 - 20:00", 500, True, True, "HIGH"),
            ("WH-CHN", "Warehouse Chennai", 8000, "06:00 - 22:00", 400, True, False, "MEDIUM"),
            ("WH-COI", "Warehouse Coimbatore", 5000, "09:00 - 18:00", 200, False, False, "LOW"),
            ("WH-HYD", "Warehouse Hyderabad", 9000, "08:00 - 20:00", 450, True, True, "HIGH"),
            ("WH-MUM", "Warehouse Mumbai", 12000, "00:00 - 23:59", 800, True, True, "HIGH"),
            ("WH-DEL", "Warehouse Delhi", 11000, "00:00 - 23:59", 700, True, True, "HIGH"),
            ("WH-KOL", "Warehouse Kolkata", 8500, "08:00 - 20:00", 350, True, False, "MEDIUM"),
            ("WH-PUN", "Warehouse Pune", 7500, "09:00 - 21:00", 300, True, True, "MEDIUM"),
            ("WH-AMD", "Warehouse Ahmedabad", 7000, "08:00 - 22:00", 250, False, False, "LOW"),
            ("WH-KER", "Warehouse Kochi", 6000, "09:00 - 18:00", 200, True, False, "LOW"),
        ]

        warehouses = []
        for wh_id, name, cap, hrs, disp, cold, temp, pri in warehouses_data:
            wh = Warehouse(id=wh_id, name=name)
            db.add(wh)
            warehouses.append(wh)
            
            wh_config = WarehouseConfiguration(
                warehouse_id=wh_id,
                warehouse_capacity=cap,
                warehouse_operating_hours=hrs,
                maximum_daily_dispatch=disp,
                cold_storage_available=cold,
                temperature_control=temp,
                priority_level=pri,
            )
            db.add(wh_config)

        db.flush()
        print("10 Warehouses and configurations created successfully.")

        # 4. Generate Demand Profiles for each warehouse x 5 product categories
        categories = ["Dairy", "Beverages", "Produce", "Bakery", "Packaged Foods"]
        
        # We use a deterministic random generation seeded with 42
        rng = random.Random(42)

        for wh in warehouses:
            # Deterministic categories personalities based on ID
            # WH-BLR (High Dairy, High Beverage)
            # WH-CHN (High Beverage, High Packaged Foods)
            # WH-COI (High Packaged Foods, Low Dairy)
            wh_type = wh.id.split("-")[1]

            for cat in categories:
                # Basic demand settings
                daily_base = 50.0
                weekly_base = 350.0
                monthly_base = 1500.0
                sell_through = 14
                trend = "STABLE"
                seasonality = 1.00

                # Fine-tune demand personalities deterministically
                if wh_type == "BLR":
                    if cat == "Dairy":
                        daily_base, sell_through, trend = 250.0, 2, "INCREASING"
                    elif cat == "Beverages":
                        daily_base, sell_through = 180.0, 4
                elif wh_type == "CHN":
                    if cat == "Beverages":
                        daily_base, sell_through, trend = 300.0, 2, "INCREASING"
                    elif cat == "Packaged Foods":
                        daily_base, sell_through = 220.0, 10
                elif wh_type == "COI":
                    if cat == "Packaged Foods":
                        daily_base, sell_through = 310.0, 8
                    elif cat == "Dairy":
                        daily_base, sell_through, trend = 15.0, 7, "DECREASING"
                elif wh_type == "MUM":
                    daily_base *= 2.0  # Mumbai general demand is higher
                    sell_through = max(1, sell_through - 2)

                # Add deterministic random variance
                variance = rng.uniform(-10.0, 10.0)
                daily_demand = max(5.0, daily_base + variance)
                weekly_demand = daily_demand * 7
                monthly_demand = daily_demand * 30
                
                # Seasonality factor between 0.8 and 1.4
                seasonality = Decimal(f"{rng.uniform(0.8, 1.4):.2f}")

                # Save demand profile
                demand_profile = WarehouseDemandProfile(
                    warehouse_id=wh.id,
                    product_category=cat,
                    average_daily_demand=Decimal(f"{daily_demand:.2f}"),
                    average_weekly_demand=Decimal(f"{weekly_demand:.2f}"),
                    average_monthly_demand=Decimal(f"{monthly_demand:.2f}"),
                    demand_trend=trend,
                    seasonality_factor=seasonality,
                    average_sell_through_days=sell_through,
                )
                db.add(demand_profile)

        db.flush()
        print(f"Generated {len(warehouses) * len(categories)} warehouse demand profiles.")

        # 5. Generate Warehouse Transfer Matrix (all pairs: 10 * 9 = 90 directional routes)
        # Fuel, labour, handling cost are derived from TransportCostConfiguration
        for src in warehouses:
            for dst in warehouses:
                if src.id == dst.id:
                    continue  # No self-transfers

                # Create deterministic values based on route
                route_hash = sum(ord(c) for c in (src.id + dst.id))
                rng_route = random.Random(42 + route_hash)

                distance = Decimal(f"{rng_route.uniform(50.0, 1000.0):.2f}")
                
                # Estimated travel hours: speed is ~60 km/h, road factor adds overhead
                base_hours = distance / Decimal("60.00")
                
                road_factor = rng_route.choice(["GOOD", "MODERATE", "POOR"])
                if road_factor == "GOOD":
                    handling_cost = config.good_handling_cost
                    estimated_hours = base_hours
                elif road_factor == "MODERATE":
                    handling_cost = config.moderate_handling_cost
                    estimated_hours = base_hours * Decimal("1.20")
                else:
                    handling_cost = config.poor_handling_cost
                    estimated_hours = base_hours * Decimal("1.50")

                # Calculations using TransportCostConfiguration properties
                fuel_cost = distance * config.fuel_cost_per_km
                labour_cost = estimated_hours * config.labour_cost_per_hour
                total_cost = fuel_cost + labour_cost + handling_cost

                # Save matrix row
                matrix_entry = WarehouseTransferMatrix(
                    source_warehouse_id=src.id,
                    destination_warehouse_id=dst.id,
                    distance_km=distance,
                    estimated_travel_hours=Decimal(f"{estimated_hours:.2f}"),
                    fuel_cost=Decimal(f"{fuel_cost:.2f}"),
                    labour_cost=Decimal(f"{labour_cost:.2f}"),
                    handling_cost=Decimal(f"{handling_cost:.2f}"),
                    total_transfer_cost=Decimal(f"{total_cost:.2f}"),
                    road_condition_factor=road_factor,
                )
                db.add(matrix_entry)

        db.flush()
        print("Warehouse transfer matrix (90 directional routes) populated successfully.")

        # 6. Generate Supplier Return Policies dynamically from products table
        # Query distinct brands
        products = db.query(Product).all()
        brands = set()
        brand_to_category = {}

        for p in products:
            # Resolve brand from SKU prefix (first part before '-') or name
            brand = p.sku.split("-")[0] if "-" in p.sku else p.name.split()[0]
            brands.add(brand)
            if p.category:
                brand_to_category[brand] = p.category

        # Fallback to standard 8 brands if DB is empty (e.g. tests / clean setup)
        if not brands:
            brands = {"Amul", "Britannia", "Nestle", "Mother Dairy", "Hindustan Unilever", "Pepsico", "Coca Cola", "Parle"}

        # Preserve allowed status for standard brands
        STANDARD_ALLOWED_MAP = {
            "Amul": True,
            "Britannia": True,
            "Nestle": True,
            "Mother Dairy": True,
            "Hindustan Unilever": True,
            "Pepsico": False,
            "Coca Cola": False,
            "Parle": True,
        }

        # Categories mapping for standard fallback brands
        STANDARD_CATEGORY_MAP = {
            "Amul": "Dairy",
            "Mother Dairy": "Dairy",
            "Britannia": "Bakery",
            "Parle": "Bakery",
            "Nestle": "Packaged Foods",
            "Hindustan Unilever": "Personal Care",
            "Pepsico": "Beverages",
            "Coca Cola": "Beverages",
        }

        sorted_brands = sorted(list(brands))
        generated_count = 0

        for brand in sorted_brands:
            # Deterministic seed per brand
            brand_seed = 42 + sum(ord(c) for c in brand)
            rng = random.Random(brand_seed)

            # Resolve Category
            category = brand_to_category.get(brand)
            if not category:
                category = STANDARD_CATEGORY_MAP.get(brand, "Packaged Foods")

            # Return Allowed flag
            if brand in STANDARD_ALLOWED_MAP:
                allowed = STANDARD_ALLOWED_MAP[brand]
            else:
                # 80% True, 20% False
                allowed = rng.choice([True, True, True, True, False])

            # Generate parameters based on category
            if not allowed:
                window = 0
                max_percent = Decimal("0.00")
                shelf_life = 0
                fee = Decimal("0.00")
                min_qty = 0
                max_qty = 0
            else:
                fee = Decimal(f"{rng.uniform(5.00, 50.00):.2f}")
                min_qty = rng.randint(5, 20)
                max_qty = rng.randint(100, 1000)

                cat_lower = category.lower()
                if "dairy" in cat_lower:
                    window = rng.randint(2, 5)
                    max_percent = Decimal(f"{rng.uniform(80.0, 95.0):.2f}")
                    shelf_life = rng.randint(3, 7)
                elif "bakery" in cat_lower:
                    window = rng.randint(3, 7)
                    max_percent = Decimal(f"{rng.uniform(60.0, 80.0):.2f}")
                    shelf_life = rng.randint(2, 5)
                elif "bever" in cat_lower:
                    window = rng.randint(5, 10)
                    max_percent = Decimal(f"{rng.uniform(60.0, 85.0):.2f}")
                    shelf_life = rng.randint(7, 15)
                elif "snack" in cat_lower or "packaged" in cat_lower or "food" in cat_lower:
                    window = rng.randint(5, 15)
                    max_percent = Decimal(f"{rng.uniform(50.0, 75.0):.2f}")
                    shelf_life = rng.randint(5, 12)
                elif "personal" in cat_lower or "care" in cat_lower:
                    window = rng.randint(15, 30)
                    max_percent = Decimal(f"{rng.uniform(50.0, 70.0):.2f}")
                    shelf_life = rng.randint(15, 45)
                else:
                    # Default / Fallback category ranges
                    window = rng.randint(5, 15)
                    max_percent = Decimal(f"{rng.uniform(50.0, 80.0):.2f}")
                    shelf_life = rng.randint(5, 10)

            policy = SupplierReturnPolicy(
                supplier_id=brand,
                return_allowed=allowed,
                return_window_days=window,
                maximum_return_percentage=max_percent,
                minimum_remaining_shelf_life=shelf_life,
                restocking_fee=fee,
                minimum_return_quantity=min_qty,
                maximum_return_quantity=max_qty,
            )
            db.add(policy)
            generated_count += 1

        db.commit()
        print(f"Supplier return policies generated successfully ({generated_count} brands).")
        print("Warehouse Intelligence data generation completed successfully!")


    except Exception as e:
        db.rollback()
        print(f"Error generating warehouse intelligence data: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
