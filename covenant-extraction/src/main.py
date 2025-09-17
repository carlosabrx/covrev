#!/usr/bin/env python3
"""
Main script for testing covenant extraction methods.
Compares regex-based and LLM-powered extraction approaches.
"""

import click
import json
from pathlib import Path
from typing import List, Optional
import os
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Import our modules
from pdf_extractor import PDFExtractor, extract_pdf_batch
from regex_extractor import RegexCovenantExtractor, CovenantSection
from llm_extractor import LLMCovenantExtractor, LLMCovenantSection

# Load environment variables
load_dotenv()

console = Console()


def compare_extraction_methods(pdf_path: Path, use_llm: bool = True) -> dict:
    """Compare regex and LLM extraction methods on a single PDF."""
    
    # Extract text from PDF
    console.print(f"\n[bold blue]Processing: {pdf_path.name}[/bold blue]")
    
    pdf_extractor = PDFExtractor()
    pdf_result = pdf_extractor.extract_text(pdf_path, method="best")
    
    if not pdf_result["success"]:
        console.print(f"[red]Failed to extract text from {pdf_path.name}[/red]")
        return {}
    
    text = pdf_result["text"]
    console.print(f"[green]✓ Extracted {len(text)} characters from PDF[/green]")
    
    # Regex extraction
    console.print("\n[cyan]Running Regex-based extraction...[/cyan]")
    regex_extractor = RegexCovenantExtractor()
    regex_sections = regex_extractor.extract_sections(text)
    console.print(f"[green]✓ Regex found {len(regex_sections)} covenant sections[/green]")
    
    # LLM extraction (if API key available and enabled)
    llm_sections = []
    if use_llm and os.getenv("OPENAI_API_KEY"):
        console.print("\n[cyan]Running LLM-powered extraction...[/cyan]")
        try:
            llm_extractor = LLMCovenantExtractor(model_name="gpt-3.5-turbo")
            llm_sections = llm_extractor.extract_sections(text)
            console.print(f"[green]✓ LLM found {len(llm_sections)} covenant sections[/green]")
        except Exception as e:
            console.print(f"[red]LLM extraction failed: {e}[/red]")
    else:
        if not os.getenv("OPENAI_API_KEY"):
            console.print("[yellow]Skipping LLM extraction (no OPENAI_API_KEY found)[/yellow]")
        else:
            console.print("[yellow]Skipping LLM extraction (disabled)[/yellow]")
    
    return {
        "pdf_name": pdf_path.name,
        "text_length": len(text),
        "regex_sections": regex_sections,
        "llm_sections": llm_sections
    }


def display_comparison_results(results: dict):
    """Display comparison results in a formatted table."""
    if not results:
        return
    
    # Create comparison table
    table = Table(title=f"Extraction Results: {results['pdf_name']}", show_lines=True)
    table.add_column("Method", style="cyan", width=15)
    table.add_column("Sections Found", style="green", width=15)
    table.add_column("Types Found", style="yellow", width=40)
    
    # Regex results
    regex_types = {}
    for section in results["regex_sections"]:
        if section.section_type not in regex_types:
            regex_types[section.section_type] = 0
        regex_types[section.section_type] += 1
    
    regex_types_str = "\n".join([f"{k}: {v}" for k, v in regex_types.items()])
    table.add_row("Regex", str(len(results["regex_sections"])), regex_types_str)
    
    # LLM results
    if results["llm_sections"]:
        llm_types = {}
        for section in results["llm_sections"]:
            if section.section_type not in llm_types:
                llm_types[section.section_type] = 0
            llm_types[section.section_type] += 1
        
        llm_types_str = "\n".join([f"{k}: {v}" for k, v in llm_types.items()])
        table.add_row("LLM", str(len(results["llm_sections"])), llm_types_str)
    
    console.print(table)


def save_comparison_results(results: dict, output_dir: Path):
    """Save comparison results to JSON files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save regex results
    regex_output = {
        "method": "regex",
        "pdf_name": results["pdf_name"],
        "sections": [
            {
                "section_type": s.section_type,
                "title": s.title,
                "content": s.content[:500] + "..." if len(s.content) > 500 else s.content,
                "confidence": s.confidence
            }
            for s in results["regex_sections"]
        ]
    }
    
    regex_file = output_dir / f"regex_results_{timestamp}.json"
    with open(regex_file, 'w') as f:
        json.dump(regex_output, f, indent=2)
    console.print(f"[green]✓ Saved regex results to {regex_file}[/green]")
    
    # Save LLM results if available
    if results["llm_sections"]:
        llm_output = {
            "method": "llm",
            "pdf_name": results["pdf_name"],
            "sections": [
                {
                    "section_type": s.section_type,
                    "title": s.title,
                    "content": s.content[:500] + "..." if len(s.content) > 500 else s.content,
                    "confidence": s.confidence,
                    "key_terms": s.key_terms,
                    "reasoning": s.reasoning
                }
                for s in results["llm_sections"]
            ]
        }
        
        llm_file = output_dir / f"llm_results_{timestamp}.json"
        with open(llm_file, 'w') as f:
            json.dump(llm_output, f, indent=2)
        console.print(f"[green]✓ Saved LLM results to {llm_file}[/green]")


@click.command()
@click.option('--pdf', '-p', type=click.Path(exists=True), help='Path to PDF file')
@click.option('--data-dir', '-d', type=click.Path(exists=True), 
              default='data', help='Directory containing PDFs')
@click.option('--output-dir', '-o', type=click.Path(), 
              default='output', help='Directory for output files')
@click.option('--use-llm/--no-llm', default=True, help='Enable/disable LLM extraction')
@click.option('--covenant-type', '-t', help='Extract specific covenant type')
def main(pdf, data_dir, output_dir, use_llm, covenant_type):
    """
    Test covenant extraction methods on PDF agreements.
    
    Examples:
        python main.py --pdf data/sample_loan_agreement.pdf
        python main.py --data-dir data --use-llm
        python main.py --pdf data/sample.pdf --covenant-type restricted_payments
    """
    
    # Setup output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    console.print(Panel.fit(
        "[bold cyan]Covenant Extraction Testing Tool[/bold cyan]\n"
        "Comparing Regex-based and LLM-powered extraction methods",
        title="Welcome"
    ))
    
    # Get PDFs to process
    if pdf:
        pdf_files = [Path(pdf)]
    else:
        data_path = Path(data_dir)
        pdf_files = list(data_path.glob("*.pdf"))
        if not pdf_files:
            console.print(f"[red]No PDF files found in {data_dir}[/red]")
            return
    
    console.print(f"\n[cyan]Found {len(pdf_files)} PDF(s) to process[/cyan]")
    
    # Process each PDF
    all_results = []
    for pdf_path in pdf_files:
        results = compare_extraction_methods(pdf_path, use_llm=use_llm)
        if results:
            all_results.append(results)
            display_comparison_results(results)
            save_comparison_results(results, output_path)
    
    # Summary
    console.print(f"\n[bold green]Processing complete! Results saved to {output_path}[/bold green]")
    
    # Display overall statistics
    if all_results:
        total_regex_sections = sum(len(r["regex_sections"]) for r in all_results)
        total_llm_sections = sum(len(r["llm_sections"]) for r in all_results)
        
        console.print(f"\n[bold]Overall Statistics:[/bold]")
        console.print(f"  Total PDFs processed: {len(all_results)}")
        console.print(f"  Total regex sections found: {total_regex_sections}")
        if any(r["llm_sections"] for r in all_results):
            console.print(f"  Total LLM sections found: {total_llm_sections}")


if __name__ == "__main__":
    main()