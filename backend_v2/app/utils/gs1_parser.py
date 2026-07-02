import re
from datetime import datetime, date
from typing import Optional, Dict

class GS1Barcode:
    def __init__(self):
        self.is_gs1 = False
        self.gtin = None
        self.manufacturing_date = None
        self.expiry_date = None
        self.best_before_date = None
        self.batch_number = None
        self.lot_number = None
        self.serial_number = None
        self.raw_ais: Dict[str, str] = {}

def parse_gs1_date(yy_mm_dd: str) -> Optional[date]:
    """Helper to convert GS1 YYMMDD string to date object."""
    if not yy_mm_dd or len(yy_mm_dd) != 6 or not yy_mm_dd.isdigit():
        return None
    try:
        yy = int(yy_mm_dd[0:2])
        mm = int(yy_mm_dd[2:4])
        dd = int(yy_mm_dd[4:6])
        year = 2000 + yy if yy <= 50 else 1900 + yy
        if dd == 0:
            dd = 1
        return date(year, mm, dd)
    except (ValueError, TypeError):
        return None

def parse_gs1_barcode(barcode: str) -> GS1Barcode:
    result = GS1Barcode()
    if not barcode:
        return result
        
    # Check if format has AI brackets like (01)08901058850817(17)260630(10)LOT
    if barcode.startswith("("):
        pattern = re.findall(r'\((\d{2,4})\)([^(]+)', barcode)
        if pattern:
            result.is_gs1 = True
            ais = {ai: val.strip() for ai, val in pattern}
            result.raw_ais = ais
            
            result.gtin = ais.get("01")
            result.batch_number = ais.get("10")
            result.lot_number = ais.get("10")
            result.serial_number = ais.get("21")
            
            result.manufacturing_date = parse_gs1_date(ais.get("11"))
            result.expiry_date = parse_gs1_date(ais.get("17"))
            result.best_before_date = parse_gs1_date(ais.get("15"))
            
    return result
