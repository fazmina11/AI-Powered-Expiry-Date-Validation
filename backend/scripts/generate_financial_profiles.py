#!/usr/bin/env python
"""
scripts/generate_financial_profiles.py — Command-line interface to trigger
the synthetic financial profile generator for all products in the database.
"""

import os
import sys
import argparse

# Add parent directory to path to enable imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.financial_profile_service import generate_synthetic_profiles


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic financial profiles for products lacking one."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed for repeatable pricing ranges (default: 42)",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print(f"Starting synthetic financial profile generator (seed={args.seed})...")
        created_count = generate_synthetic_profiles(db, seed=args.seed)
        print(f"Success: Generated {created_count} new product financial profiles.")
    except Exception as e:
        print(f"Error executing generator: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
