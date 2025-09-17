from __future__ import annotations

import os
from typing import List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


SAMPLE_TEXT = {
    "sample1": [
        ("Section 1.1 Definitions", "This Agreement uses defined terms as set forth herein."),
        (
            "Section 5.2 Restricted Payments",
            "The Company shall not, directly or indirectly, declare or make any Restricted Payment, including dividends, distributions, repurchases, or redemptions, except as permitted pursuant to Section 5.2(a)-(d).",
        ),
        (
            "Section 5.2(a) Exceptions",
            "Notwithstanding the foregoing, the Company may make Restricted Payments in an aggregate amount not exceeding $5,000,000 in any fiscal year, provided no Event of Default has occurred and is continuing.",
        ),
        (
            "Section 6.4 Change of Control",
            "Upon the occurrence of a Change of Control, each Lender may require the Company to prepay all outstanding Obligations in full, together with accrued interest and any applicable prepayment premium, subject to the notice requirements set forth in Section 2.3.",
        ),
        ("Miscellaneous", "This Section includes boilerplate provisions regarding notices, assignments, and governing law."),
    ],
    "sample2": [
        ("RECITALS", "WHEREAS, the Borrower desires to obtain financing..."),
        (
            "LIMITATIONS ON DIVIDENDS AND DISTRIBUTIONS",
            "No Restricted Payments are permitted unless the Consolidated Net Leverage Ratio is less than 3.00 to 1.00 and no Default exists immediately before and after giving effect thereto.",
        ),
        (
            "CHANGE-IN-CONTROL PROVISION",
            "If there is a change in control of the Borrower, the Borrower shall make an offer to repurchase the Notes at 101% of principal plus accrued interest.",
        ),
        ("MISCELLANEOUS", "Entire agreement; counterparts; electronic signatures."),
    ],
}


def build_story(sections: List[tuple[str, str]]):
    styles = getSampleStyleSheet()
    story: List[object] = []
    for title, body in sections:
        story.append(Paragraph(title, styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(body, styles["BodyText"]))
        story.append(Spacer(1, 12))
    return story


def generate_samples(out_dir: str = "/workspace/samples") -> None:
    os.makedirs(out_dir, exist_ok=True)
    for name, sections in SAMPLE_TEXT.items():
        file_path = os.path.join(out_dir, f"{name}.pdf")
        doc = SimpleDocTemplate(file_path, pagesize=LETTER)
        story = build_story(sections)
        doc.build(story)
        print(f"Generated: {file_path}")


if __name__ == "__main__":
    generate_samples()
