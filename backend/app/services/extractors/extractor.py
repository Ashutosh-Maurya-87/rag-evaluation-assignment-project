

from .csv import extract_csv_text
from .excel import extract_excel_text
from .pdf import extract_pdf_text


def extract_text(file_path: str, file_type: str) -> str:
    """Extracts text from a file based on its type.

    Args:
        file_path (str): The path to the file.
        file_type (str): The type of the file ('pdf', 'csv', 'excel').

    Returns:
        str: The extracted text from the file.
    """
    if file_type == "pdf":
        return extract_pdf_text(file_path)
    elif file_type == "csv":
        return extract_csv_text(file_path)
    elif file_type == "xlsx" or file_type == "xls":
        return extract_excel_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")