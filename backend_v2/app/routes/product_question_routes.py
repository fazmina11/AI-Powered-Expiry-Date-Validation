from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product_question_schema import ProductQuestionRequest, ProductQuestionResponse
from app.services.product_question_service import ask_product_question

router = APIRouter()


@router.post("/products/ask", response_model=ProductQuestionResponse)
def ask_product_question_route(
    request: ProductQuestionRequest,
    db: Session = Depends(get_db),
):
    return ask_product_question(db=db, request=request)
