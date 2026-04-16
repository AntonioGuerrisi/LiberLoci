from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.isbn import normalize_isbn


# ---------- Location ----------

class LocationCreate(BaseModel):
    room: str
    shelf: Optional[str] = None
    level: Optional[str] = None
    sort_order: Optional[int] = None


class LocationResponse(BaseModel):
    id: int
    room: str
    shelf: Optional[str] = None
    level: Optional[str] = None
    sort_order: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Book ----------

class BookCreate(BaseModel):
    title: str
    authors: str
    isbn13: Optional[str] = None
    isbn10: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    language: Optional[str] = None
    format: str = "paper"
    reading_status: str = "to_read"
    tags: list[str] = []
    location_id: Optional[int] = None
    notes: Optional[str] = None
    provider_raw_json: Optional[dict] = None

    @field_validator("isbn13", mode="before")
    @classmethod
    def normalize_isbn13(cls, v: Optional[str]) -> Optional[str]:
        return normalize_isbn(v) if v else None

    @field_validator("isbn10", mode="before")
    @classmethod
    def normalize_isbn10(cls, v: Optional[str]) -> Optional[str]:
        return normalize_isbn(v) if v else None

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed = {"paper", "ebook", "audiobook"}
        if v not in allowed:
            raise ValueError(f"format must be one of {allowed}")
        return v

    @field_validator("reading_status")
    @classmethod
    def validate_reading_status(cls, v: str) -> str:
        allowed = {"to_read", "reading", "read"}
        if v not in allowed:
            raise ValueError(f"reading_status must be one of {allowed}")
        return v


class BookUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    isbn13: Optional[str] = None
    isbn10: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    language: Optional[str] = None
    format: Optional[str] = None
    reading_status: Optional[str] = None
    tags: Optional[list[str]] = None
    location_id: Optional[int] = None
    notes: Optional[str] = None
    provider_raw_json: Optional[dict] = None

    @field_validator("isbn13", mode="before")
    @classmethod
    def normalize_isbn13(cls, v: Optional[str]) -> Optional[str]:
        return normalize_isbn(v) if v else None

    @field_validator("isbn10", mode="before")
    @classmethod
    def normalize_isbn10(cls, v: Optional[str]) -> Optional[str]:
        return normalize_isbn(v) if v else None


class BookResponse(BaseModel):
    id: int
    title: str
    authors: str
    isbn13: Optional[str] = None
    isbn10: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    language: Optional[str] = None
    format: str
    reading_status: str
    tags: list[str]
    location_id: Optional[int] = None
    location: Optional[LocationResponse] = None
    notes: Optional[str] = None
    has_cover: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_book(cls, book) -> "BookResponse":
        return cls(
            id=book.id,
            title=book.title,
            authors=book.authors,
            isbn13=book.isbn13,
            isbn10=book.isbn10,
            publisher=book.publisher,
            published_year=book.published_year,
            language=book.language,
            format=book.format,
            reading_status=book.reading_status,
            tags=book.tags or [],
            location_id=book.location_id,
            location=LocationResponse.model_validate(book.location) if book.location else None,
            notes=book.notes,
            has_cover=book.cover is not None,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )


# ---------- ISBN Lookup ----------

class ISBNLookupRequest(BaseModel):
    isbn: str

    @field_validator("isbn", mode="before")
    @classmethod
    def normalize(cls, v: str) -> str:
        return normalize_isbn(v)


class BookDraft(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    isbn13: Optional[str] = None
    isbn10: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    language: Optional[str] = None
    cover_url: Optional[str] = None
    provider_raw_json: Optional[dict] = None
    provider: Optional[str] = None


class ISBNLookupResponse(BaseModel):
    drafts: list[BookDraft]


# ---------- Export / Import ----------

class CoverExport(BaseModel):
    data_base64: str
    mime_type: str
    checksum: str
    width: Optional[int] = None
    height: Optional[int] = None


class BookExport(BaseModel):
    title: str
    authors: str
    isbn13: Optional[str] = None
    isbn10: Optional[str] = None
    publisher: Optional[str] = None
    published_year: Optional[int] = None
    language: Optional[str] = None
    format: str
    reading_status: str
    tags: list[str]
    notes: Optional[str] = None
    provider_raw_json: Optional[dict] = None
    location_room: Optional[str] = None
    location_shelf: Optional[str] = None
    location_level: Optional[str] = None
    cover: Optional[CoverExport] = None


class LibraryExport(BaseModel):
    version: int = 1
    exported_at: datetime
    locations: list[LocationCreate]
    books: list[BookExport]
