"""Tests for deduplication logic."""

import pytest
from unittest.mock import MagicMock
from app.services.search import find_by_isbn, find_soft_duplicates


class TestFindByIsbn:
    def test_finds_by_isbn13(self):
        mock_book = MagicMock()
        mock_book.isbn13 = "9780132350884"

        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.first.return_value = mock_book

        result = find_by_isbn(db, "9780132350884")
        assert result is not None
        assert result.isbn13 == "9780132350884"

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.first.return_value = None

        result = find_by_isbn(db, "9780000000000")
        assert result is None


class TestFindSoftDuplicates:
    def test_finds_by_title_and_authors(self):
        mock_book = MagicMock()
        mock_book.title = "Test Book"
        mock_book.authors = "Test Author"

        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.all.return_value = [mock_book]

        result = find_soft_duplicates(db, "Test Book", "Test Author")
        assert len(result) == 1

    def test_returns_empty_when_not_found(self):
        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.all.return_value = []

        result = find_soft_duplicates(db, "Unknown", "Nobody")
        assert len(result) == 0
