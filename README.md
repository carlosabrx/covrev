## Covenant Section Extraction Prototype

Quick prototype to extract covenant sections (e.g., "Restricted Payments", "Change of Control") from PDF agreements using regex and optional LLM assistance.

### Setup

1) Python 3.10+
2) Install deps:
```bash
pip install -r requirements.txt
```

### Usage

Generate sample PDFs and run regex extraction:
```bash
python -m covenant_extractor.cli --inputs /workspace/samples --mode regex --targets "restricted payments" "change of control" --out /workspace/outputs
```

Run with LLM (requires `OPENAI_API_KEY`):
```bash
export OPENAI_API_KEY=sk-...
python -m covenant_extractor.cli --inputs /workspace/samples --mode both --model gpt-4o-mini --targets "restricted payments" "change of control" --out /workspace/outputs
```

### Project Structure

- `src/covenant_extractor/pdf_utils.py` – PDF text extraction via PyMuPDF
- `src/covenant_extractor/regex_patterns.py` – Target synonyms and heading patterns
- `src/covenant_extractor/extractor.py` – Regex and LLM extraction logic
- `src/covenant_extractor/cli.py` – CLI to run extraction
- `samples/` – Generated sample agreements
- `outputs/` – Extraction results (JSON)

### Notes

- LLM extraction is optional and will be skipped if no API key is present.
- Regex extraction is heuristic; adjust patterns in `regex_patterns.py` to improve recall/precision.
