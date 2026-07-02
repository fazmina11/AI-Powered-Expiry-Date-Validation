import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.utils.query_detector import clean_query, detect_query_type

VALID_REQUEST_SOURCES = {"BACKEND_API", "N8N", "TELEGRAM", "WEB_DASHBOARD"}
LOG_QUERY_TYPE_MAP = {"SKU": "PRODUCT_NAME"}


def _json_safe(value: Any) -> Any:
    if isinstance(value, (UUID, Decimal)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _row_mapping(row) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row._mapping)


def _log_query_type(query_type: str) -> str:
    return LOG_QUERY_TYPE_MAP.get(query_type, query_type)


def _normalize_request_source(request_source: str | None) -> str:
    source = (request_source or "BACKEND_API").strip().upper()
    return source if source in VALID_REQUEST_SOURCES else "BACKEND_API"


def format_local_product_response(product) -> dict:
    data = _row_mapping(product)
    if not data:
        return {}

    return _json_safe({
        "id": data.get("id"),
        "name": data.get("name"),
        "sku": data.get("sku"),
        "barcode": data.get("barcode"),
        "barcode_type": data.get("barcode_type"),
        "brand": data.get("brand"),
        "category": data.get("category"),
        "sub_category": data.get("sub_category"),
        "description": data.get("description"),
        "ingredients": data.get("ingredients"),
        "nutrition_info": data.get("nutrition_info"),
        "storage_instruction": data.get("storage_instruction"),
        "manufacturer": data.get("manufacturer"),
        "country_of_origin": data.get("country_of_origin"),
        "image_url": data.get("image_url"),
        "product_source": data.get("product_source") or "LOCAL_DATABASE",
    })


def format_cache_product_response(cache_product) -> dict:
    data = _row_mapping(cache_product)
    if not data:
        return {}

    return _json_safe({
        "cache_id": data.get("id"),
        "name": data.get("product_name"),
        "barcode": data.get("barcode"),
        "brand": data.get("brand"),
        "category": data.get("category"),
        "description": data.get("description"),
        "ingredients": data.get("ingredients"),
        "nutrition_info": data.get("nutrition_info"),
        "storage_instruction": data.get("storage_instruction"),
        "image_url": data.get("image_url"),
        "external_source": data.get("external_source"),
        "external_source_url": data.get("external_source_url"),
    })


def build_not_found_response(query: str, query_type: str) -> dict:
    return {
        "status": "NOT_FOUND",
        "source": "NONE",
        "search_type": query_type,
        "result_count": 0,
        "query": query,
        "message": "Product was not found in the local database or external cache.",
        "suggested_action": "Create a new product master record.",
    }


def build_invalid_query_response(query: str) -> dict:
    return {
        "status": "INVALID_QUERY",
        "source": "NONE",
        "search_type": "UNKNOWN",
        "result_count": 0,
        "query": query,
        "message": "Query cannot be empty.",
    }


def log_product_lookup(
    db: Session,
    query_value: str,
    query_type: str,
    result_status: str,
    result_source: str | None,
    product_id: str | None = None,
    external_cache_id: str | None = None,
    request_source: str = "BACKEND_API",
    requested_by: str | None = None,
    response_payload: dict | None = None,
    error_message: str | None = None,
    lookup_duration_ms: int | None = None,
):
    sql = text("""
        INSERT INTO product_lookup_logs (
            query_value, query_type, result_status, result_source,
            product_id, external_cache_id, requested_by, request_source,
            response_payload, error_message, lookup_duration_ms
        ) VALUES (
            :query_value, :query_type, :result_status, :result_source,
            :product_id, :external_cache_id, :requested_by, :request_source,
            :response_payload, :error_message, :lookup_duration_ms
        )
    """).bindparams(bindparam("response_payload", type_=JSONB))

    db.execute(
        sql,
        {
            "query_value": query_value,
            "query_type": _log_query_type(query_type),
            "result_status": result_status,
            "result_source": result_source,
            "product_id": product_id,
            "external_cache_id": external_cache_id,
            "requested_by": requested_by,
            "request_source": _normalize_request_source(request_source),
            "response_payload": _json_safe(response_payload) if response_payload else None,
            "error_message": error_message,
            "lookup_duration_ms": lookup_duration_ms,
        },
    )
    db.commit()


