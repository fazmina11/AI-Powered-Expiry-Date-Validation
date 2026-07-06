"""
utils/exceptions.py — All application-level exception classes.

These are raised by service functions and caught by route handlers,
which translate them into structured HTTP error responses.
"""


class ProductNotFoundError(Exception):
    """Raised when a product lookup by ID or barcode returns nothing."""
    error_code = "PRODUCT_NOT_FOUND"


class InventoryItemNotFoundError(Exception):
    """Raised when an inventory item lookup by ID returns nothing."""
    error_code = "INVENTORY_NOT_FOUND"


class ValidationRecordNotFoundError(Exception):
    """Raised when no validation records exist for a given inventory item."""
    error_code = "VALIDATION_NOT_FOUND"


class DuplicateSKUError(Exception):
    """Raised when a product with the same SKU already exists."""
    error_code = "DUPLICATE_SKU"


class DuplicateBarcodeError(Exception):
    """Raised when a product with the same barcode already exists."""
    error_code = "DUPLICATE_BARCODE"


class InvalidStatusError(Exception):
    """Raised when an unknown status string is passed as a filter."""
    error_code = "INVALID_STATUS"


class FinancialProfileNotFoundError(Exception):
    """Raised when a financial profile lookup by product_id returns nothing."""
    error_code = "FINANCIAL_PROFILE_NOT_FOUND"


class DuplicateFinancialProfileError(Exception):
    """Raised when a financial profile already exists for a product."""
    error_code = "DUPLICATE_FINANCIAL_PROFILE"


class InvalidPricingError(Exception):
    """Raised when validation fails (e.g. MRP <= purchase_price)."""
    error_code = "INVALID_PRICING"

