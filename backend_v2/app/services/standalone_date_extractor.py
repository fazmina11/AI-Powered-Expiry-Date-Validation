
"""
Standalone Date Extraction Service
Extracts manufacturing and expiry dates from OCR text without requiring API keys
"""

import re
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDates:
    mfg_date: Optional[str] = None
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    ingredients: Optional[str] = None
    confidence: float = 0.0
    raw_text: str = ""


class StandaloneDateExtractor:
    """
    Comprehensive date extractor that works without API keys
    Uses enhanced regex patterns and smart parsing logic
    """
    
    # Enhanced date patterns
    DATE_PATTERNS = [
        # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
        (re.compile(r'\b(0?[1-9]|[12]\d|3[01])([\/\-\.])(0?[1-9]|1[0-2])\2((?:19|20)\d{2})\b'), 'DMY'),
        # MM/DD/YYYY, MM-DD-YYYY, MM.DD.YYYY
        (re.compile(r'\b(0?[1-9]|1[0-2])([\/\-\.])(0?[1-9]|[12]\d|3[01])\2((?:19|20)\d{2})\b'), 'MDY'),
        # YYYY/MM/DD, YYYY-MM-DD, YYYY.MM.DD
        (re.compile(r'\b((?:19|20)\d{2})([\/\-\.])(0?[1-9]|1[0-2])\2(0?[1-9]|[12]\d|3[01])\b'), 'YMD'),
        # DD/MM/YY, DD-MM-YY, DD.MM.YY (assume 20xx)
        (re.compile(r'\b(0?[1-9]|[12]\d|3[01])([\/\-\.])(0?[1-9]|1[0-2])\2(\d{2})\b'), 'DMY_SHORT'),
        # MM/DD/YY, MM-DD-YY, MM.DD.YY
        (re.compile(r'\b(0?[1-9]|1[0-2])([\/\-\.])(0?[1-9]|[12]\d|3[01])\2(\d{2})\b'), 'MDY_SHORT'),
        # DD MMM YYYY (e.g., 15 JAN 2024)
        (re.compile(r'\b(0?[1-9]|[12]\d|3[01])\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+((?:19|20)\d{2})\b', re.IGNORECASE), 'TEXTUAL_DMY'),
        # MMM DD YYYY (e.g., JAN 15 2024)
        (re.compile(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(0?[1-9]|[12]\d|3[01])\s*[,]?\s*((?:19|20)\d{2})\b', re.IGNORECASE), 'TEXTUAL_MDY'),
        # DD-MMM-YYYY (e.g., 15-JAN-2024)
        (re.compile(r'\b(0?[1-9]|[12]\d|3[01])-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-((?:19|20)\d{2})\b', re.IGNORECASE), 'TEXTUAL_DMY_DASH'),
    ]
    
    # Prefix patterns for manufacturing date
    MFG_PREFIXES = [
        r'\b(?:MFG|MFD|MANUFACTURED|MANUFACTURING|PKD|PACKED|PKG)\s*(?:DATE|DT|ON)?\s*[:\-]?\s*',
        r'\b(?:MFG\.|MFD\.)\s*[:\-]?\s*',
    ]
    
    # Prefix patterns for expiry date
    EXP_PREFIXES = [
        r'\b(?:EXP|EXPIRY|EXPIRES|USE\s+BY|BEST\s+BEFORE|BB|BBD|VAL)\s*(?:DATE|DT|BY)?\s*[:\-]?\s*',
        r'\b(?:EXP\.|EXPIRY\.|BEST\s+BEFORE\.)\s*[:\-]?\s*',
    ]
    
    # Batch/lot patterns
    BATCH_PATTERNS = [
        re.compile(r'\b(?:BATCH|B\.?NO|LOT)\s*(?:NO|NUM|NUMBER)?\s*[:\-]?\s*([A-Z0-9\-\/]{3,15})\b', re.IGNORECASE),
        re.compile(r'\b(?:LOT)\s*(?:NO|NUM|NUMBER)?\s*[:\-]?\s*([A-Z0-9\-\/]{3,15})\b', re.IGNORECASE),
    ]
    
    # Month mapping
    MONTH_MAP = {
        'JAN': 1, 'JANUARY': 1,
        'FEB': 2, 'FEBRUARY': 2,
        'MAR': 3, 'MARCH': 3,
        'APR': 4, 'APRIL': 4,
        'MAY': 5,
        'JUN': 6, 'JUNE': 6,
        'JUL': 7, 'JULY': 7,
        'AUG': 8, 'AUGUST': 8,
        'SEP': 9, 'SEPTEMBER': 9,
        'OCT': 10, 'OCTOBER': 10,
        'NOV': 11, 'NOVEMBER': 11,
        'DEC': 12, 'DECEMBER': 12,
    }
    
    @staticmethod
    def extract_dates_from_text(raw_text: str) -> ExtractedDates:
        """
        Main extraction method: extracts dates and batch number from raw OCR text
        """
        if not raw_text or not raw_text.strip():
            return ExtractedDates(raw_text=raw_text)
        
        extracted = ExtractedDates(raw_text=raw_text)
        
        # Clean text
        clean_text = StandaloneDateExtractor._clean_text(raw_text)
        
        # Extract batch number
        extracted.batch_number = StandaloneDateExtractor._extract_batch(clean_text)
        
        # Extract ingredients
        extracted.ingredients = StandaloneDateExtractor._extract_ingredients(clean_text)
        
        # Find all dates in text
        all_dates = StandaloneDateExtractor._find_all_dates(clean_text)
        
        if not all_dates:
            extracted.confidence = 0.0
            return extracted
        
        # Classify dates as MFG or EXP based on context
        mfg_candidates, exp_candidates = StandaloneDateExtractor._classify_dates(clean_text, all_dates)
        
        # Select best candidates
        if mfg_candidates:
            extracted.mfg_date = StandaloneDateExtractor._format_date(mfg_candidates[0]['date'])
        if exp_candidates:
            extracted.expiry_date = StandaloneDateExtractor._format_date(exp_candidates[0]['date'])
        
        # Calculate confidence
        extracted.confidence = StandaloneDateExtractor._calculate_confidence(
            mfg_candidates, exp_candidates, extracted.batch_number
        )
        
        return extracted
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text for better pattern matching"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Normalize separators
        text = text.replace('–', '-').replace('—', '-')
        # Add space around colons if missing
        text = re.sub(r'([A-Za-z])([:\-])(\d)', r'\1 \2 \3', text)
        return text.upper()
    
    @staticmethod
    def _find_all_dates(text: str) -> List[Dict]:
        """Find all potential dates in text"""
        dates = []
        
        for pattern, format_type in StandaloneDateExtractor.DATE_PATTERNS:
            matches = pattern.finditer(text)
            for match in matches:
                date_obj = StandaloneDateExtractor._parse_date_match(match, format_type)
                if date_obj:
                    dates.append({
                        'date': date_obj,
                        'text': match.group(0),
                        'start': match.start(),
                        'end': match.end(),
                        'format': format_type
                    })
        
        # Sort by position
        dates.sort(key=lambda x: x['start'])
        
        # Remove duplicates (same date parsed multiple times)
        unique_dates = []
        seen = set()
        for date_info in dates:
            date_str = date_info['date'].strftime('%Y-%m-%d')
            if date_str not in seen:
                seen.add(date_str)
                unique_dates.append(date_info)
        
        return unique_dates
    
    @staticmethod
    def _parse_date_match(match, format_type: str) -> Optional[datetime]:
        """Parse a regex match into a datetime object"""
        groups = match.groups()
        
        try:
            if format_type == 'DMY':
                day, month, year = int(groups[0]), int(groups[2]), int(groups[3])
                return datetime(year, month, day)
            elif format_type == 'MDY':
                month, day, year = int(groups[0]), int(groups[2]), int(groups[3])
                return datetime(year, month, day)
            elif format_type == 'YMD':
                year, month, day = int(groups[0]), int(groups[2]), int(groups[3])
                return datetime(year, month, day)
            elif format_type == 'DMY_SHORT':
                day, month, year_short = int(groups[0]), int(groups[2]), int(groups[3])
                year = 2000 + year_short if year_short < 50 else 1900 + year_short
                return datetime(year, month, day)
            elif format_type == 'MDY_SHORT':
                month, day, year_short = int(groups[0]), int(groups[2]), int(groups[3])
                year = 2000 + year_short if year_short < 50 else 1900 + year_short
                return datetime(year, month, day)
            elif format_type == 'TEXTUAL_DMY':
                day = int(groups[0])
                month = StandaloneDateExtractor.MONTH_MAP.get(groups[1].upper())
                year = int(groups[2])
                if month:
                    return datetime(year, month, day)
            elif format_type == 'TEXTUAL_MDY':
                month = StandaloneDateExtractor.MONTH_MAP.get(groups[0].upper())
                day = int(groups[1])
                year = int(groups[2])
                if month:
                    return datetime(year, month, day)
            elif format_type == 'TEXTUAL_DMY_DASH':
                day = int(groups[0])
                month = StandaloneDateExtractor.MONTH_MAP.get(groups[1].upper())
                year = int(groups[2])
                if month:
                    return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
        
        return None
    
    @staticmethod
    def _classify_dates(text: str, dates: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Classify dates as MFG or EXP based on nearby keywords"""
        mfg_candidates = []
        exp_candidates = []
        
        for date_info in dates:
            # Get context around the date
            context_start = max(0, date_info['start'] - 50)
            context_end = min(len(text), date_info['end'] + 50)
            context = text[context_start:context_end]
            
            # Check for MFG prefixes (text is already uppercase)
            is_mfg = any(prefix in context.upper() for prefix in [
                'MFG', 'MFD', 'MANUFACTURED', 'MANUFACTURING', 'PKD', 'PACKED', 'PKG'
            ])
            
            # Check for EXP prefixes
            is_exp = any(prefix in context.upper() for prefix in [
                'EXP', 'EXPIRY', 'EXPIRES', 'USE BY', 'BEST BEFORE', 'BB', 'BBD', 'VAL'
            ])
            
            if is_mfg and not is_exp:
                mfg_candidates.append(date_info)
            elif is_exp and not is_mfg:
                exp_candidates.append(date_info)
            elif is_mfg and is_exp:
                # If both prefixes are in context, check which is closer
                mfg_pos = min(context.find(p) for p in [
                    'MFG', 'MFD', 'MANUFACTURED', 'MANUFACTURING', 'PKD', 'PACKED', 'PKG'
                ] if p in context)
                exp_pos = min(context.find(p) for p in [
                    'EXP', 'EXPIRY', 'EXPIRES', 'USE BY', 'BEST BEFORE', 'BB', 'BBD', 'VAL'
                ] if p in context)
                if mfg_pos < exp_pos:
                    mfg_candidates.append(date_info)
                else:
                    exp_candidates.append(date_info)
            else:
                # No prefix - add to both, we'll sort later
                mfg_candidates.append(date_info)
                exp_candidates.append(date_info)
        
        # Now, if we have multiple dates, use date ordering to pick the right ones
        if len(dates) >= 2:
            sorted_dates = sorted(dates, key=lambda x: x['date'])
            # The earlier date is more likely to be MFG, later is EXP
            if not mfg_candidates or len(mfg_candidates) > 1:
                mfg_candidates = [sorted_dates[0]]
            if not exp_candidates or len(exp_candidates) > 1:
                exp_candidates = [sorted_dates[-1]]
        
        # Ensure MFG < EXP if both exist
        if mfg_candidates and exp_candidates:
            mfg_date = mfg_candidates[0]['date']
            exp_date = exp_candidates[0]['date']
            if mfg_date > exp_date:
                # Swap them
                mfg_candidates, exp_candidates = exp_candidates, mfg_candidates
        
        return mfg_candidates, exp_candidates
    
    @staticmethod
    def _extract_batch(text: str) -> Optional[str]:
        """Extract batch/lot number"""
        for pattern in StandaloneDateExtractor.BATCH_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return None
        
    @staticmethod
    def _extract_ingredients(text: str) -> Optional[str]:
        """Extract ingredients list using common keywords"""
        pattern = re.compile(r'\b(?:INGREDIENTS|INGREDIENT|CONTAINS)\s*[:\-]?\s*(.+)', re.IGNORECASE)
        match = pattern.search(text)
        if match:
            ingredients_text = match.group(1).strip()
            # Stop if another major header is found
            stop_headers = ['MFG', 'MFD', 'EXP', 'BATCH', 'B. NO', 'BEST BEFORE', 'BB', 'MRP', 'PRICE', 'WEIGHT', 'NET QTY']
            for header in stop_headers:
                header_pos = ingredients_text.upper().find(header)
                if header_pos != -1:
                    ingredients_text = ingredients_text[:header_pos].strip()
            # Remove trailing non-alphanumeric punctuation
            ingredients_text = re.sub(r'[\s,.:\-]+$', '', ingredients_text)
            return ingredients_text if ingredients_text else None
        return None
    
    @staticmethod
    def _format_date(date_obj: datetime) -> str:
        """Format datetime as YYYY-MM-DD"""
        return date_obj.strftime('%Y-%m-%d')
    
    @staticmethod
    def _calculate_confidence(mfg_candidates: List, exp_candidates: List, batch: Optional[str]) -> float:
        """Calculate confidence score based on what was found"""
        score = 0.0
        
        if mfg_candidates:
            score += 0.4
        if exp_candidates:
            score += 0.4
        if batch:
            score += 0.2
        
        # Bonus if both dates found and MFG < EXP
        if mfg_candidates and exp_candidates:
            if mfg_candidates[0]['date'] < exp_candidates[0]['date']:
                score += 0.1
        
        return min(score, 1.0)


def extract_dates_standalone(raw_text: str) -> ExtractedDates:
    """
    Convenience function to extract dates without API keys
    """
    return StandaloneDateExtractor.extract_dates_from_text(raw_text)
