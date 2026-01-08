# utils/chunker.py

from langchain_text_splitters import RecursiveCharacterTextSplitter

def intelligent_chunking(text, chunk_size=800, chunk_overlap=150):
    """
    Splits text recursively using semantic separators to preserve meaning.
    
    Strategy:
    1. Try splitting by double newline (Paragraphs)
    2. Try splitting by single newline (Lines)
    3. Try splitting by sentence endings (. )
    4. Fallback to character count
    
    Args:
        text (str): The full document text.
        chunk_size (int): Target size in characters (approx 200-300 tokens).
        chunk_overlap (int): Overlap to preserve context between chunks.
    
    Returns:
        List[str]: A list of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    return splitter.split_text(text)
