from typing import Any, Optional
from datetime import datetime
from app.schemas.validation_schema import ValidationResult, CategoryValidation, ValidationStatus
from app.schemas.product_intelligence_schema import ProductIntelligence

class ValidationService:
    def validate_product(self, profile: ProductIntelligence) -> ValidationResult:
        """
        Validate the complete ProductIntelligence profile and return structured results.
        Never raises exceptions, always returns a ValidationResult.
        """
        if not isinstance(profile, ProductIntelligence):
            return self._build_default_error_result("Invalid input type provided to validation engine")
            
        mfg_date_str = None
        if profile.manufacturing and getattr(profile.manufacturing, 'manufacturing_date', None):
            mfg_date_str = profile.manufacturing.manufacturing_date
        elif profile.ocr and getattr(profile.ocr, 'detected_fields', None):
            mfg_date_str = profile.ocr.detected_fields.get('mfg_date')

            
        barcode_val = self._validate_barcode(profile.barcode)
        product_val = self._validate_product(profile.product)
        mfg_val = self._validate_manufacturing(mfg_date_str)
        expiry_val = self._validate_expiry(profile.expiry, mfg_date_str)
        pricing_val = self._validate_pricing(profile.pricing)
        ocr_val = self._validate_ocr(profile.ocr)
        
        # Calculate overall score and status
        categories = [barcode_val, product_val, mfg_val, expiry_val, pricing_val, ocr_val]
        total_score = sum(c.score for c in categories)
        overall_score = total_score // len(categories)
        
        has_error = any(c.status == ValidationStatus.ERROR for c in categories)
        has_warning = any(c.status == ValidationStatus.WARNING for c in categories)
        
        overall_status = ValidationStatus.ERROR if has_error else (ValidationStatus.WARNING if has_warning else ValidationStatus.VALID)
        
        return ValidationResult(
            overall_score=overall_score,
            overall_status=overall_status,
            barcode=barcode_val,
            product=product_val,
            manufacturing=mfg_val,
            expiry=expiry_val,
            pricing=pricing_val,
            ocr=ocr_val
        )

    def _validate_barcode(self, barcode) -> CategoryValidation:
        if not barcode or not barcode.value:
            return CategoryValidation(status=ValidationStatus.ERROR, score=0, message="Barcode is missing")
            
        if barcode.checksum_valid is False:
            return CategoryValidation(status=ValidationStatus.ERROR, score=0, message="Checksum is invalid")
            
        score = 25
        messages = []
        
        if barcode.barcode_type == "EAN-13":
            score += 25
        else:
            messages.append("Barcode type is not standard EAN-13")
            
        if barcode.value and len(barcode.value) == 13:
            score += 25
        else:
            messages.append("Barcode length invalid")
            
        if barcode.country_prefix and barcode.country:
            score += 25
        else:
            messages.append("Unknown country prefix")
            
        if score == 100:
            return CategoryValidation(status=ValidationStatus.VALID, score=100, message="Barcode is valid")
        return CategoryValidation(status=ValidationStatus.WARNING, score=score, message=", ".join(messages))

    def _validate_product(self, product) -> CategoryValidation:
        if not product or not product.name:
            return CategoryValidation(status=ValidationStatus.ERROR, score=0, message="Product not found in lookup")
            
        score = 34
        messages = []
        if product.brand:
            score += 33
        else:
            messages.append("Missing brand")
            
        if product.category:
            score += 33
        else:
            messages.append("Missing category")
            
        if score == 100:
            return CategoryValidation(status=ValidationStatus.VALID, score=100, message="Product data complete")
        return CategoryValidation(status=ValidationStatus.WARNING, score=score, message=", ".join(messages))

    def _validate_manufacturing(self, mfg_date_str: Optional[str]) -> CategoryValidation:
        if not mfg_date_str:
            return CategoryValidation(status=ValidationStatus.WARNING, score=0, message="Manufacturing date missing")
            
        try:
            mfg_date = self._parse_date(mfg_date_str)
            if not mfg_date:
                return CategoryValidation(status=ValidationStatus.ERROR, score=25, message="Invalid manufacturing date format")
                
            if mfg_date > datetime.now():
                return CategoryValidation(status=ValidationStatus.ERROR, score=50, message="Manufacturing date cannot be in the future")
                
            return CategoryValidation(status=ValidationStatus.VALID, score=100, message="Manufacturing date valid")
        except Exception:
            return CategoryValidation(status=ValidationStatus.ERROR, score=25, message="Invalid manufacturing date format")

    def _validate_expiry(self, expiry, mfg_date_str: Optional[str] = None) -> CategoryValidation:
        if not expiry or not expiry.expiry_date:
            return CategoryValidation(status=ValidationStatus.ERROR, score=0, message="Expiry date missing")
            
        expiry_date = self._parse_date(expiry.expiry_date)
        if not expiry_date:
            return CategoryValidation(status=ValidationStatus.ERROR, score=25, message="Invalid expiry date format")
            
        if mfg_date_str:
            mfg_date = self._parse_date(mfg_date_str)
            if mfg_date and expiry_date <= mfg_date:
                return CategoryValidation(status=ValidationStatus.ERROR, score=50, message="Expiry date must be after manufacturing date")
                
        return CategoryValidation(status=ValidationStatus.VALID, score=100, message="Expiry date valid")
        
    def _validate_pricing(self, pricing) -> CategoryValidation:
        if not pricing or pricing.price is None:
            return CategoryValidation(status=ValidationStatus.WARNING, score=0, message="Pricing missing")
            
        try:
            price = float(pricing.price)
            if price <= 0:
                return CategoryValidation(status=ValidationStatus.ERROR, score=50, message="Pricing must be greater than zero")
            return CategoryValidation(status=ValidationStatus.VALID, score=100, message="Pricing valid")
        except (ValueError, TypeError):
            return CategoryValidation(status=ValidationStatus.ERROR, score=25, message="Pricing must be numeric")

    def _validate_ocr(self, ocr) -> CategoryValidation:
        if not ocr or not ocr.raw_text:
            return CategoryValidation(status=ValidationStatus.ERROR, score=0, message="OCR data missing")
            
        score = 50
        messages = []
        if ocr.confidence and ocr.confidence >= 0.8:
            score += 25
        else:
            messages.append("Low OCR confidence")
            
        if getattr(ocr, 'detected_fields', None):
            score += 25
        else:
            messages.append("No required fields detected")
            
        if score == 100:
            return CategoryValidation(status=ValidationStatus.VALID, score=100, message="OCR data high quality")
        
        status = ValidationStatus.ERROR if score < 75 else ValidationStatus.WARNING
        return CategoryValidation(status=status, score=score, message=", ".join(messages))

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m", "%b %Y", "%m/%y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
        
    def _build_default_error_result(self, msg: str) -> ValidationResult:
        err = CategoryValidation(status=ValidationStatus.ERROR, score=0, message=msg)
        return ValidationResult(
            overall_score=0,
            overall_status=ValidationStatus.ERROR,
            barcode=err, product=err, manufacturing=err, expiry=err, pricing=err, ocr=err
        )
