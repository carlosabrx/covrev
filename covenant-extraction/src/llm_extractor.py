"""
LLM-powered covenant section extraction from legal agreements.
Uses OpenAI GPT models and LangChain for intelligent extraction.
"""

import os
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import tiktoken

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.progress import track
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()


class ExtractedCovenant(BaseModel):
    """Pydantic model for extracted covenant sections."""
    section_type: str = Field(description="Type of covenant (e.g., 'restricted_payments', 'change_of_control')")
    title: str = Field(description="Title or heading of the covenant section")
    content: str = Field(description="Full content of the covenant section")
    key_terms: List[str] = Field(description="Key terms and conditions identified")
    confidence: float = Field(description="Confidence score (0-1)")
    reasoning: str = Field(description="Explanation of why this was identified as a covenant section")
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))


class CovenantExtractionResult(BaseModel):
    """Container for multiple extracted covenants."""
    covenants: List[ExtractedCovenant]
    document_context: str = Field(description="Brief context about the document")


@dataclass
class LLMCovenantSection:
    """Dataclass for compatibility with regex extractor."""
    section_type: str
    title: str
    content: str
    key_terms: List[str]
    confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class LLMCovenantExtractor:
    """Extract covenant sections using LLM (GPT-4 or GPT-3.5)."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1):
        """
        Initialize the LLM extractor.
        
        Args:
            model_name: OpenAI model to use
            temperature: Temperature for generation (lower = more deterministic)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key
        )
        
        self.model_name = model_name
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=500,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Token counting
        self.encoding = tiktoken.encoding_for_model(model_name)
        
        # Define covenant types we're looking for
        self.covenant_types = {
            "restricted_payments": "Restrictions on dividends, distributions, or payments to equity holders",
            "change_of_control": "Provisions triggered by ownership changes or acquisitions",
            "debt_incurrence": "Limitations on taking on new debt or leverage ratios",
            "asset_sales": "Restrictions on selling or disposing of assets",
            "merger_restrictions": "Limitations on mergers, consolidations, or amalgamations",
            "investments": "Restrictions on investments or capital expenditures",
            "liens": "Limitations on creating liens or security interests",
            "transactions_with_affiliates": "Restrictions on related party transactions"
        }
        
        # Create the parser
        self.parser = PydanticOutputParser(pydantic_object=CovenantExtractionResult)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        
        # Create extraction prompt
        self.extraction_prompt = PromptTemplate(
            input_variables=["text", "covenant_types"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""You are a legal document analyst specializing in extracting covenant sections from agreements.

Analyze the following text and extract ALL covenant sections that match these types:
{covenant_types}

For each covenant section found:
1. Identify the specific covenant type
2. Extract the complete section title
3. Extract the FULL content (don't summarize, include all details)
4. List key terms and conditions
5. Provide a confidence score (0-1)
6. Explain your reasoning

Text to analyze:
{text}

{format_instructions}

Remember:
- Extract the COMPLETE content, not summaries
- Include all subsections and conditions
- Look for section headers, numbered lists, and defined terms
- Covenants often start with "The Company shall not..." or similar restrictive language
"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.extraction_prompt)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def extract_sections(self, text: str, chunk_size: Optional[int] = None) -> List[LLMCovenantSection]:
        """Extract all covenant sections from text."""
        console.print(f"[cyan]Processing document with {self.count_tokens(text)} tokens...[/cyan]")
        
        # Split text into manageable chunks if needed
        if chunk_size:
            self.text_splitter.chunk_size = chunk_size
            
        chunks = self.text_splitter.split_text(text)
        console.print(f"[cyan]Split into {len(chunks)} chunks for processing[/cyan]")
        
        all_sections = []
        
        for i, chunk in enumerate(track(chunks, description="Processing chunks")):
            try:
                # Format covenant types for prompt
                covenant_desc = "\n".join([f"- {k}: {v}" for k, v in self.covenant_types.items()])
                
                # Run extraction
                result = self.chain.run(text=chunk, covenant_types=covenant_desc)
                
                # Parse result
                try:
                    parsed_result = self.parser.parse(result)
                except Exception as parse_error:
                    console.print(f"[yellow]Fixing parser output for chunk {i+1}...[/yellow]")
                    parsed_result = self.fixing_parser.parse(result)
                
                # Convert to LLMCovenantSection objects
                for covenant in parsed_result.covenants:
                    section = LLMCovenantSection(
                        section_type=covenant.section_type,
                        title=covenant.title,
                        content=covenant.content,
                        key_terms=covenant.key_terms,
                        confidence=covenant.confidence,
                        reasoning=covenant.reasoning
                    )
                    all_sections.append(section)
                    console.print(f"[green]✓ Found {covenant.section_type} section with {covenant.confidence:.1%} confidence[/green]")
                    
            except Exception as e:
                console.print(f"[red]Error processing chunk {i+1}: {e}[/red]")
        
        # Deduplicate sections
        all_sections = self._deduplicate_sections(all_sections)
        
        return all_sections
    
    def extract_by_type(self, text: str, covenant_type: str) -> List[LLMCovenantSection]:
        """Extract sections of a specific covenant type."""
        if covenant_type not in self.covenant_types:
            raise ValueError(f"Unknown covenant type: {covenant_type}")
        
        console.print(f"[cyan]Searching for {covenant_type.replace('_', ' ').title()} sections...[/cyan]")
        
        # Create focused prompt for specific type
        focused_prompt = PromptTemplate(
            input_variables=["text", "covenant_type", "covenant_description"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""You are a legal document analyst. 

Focus on extracting ONLY {covenant_type} sections from this text.
{covenant_type}: {covenant_description}

Look for:
- Sections with headers containing these terms
- Paragraphs discussing these restrictions
- Numbered subsections detailing conditions
- Defined terms related to this covenant type

Text to analyze:
{text}

{format_instructions}

Extract the COMPLETE content, not summaries."""
        )
        
        focused_chain = LLMChain(llm=self.llm, prompt=focused_prompt)
        
        chunks = self.text_splitter.split_text(text)
        sections = []
        
        for chunk in chunks:
            try:
                result = focused_chain.run(
                    text=chunk,
                    covenant_type=covenant_type,
                    covenant_description=self.covenant_types[covenant_type]
                )
                
                parsed_result = self.parser.parse(result)
                
                for covenant in parsed_result.covenants:
                    if covenant.section_type == covenant_type:
                        section = LLMCovenantSection(
                            section_type=covenant.section_type,
                            title=covenant.title,
                            content=covenant.content,
                            key_terms=covenant.key_terms,
                            confidence=covenant.confidence,
                            reasoning=covenant.reasoning
                        )
                        sections.append(section)
                        
            except Exception as e:
                console.print(f"[red]Error processing chunk: {e}[/red]")
        
        return self._deduplicate_sections(sections)
    
    def _deduplicate_sections(self, sections: List[LLMCovenantSection]) -> List[LLMCovenantSection]:
        """Remove duplicate sections based on content similarity."""
        if not sections:
            return []
        
        unique_sections = []
        
        for section in sections:
            is_duplicate = False
            
            for existing in unique_sections:
                # Check if content is very similar
                if (section.section_type == existing.section_type and 
                    self._similarity(section.content, existing.content) > 0.8):
                    # Keep the one with higher confidence
                    if section.confidence > existing.confidence:
                        unique_sections.remove(existing)
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_sections.append(section)
        
        return unique_sections
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (Jaccard similarity)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def display_results(self, sections: List[LLMCovenantSection]):
        """Display extracted sections in a formatted way."""
        if not sections:
            console.print("[yellow]No covenant sections found.[/yellow]")
            return
        
        for section in sections:
            console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
            console.print(f"[bold green]Type:[/bold green] {section.section_type.replace('_', ' ').title()}")
            console.print(f"[bold green]Title:[/bold green] {section.title}")
            console.print(f"[bold green]Confidence:[/bold green] {section.confidence:.1%}")
            console.print(f"[bold green]Key Terms:[/bold green] {', '.join(section.key_terms[:5])}")
            console.print(f"[bold green]Reasoning:[/bold green] {section.reasoning}")
            console.print(f"\n[bold yellow]Content:[/bold yellow]")
            console.print(section.content[:500] + "..." if len(section.content) > 500 else section.content)
    
    def save_results(self, sections: List[LLMCovenantSection], output_path: Union[str, Path]):
        """Save extracted sections to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            "model_used": self.model_name,
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


def extract_covenants_llm(text: str, covenant_types: Optional[List[str]] = None, 
                         model_name: str = "gpt-3.5-turbo") -> List[LLMCovenantSection]:
    """Convenience function to extract covenant sections using LLM."""
    extractor = LLMCovenantExtractor(model_name=model_name)
    
    if covenant_types:
        sections = []
        for covenant_type in covenant_types:
            sections.extend(extractor.extract_by_type(text, covenant_type))
        return sections
    else:
        return extractor.extract_sections(text)


if __name__ == "__main__":
    # Test the LLM extractor
    sample_text = """
    Section 4.1 - Restricted Payments
    
    The Company shall not, and shall not permit any of its Subsidiaries to, directly or indirectly:
    (a) declare or pay any dividend or make any distribution on account of the Company's or any Subsidiary's Equity Interests;
    (b) purchase, redeem or otherwise acquire or retire for value any Equity Interests of the Company;
    (c) make any principal payment on, or redeem, repurchase, defease or otherwise acquire or retire for value.
    
    Section 5.2 - Change of Control
    
    Upon the occurrence of a Change of Control, each Holder shall have the right to require the Company to purchase all or any part of such Holder's Notes at a purchase price in cash equal to 101% of the aggregate principal amount thereof.
    """
    
    # Check if API key is available
    if os.getenv("OPENAI_API_KEY"):
        extractor = LLMCovenantExtractor()
        sections = extractor.extract_sections(sample_text)
        extractor.display_results(sections)
    else:
        console.print("[yellow]No OPENAI_API_KEY found. Please set it in your .env file.[/yellow]")