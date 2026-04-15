import logging
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Book
from app.utils.isbn import looks_like_isbn, normalize_isbn

logger = logging.getLogger(__name__)


def search_books(db: Session, query: str, limit: int = 50) -> list[Book]:
    """Search books by title, authors, or ISBN. Case-insensitive, contains matching."""
    query = query.strip()
    if not query:
        return (
            db.query(Book)
            .options(joinedload(Book.location), joinedload(Book.cover))
            .order_by(Book.title)
            .limit(limit)
            .all()
        )

    results: list[Book] = []
    normalized = normalize_isbn(query)

    # If looks like ISBN, try exact ISBN match first
    if looks_like_isbn(query):
        isbn_match = (
            db.query(Book)
            .options(joinedload(Book.location), joinedload(Book.cover))
            .filter(or_(Book.isbn13 == normalized, Book.isbn10 == normalized))
            .all()
        )
        results.extend(isbn_match)
        isbn_ids = {b.id for b in isbn_match}
    else:
        isbn_ids = set()

    # Text search on title and authors
    pattern = f"%{query}%"
    text_matches = (
        db.query(Book)
        .options(joinedload(Book.location), joinedload(Book.cover))
        .filter(
            or_(
                func.lower(Book.title).like(func.lower(pattern)),
                func.lower(Book.authors).like(func.lower(pattern)),
            )
        )
        .order_by(Book.title)
        .limit(limit)
        .all()
    )

    for book in text_matches:
        if book.id not in isbn_ids:
            results.append(book)

    return results[:limit]


def find_by_isbn(db: Session, isbn: str) -> Optional[Book]:
    """Find a book by ISBN-13 or ISBN-10."""
    normalized = normalize_isbn(isbn)
    return (
        db.query(Book)
        .options(joinedload(Book.location), joinedload(Book.cover))
        .filter(or_(Book.isbn13 == normalized, Book.isbn10 == normalized))
        .first()
    )


def find_soft_duplicates(db: Session, title: str, authors: str) -> list[Book]:
    """Find possible duplicates by title + authors (case-insensitive)."""
    return (
        db.query(Book)
        .options(joinedload(Book.location), joinedload(Book.cover))
        .filter(
            func.lower(Book.title) == func.lower(title),
            func.lower(Book.authors) == func.lower(authors),
        )
        .all()
    )
