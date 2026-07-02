# Enhanced Product Date Extraction Solution

## Overview

This solution provides a robust system for extracting manufacturing dates, expiry dates, and batch numbers from product labels using webcam capture and OCR technology.

## What We've Built

### 1. **Enhanced Image Preprocessing** (`app/services/enhanced_preprocessing.py`)
- Multiple image enhancement techniques for better OCR accuracy
- Glare removal, denoising, contrast enhancement
- Adaptive thresholding for text/background separation
- Multi-view generation (rotated, contrast variations)

### 2. **Standalone Date Extractor** (`app/services/standalone_date_extractor.py`)
- No API keys required!
- Enhanced regex patterns for multiple date formats
- Smart classification of MFG vs EXP dates
- Batch number extraction
- Confidence scoring

### 3. **Enhanced OCR Pipeline** (`app/services/enhanced_ocr_pipeline.py`)
- Combines preprocessing + OCR + date extraction
- Supports both EasyOCR and PaddleOCR
- Optional Vision LLM integration (Gemini/OpenAI)
- Falls back gracefully if no API keys

### 4. **Webcam Scanner** (`dev_tools/webcam_scanner.py`)
- Real-time webcam capture
- User-friendly interface
- Visual feedback of results

## Quick Start

### Step 1: Install Dependencies

```bash
cd AI_expiry_date/AI_expiry_date/backend_v2

# Make sure your virtual environment is activated
# If using the existing venv:
# . venv/Scripts/activate  (Windows)
# source venv/bin/activate  (Linux/Mac)

# Install required packages
pip install opencv-python numpy easyocr python-dateutil
```

### Step 2: Run the Webcam Scanner

```bash
cd dev_tools
python webcam_scanner.py
```

## Usage Instructions

1. Position your product in front of the webcam
2. Make sure the date labels are clearly visible
3. Press **SPACE** to capture and process
4. View the results on screen
5. Press **SPACE** again to scan another product
6. Press **Q** to quit

## Improving Accuracy (Optional)

### Adding Vision LLM API Keys

For maximum accuracy, you can add Vision LLM support:

1. Edit the `.env` file in `backend_v2/`:

```env
# For Google Gemini (recommended, free tier available)
GEMINI_API_KEY=your_gemini_api_key_here

# OR for OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

2. Get your API keys:
   - **Gemini**: https://aistudio.google.com/app/apikey
   - **OpenAI**: https://platform.openai.com/api-keys

### Tips for Better Scans

1. **Good Lighting**: Ensure the product is well-lit without glare
2. **Steady Hands**: Keep the camera steady or use a tripod
3. **Clear View**: Make sure dates are not covered or blurry
4. **Flat Surface**: Place the product on a flat surface if possible
5. **Multiple Tries**: If it fails, try different angles or lighting

## Date Formats Supported

The system recognizes many date formats:
- `DD/MM/YYYY` (15/03/2024)
- `MM/DD/YYYY` (03/15/2024)
- `YYYY-MM-DD` (2024-03-15)
- `DD MMM YYYY` (15 MAR 2024)
- `MMM DD YYYY` (MAR 15 2024)
- Short years: `DD/MM/YY` (15/03/24)
- And many variations!

## Label Prefixes Recognized

- **Manufacturing**: MFG, MFD, PKD, PACKED, MANUFACTURED
- **Expiry**: EXP, EXPIRY, BEST BEFORE, BB, USE BY
- **Batch**: BATCH, B. NO, LOT, LOT NO

## Architecture

```
Webcam Capture
    ↓
Image Preprocessing (multiple views)
    ↓
OCR Extraction (EasyOCR + optional PaddleOCR)
    ↓
Date Extraction (standalone or Vision LLM)
    ↓
Result Display
```

## Troubleshooting

### Camera Not Opening
- Make sure no other app is using the camera
- Try restarting the script
- Check camera permissions

### Dates Not Detected
- Improve lighting
- Try different angles
- Make sure text is in focus
- Consider adding Vision LLM API keys for better accuracy

### Missing Dependencies
```bash
pip install -r requirements.txt
```

## Files Created

```
backend_v2/
├── app/services/
│   ├── enhanced_preprocessing.py      # Image enhancement
│   ├── standalone_date_extractor.py  # Date extraction (no API)
│   └── enhanced_ocr_pipeline.py      # Main pipeline
└── dev_tools/
    └── webcam_scanner.py              # Webcam interface
```

## License

This solution integrates with your existing expiry date validation system.
