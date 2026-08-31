import pytest
from unittest.mock import MagicMock
from sqlalchemy.sql.elements import BinaryExpression

from app.models import Book
from app.services.search import search_books


class TestSearchBooks:
    def test_returns_all_books_without_query(self):
        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.order_by.return_value = query
        query.all.return_value = ["book1", "book2"]

        result = search_books(db, "")

        assert result == ["book1", "book2"]
        query.limit.assert_not_called()

    def test_filters_by_location_id_without_query(self):
        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.order_by.return_value = query
        query.all.return_value = ["book3"]

        result = search_books(db, "", location_id=42)

        assert result == ["book3"]
        assert query.filter.called
        location_filter = query.filter.call_args.args[0]
        assert isinstance(location_filter, BinaryExpression)
        assert location_filter.compare(Book.location_id == 42)

    def test_filters_by_location_id_with_query(self):
        db = MagicMock()
        query = db.query.return_value
        query.options.return_value = query
        query.filter.return_value = query
        query.order_by.return_value = query
        query.limit.return_value = query
        mock_book = MagicMock()
        mock_book.id = 1
        query.all.return_value = [mock_book]

        result = search_books(db, "Dune", location_id=7)

        assert result == [mock_book]
        assert query.filter.called
        assert any(
            isinstance(call.args[0], BinaryExpression) and call.args[0].compare(Book.location_id == 7)
            for call in query.filter.call_args_list
        )
