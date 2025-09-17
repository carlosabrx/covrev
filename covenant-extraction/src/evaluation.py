"""
Evaluation and comparison utilities for covenant extraction results.
Provides metrics and analysis tools for comparing extraction methods.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import difflib
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import pandas as pd

console = Console()


@dataclass
class ExtractionMetrics:
    """Metrics for evaluating extraction quality."""
    precision: float
    recall: float
    f1_score: float
    coverage: float
    avg_confidence: float
    
    def to_dict(self) -> Dict:
        return {
            "precision": round(self.precision, 3),
            "recall": round(self.recall, 3),
            "f1_score": round(self.f1_score, 3),
            "coverage": round(self.coverage, 3),
            "avg_confidence": round(self.avg_confidence, 3)
        }


class ExtractionEvaluator:
    """Evaluate and compare extraction results."""
    
    def __init__(self):
        self.covenant_types = [
            "restricted_payments",
            "change_of_control",
            "debt_incurrence",
            "asset_sales",
            "merger_restrictions",
            "investments",
            "liens",
            "transactions_with_affiliates"
        ]
    
    def compare_sections(self, regex_sections: List, llm_sections: List) -> Dict:
        """Compare sections extracted by different methods."""
        comparison = {
            "total_regex": len(regex_sections),
            "total_llm": len(llm_sections),
            "overlapping": 0,
            "regex_only": 0,
            "llm_only": 0,
            "type_comparison": {},
            "confidence_comparison": {}
        }
        
        # Group sections by type
        regex_by_type = defaultdict(list)
        llm_by_type = defaultdict(list)
        
        for section in regex_sections:
            regex_by_type[section.section_type].append(section)
        
        for section in llm_sections:
            llm_by_type[section.section_type].append(section)
        
        # Compare by type
        all_types = set(regex_by_type.keys()) | set(llm_by_type.keys())
        
        for covenant_type in all_types:
            regex_count = len(regex_by_type.get(covenant_type, []))
            llm_count = len(llm_by_type.get(covenant_type, []))
            
            # Calculate overlap based on content similarity
            overlap_count = self._count_overlapping_sections(
                regex_by_type.get(covenant_type, []),
                llm_by_type.get(covenant_type, [])
            )
            
            comparison["type_comparison"][covenant_type] = {
                "regex_count": regex_count,
                "llm_count": llm_count,
                "overlap": overlap_count,
                "regex_only": max(0, regex_count - overlap_count),
                "llm_only": max(0, llm_count - overlap_count)
            }
            
            comparison["overlapping"] += overlap_count
        
        comparison["regex_only"] = comparison["total_regex"] - comparison["overlapping"]
        comparison["llm_only"] = comparison["total_llm"] - comparison["overlapping"]
        
        # Compare average confidence
        if regex_sections:
            comparison["confidence_comparison"]["regex_avg"] = sum(s.confidence for s in regex_sections) / len(regex_sections)
        else:
            comparison["confidence_comparison"]["regex_avg"] = 0.0
            
        if llm_sections:
            comparison["confidence_comparison"]["llm_avg"] = sum(s.confidence for s in llm_sections) / len(llm_sections)
        else:
            comparison["confidence_comparison"]["llm_avg"] = 0.0
        
        return comparison
    
    def _count_overlapping_sections(self, sections1: List, sections2: List) -> int:
        """Count overlapping sections based on content similarity."""
        overlap_count = 0
        matched_indices = set()
        
        for s1 in sections1:
            best_match_idx = -1
            best_similarity = 0.0
            
            for idx, s2 in enumerate(sections2):
                if idx in matched_indices:
                    continue
                    
                similarity = self._calculate_similarity(s1.content, s2.content)
                if similarity > best_similarity and similarity > 0.6:  # 60% threshold
                    best_similarity = similarity
                    best_match_idx = idx
            
            if best_match_idx >= 0:
                matched_indices.add(best_match_idx)
                overlap_count += 1
        
        return overlap_count
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using SequenceMatcher."""
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def evaluate_extraction_quality(self, sections: List, ground_truth: Optional[Dict] = None) -> ExtractionMetrics:
        """Evaluate extraction quality metrics."""
        if not sections:
            return ExtractionMetrics(0.0, 0.0, 0.0, 0.0, 0.0)
        
        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in sections) / len(sections)
        
        # Calculate type coverage
        types_found = set(s.section_type for s in sections)
        coverage = len(types_found) / len(self.covenant_types)
        
        # If ground truth is provided, calculate precision/recall
        if ground_truth:
            true_positives = 0
            false_positives = 0
            false_negatives = 0
            
            # This would require ground truth annotations
            # For now, we'll use heuristics
            precision = avg_confidence  # Use confidence as proxy
            recall = coverage  # Use coverage as proxy
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        else:
            # Without ground truth, use heuristics
            precision = avg_confidence
            recall = coverage
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return ExtractionMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            coverage=coverage,
            avg_confidence=avg_confidence
        )
    
    def display_comparison(self, comparison: Dict):
        """Display comparison results in a formatted way."""
        # Overview panel
        overview_text = (
            f"[bold]Total Sections:[/bold]\n"
            f"  Regex: {comparison['total_regex']}\n"
            f"  LLM: {comparison['total_llm']}\n\n"
            f"[bold]Overlap Analysis:[/bold]\n"
            f"  Overlapping: {comparison['overlapping']}\n"
            f"  Regex only: {comparison['regex_only']}\n"
            f"  LLM only: {comparison['llm_only']}\n\n"
            f"[bold]Confidence:[/bold]\n"
            f"  Regex avg: {comparison['confidence_comparison']['regex_avg']:.1%}\n"
            f"  LLM avg: {comparison['confidence_comparison']['llm_avg']:.1%}"
        )
        
        console.print(Panel(overview_text, title="Extraction Comparison Overview"))
        
        # Type comparison table
        if comparison["type_comparison"]:
            table = Table(title="Comparison by Covenant Type", show_lines=True)
            table.add_column("Covenant Type", style="cyan", width=25)
            table.add_column("Regex", style="green", justify="center")
            table.add_column("LLM", style="blue", justify="center")
            table.add_column("Overlap", style="yellow", justify="center")
            table.add_column("Regex Only", style="magenta", justify="center")
            table.add_column("LLM Only", style="red", justify="center")
            
            for cov_type, stats in comparison["type_comparison"].items():
                table.add_row(
                    cov_type.replace('_', ' ').title(),
                    str(stats["regex_count"]),
                    str(stats["llm_count"]),
                    str(stats["overlap"]),
                    str(stats["regex_only"]),
                    str(stats["llm_only"])
                )
            
            console.print(table)
    
    def generate_report(self, all_results: List[Dict], output_path: Path):
        """Generate a comprehensive evaluation report."""
        report = {
            "summary": {
                "total_pdfs": len(all_results),
                "total_regex_sections": 0,
                "total_llm_sections": 0,
                "avg_regex_confidence": 0.0,
                "avg_llm_confidence": 0.0
            },
            "by_document": [],
            "by_covenant_type": defaultdict(lambda: {"regex": 0, "llm": 0})
        }
        
        # Aggregate results
        total_regex_conf = 0
        total_llm_conf = 0
        regex_count = 0
        llm_count = 0
        
        for result in all_results:
            doc_summary = {
                "pdf_name": result["pdf_name"],
                "regex_sections": len(result["regex_sections"]),
                "llm_sections": len(result["llm_sections"])
            }
            
            # Count by type
            for section in result["regex_sections"]:
                report["by_covenant_type"][section.section_type]["regex"] += 1
                total_regex_conf += section.confidence
                regex_count += 1
            
            for section in result["llm_sections"]:
                report["by_covenant_type"][section.section_type]["llm"] += 1
                total_llm_conf += section.confidence
                llm_count += 1
            
            report["by_document"].append(doc_summary)
        
        # Update summary
        report["summary"]["total_regex_sections"] = regex_count
        report["summary"]["total_llm_sections"] = llm_count
        report["summary"]["avg_regex_confidence"] = total_regex_conf / regex_count if regex_count > 0 else 0.0
        report["summary"]["avg_llm_confidence"] = total_llm_conf / llm_count if llm_count > 0 else 0.0
        
        # Save report
        report_file = output_path / "evaluation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        console.print(f"[green]✓ Evaluation report saved to {report_file}[/green]")
        
        # Display summary
        console.print("\n[bold cyan]Evaluation Report Summary[/bold cyan]")
        console.print(f"Total PDFs processed: {report['summary']['total_pdfs']}")
        console.print(f"Total regex sections: {report['summary']['total_regex_sections']}")
        console.print(f"Total LLM sections: {report['summary']['total_llm_sections']}")
        console.print(f"Average regex confidence: {report['summary']['avg_regex_confidence']:.1%}")
        console.print(f"Average LLM confidence: {report['summary']['avg_llm_confidence']:.1%}")
        
        return report


