import os
import sys
import logging
import base64
import re
import math
from typing import List, Optional, Dict, Any, Tuple
import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, date

# Reconfigure standard output/error to use UTF-8 (Windows Unicode fix)
for stream in [sys.stdout, sys.stderr]:
    if hasattr(stream, 'reconfigure'):
        try:
            stream.reconfigure(encoding='utf-8')
        except Exception:
            pass

# Add parent directory to path and load environment variables
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.services.enhanced_ocr_pipeline import EnhancedOCRPipeline
from app.services.barcode_service import BarcodeService
from app.services.barcode_intelligence_service import BarcodeIntelligenceService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Powered Expiry Validation Web Scanner")
pipeline = EnhancedOCRPipeline()
barcode_service = BarcodeService()
barcode_intel_service = BarcodeIntelligenceService()

SUPPLIER_LOOKUP = {
    "1234": "A", "5678": "B", "9012": "C", "3456": "D",
    "0412": "A", "007": "A", "8901": "A", "1058": "A", "6081": "A",
}

# ── Field classification colors (BGR for OpenCV) ─────────────────────────────
FIELD_COLORS = {
    "MFG":         (0, 200, 100),
    "EXP":         (0, 80, 255),
    "BATCH":       (255, 180, 0),
    "MRP":         (0, 255, 255),
    "BARCODE":     (255, 100, 255),
    "INGREDIENTS": (100, 255, 100),
    "PRODUCT":     (255, 200, 100),
    "WEIGHT":      (180, 180, 255),
    "DATE":        (100, 200, 255),
    "FSSAI":       (200, 200, 200),
}


class ScanResult(BaseModel):
    filename: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    mfg_date: Optional[str] = None
    expiry_date: Optional[str] = None
    printed_shelf_life_days: Optional[int] = None
    days_since_manufacture: Optional[int] = None
    batch_number: Optional[str] = None
    ingredients: Optional[str] = None
    mrp: Optional[float] = None
    weight: Optional[str] = None
    barcode: Optional[str] = None
    barcode_type: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_grade: str = "C"
    confidence: float = 0.0
    used_vision_llm: bool = False
    success: bool = False
    error: Optional[str] = None
    annotated_image_b64: Optional[str] = None
    raw_ocr_text: Optional[str] = None


# ── Smart OCR Box Classification & Extraction ────────────────────────────────

def classify_box(text: str) -> str:
    """Classify OCR text into a field type."""
    t = text.upper().strip()
    if re.search(r'\b(MFG|MFD|MANUFACTURED|PKD|PACKED)\b', t):
        return "MFG"
    if re.search(r'\b(EXP|EXPIRY|USE\s*BY|BEST\s*BEFORE|BB)\b', t):
        return "EXP"
    if re.search(r'\b(BATCH|LOT|B\.?\s*NO)\b', t):
        return "BATCH"
    if re.search(r'\b(MRP|RS\.?|PRICE)\b', t) or re.search(r'₹', t):
        return "MRP"
    if re.search(r'\b(INGREDIENTS?|CONTAINS?)\b', t):
        return "INGREDIENTS"
    if re.search(r'\b(FSSAI|LIC\.?\s*NO|FSAT)\b', t):
        return "FSSAI"
    if re.search(r'\b\d+\s*(g|gm|gms|kg|ml|l|ltr|oz)\b', t, re.IGNORECASE):
        return "WEIGHT"
    if re.search(r'\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}', t):
        return "DATE"
    if re.search(r'\b(Rs\.?\s*\d)', t, re.IGNORECASE):
        return "MRP"
    return ""


def box_center(box):
    """Get center point of a bounding box."""
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def box_distance(box1, box2):
    """Distance between two box centers."""
    c1 = box_center(box1)
    c2 = box_center(box2)
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)


def parse_date_dmyy(text: str) -> Optional[str]:
    """Parse dates in DD/MM/YY or DD/MM/YYYY format → YYYY-MM-DD."""
    # Try DD/MM/YYYY first
    m = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= d <= 31 and 1 <= mo <= 12:
            try:
                return datetime(y, mo, d).strftime('%Y-%m-%d')
            except ValueError:
                pass
    # Try DD/MM/YY
    m = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})', text)
    if m:
        d, mo, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = 2000 + yy if yy < 50 else 1900 + yy
        if 1 <= d <= 31 and 1 <= mo <= 12:
            try:
                return datetime(y, mo, d).strftime('%Y-%m-%d')
            except ValueError:
                pass
    return None


