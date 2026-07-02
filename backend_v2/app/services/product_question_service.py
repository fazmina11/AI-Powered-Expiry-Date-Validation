from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.schemas.product_question_schema import ProductQuestionRequest
from app.utils.query_detector import is_barcode_like, is_sku_like, is_uuid
from app.utils.question_intent_detector import (
    clean_question,
    detect_question_intent,
    extract_product_entity,
    is_question_valid,
)

VALID_REQUEST_SOURCES = {"BACKEND_API", "N8N", "TELEGRAM", "WEB_DASHBOARD"}
SUPPORTED_QUESTIONS = [
    "What is the expiry date of Amul Milk?",
    "Show ingredients of 8901262010011",
    "What is the batch number of Amul Milk?",
    "How should I store Amul Milk?",
    "Is Amul Milk expired?",
]


def _normalize_request_source(request_source: str | None) -> str:
    source = (request_source or "BACKEND_API").strip().upper()
    return source if source in VALID_REQUEST_SOURCES else "BACKEND_API"


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


def _row(row) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row._mapping)


def _product_summary(product) -> dict[str, Any]:
    data = _row(product) or {}
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


def _inventory_summary(item) -> dict[str, Any]:
    data = _row(item) or {}
    return _json_safe({
        "inventory_item_id": data.get("id"),
        "batch_number": data.get("batch_number"),
        "manufacturing_date": data.get("manufacturing_date"),
        "expiry_date": data.get("expiry_date"),
        "pipeline_status": data.get("pipeline_status"),
        "status_reason": data.get("status_reason"),
        "quantity": data.get("quantity"),
        "unit": data.get("unit"),
    })


def _response(status: str, intent: str, answer_type: str, answer: str, data: dict[str, Any] | None = None) -> dict:
    return {
        "status": status,
        "intent": intent,
        "answer_type": answer_type,
        "answer": answer,
        "data": _json_safe(data or {}),
    }


def resolve_product(db: Session, entity: str):
    entity = (entity or "").strip()
    if not entity:
        return None

    if is_uuid(entity):
        return db.execute(
            text("SELECT * FROM products WHERE id = :entity AND is_active = TRUE LIMIT 1"),
            {"entity": entity},
        ).fetchone()

    if is_barcode_like(entity):
        return db.execute(
            text("""
                SELECT DISTINCT p.*
                FROM products p
                LEFT JOIN product_identifiers pi ON p.id = pi.product_id
                WHERE p.is_active = TRUE
                  AND (p.barcode = :entity OR pi.identifier_value = :entity)
                LIMIT 1
            """),
            {"entity": entity},
        ).fetchone()

    if is_sku_like(entity):
        return db.execute(
            text("""
                SELECT *
                FROM products
                WHERE is_active = TRUE
                  AND sku = :entity
                LIMIT 1
            """),
            {"entity": entity},
        ).fetchone()

    return db.execute(
        text("""
            SELECT *
            FROM products
            WHERE is_active = TRUE
              AND (
                name ILIKE '%' || :entity || '%'
                OR brand ILIKE '%' || :entity || '%'
                OR category ILIKE '%' || :entity || '%'
                OR CONCAT_WS(' ', name, brand, category) ILIKE '%' || REPLACE(:entity, ' ', '%') || '%'
              )
            ORDER BY
              CASE
                WHEN LOWER(name) = LOWER(:entity) THEN 1
                WHEN LOWER(name) LIKE LOWER(:entity) || '%' THEN 2
                WHEN LOWER(name) LIKE '%' || LOWER(:entity) || '%' THEN 3
                WHEN LOWER(CONCAT_WS(' ', name, brand, category)) LIKE '%' || REPLACE(LOWER(:entity), ' ', '%') || '%' THEN 4
                ELSE 5
              END,
              name
            LIMIT 1
        """),
        {"entity": entity},
    ).fetchone()


def get_latest_inventory_items(db: Session, product_id: str, limit: int = 5):
    return db.execute(
        text("""
            SELECT *
            FROM inventory_items
            WHERE product_id = :product_id
            ORDER BY COALESCE(intake_at, created_at) DESC
            LIMIT :limit
        """),
        {"product_id": product_id, "limit": limit},
    ).fetchall()


def _first_inventory_with(items, field: str):
    for item in items:
        if _row(item).get(field) is not None:
            return item
    return None


