from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import product_lookup_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/products/search")
def search_products(
    query: str = Query(..., description="Product ID, Barcode, SKU, or Name to search"),
    request_source: str = Query("BACKEND_API", description="Source of the request (e.g. BACKEND_API, N8N, TELEGRAM)"),
    requested_by: Optional[str] = Query(None, description="Identifier of the requester"),
    db: Session = Depends(get_db)
):
    """
    Search for a product by ID, Barcode, SKU, or Name.
    Logs the lookup request and tracks unknown products.
    """
    try:
        result = product_lookup_service.search_product(
            db=db,
            query=query,
            request_source=request_source,
            requested_by=requested_by
        )
        return result
    except Exception as e:
        logger.exception("search_products error")
        return JSONResponse(
            status_code=500,
            content={
                "status": "ERROR",
                "source": "NONE",
                "search_type": "UNKNOWN",
                "result_count": 0,
                "query": query,
                "message": "Product lookup failed due to an internal error.",
            }
        )
