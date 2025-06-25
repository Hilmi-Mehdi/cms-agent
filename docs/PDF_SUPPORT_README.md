# PDF Support for SMS-Agent

The SMS-Agent now supports analyzing PDF files in addition to individual slide images. Each page of the PDF is automatically converted to an image and processed as if it were a separate slide.

## Features

- **Automatic PDF to Image Conversion**: Each PDF page is converted to a high-quality image (200 DPI by default)
- **Page Limit Control**: Set maximum number of pages to process to control costs and processing time
- **Mixed File Support**: Upload both PDF files and individual images in the same request
- **Seamless Integration**: PDF files are processed through the same slide analyzer tool

## Installation

The PDF support requires the `pdf2image` library:

```bash
pip install pdf2image==1.16.3
```

This dependency is already included in `requirements.txt`.

## API Usage

### Analyze Slides Endpoint

**POST** `/api/v1/analyze-slides`

**Parameters:**
- `slides`: List of files (images and/or PDFs)
- `ai_provider`: "openai" or "google" (default: "openai")
- `analysis_depth`: "basic", "detailed", or "comprehensive" (default: "comprehensive")
- `target_audience`: "beginner", "intermediate", "advanced", or "general" (default: "general")
- `subject_area`: Subject hint for analysis (default: "auto-detect")
- `max_pdf_pages`: Maximum pages to process from PDF files (default: 50)

**Supported File Types:**
- Images: PNG, JPG, JPEG, WebP, BMP
- Documents: PDF

### Example Usage

#### Python with requests

```python
import requests

# Upload a PDF file
with open('course_slides.pdf', 'rb') as pdf_file:
    files = {'slides': ('course_slides.pdf', pdf_file, 'application/pdf')}
    data = {
        'ai_provider': 'google',
        'analysis_depth': 'detailed',
        'target_audience': 'intermediate',
        'max_pdf_pages': 20
    }
    
    response = requests.post(
        'http://localhost:8000/api/v1/analyze-slides',
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Document type: {result['course_data']['type_document']}")
```

#### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze-slides" \
  -F "slides=@course_slides.pdf" \
  -F "ai_provider=google" \
  -F "analysis_depth=detailed" \
  -F "max_pdf_pages=15"
```

## Tool Usage

You can also use the PDF functionality directly through the SlideAnalyzerTool:

```python
from app.tools.slide_analyzer import SlideAnalyzerTool

tool = SlideAnalyzerTool()
result = await tool.execute({
    "slide_images": ["path/to/slides.pdf"],
    "ai_provider": "google",
    "analysis_depth": "detailed",
    "max_pdf_pages": 25
})
```

## Configuration

### PDF Processing Settings

The PDF processor can be configured in `app/utils/pdf_processor.py`:

- **DPI**: Resolution for image conversion (default: 200)
- **Format**: Output image format (default: PNG)

### Performance Considerations

- **Page Limits**: Use `max_pdf_pages` to control processing time and costs
- **File Size**: Large PDFs with many pages will take longer to process
- **Memory Usage**: Each page is converted to an image in memory

### Recommended Limits

- **Development**: 10-20 pages max
- **Production**: 50 pages max (default)
- **Large Documents**: Consider splitting into smaller chunks

## Error Handling

The system gracefully handles:
- Invalid PDF files
- Corrupted pages
- Mixed file types in the same request
- PDF processing failures (skips problematic files)

## Testing

Run the test scripts to verify PDF functionality:

```bash
# Test PDF processing utilities
python test_pdf_support.py

# Test PDF analysis via API (requires server running)
python test_pdf_api.py
```

## Troubleshooting

### PDF2Image Not Found
```
ImportError: PDF processing requires pdf2image
```
**Solution**: Install pdf2image: `pip install pdf2image`

### PDF Processing Fails
```
Failed to convert PDF to images
```
**Solutions**:
- Ensure the PDF file is not corrupted
- Check file permissions
- Verify the PDF is not password-protected

### High Memory Usage
**Solutions**:
- Reduce `max_pdf_pages`
- Lower the DPI setting in PDFProcessor
- Process PDFs in smaller batches

## Examples

See `test_pdf_api.py` for complete working examples of:
- PDF upload and analysis
- Mixed PDF and image processing
- Error handling
- Result interpretation 