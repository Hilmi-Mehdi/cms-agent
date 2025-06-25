"""
PDF processing utilities for the SMS-Agent.
Converts PDF pages to images for analysis using PyMuPDF (faster than pdf2image).
"""

import io
from typing import List, Union, Optional
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PDF_SUPPORT_AVAILABLE = True
except ImportError:
    PDF_SUPPORT_AVAILABLE = False
    print("WARNING: PyMuPDF not installed. PDF support disabled.")
    print("Install with: pip install PyMuPDF")


class PDFProcessor:
    """Handles PDF to image conversion using PyMuPDF for fast processing."""
    
    def __init__(self):
        if not PDF_SUPPORT_AVAILABLE:
            raise ImportError("PyMuPDF is required for PDF processing. Install with: pip install PyMuPDF")
    
    def pdf_to_images(
        self, 
        pdf_input: Union[str, Path, bytes], 
        dpi: int = 300,  # High default DPI for complete text extraction
        max_pages: Optional[int] = None
    ) -> List[bytes]:
        """
        Convert PDF pages to images using PyMuPDF (much faster than pdf2image).
        
        Args:
            pdf_input: PDF file path or bytes
            dpi: Resolution for image conversion (default: 200)
            max_pages: Maximum number of pages to process
            
        Returns:
            List of image bytes (PNG format)
        """
        if not PDF_SUPPORT_AVAILABLE:
            raise ImportError("PyMuPDF is required for PDF processing")
        
        images = []
        
        try:
            # Open PDF document
            if isinstance(pdf_input, (str, Path)):
                doc = fitz.open(str(pdf_input))
            elif isinstance(pdf_input, bytes):
                doc = fitz.open(stream=pdf_input, filetype="pdf")
            else:
                raise ValueError(f"Unsupported PDF input type: {type(pdf_input)}")
            
            # Calculate zoom factor for desired DPI
            # PyMuPDF default is 72 DPI, so zoom = desired_dpi / 72
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            # Process pages
            total_pages = len(doc)
            pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
            
            print(f"Converting {pages_to_process} pages from PDF (DPI: {dpi})")
            
            for page_num in range(pages_to_process):
                page = doc[page_num]
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PNG bytes
                img_bytes = pix.tobytes("png")
                images.append(img_bytes)
                
                # Clean up
                pix = None
            
            doc.close()
            print(f"Successfully converted {len(images)} pages using PyMuPDF")
            
        except Exception as e:
            raise Exception(f"PDF conversion failed: {str(e)}")
        
        return images
    
    def validate_pdf(self, pdf_input: Union[str, Path, bytes]) -> bool:
        """
        Validate if input is a valid PDF using PyMuPDF.
        
        Args:
            pdf_input: PDF file path or bytes
            
        Returns:
            True if valid PDF, False otherwise
        """
        if not PDF_SUPPORT_AVAILABLE:
            return False
        
        try:
            if isinstance(pdf_input, (str, Path)):
                doc = fitz.open(str(pdf_input))
            elif isinstance(pdf_input, bytes):
                doc = fitz.open(stream=pdf_input, filetype="pdf")
            else:
                return False
            
            # Check if document has pages
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
            
        except Exception:
            return False
    
    def get_pdf_info(self, pdf_input: Union[str, Path, bytes]) -> dict:
        """
        Get PDF metadata and information using PyMuPDF.
        
        Args:
            pdf_input: PDF file path or bytes
            
        Returns:
            Dictionary with PDF information
        """
        if not PDF_SUPPORT_AVAILABLE:
            raise ImportError("PyMuPDF is required for PDF processing")
        
        try:
            if isinstance(pdf_input, (str, Path)):
                doc = fitz.open(str(pdf_input))
            elif isinstance(pdf_input, bytes):
                doc = fitz.open(stream=pdf_input, filetype="pdf")
            else:
                raise ValueError(f"Unsupported PDF input type: {type(pdf_input)}")
            
            info = {
                "page_count": len(doc),
                "metadata": doc.metadata,
                "is_encrypted": doc.is_encrypted,
                "is_pdf": doc.is_pdf,
                "page_sizes": []
            }
            
            # Get page sizes (first 5 pages for efficiency)
            for page_num in range(min(5, len(doc))):
                page = doc[page_num]
                rect = page.rect
                info["page_sizes"].append({
                    "page": page_num + 1,
                    "width": rect.width,
                    "height": rect.height
                })
            
            doc.close()
            return info
            
        except Exception as e:
            raise Exception(f"Failed to get PDF info: {str(e)}")


# Global instance
if PDF_SUPPORT_AVAILABLE:
    pdf_processor = PDFProcessor()
else:
    pdf_processor = None 