def analyze_extraction_differences(regex_sections: List, llm_sections: List) -> List[Dict]:
    """Analyze specific differences between extraction methods."""
    differences = []
    
    # Find sections unique to regex
    for regex_section in regex_sections:
        found_similar = False
        for llm_section in llm_sections:
            if (regex_section.section_type == llm_section.section_type and
                difflib.SequenceMatcher(None, regex_section.content, llm_section.content).ratio() > 0.6):
                found_similar = True
                break
        
        if not found_similar:
            differences.append({
                "type": "regex_only",
                "section_type": regex_section.section_type,
                "title": regex_section.title,
                "confidence": regex_section.confidence,
                "reason": "Found by regex pattern matching but not by LLM"
            })
    
    # Find sections unique to LLM
    for llm_section in llm_sections:
        found_similar = False
        for regex_section in regex_sections:
            if (llm_section.section_type == regex_section.section_type and
                difflib.SequenceMatcher(None, llm_section.content, regex_section.content).ratio() > 0.6):
                found_similar = True
                break
        
        if not found_similar:
            differences.append({
                "type": "llm_only",
                "section_type": llm_section.section_type,
                "title": llm_section.title,
                "confidence": llm_section.confidence,
                "reason": f"LLM reasoning: {llm_section.reasoning if hasattr(llm_section, 'reasoning') else 'Context-based identification'}"
            })
    
    return differences


if __name__ == "__main__":
    # Test the evaluator
    console.print("[cyan]Covenant Extraction Evaluator Test[/cyan]")
    
    evaluator = ExtractionEvaluator()
    
    # Example: Load results from JSON files
    output_dir = Path("../output")
    if output_dir.exists():
        json_files = list(output_dir.glob("*.json"))
        if json_files:
            console.print(f"Found {len(json_files)} result files")
            # Load and analyze results
    else:
        console.print("[yellow]No output directory found. Run main.py first to generate results.[/yellow]")