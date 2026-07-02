import httpx
import logging
import time
from typing import Optional
from app.schemas.product_lookup_schema import ProductLookup

logger = logging.getLogger(__name__)

class OpenFoodFactsProvider:
    """
    Looks up product data from Open Food Facts REST API using httpx.
    """
    BASE_URL = "https://world.openfoodfacts.org/api/v0/product/{}.json"
    WEB_URL = "https://world.openfoodfacts.org/product/{}"

    def lookup(self, barcode: str) -> Optional[ProductLookup]:
        start_time = time.time()
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(self.BASE_URL.format(barcode))
                
            if response.status_code != 200:
                logger.warning(f"[OpenFoodFacts] Non-200 response for {barcode}: {response.status_code}")
                return None
            
            data = response.json()
            if data.get("status") != 1:
                return None
            
            product = data.get("product", {})
            
            image_urls = []
            if product.get("image_url"):
                image_urls.append(product.get("image_url"))
            if product.get("image_ingredients_url"):
                image_urls.append(product.get("image_ingredients_url"))
            if product.get("image_nutrition_url"):
                image_urls.append(product.get("image_nutrition_url"))
                
            categories_hierarchy = product.get("categories_hierarchy", [])
            subcategory = categories_hierarchy[-1].replace("en:", "") if categories_hierarchy else None
                
            lookup_time_ms = (time.time() - start_time) * 1000.0

            return ProductLookup(
                found=True,
                source="OpenFoodFacts",
                barcode=barcode,
                product_name=product.get("product_name"),
                brand=product.get("brands"),
                manufacturer=product.get("manufacturing_places") or product.get("brands"),
                category=product.get("categories"),
                subcategory=subcategory,
                quantity=product.get("quantity"),
                weight=product.get("quantity"),
                ingredients=product.get("ingredients_text"),
                nutrition=str(product.get("nutriments", {})) if product.get("nutriments") else None,
                packaging=product.get("packaging"),
                image_urls=image_urls,
                country_of_sale=product.get("countries"),
                labels=product.get("labels"),
                product_url=self.WEB_URL.format(barcode),
                lookup_time_ms=lookup_time_ms,
                cache_status="MISS",
                additional_attributes={}
            )
        except httpx.TimeoutException:
            logger.error(f"[OpenFoodFacts] Timeout querying {barcode}")
            return None
        except Exception as e:
            logger.error(f"[OpenFoodFacts] Error querying {barcode}: {e}")
            return None
