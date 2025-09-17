from __future__ import annotations

import argparse
import glob
import json
import os
from dataclasses import asdict
from typing import Dict, List

from tqdm import tqdm

from .extractor import (
    extract_covenants_from_pdf,
    extract_covenants_from_text,
    llm_extract_covenants,
    to_serializable,
)
from .pdf_utils import extract_text_from_pdf


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Covenant section extraction prototype")
    parser.add_argument("--inputs", required=True, help="Directory containing PDFs or a single PDF file")
    parser.add_argument("--out", required=False, default="/workspace/outputs", help="Output directory for JSON results")
    parser.add_argument("--mode", choices=["regex", "llm", "both"], default="regex")
    parser.add_argument("--targets", nargs="+", required=False, default=["restricted payments", "change of control"], help="Target covenant names")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model name")
    parser.add_argument("--max-pages", type=int, default=None, help="Max pages to parse per PDF")
    parser.add_argument("--max-section-lines", type=int, default=120, help="Max lines in a section window")
    return parser.parse_args()


def collect_pdfs(input_path: str) -> List[str]:
    if os.path.isdir(input_path):
        files = sorted(glob.glob(os.path.join(input_path, "**", "*.pdf"), recursive=True))
    else:
        files = [input_path] if input_path.lower().endswith(".pdf") else []
    return files


def main() -> None:
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)

    pdf_files = collect_pdfs(args.inputs)
    if not pdf_files:
        print(f"No PDF files found in {args.inputs}")
        return

    for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(args.out, f"{base}.json")
        result: Dict[str, object] = {
            "file": pdf_path,
            "targets": args.targets,
        }

        if args.mode in {"regex", "both"}:
            regex_results = extract_covenants_from_pdf(
                pdf_path,
                targets=args.targets,
                max_pages=args.max_pages,
                max_section_lines=args.max_section_lines,
            )
            result["regex"] = to_serializable(regex_results)

        if args.mode in {"llm", "both"}:
            text = extract_text_from_pdf(pdf_path, max_pages=args.max_pages)
            llm_results = llm_extract_covenants(
                text,
                targets=args.targets,
                model=args.model,
            )
            result["llm"] = llm_results

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