def create_unknown_product_request(
    db: Session,
    query: str,
    query_type: str,
    request_source: str,
    requested_by: str | None = None,
):
    existing = db.execute(
        text("""
            SELECT id
            FROM unknown_product_requests
            WHERE query_value = :query
              AND query_type = :query_type
              AND status = 'PENDING'
            LIMIT 1
        """),
        {"query": query, "query_type": query_type},
    ).fetchone()

    if existing:
        return existing.id

    barcode = query if query_type == "BARCODE" else None
    product_name = query if query_type in ("PRODUCT_NAME", "SKU") else None

    row = db.execute(
        text("""
            INSERT INTO unknown_product_requests (
                query_value, query_type, barcode, product_name,
                request_source, requested_by, status
            ) VALUES (
                :query_value, :query_type, :barcode, :product_name,
                :request_source, :requested_by, 'PENDING'
            )
            RETURNING id
        """),
        {
            "query_value": query,
            "query_type": query_type,
            "barcode": barcode,
            "product_name": product_name,
            "request_source": _normalize_request_source(request_source),
            "requested_by": requested_by,
        },
    ).fetchone()
    db.commit()
    return row.id if row else None


def search_product_by_id(db: Session, product_id: str):
    return db.execute(
        text("SELECT * FROM products WHERE id = :product_id AND is_active = TRUE LIMIT 1"),
        {"product_id": product_id},
    ).fetchone()


def search_product_by_barcode(db: Session, barcode: str):
    return db.execute(
        text("""
            SELECT DISTINCT p.*
            FROM products p
            LEFT JOIN product_identifiers pi ON p.id = pi.product_id
            WHERE p.is_active = TRUE
              AND (p.barcode = :barcode OR pi.identifier_value = :barcode)
            LIMIT 1
        """),
        {"barcode": barcode},
    ).fetchone()


def search_product_by_sku(db: Session, sku: str):
    return db.execute(
        text("""
            SELECT DISTINCT p.*
            FROM products p
            LEFT JOIN product_identifiers pi ON p.id = pi.product_id
            WHERE p.is_active = TRUE
              AND (p.sku = :sku OR pi.identifier_value = :sku)
            LIMIT 1
        """),
        {"sku": sku},
    ).fetchone()


def search_product_by_name(db: Session, product_name: str):
    return db.execute(
        text("""
            SELECT *
            FROM products
            WHERE is_active = TRUE
              AND (
                name ILIKE '%' || :product_name || '%'
                OR brand ILIKE '%' || :product_name || '%'
                OR category ILIKE '%' || :product_name || '%'
              )
            ORDER BY
                CASE
                    WHEN LOWER(name) = LOWER(:product_name) THEN 1
                    WHEN LOWER(name) LIKE LOWER(:product_name) || '%' THEN 2
                    ELSE 3
                END,
                name
            LIMIT 10
        """),
        {"product_name": product_name},
    ).fetchall()


def search_external_cache(db: Session, query: str, query_type: str):
    if query_type in ("BARCODE", "SKU"):
        return db.execute(
            text("""
                SELECT *
                FROM external_product_cache
                WHERE cache_status = 'ACTIVE'
                  AND (barcode = :query OR query_value = :query)
                ORDER BY fetched_at DESC
                LIMIT 1
            """),
            {"query": query},
        ).fetchone()

    if query_type == "PRODUCT_NAME":
        return db.execute(
            text("""
                SELECT *
                FROM external_product_cache
                WHERE cache_status = 'ACTIVE'
                  AND (
                    product_name ILIKE '%' || :query || '%'
                    OR query_value ILIKE '%' || :query || '%'
                  )
                ORDER BY fetched_at DESC
                LIMIT 5
            """),
            {"query": query},
        ).fetchone()

    return None


def _found_response(query_type: str, product) -> dict:
    return {
        "status": "FOUND",
        "source": "LOCAL_DATABASE",
        "search_type": query_type,
        "result_count": 1,
        "product": format_local_product_response(product),
    }


