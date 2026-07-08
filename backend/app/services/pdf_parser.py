import fitz  # PyMuPDF
from app.utils.helper import clean_text
from app.utils.logger import logger


def parse_pdf(file_path: str) -> str:
    """
    Extract and clean text from a PDF file.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        Cleaned text content of the PDF.

    Raises:
        ValueError: If the PDF cannot be opened or is empty.
    """
    try:
        doc = fitz.open(file_path)
        full_text = []

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                full_text.append(text)
            logger.debug(f"Parsed page {page_num} — {len(text)} chars")

        doc.close()

        if not full_text:
            raise ValueError("PDF appears to be empty or contains only images.")

        combined = "\n".join(full_text)
        return clean_text(combined)

    except Exception as e:
        logger.error(f"Failed to parse PDF '{file_path}': {e}")
        raise ValueError(f"Could not parse PDF: {e}")
