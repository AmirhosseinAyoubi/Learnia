"""
processors/txt_processor.py — Reads plain text files.

Handles common encodings gracefully.
"""


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Decode a plain text file.

    Tries UTF-8 first, then falls back to latin-1 which never fails
    (every byte sequence is valid latin-1).

    Args:
        file_bytes: raw bytes of the text file

    Returns:
        Decoded string content of the file.
    """
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")
