# 🤖 AI-Powered PDF to Excel Converter

A fully automated, robust solution that uses artificial intelligence to convert PDF documents with tables into structured Excel files. **No hardcoding required** - the system adapts to any document structure automatically.

## 🎯 Features

- **🤖 AI-Powered Table Detection**: Uses machine learning and spatial clustering to automatically detect table structures
- **📊 Intelligent Column Recognition**: Automatically identifies column headers using pattern recognition
- **🔍 Adaptive Data Extraction**: Works with any table layout without hardcoding
- **🧠 Smart OCR Error Correction**: AI-powered cleaning based on detected data types
- **⚡ Multiple OCR Engines**: Supports both PaddleOCR and EasyOCR for maximum compatibility
- **🚀 Production Ready**: Handles real-world documents with complex layouts

## 🏗️ Architecture

```
pdf_to_excel_converter/
├── main_ai.py              # AI-powered main script (recommended)
├── main_easyocr.py         # EasyOCR-based main script
├── pdf_processor.py        # PDF to image conversion
├── ocr_processor_easyocr.py # EasyOCR implementation
├── data_mapper_ai.py       # AI-powered table structure detection
├── excel_exporter.py       # Excel file generation
├── config.py              # Configuration settings
└── output_excel/          # Generated Excel files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- macOS/Linux/Windows
- Poppler (for PDF processing)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd table
```

2. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install pdf2image pillow pandas openpyxl easyocr scikit-learn
brew install poppler  # On macOS
```

### Usage

**AI-Powered Conversion (Recommended):**
```bash
cd pdf_to_excel_converter
source ../venv/bin/activate
python main_ai.py "your_document.pdf" -o "output_name.xlsx"
```

**EasyOCR-Based Conversion:**
```bash
python main_easyocr.py "your_document.pdf" -o "output_name.xlsx"
```

## 🤖 AI Technology Stack

### Core AI Components

1. **Spatial Clustering (DBSCAN)**
   - Groups text elements into table regions
   - Automatically detects table boundaries

2. **Pattern Recognition**
   - Identifies column headers using regex patterns
   - Scores potential headers based on content

3. **Machine Learning Data Type Detection**
   - Automatically classifies columns (numeric, code, tolerance, text)
   - Applies appropriate cleaning based on detected types

4. **Intelligent Column Alignment**
   - Uses spatial analysis to align data with headers
   - Handles irregular layouts and OCR positioning errors

### OCR Error Correction

The AI system includes intelligent OCR error correction:
- **Numeric columns**: Fixes common OCR errors (O→0, I→1, S→5, etc.)
- **Code columns**: Corrects part number misreads (SSI→551, I2→12)
- **Tolerance columns**: Standardizes format (t0.05→±0.05)

## 📊 Example Results

**Input PDF Table:**
```
Part Number | Machine Number | Diameter (mm) | Length (cm) | Tolerance (mm) | Quantity
PN-482-4   | M-03          | 12.5          | 30.2        | ±0.05         | 150
PN-551-C   | M-03          | 8.0           | 15.7        | +0.02         | 320
```

**AI-Generated Excel Output:**
- ✅ Automatically detected 6 columns
- ✅ Extracted 7 data rows
- ✅ Applied intelligent data cleaning
- ✅ No hardcoding required

## 🔧 Configuration

Edit `config.py` to customize:

```python
# OCR Configuration
OCR_CONFIG = {
    "lang": "en",                    # Language for OCR
    "use_angle_cls": True,          # Detect rotated text
    "use_gpu": False                # Use GPU acceleration
}

# Output directories
OUTPUT_DIR = "output_excel"
TEMP_IMAGE_DIR = "temp_images"
```

## 🧪 Testing

The system has been tested with:
- ✅ Manufacturing parts tables
- ✅ Different column structures
- ✅ Various data types (codes, numbers, tolerances)
- ✅ Multiple document layouts

**Test with sample data:**
```bash
python main_ai.py "Manufacturing Parts Log.pdf" -o "test_output.xlsx"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different PDF documents
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **EasyOCR**: Robust OCR engine
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation
- **pdf2image**: PDF processing

## 🚀 Future Enhancements

- [ ] GPU acceleration for faster processing
- [ ] Support for multi-page documents
- [ ] Advanced table structure detection
- [ ] Web interface for easy usage
- [ ] Batch processing capabilities

---

**Built with ❤️ and AI** - A truly adaptive, non-hardcoded solution for PDF to Excel conversion! 