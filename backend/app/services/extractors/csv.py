import pandas as pd


def extract_csv_text(file_path: str) -> str:
    """Extracts text data from a CSV file.
    Args: file_path (str): The path to the CSV file.

    Returns:
        str: The extracted text data as a string.
    """
    df = pd.read_csv(file_path)
    return df.to_string(index=False)
