from typing import List, Protocol, Optional, Dict
import time
import logging
from app.schemas.product_lookup_schema import ProductLookup
from app.services.providers.local_provider import LocalProvider
from app.services.providers.openfoodfacts_provider import OpenFoodFactsProvider
from app.services.providers.openbeautyfacts_provider import OpenBeautyFactsProvider
from app.services.providers.openpetfoodfacts_provider import OpenPetFoodFactsProvider

logger = logging.getLogger(__name__)

class ProductProvider(Protocol):
    def lookup(self, barcode: str) -> Optional[ProductLookup]:
        ...

class ProductLookupService:
    def __init__(self, providers: Optional[List[ProductProvider]] = None):
        """
        Initialize the ProductLookupService with an ordered list of providers.
        Priority:
        1. LocalProvider
        2. OpenFoodFactsProvider
        3. OpenBeautyFactsProvider
        4. OpenPetFoodFactsProvider
        """
        if providers is None:
            self.providers = [
                LocalProvider(),
                OpenFoodFactsProvider(),
                OpenBeautyFactsProvider(),
                OpenPetFoodFactsProvider()
            ]
        else:
            self.providers = providers
            
        # In-memory cache for product lookups to avoid external API calls on repeated scans
        self._cache: Dict[str, ProductLookup] = {}

    def lookup_product(self, barcode: str) -> ProductLookup:
        """
        Lookup a product by barcode across configured providers.
        Returns the first successful result or an Unknown Product response.
        Uses in-memory caching.
        """
        start_time = time.time()
        
        if not barcode or not isinstance(barcode, str):
            logger.error(f"[ProductLookupService] Invalid barcode provided: {barcode}")
            raise ValueError("Barcode must be a valid string")
            
        barcode = barcode.strip()
        
        # Check cache
        if barcode in self._cache:
            logger.info(f"[ProductLookupService] Cache hit for barcode: {barcode}")
            cached_result = self._cache[barcode]
            # Create a copy so we don't accidentally mutate the cached object later
            result = cached_result.model_copy()
            result.cache_status = "HIT"
            result.lookup_time_ms = (time.time() - start_time) * 1000.0
            return result
            
        logger.info(f"[ProductLookupService] Cache miss for barcode: {barcode}. Querying providers...")

        # Query providers in order
        for provider in self.providers:
            try:
                result = provider.lookup(barcode)
                if result and result.found:
                    logger.info(f"[ProductLookupService] Found product in {result.source}")
                    result.cache_status = "MISS"
                    # Cache the successful result
                    self._cache[barcode] = result.model_copy()
                    return result
            except Exception as e:
                provider_name = provider.__class__.__name__
                logger.error(f"[ProductLookupService] Unexpected error in {provider_name} for barcode {barcode}: {e}", exc_info=True)
                # Continue to next provider on error
                continue

        # Unknown Product Fallback Response
        logger.info(f"[ProductLookupService] Product not found in any provider for barcode: {barcode}")
        total_time_ms = (time.time() - start_time) * 1000.0
        
        fallback_result = ProductLookup(
            found=False,
            source="Unknown",
            barcode=barcode,
            product_name=None,
            brand=None,
            manufacturer=None,
            category=None,
            subcategory=None,
            quantity=None,
            weight=None,
            ingredients=None,
            nutrition=None,
            packaging=None,
            image_urls=[],
            country_of_sale=None,
            labels=None,
            product_url=None,
            lookup_time_ms=total_time_ms,
            cache_status="MISS",
            additional_attributes={}
        )
        
        # We also cache MISSES to avoid hammering APIs for known bad barcodes
        self._cache[barcode] = fallback_result.model_copy()
        
        return fallback_result
