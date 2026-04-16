import logging
import time
from typing import Optional

import httpx

from app.schemas import BookDraft

logger = logging.getLogger(__name__)

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"
HTTP_TIMEOUT = 10.0


def _parse_google_books(data: dict, isbn: str) -> Optional[BookDraft]:
    """Parse a Google Books API response into a BookDraft."""
    items = data.get("items")
    if not items:
        return None
    info = items[0].get("volumeInfo", {})
    identifiers = {i["type"]: i["identifier"] for i in info.get("industryIdentifiers", [])}

    isbn13 = identifiers.get("ISBN_13")
    isbn10 = identifiers.get("ISBN_10")

    cover_url = None
    image_links = info.get("imageLinks", {})
    for key in ("thumbnail", "smallThumbnail"):
        if key in image_links:
            cover_url = image_links[key].replace("http://", "https://")
            break

    published_year = None
    pub_date = info.get("publishedDate", "")
    if pub_date and len(pub_date) >= 4:
        try:
            published_year = int(pub_date[:4])
        except ValueError:
            pass

    return BookDraft(
        title=info.get("title"),
        authors=", ".join(info.get("authors", [])) or None,
        isbn13=isbn13 or (isbn if len(isbn) == 13 else None),
        isbn10=isbn10 or (isbn if len(isbn) == 10 else None),
        publisher=info.get("publisher"),
        published_year=published_year,
        language=info.get("language"),
        cover_url=cover_url,
        provider_raw_json=data,
        provider="google_books",
    )


def _parse_open_library(data: dict, isbn: str) -> Optional[BookDraft]:
    """Parse an Open Library API response into a BookDraft."""
    key = f"ISBN:{isbn}"
    if key not in data:
        return None
    info = data[key]

    cover_url = None
    cover_info = info.get("cover", {})
    for size in ("medium", "small", "large"):
        if size in cover_info:
            cover_url = cover_info[size]
            break

    published_year = None
    pub_date = info.get("publish_date", "")
    if pub_date:
        try:
            published_year = int(pub_date[-4:]) if len(pub_date) >= 4 else None
        except ValueError:
            pass

    isbn13 = None
    isbn10 = None
    for ident in info.get("identifiers", {}).get("isbn_13", []):
        isbn13 = ident
        break
    for ident in info.get("identifiers", {}).get("isbn_10", []):
        isbn10 = ident
        break

    authors_list = [a.get("name", "") for a in info.get("authors", [])]

    return BookDraft(
        title=info.get("title"),
        authors=", ".join(authors_list) or None,
        isbn13=isbn13 or (isbn if len(isbn) == 13 else None),
        isbn10=isbn10 or (isbn if len(isbn) == 10 else None),
        publisher=", ".join(p.get("name", "") for p in info.get("publishers", [])) or None,
        published_year=published_year,
        language=None,
        cover_url=cover_url,
        provider_raw_json=data,
        provider="open_library",
    )


def lookup_google_books(isbn: str) -> Optional[BookDraft]:
    """Look up a book by ISBN using Google Books API."""
    start = time.monotonic()
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(GOOGLE_BOOKS_URL, params={"q": f"isbn:{isbn}"})
            resp.raise_for_status()
            data = resp.json()
        latency_ms = int((time.monotonic() - start) * 1000)
        draft = _parse_google_books(data, isbn)
        logger.info(
            "isbn_lookup",
            extra={"provider": "google_books", "isbn": isbn, "hit": draft is not None, "latency_ms": latency_ms},
        )
        return draft
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.warning(
            "isbn_lookup_error",
            extra={"provider": "google_books", "isbn": isbn, "error": str(exc), "latency_ms": latency_ms},
        )
        return None


def lookup_open_library(isbn: str) -> Optional[BookDraft]:
    """Look up a book by ISBN using Open Library API."""
    start = time.monotonic()
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(
                OPEN_LIBRARY_URL,
                params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
            )
            resp.raise_for_status()
            data = resp.json()
        latency_ms = int((time.monotonic() - start) * 1000)
        draft = _parse_open_library(data, isbn)
        logger.info(
            "isbn_lookup",
            extra={"provider": "open_library", "isbn": isbn, "hit": draft is not None, "latency_ms": latency_ms},
        )
        return draft
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.warning(
            "isbn_lookup_error",
            extra={"provider": "open_library", "isbn": isbn, "error": str(exc), "latency_ms": latency_ms},
        )
        return None


def lookup_isbn(isbn: str) -> Optional[BookDraft]:
    """Look up ISBN with fallback: Google Books → Open Library."""
    draft = lookup_google_books(isbn)
    if draft and draft.title:
        return draft
    draft = lookup_open_library(isbn)
    if draft and draft.title:
        return draft
    return None


def lookup_all_providers(isbn: str) -> list[BookDraft]:
    """Query all providers and return every non-empty result."""
    results: list[BookDraft] = []
    for lookup_fn in (lookup_google_books, lookup_open_library):
        draft = lookup_fn(isbn)
        if draft and draft.title:
            results.append(draft)
    return results
