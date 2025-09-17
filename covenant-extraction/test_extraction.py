#!/usr/bin/env python3
"""
Quick test script to demonstrate covenant extraction functionality.
"""

import sys
from pathlib import Path
from rich.console import Console

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_extractor import PDFExtractor
from regex_extractor import RegexCovenantExtractor
from llm_extractor import LLMCovenantExtractor
import os

console = Console()


def test_regex_extraction():
    """Test regex-based extraction on sample text."""
    console.print("\n[bold cyan]Testing Regex-based Extraction[/bold cyan]")
    
    sample_text = """
    Section 4.1 - Restricted Payments
    
    The Company shall not, and shall not permit any of its Subsidiaries to, directly or indirectly:
    (a) declare or pay any dividend or make any distribution on account of the Company's Equity Interests;
    (b) purchase, redeem or otherwise acquire or retire for value any Equity Interests of the Company;
    
    Section 5.2 - Change of Control
    
    Upon the occurrence of a Change of Control, each Holder shall have the right to require the Company 
    to purchase all Notes at a purchase price in cash equal to 101% of the aggregate principal amount.
    
    Section 6.1 - Limitation on Liens
    
    The Company will not create, incur, assume or suffer to exist any Lien of any kind securing 
    Indebtedness on any asset now owned or hereafter acquired, except Permitted Liens.
    """
    
    extractor = RegexCovenantExtractor()
    sections = extractor.extract_sections(sample_text)
    
    console.print(f"\n[green]Found {len(sections)} covenant sections:[/green]")
    for section in sections:
        console.print(f"  - {section.section_type}: {section.title} (confidence: {section.confidence:.1%})")
    
    extractor.display_results(sections)


def test_pdf_extraction():
    """Test PDF extraction on sample files."""
    console.print("\n[bold cyan]Testing PDF Extraction[/bold cyan]")
    
    # Check if sample PDFs exist
    data_dir = Path("data")
    if not data_dir.exists():
        console.print("[yellow]No data directory found. Creating sample PDFs...[/yellow]")
        from create_sample_pdfs import create_sample_pdfs
        create_sample_pdfs()
    
    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        console.print("[red]No PDF files found in data directory[/red]")
        return
    
    # Test extraction on first PDF
    pdf_path = pdf_files[0]
    console.print(f"\n[cyan]Extracting text from: {pdf_path.name}[/cyan]")
    
    extractor = PDFExtractor()
    result = extractor.extract_text(pdf_path)
    
    if result["success"]:
        console.print(f"[green]✓ Successfully extracted {len(result['text'])} characters[/green]")
        console.print(f"[green]✓ Method used: {result['method_used']}[/green]")
        
        # Show preview
        preview = result['text'][:500] + "..." if len(result['text']) > 500 else result['text']
        console.print(f"\n[yellow]Preview:[/yellow]\n{preview}")
        
        # Test covenant extraction on the PDF text
        console.print("\n[cyan]Extracting covenants from PDF text...[/cyan]")
        regex_extractor = RegexCovenantExtractor()
        sections = regex_extractor.extract_sections(result['text'])
        console.print(f"[green]✓ Found {len(sections)} covenant sections[/green]")
        
        # Display summary
        section_types = {}
        for section in sections:
            if section.section_type not in section_types:
                section_types[section.section_type] = 0
            section_types[section.section_type] += 1
        
        console.print("\n[bold]Covenant types found:[/bold]")
        for stype, count in section_types.items():
            console.print(f"  - {stype.replace('_', ' ').title()}: {count}")
    else:
        console.print(f"[red]✗ Failed to extract text from PDF[/red]")


def test_llm_extraction():
    """Test LLM extraction if API key is available."""
    console.print("\n[bold cyan]Testing LLM-powered Extraction[/bold cyan]")
    
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[yellow]No OPENAI_API_KEY found. Skipping LLM test.[/yellow]")
        console.print("[yellow]To test LLM extraction:[/yellow]")
        console.print("  1. Copy .env.example to .env")
        console.print("  2. Add your OpenAI API key")
        return
    
    sample_text = """
    The Borrower agrees to the following financial covenants:
    
    The Borrower shall not make any distributions to equity holders or repurchase any shares 
    if such payment would cause the leverage ratio to exceed 3.0x.
    
    In the event that any person or group acquires more than 50% of the voting power of the 
    Borrower, the Lender may declare all obligations immediately due and payable.
    """
    
    try:
        extractor = LLMCovenantExtractor(model_name="gpt-3.5-turbo")
        sections = extractor.extract_sections(sample_text)
        
        console.print(f"\n[green]Found {len(sections)} covenant sections:[/green]")
        for section in sections:
            console.print(f"  - {section.section_type}: {section.title}")
            console.print(f"    Confidence: {section.confidence:.1%}")
            console.print(f"    Key terms: {', '.join(section.key_terms[:3])}")
            console.print(f"    Reasoning: {section.reasoning[:100]}...")
            
    except Exception as e:
        console.print(f"[red]LLM extraction failed: {e}[/red]")


def main():
    """Run all tests."""
    console.print("[bold green]Covenant Extraction Test Suite[/bold green]")
    console.print("=" * 50)
    
    # Test regex extraction
    test_regex_extraction()
    
    # Test PDF extraction
    test_pdf_extraction()
    
    # Test LLM extraction
    test_llm_extraction()
    
    console.print("\n[bold green]✓ All tests completed![/bold green]")
    console.print("\n[cyan]To run full extraction on all PDFs:[/cyan]")
    console.print("  python src/main.py --data-dir data")


if __name__ == "__main__":
    main()