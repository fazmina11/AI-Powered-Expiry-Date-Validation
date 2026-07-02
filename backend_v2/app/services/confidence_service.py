from typing import Optional
from app.schemas.enterprise_product_dto import EnterpriseProductDTO, ExtractedField
import re

class ConfidenceService:
    """
    Evaluates and calculates confidence scores for extracted product data fields.
    """

    def calculate_confidence(self, dto: EnterpriseProductDTO) -> EnterpriseProductDTO:
        """
        Calculates or recalculates confidence for all extracted fields in the DTO.
        Returns the updated DTO.
        """
        if dto.product.name:
            dto.product.name.confidence = self._eval_product_name(dto.product.name.value)
        if dto.product.brand:
            dto.product.brand.confidence = self._eval_brand(dto.product.brand.value)
        if dto.manufacturing.date:
            dto.manufacturing.date.confidence = self._eval_date(dto.manufacturing.date.value)
        if dto.expiry.date:
            dto.expiry.date.confidence = self._eval_date(dto.expiry.date.value)
        if dto.pricing.mrp:
            dto.pricing.mrp.confidence = self._eval_mrp(dto.pricing.mrp.value)
        if dto.batch.batch_number:
            dto.batch.batch_number.confidence = self._eval_batch(dto.batch.batch_number.value)

        # Calculate OCR completeness score based on how many expected fields were found
        expected_fields = [
            dto.product.name, dto.manufacturing.date, dto.expiry.date, 
            dto.pricing.mrp, dto.batch.batch_number
        ]
        found = sum(1 for field in expected_fields if field is not None)
        dto.ocr.completeness_score = round(found / len(expected_fields), 2) if expected_fields else 0.0

        return dto

    def _eval_product_name(self, value: str) -> float:
        if not value: return 0.0
        # If it's very short or just symbols, low confidence
        if len(value) < 4 or re.fullmatch(r'[\d\W_]+', value):
            return 0.3
        return 0.85

    def _eval_brand(self, value: str) -> float:
        if not value: return 0.0
        return 0.90 # Usually brand is extracted via strong heuristics/dictionaries

    def _eval_date(self, value: str) -> float:
        if not value: return 0.0
        # Check if it strictly matches a common date format
        if re.match(r'^\d{2}/\d{2}/\d{2,4}$', value) or re.match(r'^\d{2}-\d{2}-\d{2,4}$', value):
            return 0.95
        if re.match(r'^[A-Za-z]{3}\s*\d{4}$', value): # e.g. JAN 2024
            return 0.90
        return 0.75

    def _eval_mrp(self, value: str) -> float:
        if not value: return 0.0
        # Check if it's a valid float/integer
        try:
            float(re.sub(r'[^\d.]', '', value))
            return 0.95
        except ValueError:
            return 0.40

    def _eval_batch(self, value: str) -> float:
        if not value: return 0.0
        if len(value) > 3:
            return 0.90
        return 0.50