def parse_mrp(text: str) -> Optional[float]:
    """Extract MRP value from text like 'Rs.50.00' or 'MRP 50.00'."""
    m = re.search(r'(?:Rs\.?|MRP|₹)\s*(\d+(?:\.\d{1,2})?)', text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    # Try standalone number with decimal
    m = re.search(r'\b(\d+\.\d{2})\b', text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def parse_weight(text: str) -> Optional[str]:
    """Extract weight from text like '200 g' or '500ml'."""
    m = re.search(r'(\d+(?:\.\d+)?)\s*(g|gm|gms|kg|ml|l|ltr|oz)\b', text, re.IGNORECASE)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return None


def extract_fields_from_ocr_boxes(ocr_boxes: list) -> dict:
    """
    Smart extraction: Use classified OCR boxes and spatial proximity 
    to map text to structured fields.
    """
    fields = {
        'mfg_date': None, 'expiry_date': None, 'batch_number': None,
        'mrp': None, 'weight': None, 'product_name': None,
        'ingredients': None, 'raw_text': '',
    }
    
    # Sort boxes top-to-bottom, left-to-right for reading order
    sorted_boxes = sorted(ocr_boxes, key=lambda b: (box_center(b['box'])[1], box_center(b['box'])[0]))
    
    # Collect raw text
    fields['raw_text'] = ' '.join(b['text'] for b in sorted_boxes)
    
    # Index boxes by type
    mfg_keywords = []
    exp_keywords = []
    date_boxes = []
    batch_keywords = []
    mrp_boxes = []
    weight_boxes = []
    ingredient_keyword = []
    product_texts = []
    
    for b in sorted_boxes:
        ft = b['field_type']
        text = b['text'].strip()
        if ft == 'MFG':
            mfg_keywords.append(b)
            # Check if the MFG box itself contains a date
            d = parse_date_dmyy(text)
            if d:
                date_boxes.append(b)
        elif ft == 'EXP':
            exp_keywords.append(b)
            d = parse_date_dmyy(text)
            if d:
                date_boxes.append(b)
        elif ft == 'DATE':
            date_boxes.append(b)
        elif ft == 'BATCH':
            batch_keywords.append(b)
        elif ft == 'MRP':
            mrp_boxes.append(b)
        elif ft == 'WEIGHT':
            weight_boxes.append(b)
        elif ft == 'INGREDIENTS':
            ingredient_keyword.append(b)
    
    # ── Extract dates via spatial proximity ────────────────────────────
    all_date_strings = []
    for db in date_boxes:
        d = parse_date_dmyy(db['text'])
        if d:
            all_date_strings.append({'date_str': d, 'box': db['box'], 'text': db['text']})
    
    # Try to associate dates with MFG/EXP keywords by proximity
    if mfg_keywords and all_date_strings:
        closest = min(all_date_strings, key=lambda d: box_distance(mfg_keywords[0]['box'], d['box']))
        fields['mfg_date'] = closest['date_str']
    
    if exp_keywords and all_date_strings:
        closest = min(all_date_strings, key=lambda d: box_distance(exp_keywords[0]['box'], d['box']))
        # Don't pick the same date as MFG if we have multiple
        if fields['mfg_date'] == closest['date_str'] and len(all_date_strings) > 1:
            remaining = [d for d in all_date_strings if d['date_str'] != fields['mfg_date']]
            if remaining:
                closest = min(remaining, key=lambda d: box_distance(exp_keywords[0]['box'], d['box']))
        fields['expiry_date'] = closest['date_str']
    
    # Fallback: if no keywords found but dates exist, earliest=MFG, latest=EXP
    if not fields['mfg_date'] and not fields['expiry_date'] and len(all_date_strings) >= 2:
        sorted_dates = sorted(all_date_strings, key=lambda d: d['date_str'])
        fields['mfg_date'] = sorted_dates[0]['date_str']
        fields['expiry_date'] = sorted_dates[-1]['date_str']
    elif not fields['mfg_date'] and not fields['expiry_date'] and len(all_date_strings) == 1:
        fields['expiry_date'] = all_date_strings[0]['date_str']
    
    # Ensure MFG < EXP
    if fields['mfg_date'] and fields['expiry_date'] and fields['mfg_date'] > fields['expiry_date']:
        fields['mfg_date'], fields['expiry_date'] = fields['expiry_date'], fields['mfg_date']
    
    # ── Extract MRP ────────────────────────────────────────────────────
    for mb in mrp_boxes:
        mrp_val = parse_mrp(mb['text'])
        if mrp_val:
            fields['mrp'] = mrp_val
            break
    
    # ── Extract Weight ─────────────────────────────────────────────────
    for wb in weight_boxes:
        w = parse_weight(wb['text'])
        if w:
            fields['weight'] = w
            break
    
    # ── Extract Batch ──────────────────────────────────────────────────
    if batch_keywords:
        # Look for text near the BATCH keyword
        for bk in batch_keywords:
            # Check the keyword box itself for a number
            m = re.search(r'[A-Z]?\d{4,}', bk['text'], re.IGNORECASE)
            if m:
                fields['batch_number'] = m.group(0)
                break
            # Find nearest text box that looks like a batch code
            nearby = sorted(sorted_boxes, key=lambda b: box_distance(bk['box'], b['box']))
            for nb in nearby[1:5]:
                if re.match(r'^[A-Z0-9\-/]{3,15}$', nb['text'].strip(), re.IGNORECASE):
                    if nb['field_type'] not in ('MFG', 'EXP', 'MRP', 'WEIGHT', 'DATE', 'FSSAI'):
                        fields['batch_number'] = nb['text'].strip()
                        break
            if fields['batch_number']:
                break
    
    # ── Extract product name from brand-like text ──────────────────────
    # Look for product/brand text (usually large text at top) or company name
    for b in sorted_boxes:
        t = b['text'].strip()
        if re.search(r'\b(BRITANNIA|HAPPILO|PARLE|AMUL|NESTLÉ?|NESTLE|HALDIRAM|MTR|ITC|TATA|CADBURY|DAIRY\s*MILK)\b', t, re.IGNORECASE):
            product_texts.append(t)
            break
    # Also look for product description
    for b in sorted_boxes:
        t = b['text'].strip()
        if re.search(r'\b(BISCUITS?|COOKIES?|BREAD|CAKE|MILK|BUTTER|CHEESE|CHIPS?|NOODLES?|DATES?|NUTS?|CHOCOLATE)\b', t, re.IGNORECASE):
            product_texts.append(t)
            break
    if product_texts:
        fields['product_name'] = ' '.join(dict.fromkeys(product_texts))  # deduplicate while keeping order
    
    # ── Extract ingredients ────────────────────────────────────────────
    if ingredient_keyword:
        # Gather text from ingredient keyword box and nearby boxes below it
        ik = ingredient_keyword[0]
        ik_center = box_center(ik['box'])
        ing_texts = [ik['text']]
        for b in sorted_boxes:
            bc = box_center(b['box'])
            # Below the ingredient keyword and close horizontally
            if bc[1] > ik_center[1] and abs(bc[0] - ik_center[0]) < 300 and bc[1] - ik_center[1] < 100:
                if b['field_type'] not in ('MFG', 'EXP', 'MRP', 'BATCH', 'DATE', 'WEIGHT', 'FSSAI'):
                    ing_texts.append(b['text'])
        combined = ' '.join(ing_texts)
        # Clean up: remove the "INGREDIENTS:" prefix
        combined = re.sub(r'^.*?INGREDIENTS?\s*[:\-]?\s*', '', combined, flags=re.IGNORECASE).strip()
        if combined:
            fields['ingredients'] = combined
    
    return fields


def run_easyocr_once(image: np.ndarray) -> Tuple[list, str]:
    """
    Run EasyOCR ONCE on the image. Returns:
    - list of classified boxes (text, confidence, field_type, box)
    - concatenated raw text
    """
    ocr_boxes = []
    raw_texts = []
    
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        results = reader.readtext(image)
        
        for (box, text, conf) in results:
            if not text.strip() or conf < 0.15:
                continue
            field_type = classify_box(text)
            ocr_boxes.append({
                'text': text.strip(),
                'confidence': round(conf, 3),
                'field_type': field_type or 'TEXT',
                'box': [[int(p[0]), int(p[1])] for p in box],
            })
            raw_texts.append(text.strip())
    except Exception as e:
        logger.error(f"EasyOCR failed: {e}")
    
    return ocr_boxes, '\n'.join(raw_texts)


def draw_annotations(image: np.ndarray, ocr_boxes: list, barcode_res: dict = None) -> str:
    """
    Draw color-coded bounding boxes on the image and return as base64 JPEG.
    """
    annotated = image.copy()
    
    for b in ocr_boxes:
        ft = b['field_type']
        color = FIELD_COLORS.get(ft, (150, 150, 150))
        pts = np.array(b['box'], dtype=np.int32)
        cv2.polylines(annotated, [pts], isClosed=True, color=color, thickness=2)
        
        x_min = min(p[0] for p in b['box'])
        y_min = min(p[1] for p in b['box'])
        label = f"{ft}: {b['text'][:35]}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.rectangle(annotated, (x_min, y_min - th - 6), (x_min + tw + 4, y_min), color, -1)
        cv2.putText(annotated, label, (x_min + 2, y_min - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    
    # Draw barcode box
    if barcode_res and barcode_res.get("points"):
        color = FIELD_COLORS["BARCODE"]
        pts = np.array(barcode_res["points"], dtype=np.int32)
        cv2.polylines(annotated, [pts], isClosed=True, color=color, thickness=3)
        x_min = int(min(p[0] for p in barcode_res["points"]))
        y_min = int(min(p[1] for p in barcode_res["points"]))
        label = f"BARCODE: {barcode_res.get('barcode', '')}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x_min, y_min - th - 8), (x_min + tw + 6, y_min), color, -1)
        cv2.putText(annotated, label, (x_min + 3, y_min - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    
    _, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buffer).decode('utf-8')


# ── Main Scan Endpoint ────────────────────────────────────────────────────────

@app.post("/scan", response_model=List[ScanResult])
async def scan_images(files: List[UploadFile] = File(...)):
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files can be uploaded at once")
    
    results = []
    
    for file in files:
        filename = file.filename
        try:
            logger.info(f"Processing uploaded file: {filename}")
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                results.append(ScanResult(filename=filename, error="Invalid image format or corrupt file"))
                continue
            
            # ── Step 1: Barcode detection ──────────────────────────────────
            supplier_id = None
            supplier_grade = "C"
            barcode_val = None
            barcode_type = None
            barcode_res = barcode_service.detect(frame)
            if barcode_res and barcode_res.get("barcode"):
                barcode_val = barcode_res["barcode"]
                barcode_type = barcode_res.get("barcode_type")
                try:
                    intel = barcode_intel_service.parse_barcode(barcode_val)
                    if intel:
                        supplier_id = intel.manufacturer_code
                        if supplier_id:
                            supplier_grade = SUPPLIER_LOOKUP.get(supplier_id, "C")
                except Exception as e:
                    logger.warning(f"Barcode parsing failed: {e}")
            
            # ── Step 2: Run EasyOCR ONCE (for both annotation + extraction)
            ocr_boxes, raw_text = run_easyocr_once(frame)
            logger.info(f"EasyOCR detected {len(ocr_boxes)} text boxes")
            
            # ── Step 3: Smart field extraction from OCR boxes ──────────────
            local_fields = extract_fields_from_ocr_boxes(ocr_boxes)
            
            # ── Step 4: Try Vision LLM for enhanced extraction (optional) ──
            llm_result = None
            used_llm = False
            try:
                llm_result = pipeline._try_vision_llm(frame, None)
                if llm_result and llm_result.confidence > 0.5:
                    used_llm = True
                    logger.info("Vision LLM succeeded, merging results")
                else:
                    llm_result = None
            except Exception as e:
                logger.warning(f"Vision LLM failed: {e}")
            
            # ── Step 5: Merge results (LLM takes priority, local fills gaps)
            final_mfg = None
            final_exp = None
            final_batch = None
            final_ingredients = None
            final_product = None
            final_category = None
            final_mrp = None
            final_weight = None
            final_confidence = 0.0
            
            if llm_result:
                final_mfg = llm_result.mfg_date or local_fields.get('mfg_date')
                final_exp = llm_result.expiry_date or local_fields.get('expiry_date')
                final_batch = llm_result.batch_number or local_fields.get('batch_number')
                final_ingredients = llm_result.ingredients or local_fields.get('ingredients')
                final_product = llm_result.product_name or local_fields.get('product_name')
                final_category = llm_result.category
                final_mrp = llm_result.mrp or local_fields.get('mrp')
                final_weight = llm_result.weight or local_fields.get('weight')
                final_confidence = llm_result.confidence
            else:
                final_mfg = local_fields.get('mfg_date')
                final_exp = local_fields.get('expiry_date')
                final_batch = local_fields.get('batch_number')
                final_ingredients = local_fields.get('ingredients')
                final_product = local_fields.get('product_name')
                final_mrp = local_fields.get('mrp')
                final_weight = local_fields.get('weight')
                # Compute confidence from what we found locally
                score = 0.0
                if final_mfg: score += 0.25
                if final_exp: score += 0.25
                if final_batch: score += 0.1
                if final_mrp: score += 0.1
                if final_weight: score += 0.1
                if final_product: score += 0.1
                if final_ingredients: score += 0.1
                final_confidence = min(score, 1.0)
            
            # ── Step 6: Draw annotation image ─────────────────────────────
            annotated_b64 = draw_annotations(frame, ocr_boxes, barcode_res)
            
            # ── Step 7: Date math ─────────────────────────────────────────
            mfg_date_obj = None
            exp_date_obj = None
            printed_shelf_life = None
            days_since_mfg = None
            
            if final_mfg:
                try:
                    mfg_date_obj = datetime.strptime(final_mfg, "%Y-%m-%d").date()
                except ValueError:
                    pass
            if final_exp:
                try:
                    exp_date_obj = datetime.strptime(final_exp, "%Y-%m-%d").date()
                except ValueError:
                    pass
            if mfg_date_obj and exp_date_obj:
                printed_shelf_life = (exp_date_obj - mfg_date_obj).days
            if mfg_date_obj:
                days_since_mfg = (date.today() - mfg_date_obj).days
            
            success = bool(final_mfg or final_exp or final_product or final_mrp)
            
            results.append(ScanResult(
                filename=filename,
                product_name=final_product or "Unknown Product",
                category=final_category or "Unclassified",
                mfg_date=final_mfg,
                expiry_date=final_exp,
                printed_shelf_life_days=printed_shelf_life,
                days_since_manufacture=days_since_mfg,
                batch_number=final_batch,
                ingredients=final_ingredients,
                mrp=final_mrp,
                weight=final_weight,
                barcode=barcode_val,
                barcode_type=barcode_type,
                supplier_id=supplier_id,
                supplier_grade=supplier_grade,
                confidence=final_confidence,
                used_vision_llm=used_llm,
                success=success,
                annotated_image_b64=annotated_b64,
                raw_ocr_text=raw_text if raw_text else None,
            ))
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}", exc_info=True)
            results.append(ScanResult(filename=filename, error=str(e)))
    
    return results


# ── HTML Frontend ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def get_home_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Expiry & Ingredients Scanner</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-primary: #0a0a0c; --card-bg: rgba(22, 22, 28, 0.45);
                --card-border: rgba(255, 255, 255, 0.08);
                --glow-primary: rgba(124, 58, 237, 0.15); --glow-secondary: rgba(6, 182, 212, 0.15);
                --accent-primary: #8b5cf6; --accent-secondary: #06b6d4;
                --text-main: #f3f4f6; --text-muted: #9ca3af;
                --status-valid: #10b981; --status-warning: #f59e0b; --status-error: #ef4444;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { background: var(--bg-primary); color: var(--text-main); font-family: 'Inter', sans-serif; min-height: 100vh; padding: 2rem 1rem; display: flex; flex-direction: column; align-items: center; }
            .bg-glow-1 { position: fixed; top: 10%; left: 15%; width: 400px; height: 400px; border-radius: 50%; background: radial-gradient(circle, var(--glow-primary), transparent 70%); z-index: -1; filter: blur(40px); animation: float 20s infinite alternate; }
            .bg-glow-2 { position: fixed; bottom: 15%; right: 15%; width: 450px; height: 450px; border-radius: 50%; background: radial-gradient(circle, var(--glow-secondary), transparent 70%); z-index: -1; filter: blur(40px); animation: float 25s infinite alternate-reverse; }
            @keyframes float { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(50px,30px) scale(1.1)} }
            .container { max-width: 1200px; width: 100%; display: flex; flex-direction: column; gap: 2.5rem; }
            header { text-align: center; margin-bottom: 1rem; }
            h1 { font-family: 'Outfit', sans-serif; font-size: 2.75rem; font-weight: 800; background: linear-gradient(135deg, #fff 30%, #a78bfa 70%, #22d3ee 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.03em; }
            p.subtitle { font-size: 1.1rem; color: var(--text-muted); font-weight: 300; margin-top: 0.5rem; }
            .upload-section { background: var(--card-bg); border: 2px dashed rgba(139,92,246,0.3); border-radius: 20px; padding: 3.5rem 2rem; text-align: center; cursor: pointer; transition: all 0.4s cubic-bezier(0.16,1,0.3,1); backdrop-filter: blur(16px); }
            .upload-section:hover,.upload-section.dragover { border-color: var(--accent-secondary); box-shadow: 0 0 30px rgba(6,182,212,0.15); transform: translateY(-2px); background: rgba(22,22,28,0.6); }
            .upload-icon { font-size: 3rem; margin-bottom: 1.25rem; display: inline-block; background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; transition: transform 0.3s; }
            .upload-section:hover .upload-icon { transform: scale(1.15) translateY(-3px); }
            .upload-text h3 { font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 600; }
            .upload-text p { color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem; }
            #file-input { display: none; }
            .results-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--card-border); padding-bottom: 0.75rem; margin-bottom: 1.5rem; }
            .results-header h2 { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 600; }
            .results-grid { display: grid; grid-template-columns: 1fr; gap: 1.75rem; }
            .result-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 20px; padding: 1.75rem; backdrop-filter: blur(16px); display: flex; flex-direction: column; gap: 1.5rem; animation: slideUp 0.5s cubic-bezier(0.16,1,0.3,1) both; transition: all 0.3s; }
            @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
            .result-card:hover { border-color: rgba(139,92,246,0.25); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
            .card-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 1rem; }
            .product-title { display: flex; flex-direction: column; gap: 0.25rem; }
            .product-title h3 { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 600; }
            .file-name { font-size: 0.8rem; color: var(--text-muted); }
            .badges { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
            .badge { padding: 0.35rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
            .badge-category { background: rgba(6,182,212,0.15); color: #22d3ee; border: 1px solid rgba(6,182,212,0.3); }
            .badge-llm { background: rgba(139,92,246,0.15); color: #c084fc; border: 1px solid rgba(139,92,246,0.3); }
            .badge-grade { font-family: 'Outfit', sans-serif; font-size: 0.85rem; padding: 0.25rem 0.6rem; }
            .grade-A{background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.4)}
            .grade-B{background:rgba(59,130,246,0.2);color:#60a5fa;border:1px solid rgba(59,130,246,0.4)}
            .grade-C{background:rgba(245,158,11,0.2);color:#fbbf24;border:1px solid rgba(245,158,11,0.4)}
            .grade-D{background:rgba(239,68,68,0.2);color:#f87171;border:1px solid rgba(239,68,68,0.4)}
            .details-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.25rem; }
            .detail-item { display: flex; flex-direction: column; gap: 0.35rem; }
            .detail-label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; }
            .detail-value { font-size: 1.05rem; font-weight: 500; }
            .detail-value.date { font-family: 'Outfit', sans-serif; color: #fff; }
            .detail-value.computed { font-size: 0.85rem; color: #c084fc; font-weight: 400; }
            .full-width-section { display: flex; flex-direction: column; gap: 0.5rem; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 12px; padding: 1rem; }
            .ingredients-box { font-size: 0.9rem; line-height: 1.5; color: var(--text-main); font-style: italic; }
            .annotated-img-wrap { border: 1px solid rgba(139,92,246,0.2); border-radius: 16px; overflow: hidden; position: relative; background: #111; }
            .annotated-img-wrap img { width: 100%; height: auto; display: block; max-height: 600px; object-fit: contain; }
            .annotated-img-wrap .img-tag { position: absolute; top: 12px; left: 12px; background: rgba(139,92,246,0.85); color: #fff; padding: 0.3rem 0.8rem; border-radius: 8px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; backdrop-filter: blur(4px); }
            .color-legend { display: flex; flex-wrap: wrap; gap: 0.75rem; padding: 0.75rem 0; }
            .legend-item { display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; color: var(--text-muted); }
            .legend-dot { width: 12px; height: 12px; border-radius: 3px; }
            .progress-ring-container { display: flex; align-items: center; gap: 0.75rem; }
            .progress-bar-bg { width: 100px; height: 8px; background: rgba(255,255,255,0.1); border-radius: 9999px; overflow: hidden; }
            .progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); border-radius: 9999px; }
            .loader-container { display: none; flex-direction: column; align-items: center; gap: 1rem; padding: 3rem 0; }
            .spinner { width: 50px; height: 50px; border: 3px solid rgba(139,92,246,0.2); border-radius: 50%; border-top-color: var(--accent-primary); animation: spin 1s linear infinite; }
            @keyframes spin { to{transform:rotate(360deg)} }
            .no-results { text-align: center; padding: 4rem 2rem; color: var(--text-muted); border: 1px dashed var(--card-border); border-radius: 20px; }
            .raw-ocr-section { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.75rem 1rem; max-height: 150px; overflow-y: auto; }
            .raw-ocr-section pre { font-size: 0.8rem; color: var(--text-muted); white-space: pre-wrap; word-break: break-word; font-family: 'Courier New', monospace; }
            .toggle-btn { background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3); color: #c084fc; padding: 0.4rem 0.85rem; border-radius: 8px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; font-weight: 500; }
            .toggle-btn:hover { background: rgba(139,92,246,0.3); }
        </style>
    </head>
    <body>
        <div class="bg-glow-1"></div><div class="bg-glow-2"></div>
        <div class="container">
            <header>
                <h1>AI Expiry & Ingredients Scanner</h1>
                <p class="subtitle">Upload up to 5 product images. All fields are extracted and highlighted with color-coded bounding boxes.</p>
            </header>
            <main>
                <div class="upload-section" id="drop-area">
                    <span class="upload-icon">✦</span>
                    <div class="upload-text">
                        <h3>Drag & drop product images here</h3>
                        <p>Supports PNG, JPG, JPEG (Max 5 images)</p>
                    </div>
                    <input type="file" id="file-input" multiple accept="image/*">
                </div>
                <div class="loader-container" id="loader"><div class="spinner"></div><p>Processing images with OCR Pipeline...</p></div>
                <section style="margin-top:3rem;">
                    <div class="results-header"><h2>Scan Results</h2><span id="results-count" style="color:var(--text-muted);font-size:0.9rem;">0 items scanned</span></div>
                    <div id="no-results-view" class="no-results">No products scanned yet. Drag files above or click to upload.</div>
                    <div class="results-grid" id="results-container"></div>
                </section>
            </main>
        </div>
        <script>
            const dropArea=document.getElementById('drop-area'),fileInput=document.getElementById('file-input'),loader=document.getElementById('loader'),resultsContainer=document.getElementById('results-container'),resultsCount=document.getElementById('results-count'),noResultsView=document.getElementById('no-results-view');
            ['dragenter','dragover','dragleave','drop'].forEach(e=>dropArea.addEventListener(e,ev=>{ev.preventDefault();ev.stopPropagation()},false));
            ['dragenter','dragover'].forEach(e=>dropArea.addEventListener(e,()=>dropArea.classList.add('dragover'),false));
            ['dragleave','drop'].forEach(e=>dropArea.addEventListener(e,()=>dropArea.classList.remove('dragover'),false));
            dropArea.addEventListener('drop',e=>processFiles(e.dataTransfer.files),false);
            dropArea.addEventListener('click',()=>fileInput.click());
            fileInput.addEventListener('change',e=>processFiles(e.target.files));

            const LEGEND={MFG:'#00c864',EXP:'#ff5000',BATCH:'#00b4ff',MRP:'#ffff00',BARCODE:'#ff64ff',INGREDIENTS:'#64ff64',PRODUCT:'#64c8ff',WEIGHT:'#ffb4b4',DATE:'#ffc864'};

            function processFiles(files){
                if(!files.length)return;
                if(files.length>5){alert("Max 5 files.");return;}
                loader.style.display='flex';noResultsView.style.display='none';resultsContainer.innerHTML='';resultsCount.innerText='Scanning...';
                const fd=new FormData();
                for(let i=0;i<files.length;i++)fd.append('files',files[i]);
                fetch('/scan',{method:'POST',body:fd})
                .then(r=>{if(!r.ok)return r.json().then(e=>{throw new Error(e.detail||'Upload failed')});return r.json()})
                .then(data=>{loader.style.display='none';renderResults(data)})
                .catch(err=>{loader.style.display='none';resultsCount.innerText='Error';noResultsView.style.display='block';noResultsView.innerText='Error: '+err.message});
            }

            function renderResults(results){
                resultsCount.innerText=results.length+' item'+(results.length!==1?'s':'')+' scanned';
                if(!results.length){noResultsView.style.display='block';return;}
                results.forEach((item,idx)=>{
                    const card=document.createElement('div');card.className='result-card';card.style.animationDelay=idx*100+'ms';
                    if(item.error){card.innerHTML=`<div class="card-header"><div class="product-title"><h3 style="color:var(--status-error)">Error</h3><span class="file-name">${item.filename}</span></div></div><div class="full-width-section" style="border-color:rgba(239,68,68,0.2)"><p style="color:var(--status-error)">${item.error}</p></div>`;resultsContainer.appendChild(card);return;}
                    let badges=`<span class="badge badge-category">${item.category||'Unclassified'}</span>`;
                    if(item.used_vision_llm)badges+=`<span class="badge badge-llm">Vision LLM</span>`;
                    if(item.supplier_grade)badges+=`<span class="badge badge-grade grade-${item.supplier_grade}">Grade ${item.supplier_grade}</span>`;
                    const sl=item.printed_shelf_life_days!=null?item.printed_shelf_life_days+' Days':'Not Calculated';
                    const dm=item.days_since_manufacture!=null?`(${item.days_since_manufacture} Days ago)`:'';
                    const conf=Math.round(item.confidence*100);
                    let imgHtml='';
                    if(item.annotated_image_b64){
                        let leg='';for(const[k,c]of Object.entries(LEGEND))leg+=`<div class="legend-item"><div class="legend-dot" style="background:${c}"></div>${k}</div>`;
                        imgHtml=`<div class="annotated-img-wrap"><span class="img-tag">OCR Highlighted Output</span><img src="data:image/jpeg;base64,${item.annotated_image_b64}" alt="Annotated"></div><div class="color-legend">${leg}</div>`;
                    }
                    let rawHtml='';
                    if(item.raw_ocr_text){const uid='r'+idx;rawHtml=`<div style="display:flex;justify-content:flex-end"><button class="toggle-btn" onclick="document.getElementById('${uid}').style.display=document.getElementById('${uid}').style.display==='none'?'block':'none'">Toggle Raw OCR</button></div><div id="${uid}" class="raw-ocr-section" style="display:none"><pre>${item.raw_ocr_text}</pre></div>`;}
                    card.innerHTML=`
                        <div class="card-header"><div class="product-title"><h3>${item.product_name||'Unknown Product'}</h3><span class="file-name">${item.filename}</span></div><div class="badges">${badges}</div></div>
                        ${imgHtml}
                        <div class="details-grid">
                            <div class="detail-item"><span class="detail-label">Manufacturing Date</span><span class="detail-value date">${item.mfg_date||'Not Detected'}</span>${dm?`<span class="detail-value computed">${dm}</span>`:''}</div>
                            <div class="detail-item"><span class="detail-label">Expiry Date</span><span class="detail-value date">${item.expiry_date||'Not Detected'}</span></div>
                            <div class="detail-item"><span class="detail-label">Shelf Life</span><span class="detail-value" style="color:var(--accent-secondary);font-weight:600">${sl}</span></div>
                            <div class="detail-item"><span class="detail-label">MRP / Price</span><span class="detail-value">${item.mrp!=null?'₹'+item.mrp:'Not Detected'}</span></div>
                            <div class="detail-item"><span class="detail-label">Weight</span><span class="detail-value">${item.weight||'Not Detected'}</span></div>
                            <div class="detail-item"><span class="detail-label">Batch Number</span><span class="detail-value">${item.batch_number||'N/A'}</span></div>
                            <div class="detail-item"><span class="detail-label">Barcode</span><span class="detail-value">${item.barcode||'Not Detected'}</span>${item.barcode_type?`<span class="detail-value computed">${item.barcode_type}</span>`:''}</div>
                            <div class="detail-item"><span class="detail-label">Supplier</span><span class="detail-value">${item.supplier_id?'ID: '+item.supplier_id:'N/A'}</span></div>
                        </div>
                        ${item.ingredients?`<div class="full-width-section"><span class="detail-label">Ingredients Detected</span><div class="ingredients-box">${item.ingredients}</div></div>`:''}
                        ${rawHtml}
                        <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(255,255,255,0.05);padding-top:1rem">
                            <div class="progress-ring-container"><span class="detail-label">OCR Confidence:</span><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${conf}%"></div></div><span style="font-size:0.85rem;font-weight:600">${conf}%</span></div>
                            <span class="badge" style="background:${item.success?'rgba(16,185,129,0.15)':'rgba(239,68,68,0.15)'};color:${item.success?'#34d399':'#f87171'}">${item.success?'Scan Success':'Scan Failed'}</span>
                        </div>`;
                    resultsContainer.appendChild(card);
                });
            }
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8050)
