"""Seed the database with demo data for quick UI testing."""

import logging
import sys

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Book, Location

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

LOCATIONS = [
    {"room": "Living Room", "shelf": "Bookcase A", "level": "Top", "sort_order": 1},
    {"room": "Living Room", "shelf": "Bookcase A", "level": "Middle", "sort_order": 2},
    {"room": "Living Room", "shelf": "Bookcase A", "level": "Bottom", "sort_order": 3},
    {"room": "Bedroom", "shelf": "Nightstand", "level": None, "sort_order": 4},
    {"room": "Study", "shelf": "Desk Shelf", "level": "Left", "sort_order": 5},
    {"room": "Study", "shelf": "Desk Shelf", "level": "Right", "sort_order": 6},
    {"room": "Study", "shelf": "Wall Unit", "level": "Row 1", "sort_order": 7},
    {"room": "Study", "shelf": "Wall Unit", "level": "Row 2", "sort_order": 8},
]

BOOKS = [
    {
        "title": "Clean Code",
        "authors": "Robert C. Martin",
        "isbn13": "9780132350884",
        "isbn10": "0132350882",
        "publisher": "Prentice Hall",
        "published_year": 2008,
        "language": "en",
        "format": "paper",
        "reading_status": "read",
        "tags": ["programming", "software engineering"],
        "notes": "A classic on writing readable code.",
    },
    {
        "title": "The Pragmatic Programmer",
        "authors": "David Thomas, Andrew Hunt",
        "isbn13": "9780135957059",
        "isbn10": "0135957052",
        "publisher": "Addison-Wesley",
        "published_year": 2019,
        "language": "en",
        "format": "paper",
        "reading_status": "read",
        "tags": ["programming", "software engineering"],
    },
    {
        "title": "Designing Data-Intensive Applications",
        "authors": "Martin Kleppmann",
        "isbn13": "9781449373320",
        "isbn10": "1449373321",
        "publisher": "O'Reilly Media",
        "published_year": 2017,
        "language": "en",
        "format": "paper",
        "reading_status": "reading",
        "tags": ["distributed systems", "databases"],
    },
    {
        "title": "Dune",
        "authors": "Frank Herbert",
        "isbn13": "9780441013593",
        "isbn10": "0441013597",
        "publisher": "Ace Books",
        "published_year": 1965,
        "language": "en",
        "format": "paper",
        "reading_status": "read",
        "tags": ["science fiction", "classic"],
    },
    {
        "title": "1984",
        "authors": "George Orwell",
        "isbn13": "9780451524935",
        "isbn10": "0451524934",
        "publisher": "Signet Classics",
        "published_year": 1949,
        "language": "en",
        "format": "paper",
        "reading_status": "read",
        "tags": ["dystopian", "classic"],
    },
    {
        "title": "The Lord of the Rings",
        "authors": "J.R.R. Tolkien",
        "isbn13": "9780618640157",
        "isbn10": "0618640150",
        "publisher": "Mariner Books",
        "published_year": 1954,
        "language": "en",
        "format": "paper",
        "reading_status": "read",
        "tags": ["fantasy", "classic"],
        "notes": "One volume edition.",
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "authors": "Yuval Noah Harari",
        "isbn13": "9780062316097",
        "isbn10": "0062316095",
        "publisher": "Harper",
        "published_year": 2015,
        "language": "en",
        "format": "paper",
        "reading_status": "to_read",
        "tags": ["history", "non-fiction"],
    },
    {
        "title": "Il nome della rosa",
        "authors": "Umberto Eco",
        "isbn13": "9788845292613",
        "publisher": "Bompiani",
        "published_year": 1980,
        "language": "it",
        "format": "paper",
        "reading_status": "read",
        "tags": ["mystery", "historical fiction", "italian"],
    },
    {
        "title": "Structure and Interpretation of Computer Programs",
        "authors": "Harold Abelson, Gerald Jay Sussman",
        "isbn13": "9780262510875",
        "isbn10": "0262510871",
        "publisher": "MIT Press",
        "published_year": 1996,
        "language": "en",
        "format": "paper",
        "reading_status": "to_read",
        "tags": ["programming", "computer science"],
    },
    {
        "title": "Meditations",
        "authors": "Marcus Aurelius",
        "isbn13": "9780140449334",
        "isbn10": "0140449337",
        "publisher": "Penguin Classics",
        "published_year": 180,
        "language": "en",
        "format": "ebook",
        "reading_status": "reading",
        "tags": ["philosophy", "classic", "stoicism"],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if db.query(Book).count() > 0:
            logger.info("Database already has books, skipping seed.")
            return

        # Create locations
        location_ids: list[int] = []
        for loc_data in LOCATIONS:
            loc = Location(**loc_data)
            db.add(loc)
            db.flush()
            location_ids.append(loc.id)
        logger.info(f"Created {len(location_ids)} locations.")

        # Create books and assign locations round-robin
        for i, book_data in enumerate(BOOKS):
            book_data["location_id"] = location_ids[i % len(location_ids)]
            book = Book(**book_data)
            db.add(book)
        db.commit()
        logger.info(f"Created {len(BOOKS)} demo books.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
