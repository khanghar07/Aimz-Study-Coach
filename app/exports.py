from io import BytesIO
from typing import Dict, Any

from fpdf import FPDF


def _latin1_safe(text: str) -> str:
    if text is None:
        return ""
    # FPDF (classic) supports latin-1; replace unsupported chars
    return str(text).encode("latin-1", errors="replace").decode("latin-1")


def to_markdown(data: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Study Coach Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(data.get("summary", ""))
    lines.append("")

    def section_list(title, items):
        lines.append(f"## {title}")
        for item in items or []:
            lines.append(f"- {item}")
        lines.append("")

    section_list("Key Concepts", data.get("key_concepts"))
    section_list("Confusion Points", data.get("confusion_points"))

    lines.append("## Study Plan")
    for step in data.get("study_plan", []) or []:
        lines.append(f"- **{step.get('time','')}** {step.get('step','')}")
        goal = step.get("goal")
        if goal:
            lines.append(f"  - Goal: {goal}")
    lines.append("")

    lines.append("## Flashcards")
    for card in data.get("flashcards", []) or []:
        lines.append(f"- **Q:** {card.get('q','')}")
        lines.append(f"  - **A:** {card.get('a','')}")
    lines.append("")

    lines.append("## Quiz")
    for q in data.get("quiz", []) or []:
        lines.append(f"- **Q:** {q.get('q','')}")
        lines.append(f"  - **A:** {q.get('a','')}")
        exp = q.get("explanation")
        if exp:
            lines.append(f"  - **Why:** {exp}")
    lines.append("")

    section_list("Next Actions", data.get("next_actions"))

    return "\n".join(lines)


def to_pdf_bytes(data: Dict[str, Any]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 10, _latin1_safe("Study Coach Report"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    def heading(text):
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 8, _latin1_safe(text), ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=11)

    def paragraph(text):
        pdf.multi_cell(0, 6, _latin1_safe(text or ""))
        pdf.ln(2)

    heading("Summary")
    paragraph(data.get("summary", ""))

    def list_section(title, items):
        heading(title)
        for item in items or []:
            pdf.multi_cell(0, 6, _latin1_safe(f"- {item}"))
        pdf.ln(2)

    list_section("Key Concepts", data.get("key_concepts"))
    list_section("Confusion Points", data.get("confusion_points"))

    heading("Study Plan")
    for step in data.get("study_plan", []) or []:
        line = f"- {step.get('time','')} {step.get('step','')}"
        pdf.multi_cell(0, 6, _latin1_safe(line))
        goal = step.get("goal")
        if goal:
            pdf.multi_cell(0, 6, _latin1_safe(f"  Goal: {goal}"))
    pdf.ln(2)

    heading("Flashcards")
    for card in data.get("flashcards", []) or []:
        pdf.multi_cell(0, 6, _latin1_safe(f"Q: {card.get('q','')}"))
        pdf.multi_cell(0, 6, _latin1_safe(f"A: {card.get('a','')}"))
        pdf.ln(1)

    heading("Quiz")
    for q in data.get("quiz", []) or []:
        pdf.multi_cell(0, 6, _latin1_safe(f"Q: {q.get('q','')}"))
        pdf.multi_cell(0, 6, _latin1_safe(f"A: {q.get('a','')}"))
        exp = q.get("explanation")
        if exp:
            pdf.multi_cell(0, 6, _latin1_safe(f"Why: {exp}"))
        pdf.ln(1)

    list_section("Next Actions", data.get("next_actions"))

    # FPDF returns a string when dest="S" (latin-1). Convert to bytes.
    pdf_str = pdf.output(dest="S")
    return pdf_str.encode("latin-1")
