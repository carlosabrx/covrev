# Covenant Extraction from Legal Agreements

A Python toolkit for extracting covenant sections from legal agreements in PDF format using both regex-based pattern matching and LLM-powered extraction methods.

## Features

- **PDF Text Extraction**: Robust text extraction from PDF files using multiple libraries (PyPDF2 and pdfplumber)
- **Regex-based Extraction**: Pattern-based identification of covenant sections
- **LLM-powered Extraction**: Intelligent extraction using OpenAI GPT models
- **Comparison Tools**: Compare and evaluate different extraction methods
- **Support for Multiple Covenant Types**:
  - Restricted Payments
  - Change of Control
  - Debt Incurrence
  - Asset Sales
  - Merger Restrictions
  - Investments
  - Liens
  - Transactions with Affiliates

## Installation

1. Clone the repository:
```bash
cd /workspace/covenant-extraction
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key (optional, for LLM extraction)
```

## Quick Start

1. **Create sample PDFs for testing**:
```bash
python src/create_sample_pdfs.py
```

2. **Run extraction on sample PDFs**:
```bash
# Test both regex and LLM extraction
python src/main.py --data-dir data

# Test only regex extraction (no API key required)
python src/main.py --data-dir data --no-llm

# Process a specific PDF
python src/main.py --pdf data/sample_loan_agreement.pdf
```

## Usage

### Basic PDF Text Extraction

```python
from src.pdf_extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract_text("path/to/agreement.pdf")
print(f"Extracted {len(result['text'])} characters")
```

### Regex-based Covenant Extraction

```python
from src.regex_extractor import RegexCovenantExtractor

text = "... agreement text ..."
extractor = RegexCovenantExtractor()
sections = extractor.extract_sections(text)

# Extract specific covenant type
debt_sections = extractor.extract_by_type(text, "debt_incurrence")
```

### LLM-powered Covenant Extraction

```python
from src.llm_extractor import LLMCovenantExtractor

# Requires OPENAI_API_KEY in environment
extractor = LLMCovenantExtractor(model_name="gpt-3.5-turbo")
sections = extractor.extract_sections(text)

# Display results
extractor.display_results(sections)
```

### Comparing Extraction Methods

```python
from src.evaluation import ExtractionEvaluator

evaluator = ExtractionEvaluator()
comparison = evaluator.compare_sections(regex_sections, llm_sections)
evaluator.display_comparison(comparison)
```

## Command Line Interface

The main script provides a CLI for testing extraction methods:

```bash
# Show help
python src/main.py --help

# Process all PDFs in a directory
python src/main.py --data-dir data --output-dir results

# Process specific PDF with LLM disabled
python src/main.py --pdf agreement.pdf --no-llm

# Extract specific covenant type
python src/main.py --pdf agreement.pdf --covenant-type restricted_payments
```

## Project Structure

```
covenant-extraction/
├── src/
│   ├── pdf_extractor.py       # PDF text extraction utilities
│   ├── regex_extractor.py     # Regex-based covenant extraction
│   ├── llm_extractor.py       # LLM-powered covenant extraction
│   ├── evaluation.py          # Comparison and evaluation tools
│   ├── create_sample_pdfs.py  # Generate sample PDFs for testing
│   └── main.py               # Main script for testing
├── data/                     # Sample PDF agreements
├── output/                   # Extraction results
├── tests/                    # Test files
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Extraction Methods Comparison

### Regex-based Extraction
- **Pros**: Fast, deterministic, no API costs
- **Cons**: Limited to predefined patterns, may miss variations
- **Best for**: Standard agreement formats, known covenant structures

### LLM-powered Extraction
- **Pros**: Understands context, handles variations, identifies implicit covenants
- **Cons**: Requires API key, costs per token, slower
- **Best for**: Complex agreements, non-standard formats, comprehensive analysis

## Output Format

Results are saved as JSON files with the following structure:

```json
{
  "method": "regex|llm",
  "pdf_name": "agreement.pdf",
  "sections": [
    {
      "section_type": "restricted_payments",
      "title": "Section 4.1 Restricted Payments",
      "content": "The Company shall not...",
      "confidence": 0.85,
      "key_terms": ["dividend", "distribution"],  // LLM only
      "reasoning": "Identified based on..."        // LLM only
    }
  ]
}
```

## Customization

### Adding New Covenant Types

1. For regex extraction, edit `regex_extractor.py`:
```python
self.covenant_patterns["new_covenant_type"] = {
    "patterns": [...],
    "keywords": [...],
    "section_indicators": [...]
}
```

2. For LLM extraction, edit `llm_extractor.py`:
```python
self.covenant_types["new_covenant_type"] = "Description of the covenant"
```

### Adjusting Extraction Parameters

- **Confidence thresholds**: Modify minimum confidence in extractors
- **Text chunk size**: Adjust `chunk_size` for LLM processing
- **Pattern matching**: Customize regex patterns for specific formats

## Performance Tips

1. **For large PDFs**: Use chunking to process sections separately
2. **For batch processing**: Use `extract_pdf_batch()` function
3. **For cost optimization**: Use regex first, then LLM for validation
4. **For speed**: Disable LLM extraction with `--no-llm` flag

## Troubleshooting

### Common Issues

1. **PDF extraction fails**: Try different extraction method (`pypdf2` vs `pdfplumber`)
2. **LLM timeout**: Reduce chunk size or use simpler model
3. **Low confidence scores**: Adjust patterns or provide more context
4. **Missing covenants**: Check PDF quality and text extraction output

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- [ ] Support for more covenant types
- [ ] Machine learning model for pattern learning
- [ ] Web interface for interactive extraction
- [ ] Batch processing with progress tracking
- [ ] Export to multiple formats (CSV, Excel, Word)
- [ ] Integration with document management systems

## License

This project is for demonstration purposes. Ensure compliance with your organization's policies when processing legal documents.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review sample code in `main.py`
3. Examine test outputs in the `output/` directory