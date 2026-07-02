from typing import Optional
from app.schemas.product_lookup_schema import ProductLookup

class LocalProvider:
    """
    Placeholder for future PostgreSQL integration.
    Currently returns None for all lookups as the DB is not implemented in Phase 2.2.
    """
    def lookup(self, barcode: str) -> Optional[ProductLookup]:
        # TODO: Implement DB lookup when PostgreSQL is ready.
        return None
