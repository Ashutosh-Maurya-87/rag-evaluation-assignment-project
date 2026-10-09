from langchain_text_splitters import RecursiveCharacterTextSplitter

# This creates our text splitter with limits suitable for our first RAG pipeline.
# We can tune these values later using our RAG evaluation results.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Try to keep each chunk around 1000 characters.
    chunk_overlap=150,  # Keep around 150 characters from the previous chunk in the next chunk.
    separators=[
        "\n\n",  # Try to keep paragraphs together.
        "\n",  # If needed, split at a new line.
        ". ",  # Then try to split at the end of a sentence.
        " ",  # Finally split at spaces.
        "",  # Last fallback: split wherever necessary.
    ],
)


def create_chunks(text: str) -> list[str]:
    # Remove unnecessary spaces before creating chunks.
    text = text.strip()

    # Don't create chunks when the document has no useful text.
    if not text:
        return []

    # Split the complete document into smaller pieces.
    return text_splitter.split_text(text)