def search_product(
    db: Session,
    query: str,
    request_source: str = "BACKEND_API",
    requested_by: str | None = None,
) -> dict:
    start_time = time.time()
    request_source = _normalize_request_source(request_source)
    cleaned = clean_query(query)

    if not cleaned:
        response = build_invalid_query_response(cleaned)
        log_product_lookup(
            db, cleaned, "UNKNOWN", "INVALID_QUERY", "NONE",
            request_source=request_source, requested_by=requested_by,
            response_payload=response, lookup_duration_ms=0,
        )
        return response

    query_type = detect_query_type(cleaned)

    try:
        if query_type == "PRODUCT_ID":
            product = search_product_by_id(db, cleaned)
            if product:
                response = _found_response(query_type, product)
                duration_ms = int((time.time() - start_time) * 1000)
                log_product_lookup(
                    db, cleaned, query_type, "FOUND", "LOCAL_DATABASE",
                    product_id=str(product.id), request_source=request_source,
                    requested_by=requested_by, response_payload=response,
                    lookup_duration_ms=duration_ms,
                )
                return response

        elif query_type == "BARCODE":
            product = search_product_by_barcode(db, cleaned)
            if product:
                response = _found_response(query_type, product)
                duration_ms = int((time.time() - start_time) * 1000)
                log_product_lookup(
                    db, cleaned, query_type, "FOUND", "LOCAL_DATABASE",
                    product_id=str(product.id), request_source=request_source,
                    requested_by=requested_by, response_payload=response,
                    lookup_duration_ms=duration_ms,
                )
                return response

        elif query_type == "SKU":
            product = search_product_by_sku(db, cleaned)
            if product:
                response = _found_response(query_type, product)
                duration_ms = int((time.time() - start_time) * 1000)
                log_product_lookup(
                    db, cleaned, query_type, "FOUND", "LOCAL_DATABASE",
                    product_id=str(product.id), request_source=request_source,
                    requested_by=requested_by, response_payload=response,
                    lookup_duration_ms=duration_ms,
                )
                return response

        elif query_type == "PRODUCT_NAME":
            products = search_product_by_name(db, cleaned)
            if products:
                if len(products) == 1:
                    response = _found_response(query_type, products[0])
                else:
                    response = {
                        "status": "FOUND",
                        "source": "LOCAL_DATABASE",
                        "search_type": query_type,
                        "result_count": len(products),
                        "products": [format_local_product_response(product) for product in products],
                    }
                duration_ms = int((time.time() - start_time) * 1000)
                log_product_lookup(
                    db, cleaned, query_type, "FOUND", "LOCAL_DATABASE",
                    product_id=str(products[0].id), request_source=request_source,
                    requested_by=requested_by, response_payload=response,
                    lookup_duration_ms=duration_ms,
                )
                return response

        cached = search_external_cache(db, cleaned, query_type)
        if cached:
            response = {
                "status": "FOUND",
                "source": "CACHE",
                "search_type": query_type,
                "result_count": 1,
                "product": format_cache_product_response(cached),
            }
            duration_ms = int((time.time() - start_time) * 1000)
            log_product_lookup(
                db, cleaned, query_type, "FOUND", "CACHE",
                external_cache_id=str(cached.id), request_source=request_source,
                requested_by=requested_by, response_payload=response,
                lookup_duration_ms=duration_ms,
            )
            return response

        response = build_not_found_response(cleaned, query_type)
        create_unknown_product_request(db, cleaned, query_type, request_source, requested_by)
        duration_ms = int((time.time() - start_time) * 1000)
        log_product_lookup(
            db, cleaned, query_type, "NOT_FOUND", "NONE",
            request_source=request_source, requested_by=requested_by,
            response_payload=response, lookup_duration_ms=duration_ms,
        )
        return response

    except Exception as exc:
        db.rollback()
        duration_ms = int((time.time() - start_time) * 1000)
        response = {
            "status": "ERROR",
            "source": "NONE",
            "search_type": query_type,
            "result_count": 0,
            "query": cleaned,
            "message": "Product lookup failed due to an internal error.",
        }
        try:
            log_product_lookup(
                db, cleaned, query_type, "ERROR", "NONE",
                request_source=request_source, requested_by=requested_by,
                response_payload=response, error_message=str(exc),
                lookup_duration_ms=duration_ms,
            )
        except Exception:
            db.rollback()
        return response
