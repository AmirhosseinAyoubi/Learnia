from unittest.mock import patch, MagicMock, mock_open

import pytest

from src.processors import extract_text, chunk_text


class TestChunkText:
    def test_empty_string_returns_empty_list(self):
        assert chunk_text("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert chunk_text("   \n  ") == []

    def test_short_text_single_chunk(self):
        text = "Hello world"
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_multiple_chunks(self):
        word = "token " * 600
        chunks = chunk_text(word, max_tokens=512)
        assert len(chunks) > 1

    def test_chunk_token_count_within_limit(self):
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        text = "word " * 2000
        chunks = chunk_text(text, max_tokens=512)
        for chunk in chunks:
            assert len(enc.encode(chunk)) <= 512

    def test_chunks_cover_all_tokens(self):
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        text = "alpha beta gamma " * 300
        chunks = chunk_text(text, max_tokens=100)
        total_tokens = sum(len(enc.encode(c)) for c in chunks)
        original_tokens = len(enc.encode(text))
        assert total_tokens == original_tokens


class TestExtractTextPdf:
    def test_pdf_extracts_text_and_page_count(self):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page, mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None

        with patch("src.processors.pdfplumber.open", return_value=mock_pdf):
            text, page_count = extract_text("/fake/file.pdf", "PDF")

        assert page_count == 2
        assert "Page content" in text

    def test_pdf_skips_none_pages(self):
        mock_page_none = MagicMock()
        mock_page_none.extract_text.return_value = None
        mock_page_text = MagicMock()
        mock_page_text.extract_text.return_value = "Real content"
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page_none, mock_page_text]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None

        with patch("src.processors.pdfplumber.open", return_value=mock_pdf):
            text, page_count = extract_text("/fake/file.pdf", "PDF")

        assert page_count == 2
        assert "Real content" in text
        assert text.count("Real content") == 1

    def test_pdf_all_empty_pages(self):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = None
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__exit__.return_value = None

        with patch("src.processors.pdfplumber.open", return_value=mock_pdf):
            text, page_count = extract_text("/fake/file.pdf", "pdf")

        assert text == ""
        assert page_count == 1


class TestExtractTextPptx:
    def _make_pptx(self, slide_texts):
        shapes_per_slide = []
        for texts in slide_texts:
            shapes = []
            for t in texts:
                shape = MagicMock()
                shape.text = t
                shapes.append(shape)
            slide = MagicMock()
            slide.shapes = shapes
            shapes_per_slide.append(slide)

        prs = MagicMock()
        prs.slides = shapes_per_slide
        return prs

    def test_pptx_extracts_text_and_slide_count(self):
        prs = self._make_pptx([["Slide 1 text"], ["Slide 2 text"]])
        with patch("src.processors.Presentation", return_value=prs):
            text, page_count = extract_text("/fake/deck.pptx", "PPTX")

        assert page_count == 2
        assert "Slide 1 text" in text
        assert "Slide 2 text" in text

    def test_pptx_ppt_extension_also_works(self):
        prs = self._make_pptx([["Content"]])
        with patch("src.processors.Presentation", return_value=prs):
            text, page_count = extract_text("/fake/deck.ppt", "PPT")

        assert page_count == 1

    def test_pptx_skips_blank_shapes(self):
        prs = self._make_pptx([["   ", "Real text", ""]])
        with patch("src.processors.Presentation", return_value=prs):
            text, page_count = extract_text("/fake/deck.pptx", "PPTX")

        assert "Real text" in text
        assert "   " not in text


class TestExtractTextTxt:
    def test_txt_reads_content_and_estimates_pages(self):
        content = "line\n" * 200
        with patch("builtins.open", mock_open(read_data=content)):
            text, page_count = extract_text("/fake/file.txt", "TXT")

        assert text == content
        assert page_count == 4  # 200 lines // 50

    def test_txt_short_file_at_least_one_page(self):
        with patch("builtins.open", mock_open(read_data="short")):
            text, page_count = extract_text("/fake/file.txt", "TXT")

        assert page_count == 1

    def test_unsupported_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text("/fake/file.docx", "DOCX")
