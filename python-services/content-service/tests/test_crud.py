# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Unit tests for the Content Service CRUD layer.

Uses an in-memory SQLite database (via SQLAlchemy) so no PostgreSQL instance
is needed.  UUID columns are stored as VARCHAR in SQLite.

Tests verify:
- save_chunks persists rows with correct indices
- get_chunks returns rows ordered by chunk_index
- get_chunks returns empty list when no rows exist
- save_material persists the correct row
- get_materials returns all rows for a document
- delete_chunks removes all rows and returns the count
- delete_materials removes all rows and returns the count
"""
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.crud import (
    delete_chunks,
    delete_materials,
    get_chunks,
    get_materials,
    save_chunks,
    save_material,
)
from src.database import Base

# Use SQLite in-memory for fast, isolated tests (no PostgreSQL required)
_TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture()
def db():
    """Provide a fresh in-memory SQLite session for each test.

    The database schema is created before each test and dropped after
    to ensure full isolation between tests.
    """
    engine = create_engine(_TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


class TestSaveChunks:
    """Tests for the ``save_chunks`` CRUD function."""

    def test_save_chunks_persists_correct_number_of_rows(self, db):
        """Three input chunks result in three rows in the database.

        Input: document_id + list of three strings.
        Expected: Three DocumentChunk rows with sequential indices 0, 1, 2.
        """
        doc_id = str(uuid.uuid4())
        chunks = save_chunks(db, doc_id, ["a", "b", "c"])
        assert len(chunks) == 3

    def test_save_chunks_assigns_sequential_indices(self, db):
        """Chunk indices are 0, 1, 2, ... in insertion order.

        Ensures that text ordering is preserved when chunks are retrieved later.
        """
        doc_id = str(uuid.uuid4())
        chunks = save_chunks(db, doc_id, ["first", "second", "third"])
        indices = [c.chunk_index for c in chunks]
        assert indices == [0, 1, 2]

    def test_save_chunks_stores_correct_content(self, db):
        """Each chunk's content matches the corresponding input string.

        Input: chunks ["hello", "world"].
        Expected: chunk_index 0 has content "hello", index 1 has "world".
        """
        doc_id = str(uuid.uuid4())
        chunks = save_chunks(db, doc_id, ["hello", "world"])
        contents = {c.chunk_index: c.content for c in chunks}
        assert contents[0] == "hello"
        assert contents[1] == "world"

    def test_save_empty_chunks_list_returns_empty(self, db):
        """Saving an empty list does not raise and returns an empty list.

        Input: empty chunks list.
        Expected: empty list returned, no rows inserted.
        """
        doc_id = str(uuid.uuid4())
        result = save_chunks(db, doc_id, [])
        assert result == []


class TestGetChunks:
    """Tests for the ``get_chunks`` CRUD function."""

    def test_get_chunks_returns_ordered_by_index(self, db):
        """Chunks are returned in ascending chunk_index order regardless of insert order.

        Input: save chunks in order [2, 0, 1].
        Expected: get_chunks returns them ordered 0, 1, 2.
        """
        doc_id = str(uuid.uuid4())
        # Insert in reverse order to verify ORDER BY
        for idx, text in [(2, "c"), (0, "a"), (1, "b")]:
            from src.models import DocumentChunk  # pylint: disable=import-outside-toplevel
            db.add(DocumentChunk(document_id=doc_id, chunk_index=idx, content=text))
        db.commit()

        result = get_chunks(db, doc_id)
        assert [c.chunk_index for c in result] == [0, 1, 2]

    def test_get_chunks_returns_empty_for_unknown_document(self, db):
        """Querying an unknown document_id returns an empty list (not an error).

        Input: document_id that has no stored chunks.
        Expected: empty list.
        """
        result = get_chunks(db, str(uuid.uuid4()))
        assert result == []

    def test_get_chunks_returns_only_own_document_chunks(self, db):
        """Chunks from other documents are not included in the result.

        Input: two documents each with one chunk.
        Expected: get_chunks for doc_a returns only doc_a's chunk.
        """
        doc_a = str(uuid.uuid4())
        doc_b = str(uuid.uuid4())
        save_chunks(db, doc_a, ["chunk for a"])
        save_chunks(db, doc_b, ["chunk for b"])

        result = get_chunks(db, doc_a)
        assert len(result) == 1
        assert result[0].content == "chunk for a"


class TestDeleteChunks:
    """Tests for the ``delete_chunks`` CRUD function."""

    def test_delete_chunks_removes_all_rows(self, db):
        """Deleting chunks removes every row for the given document.

        Input: document with two stored chunks.
        Expected: zero chunks remain after deletion.
        """
        doc_id = str(uuid.uuid4())
        save_chunks(db, doc_id, ["x", "y"])
        delete_chunks(db, doc_id)
        assert get_chunks(db, doc_id) == []

    def test_delete_chunks_returns_deleted_count(self, db):
        """The function returns the number of rows deleted.

        Input: document with three stored chunks.
        Expected: delete_chunks returns 3.
        """
        doc_id = str(uuid.uuid4())
        save_chunks(db, doc_id, ["a", "b", "c"])
        count = delete_chunks(db, doc_id)
        assert count == 3

    def test_delete_chunks_no_rows_returns_zero(self, db):
        """Deleting chunks for a document with none returns 0 (no error).

        Input: document_id that has no stored chunks.
        Expected: 0 returned, no exception raised.
        """
        count = delete_chunks(db, str(uuid.uuid4()))
        assert count == 0


class TestSaveAndGetMaterials:
    """Tests for ``save_material`` and ``get_materials`` CRUD functions."""

    def test_save_material_persists_summary(self, db):
        """A summary material is stored with the correct type and content.

        Input: document_id, type "summary", string content.
        Expected: get_materials returns one row with matching content.
        """
        doc_id = str(uuid.uuid4())
        save_material(db, doc_id, "summary", "A brief summary.")
        materials = get_materials(db, doc_id)
        assert len(materials) == 1
        assert materials[0].material_type == "summary"
        assert materials[0].content == "A brief summary."

    def test_save_multiple_material_types(self, db):
        """Three material types stored for one document are all retrievable.

        Input: summary, key_concepts, and flashcards for the same document.
        Expected: get_materials returns all three rows.
        """
        doc_id = str(uuid.uuid4())
        save_material(db, doc_id, "summary", "text")
        save_material(db, doc_id, "key_concepts", ["k1", "k2"])
        save_material(db, doc_id, "flashcards", [{"question": "Q?", "answer": "A."}])
        materials = get_materials(db, doc_id)
        assert len(materials) == 3

    def test_get_materials_empty_document(self, db):
        """Querying an unknown document returns an empty list (not an error).

        Input: document_id that has no stored materials.
        Expected: empty list.
        """
        result = get_materials(db, str(uuid.uuid4()))
        assert result == []


class TestDeleteMaterials:
    """Tests for the ``delete_materials`` CRUD function."""

    def test_delete_materials_removes_all_rows(self, db):
        """Deleting materials removes every row for the given document.

        Input: document with two stored materials.
        Expected: zero materials remain after deletion.
        """
        doc_id = str(uuid.uuid4())
        save_material(db, doc_id, "summary", "text")
        save_material(db, doc_id, "key_concepts", ["k1"])
        delete_materials(db, doc_id)
        assert get_materials(db, doc_id) == []

    def test_delete_materials_returns_deleted_count(self, db):
        """The function returns the number of rows deleted.

        Input: document with two stored materials.
        Expected: delete_materials returns 2.
        """
        doc_id = str(uuid.uuid4())
        save_material(db, doc_id, "summary", "text")
        save_material(db, doc_id, "key_concepts", ["k1"])
        count = delete_materials(db, doc_id)
        assert count == 2