def answer_product_details(db: Session, product) -> tuple[dict, str | None]:
    product_data = _product_summary(product)
    return (
        _response(
            "ANSWERED",
            "PRODUCT_DETAILS",
            "PRODUCT_DETAILS",
            f"Product details found for {product_data.get('name')}.",
            {"product": product_data},
        ),
        None,
    )


def answer_expiry_date(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    items = get_latest_inventory_items(db, str(product_data["id"]))
    item = _first_inventory_with(items, "expiry_date")
    if not item:
        return (
            _response(
                "NOT_FOUND",
                "EXPIRY_DATE",
                "EXPIRY_DATE",
                "Product was found, but no inventory record with expiry date is available.",
                {"product_name": product_data.get("name"), "expiry_date": None},
            ),
            None,
        )
    inv = _inventory_summary(item)
    return (
        _response(
            "ANSWERED",
            "EXPIRY_DATE",
            "EXPIRY_DATE",
            f"The latest expiry date for {product_data.get('name')} is {inv.get('expiry_date')}.",
            {
                "product_name": product_data.get("name"),
                "barcode": product_data.get("barcode"),
                "batch_number": inv.get("batch_number"),
                "expiry_date": inv.get("expiry_date"),
                "pipeline_status": inv.get("pipeline_status"),
            },
        ),
        str(inv.get("inventory_item_id")),
    )


def answer_mfg_date(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    items = get_latest_inventory_items(db, str(product_data["id"]))
    item = _first_inventory_with(items, "manufacturing_date")
    if not item:
        return (
            _response(
                "NOT_FOUND",
                "MFG_DATE",
                "MFG_DATE",
                "Product was found, but no inventory record with manufacturing date is available.",
                {"product_name": product_data.get("name"), "manufacturing_date": None},
            ),
            None,
        )
    inv = _inventory_summary(item)
    return (
        _response(
            "ANSWERED",
            "MFG_DATE",
            "MFG_DATE",
            f"The latest manufacturing date for {product_data.get('name')} is {inv.get('manufacturing_date')}.",
            {
                "product_name": product_data.get("name"),
                "batch_number": inv.get("batch_number"),
                "manufacturing_date": inv.get("manufacturing_date"),
                "pipeline_status": inv.get("pipeline_status"),
            },
        ),
        str(inv.get("inventory_item_id")),
    )


def answer_batch_number(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    items = get_latest_inventory_items(db, str(product_data["id"]))
    item = _first_inventory_with(items, "batch_number")
    if not item:
        return (
            _response(
                "NOT_FOUND",
                "BATCH_NUMBER",
                "BATCH_NUMBER",
                "Product was found, but no inventory record with batch number is available.",
                {"product_name": product_data.get("name"), "batch_number": None},
            ),
            None,
        )
    inv = _inventory_summary(item)
    return (
        _response(
            "ANSWERED",
            "BATCH_NUMBER",
            "BATCH_NUMBER",
            f"The latest batch number for {product_data.get('name')} is {inv.get('batch_number')}.",
            {
                "product_name": product_data.get("name"),
                "batch_number": inv.get("batch_number"),
                "manufacturing_date": inv.get("manufacturing_date"),
                "expiry_date": inv.get("expiry_date"),
            },
        ),
        str(inv.get("inventory_item_id")),
    )


def answer_ingredients(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    ingredients = product_data.get("ingredients")
    if not ingredients:
        return (
            _response(
                "NOT_FOUND",
                "INGREDIENTS",
                "INGREDIENTS",
                "Product was found, but ingredients information is not available.",
                {"product_name": product_data.get("name"), "ingredients": None},
            ),
            None,
        )
    return (
        _response(
            "ANSWERED",
            "INGREDIENTS",
            "INGREDIENTS",
            f"Ingredients for {product_data.get('name')}: {ingredients}.",
            {"product_name": product_data.get("name"), "ingredients": ingredients},
        ),
        None,
    )


def answer_nutrition(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    nutrition_info = product_data.get("nutrition_info")
    if not nutrition_info:
        return (
            _response(
                "NOT_FOUND",
                "NUTRITION",
                "NUTRITION",
                "Product was found, but nutrition information is not available.",
                {"product_name": product_data.get("name"), "nutrition_info": None},
            ),
            None,
        )
    return (
        _response(
            "ANSWERED",
            "NUTRITION",
            "NUTRITION",
            f"Nutrition information found for {product_data.get('name')}.",
            {"product_name": product_data.get("name"), "nutrition_info": nutrition_info},
        ),
        None,
    )


def answer_storage_instruction(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    storage_instruction = product_data.get("storage_instruction")
    if not storage_instruction:
        return (
            _response(
                "NOT_FOUND",
                "STORAGE_INSTRUCTION",
                "STORAGE_INSTRUCTION",
                "Product was found, but storage instruction is not available.",
                {"product_name": product_data.get("name"), "storage_instruction": None},
            ),
            None,
        )
    return (
        _response(
            "ANSWERED",
            "STORAGE_INSTRUCTION",
            "STORAGE_INSTRUCTION",
            f"Storage instruction for {product_data.get('name')}: {storage_instruction}.",
            {"product_name": product_data.get("name"), "storage_instruction": storage_instruction},
        ),
        None,
    )


def answer_product_status(db: Session, product) -> tuple[dict, str | None]:
    product_data = _row(product)
    items = get_latest_inventory_items(db, str(product_data["id"]))
    item = _first_inventory_with(items, "expiry_date")
    if not item:
        return (
            _response(
                "NOT_FOUND",
                "PRODUCT_STATUS",
                "PRODUCT_STATUS",
                "Product was found, but no inventory record with expiry date is available.",
                {"product_name": product_data.get("name"), "status": "UNKNOWN", "expiry_date": None},
            ),
            None,
        )
    inv = _inventory_summary(item)
    expiry_date = date.fromisoformat(inv["expiry_date"]) if isinstance(inv.get("expiry_date"), str) else _row(item).get("expiry_date")
    status = "EXPIRED" if expiry_date and expiry_date < date.today() else "NOT_EXPIRED"
    answer = (
        f"{product_data.get('name')} is expired. Latest expiry date is {inv.get('expiry_date')}."
        if status == "EXPIRED"
        else f"{product_data.get('name')} is not expired. Latest expiry date is {inv.get('expiry_date')}."
    )
    return (
        _response(
            "ANSWERED",
            "PRODUCT_STATUS",
            "PRODUCT_STATUS",
            answer,
            {
                "product_name": product_data.get("name"),
                "batch_number": inv.get("batch_number"),
                "expiry_date": inv.get("expiry_date"),
                "status": status,
                "pipeline_status": inv.get("pipeline_status"),
            },
        ),
        str(inv.get("inventory_item_id")),
    )


ANSWER_HANDLERS = {
    "PRODUCT_DETAILS": answer_product_details,
    "EXPIRY_DATE": answer_expiry_date,
    "MFG_DATE": answer_mfg_date,
    "BATCH_NUMBER": answer_batch_number,
    "INGREDIENTS": answer_ingredients,
    "NUTRITION": answer_nutrition,
    "STORAGE_INSTRUCTION": answer_storage_instruction,
    "PRODUCT_STATUS": answer_product_status,
}


def log_product_question(
    db: Session,
    question: str,
    detected_intent: str | None,
    extracted_entity: str | None,
    result_status: str,
    result_source: str | None,
    product_id: str | None = None,
    inventory_item_id: str | None = None,
    request_source: str = "BACKEND_API",
    requested_by: str | None = None,
    telegram_chat_id: str | None = None,
    telegram_user_id: str | None = None,
    n8n_execution_id: str | None = None,
    response_payload: dict | None = None,
    error_message: str | None = None,
):
    sql = text("""
        INSERT INTO product_question_logs (
            question, detected_intent, extracted_entity, result_status, result_source,
            product_id, inventory_item_id, request_source, requested_by,
            telegram_chat_id, telegram_user_id, n8n_execution_id,
            response_payload, error_message
        ) VALUES (
            :question, :detected_intent, :extracted_entity, :result_status, :result_source,
            :product_id, :inventory_item_id, :request_source, :requested_by,
            :telegram_chat_id, :telegram_user_id, :n8n_execution_id,
            :response_payload, :error_message
        )
    """).bindparams(bindparam("response_payload", type_=JSONB))

    db.execute(
        sql,
        {
            "question": question,
            "detected_intent": detected_intent,
            "extracted_entity": extracted_entity,
            "result_status": result_status,
            "result_source": result_source,
            "product_id": product_id,
            "inventory_item_id": inventory_item_id,
            "request_source": _normalize_request_source(request_source),
            "requested_by": requested_by,
            "telegram_chat_id": telegram_chat_id,
            "telegram_user_id": telegram_user_id,
            "n8n_execution_id": n8n_execution_id,
            "response_payload": _json_safe(response_payload) if response_payload else None,
            "error_message": error_message,
        },
    )
    db.commit()


def ask_product_question(db: Session, request: ProductQuestionRequest) -> dict:
    question = clean_question(request.question)
    request_source = _normalize_request_source(request.request_source)

    if not is_question_valid(question):
        response = _response(
            "INVALID_QUESTION",
            "UNKNOWN",
            "UNKNOWN",
            "Question cannot be empty.",
            {},
        )
        log_product_question(
            db, question, "UNKNOWN", None, "INVALID_QUESTION", "NONE",
            request_source=request_source, requested_by=request.requested_by,
            telegram_chat_id=request.telegram_chat_id,
            telegram_user_id=request.telegram_user_id,
            n8n_execution_id=request.n8n_execution_id,
            response_payload=response,
        )
        return response

    intent = detect_question_intent(question)
    entity = extract_product_entity(question, intent)

    try:
        if intent == "UNKNOWN":
            response = _response(
                "UNSUPPORTED_INTENT",
                "UNKNOWN",
                "UNKNOWN",
                "I can answer product details, expiry date, manufacturing date, batch number, ingredients, nutrition, storage instruction, and product status questions.",
                {"supported_questions": SUPPORTED_QUESTIONS},
            )
            log_product_question(
                db, question, intent, entity, "UNSUPPORTED_INTENT", "NONE",
                request_source=request_source, requested_by=request.requested_by,
                telegram_chat_id=request.telegram_chat_id,
                telegram_user_id=request.telegram_user_id,
                n8n_execution_id=request.n8n_execution_id,
                response_payload=response,
            )
            return response

        if not entity:
            response = _response(
                "NOT_FOUND",
                intent,
                intent,
                "I could not identify which product you are asking about.",
                {"entity": None},
            )
            log_product_question(
                db, question, intent, entity, "NOT_FOUND", "NONE",
                request_source=request_source, requested_by=request.requested_by,
                telegram_chat_id=request.telegram_chat_id,
                telegram_user_id=request.telegram_user_id,
                n8n_execution_id=request.n8n_execution_id,
                response_payload=response,
            )
            return response

        product = resolve_product(db, entity)
        if not product:
            response = _response(
                "NOT_FOUND",
                intent,
                intent,
                f"I could not find a matching product for '{entity}'.",
                {"entity": entity},
            )
            log_product_question(
                db, question, intent, entity, "NOT_FOUND", "NONE",
                request_source=request_source, requested_by=request.requested_by,
                telegram_chat_id=request.telegram_chat_id,
                telegram_user_id=request.telegram_user_id,
                n8n_execution_id=request.n8n_execution_id,
                response_payload=response,
            )
            return response

        response, inventory_item_id = ANSWER_HANDLERS[intent](db, product)
        product_id = str(_row(product).get("id"))
        log_product_question(
            db, question, intent, entity, response["status"],
            "LOCAL_DATABASE" if response["status"] == "ANSWERED" else "NONE",
            product_id=product_id,
            inventory_item_id=inventory_item_id,
            request_source=request_source,
            requested_by=request.requested_by,
            telegram_chat_id=request.telegram_chat_id,
            telegram_user_id=request.telegram_user_id,
            n8n_execution_id=request.n8n_execution_id,
            response_payload=response,
        )
        return response

    except Exception as exc:
        db.rollback()
        response = _response(
            "ERROR",
            intent or "UNKNOWN",
            intent or "UNKNOWN",
            "Product question answering failed due to an internal error.",
            {},
        )
        try:
            log_product_question(
                db, question, intent, entity, "ERROR", "NONE",
                request_source=request_source,
                requested_by=request.requested_by,
                telegram_chat_id=request.telegram_chat_id,
                telegram_user_id=request.telegram_user_id,
                n8n_execution_id=request.n8n_execution_id,
                response_payload=response,
                error_message=str(exc),
            )
        except Exception:
            db.rollback()
        return response
