from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Tuple

from .pdf_utils import extract_text_from_pdf
from .regex_patterns import build_target_regexes, is_heading_line, normalize_target


@dataclass
class CovenantSection:
    target: str
    title: str
    start_line: int
    end_line: int
    text: str


def _split_lines(text: str) -> List[str]:
    return text.splitlines()


def _find_heading_indices(lines: List[str]) -> List[int]:
    heading_indices: List[int] = []
    for index, line in enumerate(lines):
        if is_heading_line(line):
            heading_indices.append(index)
    return heading_indices


def _find_section_bounds(
    lines: List[str],
    candidate_start_index: int,
    heading_indices: List[int],
    max_section_lines: int = 120,
) -> Tuple[int, int]:
    """
    Given a candidate heading line, find the section bounds from that line
    to the next heading or a max line window.
    """
    start_index = candidate_start_index
    end_index = min(len(lines) - 1, start_index + max_section_lines)
    for next_heading in heading_indices:
        if next_heading > start_index:
            end_index = min(end_index, next_heading - 1)
            break
    return start_index, end_index


def extract_covenants_from_text(
    text: str,
    targets: Iterable[str],
    max_section_lines: int = 120,
) -> Dict[str, List[CovenantSection]]:
    """
    Extract covenant sections by regex heuristics.

    Returns: mapping canonical target -> list of CovenantSection
    """
    compiled = build_target_regexes(targets)
    lines = _split_lines(text)
    heading_indices = _find_heading_indices(lines)

    results: Dict[str, List[CovenantSection]] = {normalize_target(t): [] for t in targets}

    for canonical, pattern in compiled.items():
        # Search line-by-line for potential heading lines matching the target
        for line_index, line in enumerate(lines):
            if not line.strip():
                continue
            if pattern.search(line):
                start_index, end_index = _find_section_bounds(
                    lines, line_index, heading_indices, max_section_lines=max_section_lines
                )
                title_text = lines[line_index].strip()
                section_text = "\n".join(lines[start_index : end_index + 1]).strip()
                results[canonical].append(
                    CovenantSection(
                        target=canonical,
                        title=title_text,
                        start_line=start_index + 1,
                        end_line=end_index + 1,
                        text=section_text,
                    )
                )
    return results


def extract_covenants_from_pdf(
    file_path: str,
    targets: Iterable[str],
    max_pages: Optional[int] = None,
    max_section_lines: int = 120,
) -> Dict[str, List[CovenantSection]]:
    text = extract_text_from_pdf(file_path, max_pages=max_pages)
    return extract_covenants_from_text(text, targets, max_section_lines=max_section_lines)


def llm_extract_covenants(
    text: str,
    targets: Iterable[str],
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    max_tokens: int = 800,
) -> Dict[str, Dict[str, str]]:
    """
    Use an LLM to identify covenant sections. Returns a mapping of canonical target to
    a dict with keys: title, excerpt, rationale. If `api_key` is None or not set, returns {}.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {}

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return {}

    client = OpenAI(api_key=api_key)

    canonical_targets = [normalize_target(t) for t in targets]
    system_prompt = (
        "You are a legal AI that extracts covenant sections from agreements. "
        "Identify the best matching section title and an excerpt for each target. "
        "Return strict JSON with keys for each target (canonical, lowercase)."
    )
    user_prompt = {
        "instruction": "Find these targets (canonical, lowercase):",
        "targets": canonical_targets,
        "requirements": [
            "If not found, set title='' and excerpt=''",
            "Prefer section or subsection titles",
            "Return concise 3-6 sentence excerpt around the section start",
        ],
        "text": text[:100_000],  # safety cap
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Extract and return JSON only. Format: {target: {title, excerpt}}\n\n" + json.dumps(user_prompt)
            ),
        },
    ]

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )

    content = completion.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
        # Normalize keys back to canonical order
        result: Dict[str, Dict[str, str]] = {}
        for t in canonical_targets:
            v = data.get(t) or {}
            title = v.get("title", "") if isinstance(v, dict) else ""
            excerpt = v.get("excerpt", "") if isinstance(v, dict) else ""
            rationale = v.get("rationale", "") if isinstance(v, dict) else ""
            result[t] = {"title": title, "excerpt": excerpt, "rationale": rationale}
        return result
    except Exception:
        return {}


def to_serializable(results: Dict[str, List[CovenantSection]]) -> Dict[str, List[Dict[str, object]]]:
    return {k: [asdict(v) for v in sections] for k, sections in results.items()}
