import pymupdf  # PyMuPDF


def extract_pdf_text(file_path: str) -> str:
    """Extracts text from a PDF file.
    Args: file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text
