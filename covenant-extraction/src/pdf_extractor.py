"""
PDF text extraction utilities for covenant section extraction.
Supports multiple PDF processing libraries for robust text extraction.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import re

import PyPDF2
import pdfplumber
from rich.console import Console
from rich.progress import track

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class PDFExtractor:
    """Extracts text from PDF files using multiple methods for robustness."""
    
    def __init__(self):
        self.pypdf2_enabled = True
        self.pdfplumber_enabled = True
    
    def extract_text_pypdf2(self, pdf_path: Union[str, Path]) -> str:
        """Extract text using PyPDF2."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in track(range(num_pages), description="Extracting with PyPDF2"):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
                    
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
            return ""
        
        return text
    
    def extract_text_pdfplumber(self, pdf_path: Union[str, Path]) -> str:
        """Extract text using pdfplumber (often better for complex layouts)."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(track(pdf.pages, description="Extracting with pdfplumber")):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
                        
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return ""
        
        return text
    
    def extract_text(self, pdf_path: Union[str, Path], method: str = "best") -> Dict[str, str]:
        """
        Extract text from PDF using specified method.
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method - "pypdf2", "pdfplumber", "both", or "best"
            
        Returns:
            Dictionary with extracted text and metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        results = {
            "file_path": str(pdf_path),
            "file_name": pdf_path.name,
            "text": "",
            "method_used": method,
            "success": False
        }
        
        if method == "pypdf2" or method == "both":
            console.print(f"[cyan]Extracting text from {pdf_path.name} using PyPDF2...[/cyan]")
            pypdf2_text = self.extract_text_pypdf2(pdf_path)
            if pypdf2_text and method == "pypdf2":
                results["text"] = pypdf2_text
                results["success"] = True
                return results
        
        if method == "pdfplumber" or method == "both":
            console.print(f"[cyan]Extracting text from {pdf_path.name} using pdfplumber...[/cyan]")
            pdfplumber_text = self.extract_text_pdfplumber(pdf_path)
            if pdfplumber_text and method == "pdfplumber":
                results["text"] = pdfplumber_text
                results["success"] = True
                return results
        
        if method == "best" or method == "both":
            # Try pdfplumber first (usually better), fall back to PyPDF2
            console.print(f"[cyan]Extracting text from {pdf_path.name} using best method...[/cyan]")
            pdfplumber_text = self.extract_text_pdfplumber(pdf_path)
            if pdfplumber_text:
                results["text"] = pdfplumber_text
                results["method_used"] = "pdfplumber"
                results["success"] = True
            else:
                pypdf2_text = self.extract_text_pypdf2(pdf_path)
                if pypdf2_text:
                    results["text"] = pypdf2_text
                    results["method_used"] = "pypdf2"
                    results["success"] = True
        
        if method == "both":
            results["pypdf2_text"] = pypdf2_text if 'pypdf2_text' in locals() else ""
            results["pdfplumber_text"] = pdfplumber_text if 'pdfplumber_text' in locals() else ""
            results["text"] = pdfplumber_text if pdfplumber_text else pypdf2_text
            results["success"] = bool(results["text"])
        
        return results
    
    def extract_pages(self, pdf_path: Union[str, Path], start_page: int = 1, 
                     end_page: Optional[int] = None) -> str:
        """Extract text from specific page range."""
        pdf_path = Path(pdf_path)
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                end_page = end_page or total_pages
                
                # Adjust for 0-based indexing
                start_idx = max(0, start_page - 1)
                end_idx = min(total_pages, end_page)
                
                for page_num in range(start_idx, end_idx):
                    page = pdf.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
                        
        except Exception as e:
            logger.error(f"Page extraction failed: {e}")
            
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR issues
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between camelCase
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def extract_and_clean(self, pdf_path: Union[str, Path], method: str = "best") -> str:
        """Extract text and apply cleaning."""
        results = self.extract_text(pdf_path, method)
        if results["success"]:
            return self.clean_text(results["text"])
        return ""


def extract_pdf_batch(pdf_paths: List[Union[str, Path]], method: str = "best") -> Dict[str, Dict]:
    """Extract text from multiple PDFs in batch."""
    extractor = PDFExtractor()
    results = {}
    
    for pdf_path in pdf_paths:
        pdf_path = Path(pdf_path)
        console.print(f"\n[bold blue]Processing: {pdf_path.name}[/bold blue]")
        
        try:
            result = extractor.extract_text(pdf_path, method)
            results[pdf_path.name] = result
            
            if result["success"]:
                console.print(f"[green]✓ Successfully extracted {len(result['text'])} characters[/green]")
            else:
                console.print(f"[red]✗ Failed to extract text[/red]")
                
        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            results[pdf_path.name] = {
                "file_path": str(pdf_path),
                "file_name": pdf_path.name,
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    return results


if __name__ == "__main__":
    # Test the extractor
    extractor = PDFExtractor()
    
    # Example usage
    test_pdf = Path("../data/sample_agreement.pdf")
    if test_pdf.exists():
        result = extractor.extract_text(test_pdf, method="best")
        if result["success"]:
            console.print(f"[green]Extracted {len(result['text'])} characters using {result['method_used']}[/green]")
            console.print("\n[yellow]First 500 characters:[/yellow]")
            console.print(result["text"][:500])
    else:
        console.print("[yellow]No test PDF found. Please add a sample PDF to data/sample_agreement.pdf[/yellow]")