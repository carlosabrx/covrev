"""
Regex-based covenant section extraction from legal agreements.
Uses pattern matching to identify and extract specific covenant sections.
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class CovenantSection:
    """Represents an extracted covenant section."""
    section_type: str
    title: str
    content: str
    start_pos: int
    end_pos: int
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "section_type": self.section_type,
            "title": self.title,
            "content": self.content,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "confidence": self.confidence
        }


class RegexCovenantExtractor:
    """Extract covenant sections using regex patterns."""
    
    def __init__(self):
        # Define covenant patterns with variations
        self.covenant_patterns = {
            "restricted_payments": {
                "patterns": [
                    r"(?i)(restricted\s+payments?|dividend\s+restrictions?|distribution\s+limitations?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(restricted\s+payments?|limitations?\s+on\s+dividends?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(?:covenants?\s+regarding|limitations?\s+on)\s+(payments?|dividends?|distributions?)[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["restricted payment", "dividend", "distribution", "payment restriction"],
                "section_indicators": ["shall not", "may not", "prohibited", "limitation", "restriction"]
            },
            "change_of_control": {
                "patterns": [
                    r"(?i)(change\s+(?:of|in)\s+control)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(change\s+(?:of|in)\s+control)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(?:upon|in\s+the\s+event\s+of)\s+(?:a\s+)?(change\s+(?:of|in)\s+control)[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["change of control", "change in control", "control change", "acquisition"],
                "section_indicators": ["means", "shall mean", "defined as", "constitutes", "triggers"]
            },
            "debt_incurrence": {
                "patterns": [
                    r"(?i)(incurrence\s+of\s+(?:debt|indebtedness)|debt\s+incurrence)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(limitations?\s+on\s+(?:debt|indebtedness))[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(additional\s+(?:debt|indebtedness)|borrowing\s+restrictions?)[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["debt", "indebtedness", "borrowing", "leverage", "debt incurrence"],
                "section_indicators": ["shall not incur", "may not incur", "limitation", "ratio", "permitted"]
            },
            "asset_sales": {
                "patterns": [
                    r"(?i)(asset\s+sales?|sale\s+of\s+assets?|disposition\s+of\s+assets?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(limitations?\s+on\s+asset\s+sales?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(restrictions?\s+on\s+(?:sales?|dispositions?)\s+of\s+(?:assets?|property))[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["asset sale", "disposition", "transfer of assets", "sale of property"],
                "section_indicators": ["shall not sell", "may not dispose", "permitted asset sale", "exceptions"]
            },
            "merger_restrictions": {
                "patterns": [
                    r"(?i)(merger\s+(?:restrictions?|covenants?)|consolidation\s+restrictions?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(mergers?\s+and\s+consolidations?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(limitations?\s+on\s+(?:mergers?|consolidations?|amalgamations?))[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["merger", "consolidation", "amalgamation", "combination"],
                "section_indicators": ["shall not merge", "may not consolidate", "prohibited", "permitted merger"]
            },
            "investments": {
                "patterns": [
                    r"(?i)(permitted\s+investments?|investment\s+restrictions?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(limitations?\s+on\s+investments?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(restrictions?\s+on\s+investments?|investment\s+covenants?)[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["investment", "capital expenditure", "acquisition", "equity investment"],
                "section_indicators": ["shall not invest", "permitted investments", "investment basket", "limitations"]
            },
            "liens": {
                "patterns": [
                    r"(?i)(liens?\s+(?:restrictions?|covenants?)|negative\s+pledge)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(limitations?\s+on\s+liens?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(permitted\s+liens?|security\s+interests?\s+restrictions?)[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["lien", "security interest", "encumbrance", "pledge", "mortgage"],
                "section_indicators": ["shall not create", "permitted liens", "negative pledge", "exceptions"]
            },
            "transactions_with_affiliates": {
                "patterns": [
                    r"(?i)(transactions?\s+with\s+affiliates?|affiliate\s+transactions?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)section\s*\d+\.?\d*\s*[-–—]?\s*(affiliate\s+transactions?)[:\s]*([^.]+(?:\.[^.]+){0,10})",
                    r"(?i)(related\s+party\s+transactions?|intercompany\s+transactions?)[:\s]*([^.]+(?:\.[^.]+){0,10})"
                ],
                "keywords": ["affiliate", "related party", "intercompany", "subsidiary transaction"],
                "section_indicators": ["arm's length", "fair market value", "prohibited", "permitted"]
            }
        }
        
        # Section boundary patterns
        self.section_boundaries = [
            r"(?i)(?:section|article|clause)\s+\d+(?:\.\d+)*",
            r"(?i)(?:section|article|clause)\s+[A-Z](?:\.\d+)*",
            r"\n\s*\d+\.\d+\s+[A-Z]",
            r"\n\s*[A-Z]\.\s+[A-Z]"
        ]
    
    def extract_sections(self, text: str) -> List[CovenantSection]:
        """Extract all covenant sections from text."""
        sections = []
        
        for covenant_type, config in self.covenant_patterns.items():
            console.print(f"[cyan]Searching for {covenant_type.replace('_', ' ').title()} sections...[/cyan]")
            
            for pattern in config["patterns"]:
                matches = list(re.finditer(pattern, text, re.MULTILINE | re.DOTALL))
                
                for match in matches:
                    # Extract the full section content
                    section_content = self._extract_full_section(text, match.start(), match.end())
                    
                    # Calculate confidence based on keyword presence
                    confidence = self._calculate_confidence(section_content, config)
                    
                    if confidence > 0.3:  # Minimum confidence threshold
                        section = CovenantSection(
                            section_type=covenant_type,
                            title=match.group(1) if match.groups() else covenant_type.replace('_', ' ').title(),
                            content=section_content,
                            start_pos=match.start(),
                            end_pos=match.start() + len(section_content),
                            confidence=confidence
                        )
                        sections.append(section)
                        console.print(f"[green]✓ Found {covenant_type} section with {confidence:.1%} confidence[/green]")
        
        # Remove duplicates and overlapping sections
        sections = self._deduplicate_sections(sections)
        
        return sections
    
    def _extract_full_section(self, text: str, start_pos: int, initial_end: int) -> str:
        """Extract the complete section content, including multi-paragraph content."""
        # Look for the next section boundary
        next_section_pos = len(text)
        
        for boundary_pattern in self.section_boundaries:
            matches = re.finditer(boundary_pattern, text[initial_end:])
            for match in matches:
                pos = initial_end + match.start()
                if pos < next_section_pos:
                    next_section_pos = pos
                    break
        
        # Extract content up to the next section or a reasonable limit
        max_length = 5000  # Maximum characters for a section
        end_pos = min(next_section_pos, start_pos + max_length)
        
        # Try to end at a paragraph boundary
        section_text = text[start_pos:end_pos]
        last_para = section_text.rfind('\n\n')
        if last_para > len(section_text) * 0.7:  # If we're past 70% of the content
            section_text = section_text[:last_para]
        
        return section_text.strip()
    
    def _calculate_confidence(self, text: str, config: Dict) -> float:
        """Calculate confidence score based on keyword presence."""
        text_lower = text.lower()
        keyword_score = 0
        indicator_score = 0
        
        # Check for keywords
        for keyword in config["keywords"]:
            if keyword.lower() in text_lower:
                keyword_score += 1
        
        # Check for section indicators
        for indicator in config["section_indicators"]:
            if indicator.lower() in text_lower:
                indicator_score += 1
        
        # Calculate weighted confidence
        keyword_weight = 0.6
        indicator_weight = 0.4
        
        keyword_confidence = min(1.0, keyword_score / max(1, len(config["keywords"])))
        indicator_confidence = min(1.0, indicator_score / max(1, len(config["section_indicators"])))
        
        return (keyword_confidence * keyword_weight + indicator_confidence * indicator_weight)
    
    def _deduplicate_sections(self, sections: List[CovenantSection]) -> List[CovenantSection]:
        """Remove duplicate and overlapping sections."""
        if not sections:
            return []
        
        # Sort by start position
        sections.sort(key=lambda x: x.start_pos)
        
        deduplicated = []
        for section in sections:
            # Check if this section overlaps with any already added
            overlaps = False
            for existing in deduplicated:
                if (section.start_pos >= existing.start_pos and 
                    section.start_pos < existing.end_pos):
                    # If overlapping, keep the one with higher confidence
                    if section.confidence > existing.confidence:
                        deduplicated.remove(existing)
                    else:
                        overlaps = True
                        break
            
            if not overlaps:
                deduplicated.append(section)
        
        return deduplicated
    
    def extract_by_type(self, text: str, covenant_type: str) -> List[CovenantSection]:
        """Extract sections of a specific covenant type."""
        if covenant_type not in self.covenant_patterns:
            raise ValueError(f"Unknown covenant type: {covenant_type}")
        
        sections = []
        config = self.covenant_patterns[covenant_type]
        
        for pattern in config["patterns"]:
            matches = list(re.finditer(pattern, text, re.MULTILINE | re.DOTALL))
            
            for match in matches:
                section_content = self._extract_full_section(text, match.start(), match.end())
                confidence = self._calculate_confidence(section_content, config)
                
                if confidence > 0.3:
                    section = CovenantSection(
                        section_type=covenant_type,
                        title=match.group(1) if match.groups() else covenant_type.replace('_', ' ').title(),
                        content=section_content,
                        start_pos=match.start(),
                        end_pos=match.start() + len(section_content),
                        confidence=confidence
                    )
                    sections.append(section)
        
        return self._deduplicate_sections(sections)
    
    def display_results(self, sections: List[CovenantSection]):
        """Display extracted sections in a formatted table."""
        if not sections:
            console.print("[yellow]No covenant sections found.[/yellow]")
            return
        
        table = Table(title="Extracted Covenant Sections", show_lines=True)
        table.add_column("Type", style="cyan", width=20)
        table.add_column("Title", style="green", width=30)
        table.add_column("Content Preview", style="white", width=50)
        table.add_column("Confidence", style="yellow", width=10)
        
        for section in sections:
            content_preview = section.content[:200] + "..." if len(section.content) > 200 else section.content
            content_preview = content_preview.replace('\n', ' ')
            
            table.add_row(
                section.section_type.replace('_', ' ').title(),
                section.title,
                content_preview,
                f"{section.confidence:.1%}"
            )
        
        console.print(table)
    
    def save_results(self, sections: List[CovenantSection], output_path: Union[str, Path]):
        """Save extracted sections to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "total_sections": len(sections),
            "sections_by_type": {},
            "sections": [section.to_dict() for section in sections]
        }
        
        # Count sections by type
        for section in sections:
            section_type = section.section_type
            if section_type not in results["sections_by_type"]:
                results["sections_by_type"][section_type] = 0
            results["sections_by_type"][section_type] += 1
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✓ Results saved to {output_path}[/green]")


