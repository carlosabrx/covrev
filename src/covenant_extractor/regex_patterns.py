from __future__ import annotations

import re
from typing import Dict, Iterable, List


# Canonical target keys map to common synonyms and variants
TARGET_SYNONYMS: Dict[str, List[str]] = {
    "restricted payments": [
        "restricted payment",
        "restricted payments",
        "limitation on restricted payments",
        "limitations on restricted payments",
        "limitations on dividends and distributions",
        "restricted dividends",
    ],
    "change of control": [
        "change of control",
        "change-of-control",
        "change in control",
        "change-of-control provision",
    ],
}


def normalize_target(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower().replace("-", "-")).strip()


def _synonym_to_regex(s: str) -> str:
    """Create a robust regex for a synonym, tolerating hyphens and extra spaces."""
    s = s.strip()
    # Replace spaces or hyphens between words with a flexible pattern
    tokens = re.split(r"\s+", s)
    escaped = [re.escape(t) for t in tokens]
    # Allow space or hyphen between tokens
    return r"[\s\-]+".join(escaped)


def build_target_regexes(targets: Iterable[str]) -> Dict[str, re.Pattern]:
    """
    Build compiled regexes mapping canonical target name -> compiled pattern
    that matches any of its synonyms as a heading/line occurrence.
    """
    compiled: Dict[str, re.Pattern] = {}
    for raw in targets:
        canonical = normalize_target(raw)
        synonyms = TARGET_SYNONYMS.get(canonical, [canonical])
        parts = [_synonym_to_regex(s) for s in synonyms]
        # Anchor to line start with optional 'Section 1.2' prefix, or match anywhere in the line
        name_group = "(?:" + "|".join(parts) + ")"
        pattern = (
            r"(?mi)"  # multiline, case-insensitive
            r"^(?:\s*Section\s+\d+(?:\.\d+)*)?\s*(?:[:\-\.])?\s*" + name_group + r"\b.*$"
        )
        compiled[canonical] = re.compile(pattern)
    return compiled


SECTION_HEADING_PATTERN = re.compile(
    r"(?mi)^\s*(?:Section\s+\d+(?:\.\d+)*)\s+[A-Z][^\n]*$"
)


def is_heading_line(line: str) -> bool:
    """Heuristic to detect a section heading line."""
    if SECTION_HEADING_PATTERN.search(line):
        return True
    # All-caps headings (allow punctuation and connectors)
    stripped = line.strip()
    if len(stripped) >= 8 and re.fullmatch(r"[A-Z0-9 &/\-_,\.\(\)]+", stripped):
        return True
    # Title Case heuristic: 2+ capitalized words and short length
    if len(stripped) <= 120:
        words = stripped.split()
        caps = sum(1 for w in words if w[:1].isupper())
        if len(words) >= 2 and caps / max(1, len(words)) > 0.6:
            return True
    return False
