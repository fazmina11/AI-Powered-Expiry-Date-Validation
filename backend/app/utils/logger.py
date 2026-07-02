"""
utils/logger.py — Structured application logger.

Usage:
    from app.utils.logger import logger
    logger.info("Inventory item created", extra={"item_id": 1, "status": "ACCEPTED"})

All log records include:
  - timestamp (ISO 8601)
  - log level
  - module name
  - message
  - any extra key-value context passed via `extra=`

In production, swap the handler/formatter for JSON output
(e.g. python-json-logger) to feed into your log aggregator.
"""

import logging
import sys

# ── Formatter ─────────────────────────────────────────────────
_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

# ── Handler ───────────────────────────────────────────────────
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(_formatter)

# ── Root app logger ───────────────────────────────────────────
logger = logging.getLogger("expiry_validation")
logger.setLevel(logging.DEBUG)
logger.addHandler(_handler)
logger.propagate = False   # don't double-log to uvicorn's root logger


# ── Convenience helpers ───────────────────────────────────────

def log_product_created(product_id: int, sku: str) -> None:
    logger.info("Product created | id=%d sku=%s", product_id, sku)


def log_inventory_created(item_id: int, status: str, remaining_days) -> None:
    logger.info(
        "Inventory item created | id=%d status=%s remaining_days=%s",
        item_id, status, remaining_days,
    )


def log_validation_stored(record_id: int, inventory_item_id: int, validation_status: str) -> None:
    logger.info(
        "Validation record stored | id=%d inventory_item_id=%d validation_status=%s",
        record_id, inventory_item_id, validation_status,
    )


def log_status_generated(item_id: int, status: str, reason: str) -> None:
    logger.info(
        "Status generated | inventory_item_id=%d status=%s reason=%s",
        item_id, status, reason,
    )