def extract_covenants_regex(text: str, covenant_types: Optional[List[str]] = None) -> List[CovenantSection]:
    """Convenience function to extract covenant sections."""
    extractor = RegexCovenantExtractor()
    
    if covenant_types:
        sections = []
        for covenant_type in covenant_types:
            sections.extend(extractor.extract_by_type(text, covenant_type))
        return sections
    else:
        return extractor.extract_sections(text)


if __name__ == "__main__":
    # Test the regex extractor
    sample_text = """
    Section 4.1 - Restricted Payments
    
    The Company shall not, and shall not permit any of its Subsidiaries to, directly or indirectly:
    (a) declare or pay any dividend or make any distribution on account of the Company's or any Subsidiary's Equity Interests;
    (b) purchase, redeem or otherwise acquire or retire for value any Equity Interests of the Company;
    (c) make any principal payment on, or redeem, repurchase, defease or otherwise acquire or retire for value, in each case prior to any scheduled repayment, sinking fund payment or maturity, any Subordinated Indebtedness.
    
    Section 5.2 - Change of Control
    
    Upon the occurrence of a Change of Control, each Holder shall have the right to require the Company to purchase all or any part of such Holder's Notes at a purchase price in cash equal to 101% of the aggregate principal amount thereof plus accrued and unpaid interest.
    
    "Change of Control" means the occurrence of any of the following:
    (a) the direct or indirect sale, lease, transfer, conveyance or other disposition of all or substantially all of the properties or assets of the Company;
    (b) the adoption of a plan relating to the liquidation or dissolution of the Company.
    """
    
    extractor = RegexCovenantExtractor()
    sections = extractor.extract_sections(sample_text)
    extractor.display_results(sections)