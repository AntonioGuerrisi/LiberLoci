import logging
import time
import xml.etree.ElementTree as ET
from typing import Optional

import httpx

from app.config import settings
from app.schemas import BookDraft

logger = logging.getLogger(__name__)

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"
WORLDCAT_XISBN_URL = "https://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?method=getMetadata&format=json&fl=*"
BNF_SRU_URL = "https://catalogue.bnf.fr/api/SRU"
HTTP_TIMEOUT = 10.0

# XML namespaces used by BNF Dublin Core responses
_BNF_NS = {
    "srw": "http://www.loc.gov/zing/srw/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


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


def _parse_worldcat(data: dict, isbn: str) -> Optional[BookDraft]:
    """Parse a WorldCat xISBN API response into a BookDraft."""
    if data.get("stat") != "ok":
        return None
    entries = data.get("list")
    if not entries:
        return None
    entry = entries[0]

    title = entry.get("title")
    if not title:
        return None

    published_year = None
    year_str = entry.get("year", "")
    if year_str:
        try:
            published_year = int(year_str[:4])
        except ValueError:
            pass

    isbn13 = isbn if len(isbn) == 13 else None
    isbn10 = isbn if len(isbn) == 10 else None

    return BookDraft(
        title=title,
        authors=entry.get("author") or None,
        isbn13=isbn13,
        isbn10=isbn10,
        publisher=entry.get("publisher") or None,
        published_year=published_year,
        language=entry.get("lang") or None,
        cover_url=None,
        provider_raw_json=data,
        provider="worldcat",
    )


def _parse_bnf(xml_bytes: bytes, isbn: str) -> Optional[BookDraft]:
    """Parse a BNF SRU Dublin Core XML response into a BookDraft."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None

    # Check if there are any records
    number_of_records_el = root.find("srw:numberOfRecords", _BNF_NS)
    if number_of_records_el is None or number_of_records_el.text == "0":
        return None

    record_data = root.find(".//srw:recordData", _BNF_NS)
    if record_data is None:
        return None
    dc = record_data.find("oai_dc:dc", _BNF_NS)
    if dc is None:
        return None

    def _text(tag: str) -> Optional[str]:
        el = dc.find(f"dc:{tag}", _BNF_NS)
        return el.text.strip() if el is not None and el.text else None

    title = _text("title")
    if not title:
        return None

    published_year = None
    date_str = _text("date")
    if date_str:
        try:
            published_year = int(date_str[:4])
        except ValueError:
            pass

    isbn13 = isbn if len(isbn) == 13 else None
    isbn10 = isbn if len(isbn) == 10 else None

    return BookDraft(
        title=title,
        authors=_text("creator"),
        isbn13=isbn13,
        isbn10=isbn10,
        publisher=_text("publisher"),
        published_year=published_year,
        language=_text("language"),
        cover_url=None,
        provider_raw_json={"bnf_xml": xml_bytes.decode("utf-8", errors="replace")},
        provider="bnf",
    )


def lookup_google_books(isbn: str) -> Optional[BookDraft]:
    """Look up a book by ISBN using Google Books API."""
    start = time.monotonic()
    try:
        params: dict = {"q": f"isbn:{isbn}"}
        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(GOOGLE_BOOKS_URL, params=params)
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


def lookup_worldcat(isbn: str) -> Optional[BookDraft]:
    """Look up a book by ISBN using WorldCat xISBN API."""
    start = time.monotonic()
    try:
        url = WORLDCAT_XISBN_URL.format(isbn=isbn)
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
        latency_ms = int((time.monotonic() - start) * 1000)
        draft = _parse_worldcat(data, isbn)
        logger.info(
            "isbn_lookup",
            extra={"provider": "worldcat", "isbn": isbn, "hit": draft is not None, "latency_ms": latency_ms},
        )
        return draft
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.warning(
            "isbn_lookup_error",
            extra={"provider": "worldcat", "isbn": isbn, "error": str(exc), "latency_ms": latency_ms},
        )
        return None


def lookup_bnf(isbn: str) -> Optional[BookDraft]:
    """Look up a book by ISBN using BNF SRU catalogue (Dublin Core XML)."""
    start = time.monotonic()
    try:
        params = {
            "version": "1.2",
            "operation": "searchRetrieve",
            "query": f'bib.isbn all "{isbn}"',
            "recordSchema": "dc",
            "maximumRecords": "1",
        }
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            resp = client.get(BNF_SRU_URL, params=params)
            resp.raise_for_status()
            xml_bytes = resp.content
        latency_ms = int((time.monotonic() - start) * 1000)
        draft = _parse_bnf(xml_bytes, isbn)
        logger.info(
            "isbn_lookup",
            extra={"provider": "bnf", "isbn": isbn, "hit": draft is not None, "latency_ms": latency_ms},
        )
        return draft
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.warning(
            "isbn_lookup_error",
            extra={"provider": "bnf", "isbn": isbn, "error": str(exc), "latency_ms": latency_ms},
        )
        return None


def lookup_isbn(isbn: str) -> Optional[BookDraft]:
    """Look up ISBN with fallback: Google Books → WorldCat → BNF → Open Library."""
    for lookup_fn in (lookup_google_books, lookup_worldcat, lookup_bnf, lookup_open_library):
        draft = lookup_fn(isbn)
        if draft and draft.title:
            return draft
    return None


def lookup_all_providers(isbn: str) -> list[BookDraft]:
    """Query all providers and return every non-empty result."""
    results: list[BookDraft] = []
    for lookup_fn in (lookup_google_books, lookup_worldcat, lookup_bnf, lookup_open_library):
        draft = lookup_fn(isbn)
        if draft and draft.title:
            results.append(draft)
    return results
