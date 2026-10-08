import pandas as pd


def extract_excel_text(file_path: str) -> str:
    """Extracts text data from an Excel file."""

    df = pd.read_excel(file_path)
    return df.to_string(index=False)
