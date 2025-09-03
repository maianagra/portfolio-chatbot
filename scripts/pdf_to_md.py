import re
from pypdf import PdfReader
from pathlib import Path

PDF_PATH = "assets/Maia Nagra.pdf"
MD_PATH = "assets/maia_cv.md"


def clean_text(text):
    # Keep only content from CAREER SUMMARY onward
    start = text.find("CAREER SUMMARY")
    if start != -1:
        text = text[start:]

    # Remove soft hyphens
    text = re.sub(r"\u00ad", "", text)

    # Fix spaces around hyphens: "front -end" → "front-end"
    text = re.sub(r"\s*-\s*", "-", text)

    # Fix multiple spaces
    text = re.sub(r"\s{2,}", " ", text)

    # Fix spacing around punctuation
    text = re.sub(r"\s+([,.:;])", r"\1", text)
    text = re.sub(r"([,.:;])([^\s])", r"\1 \2", text)

    # Remove page markers
    text = re.sub(r"<!-- Page \d+ -->", "", text)

    # Strip each line
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    return "\n".join(lines)


def pdf_to_markdown(pdf_path, md_path):
    reader = PdfReader(pdf_path)
    md_lines = []

    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        cleaned = clean_text(text)
        md_lines.append(cleaned)

    # Join pages with double newlines
    final_md = "\n\n".join(md_lines)
    Path(md_path).write_text(final_md, encoding="utf-8")
    print(f"Markdown CV saved to {md_path}")


if __name__ == "__main__":
    pdf_to_markdown(PDF_PATH, MD_PATH)
