# KayGraph Tool Integration - PDF Vision

Demonstrates PDF processing with vision/OCR capabilities for extracting structured data from various document types using KayGraph.

## What it does

This example shows how to:
- **Process PDFs**: Extract text and structured data
- **Vision/OCR Integration**: Simulate document understanding
- **Multi-format Support**: Handle invoices, forms, reports
- **Batch Processing**: Process multiple PDFs efficiently
- **Data Extraction**: Convert unstructured PDFs to structured data

## Features

- Mock vision API for PDF text extraction
- Support for multiple document types
- Table and form field detection
- Confidence scoring for extraction quality
- Structured data extraction (invoices, forms, reports)
- Comprehensive analysis and reporting

## How to run

```bash
python main.py
```

## Architecture

```
LoadPDFNode → ProcessPDFBatchNode → AnalyzePDFsNode → ExtractStructuredDataNode → GenerateReportNode
```

### Node Descriptions

1. **LoadPDFNode**: Discover and load PDF files
2. **ProcessPDFBatchNode**: Extract content from PDFs using vision/OCR
3. **AnalyzePDFsNode**: Analyze extraction quality and content
4. **ExtractStructuredDataNode**: Extract structured data by document type
5. **GenerateReportNode**: Create comprehensive processing report

## Supported Document Types

### 1. Invoices
- Invoice number, date, due date
- Line items with amounts
- Customer and vendor information
- Total calculations

### 2. Forms
- Form field extraction
- Checkbox and signature detection
- Personal information parsing
- Structured form data output

### 3. Reports
- Financial metrics extraction
- Table parsing
- Chart and graph detection
- Key performance indicators

### 4. Research Papers
- Title and author extraction
- Abstract and keywords
- Reference parsing
- Section identification

## Example Output

```
📄 KayGraph PDF Vision Tool Integration
============================================================
This example demonstrates PDF processing with
vision/OCR capabilities for data extraction.

📄 Found 8 PDF files:
  - invoice_2024_001.pdf
  - invoice_2024_002.pdf
  - quarterly_report_Q1.pdf
  - research_paper_nlp.pdf
  - application_form_jane.pdf
  ... and 3 more

📑 PDF Processing Results:
  ✅ Successful: 8
  ❌ Failed: 0

Sample extractions:

  📄 invoice_2024_001.pdf:
     Pages: 1
     > INVOICE...

  📄 quarterly_report_Q1.pdf:
     Pages: 2
     > QUARTERLY BUSINESS REPORT...

📊 PDF Analysis Summary:
  Total documents: 8
  Total pages: 10
  Average quality: 0.93

📋 Document Types:
  - invoice: 2
  - quarterly_report: 1
  - research_paper: 1
  - application_form: 1
  - generic: 3

🎯 Quality Distribution:
  - High (≥90%): 7
  - Medium (70-89%): 1
  - Low (<70%): 0

💎 Structured Data Extraction:

📑 Invoices (2):
  - INV-2024-001: $10,368.00 (invoice_2024_001.pdf)
  - INV-2024-002: $8,542.00 (invoice_2024_002.pdf)
  Total: $18,910.00

📝 Forms (1):
  - application_form_jane.pdf: Jane Doe

📊 Reports (1):
  - quarterly_report_Q1.pdf: Q1 2024 - Revenue: $45,200,000

============================================================
📋 PDF PROCESSING REPORT
============================================================
Generated: 2024-03-15T10:45:30

📊 Processing Summary:
  - Files processed: 8
  - Successful: 8
  - Total pages: 10
  - Average quality: 93.0%

📁 Structured Extractions:
  - Invoices: 2
  - Forms: 1
  - Reports: 1

💾 Full report saved to: pdf_processing_report.json

✨ PDF processing example complete!
```

## Integration with Real Vision APIs

### Google Cloud Vision
```python
from google.cloud import vision

class GoogleVisionProcessor(PDFProcessor):
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    def process_pdf(self, pdf_path):
        # Convert PDF to images
        images = pdf_to_images(pdf_path)
        
        # Process each page
        pages = []
        for image in images:
            response = self.client.text_detection(image=image)
            pages.append({
                "text": response.text_annotations[0].description,
                "confidence": response.text_annotations[0].confidence
            })
        
        return {"pages": pages}
```

### Azure Form Recognizer
```python
from azure.ai.formrecognizer import DocumentAnalysisClient

class AzureFormProcessor(PDFProcessor):
    def __init__(self):
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    def process_pdf(self, pdf_path):
        with open(pdf_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-invoice", f
            )
        result = poller.result()
        
        # Extract structured data
        return self._parse_azure_result(result)
```

### AWS Textract
```python
import boto3

class TextractProcessor(PDFProcessor):
    def __init__(self):
        self.client = boto3.client('textract')
    
    def process_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as f:
            response = self.client.analyze_document(
                Document={'Bytes': f.read()},
                FeatureTypes=['TABLES', 'FORMS']
            )
        
        # Parse Textract response
        return self._parse_textract_response(response)
```

## Advanced Features

### 1. Table Extraction
```python
def extract_tables(page_data):
    """Extract structured tables from page."""
    tables = []
    for table in page_data.get("tables", []):
        df = pd.DataFrame(
            table["rows"],
            columns=table["headers"]
        )
        tables.append(df)
    return tables
```

### 2. Multi-language Support
```python
def detect_language(text):
    """Detect document language."""
    from langdetect import detect
    return detect(text)
```

### 3. Document Classification
```python
def classify_document(text, layout_features):
    """Classify document type using ML."""
    features = extract_features(text, layout_features)
    return classifier.predict(features)
```

## Performance Optimization

1. **Parallel Processing**: Use BatchNode for concurrent PDF processing
2. **Caching**: Cache extracted data to avoid reprocessing
3. **Streaming**: Process large PDFs page by page
4. **Compression**: Reduce PDF size before processing
5. **Selective Processing**: Only process pages with relevant content

## Use Cases

- **Invoice Processing**: Automate accounts payable
- **Form Digitization**: Convert paper forms to digital
- **Contract Analysis**: Extract key terms and dates
- **Report Mining**: Extract KPIs from business reports
- **Resume Parsing**: Extract candidate information

## Best Practices

1. **Quality Control**: Check confidence scores
2. **Validation**: Verify extracted data against schemas
3. **Error Handling**: Gracefully handle extraction failures
4. **Security**: Redact sensitive information
5. **Compliance**: Ensure GDPR/privacy compliance

## Dependencies

This example uses mock processing. For production:
- `pypdf2`: PDF manipulation
- `pdf2image`: PDF to image conversion
- `pytesseract`: Open source OCR
- Cloud APIs: Google Vision, Azure Form Recognizer, AWS Textract