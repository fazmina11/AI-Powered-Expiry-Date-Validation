from datetime import datetime, timezone
from app.schemas.barcode_intelligence_schema import BarcodeIntelligence
from app.utils.gs1_country_codes import get_country_from_prefix
from app.utils.gs1_parser import parse_gs1_barcode
import logging
import re

logger = logging.getLogger(__name__)


class BarcodeIntelligenceService:

    @staticmethod
    def _calculate_ean13_checksum(barcode: str) -> int:
        """
        Calculate EAN-13 checksum.
        Algorithm:
        1. Multiply every alternating digit starting from the rightmost (excluding check digit) by 3 and 1.
        2. Sum them up.
        3. Check digit is (10 - (sum % 10)) % 10.
        """
        digits = [int(d) for d in barcode[:-1]]
        total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
        return (10 - (total % 10)) % 10

    def parse_barcode(self, barcode: str) -> BarcodeIntelligence:
        """
        Parse and validate a barcode string, returning structured intelligence.

        Handles:
          - EAN-13 / EAN-8 / UPC-A / GTIN-14 (numeric only)
          - GS1-128 / DataMatrix / QR Code with embedded Application Identifiers
            e.g. (01)08901234567890(17)270101(11)250115(10)LOT123
          - Plain QR / Code128 text strings
        """
        if not barcode:
            raise ValueError("Barcode cannot be empty")

        barcode = barcode.strip()
        length = len(barcode)

        # ── GS1 Application Identifier parsing (runs on ALL barcode types) ──────
        # Runs BEFORE the numeric-only path so QR/DataMatrix dates are captured.
        gs1 = parse_gs1_barcode(barcode)

        if gs1.is_gs1:
            # GS1 structured barcode (DataMatrix, QR, GS1-128, etc.)
            logger.info("[BarcodeIntel] GS1 barcode detected. AIs: %s", list(gs1.raw_ais.keys()))
            gtin = gs1.gtin or barcode
            return BarcodeIntelligence(
                value=barcode,
                barcode_type="GS1",
                length=length,
                country_prefix=gtin[1:4] if gtin and len(gtin) >= 4 else None,
                country=get_country_from_prefix(gtin[1:4]) if gtin and len(gtin) >= 4 else None,
                manufacturer_code=gtin[4:8] if gtin and len(gtin) >= 8 else None,
                product_code=gtin[8:13] if gtin and len(gtin) >= 13 else None,
                check_digit=int(gtin[-1]) if gtin and gtin[-1].isdigit() else None,
                checksum_valid=True,
                scan_timestamp=datetime.now(timezone.utc),
                is_gs1_barcode=True,
                gtin=gs1.gtin,
                manufacturing_date=gs1.manufacturing_date,
                expiry_date=gs1.expiry_date,
                best_before_date=gs1.best_before_date,
                batch_number=gs1.batch_number,
                lot_number=gs1.lot_number,
                serial_number=gs1.serial_number,
            )

        # ── Non-numeric plain barcode (QR text, Code39, etc.) ───────────────────
        if not barcode.isdigit():
            logger.info("[BarcodeIntel] Non-numeric plain barcode: %s", barcode[:30])
            return BarcodeIntelligence(
                value=barcode,
                barcode_type="UNKNOWN",
                length=length,
                checksum_valid=False,
                scan_timestamp=datetime.now(timezone.utc),
            )

        # ── Numeric-only path: EAN-13, EAN-8, UPC-A, GTIN-14 ───────────────────
        if length == 13:
            barcode_type = "EAN-13"
            prefix = barcode[0:3]
            country = get_country_from_prefix(prefix)
            manufacturer = barcode[3:7]
            product = barcode[7:12]
            check_digit = int(barcode[12])
            is_valid = (check_digit == self._calculate_ean13_checksum(barcode))
        elif length == 8:
            barcode_type = "EAN-8"
            prefix = barcode[0:3]
            country = get_country_from_prefix(prefix)
            manufacturer = None
            product = barcode[3:7]
            check_digit = int(barcode[7])
            is_valid = True
        elif length == 12:
            barcode_type = "UPC-A"
            prefix = barcode[0:1]
            country = "United States"
            manufacturer = barcode[1:6]
            product = barcode[6:11]
            check_digit = int(barcode[11])
            is_valid = True
        elif length == 14:
            barcode_type = "GTIN-14"
            prefix = barcode[1:4]
            country = get_country_from_prefix(prefix)
            manufacturer = barcode[4:8]
            product = barcode[8:13]
            check_digit = int(barcode[13])
            is_valid = True
        else:
            barcode_type = f"NUMERIC-{length}"
            prefix = barcode[0:3] if length >= 3 else None
            country = get_country_from_prefix(prefix) if prefix else None
            manufacturer = None
            product = None
            check_digit = None
            is_valid = False

        logger.info("[BarcodeIntel] Parsed %s: valid=%s", barcode_type, is_valid)

        return BarcodeIntelligence(
            value=barcode,
            barcode_type=barcode_type,
            length=length,
            country_prefix=prefix if length >= 3 else None,
            country=country,
            manufacturer_code=manufacturer,
            product_code=product,
            check_digit=check_digit,
            checksum_valid=is_valid,
            scan_timestamp=datetime.now(timezone.utc),
            # GS1 date fields (None for plain numeric EAN barcodes)
            is_gs1_barcode=False,
            gtin=None,
            manufacturing_date=None,
            expiry_date=None,
            best_before_date=None,
            batch_number=None,
            lot_number=None,
            serial_number=None,
        )
