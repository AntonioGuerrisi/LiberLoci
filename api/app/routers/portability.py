import base64
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Book, Cover, Location
from app.schemas import BookExport, CoverExport, LibraryExport, LocationCreate
from app.services.cover import process_cover

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/library", tags=["portability"])


@router.get("/export")
def export_library(db: Session = Depends(get_db)):
    """Export the full library as JSON including cover bytes (base64)."""
    locations = db.query(Location).order_by(Location.id).all()
    books = db.query(Book).options(joinedload(Book.location), joinedload(Book.cover)).order_by(Book.id).all()

    location_exports = [LocationCreate(room=loc.room, shelf=loc.shelf, level=loc.level, sort_order=loc.sort_order) for loc in locations]

    book_exports = []
    for book in books:
        cover_export = None
        if book.cover:
            cover_export = CoverExport(
                data_base64=base64.b64encode(book.cover.data).decode("ascii"),
                mime_type=book.cover.mime_type,
                checksum=book.cover.checksum,
                width=book.cover.width,
                height=book.cover.height,
            )
        book_exports.append(
            BookExport(
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
                notes=book.notes,
                provider_raw_json=book.provider_raw_json,
                location_room=book.location.room if book.location else None,
                location_shelf=book.location.shelf if book.location else None,
                location_level=book.location.level if book.location else None,
                cover=cover_export,
            )
        )

    export = LibraryExport(
        version=1,
        exported_at=datetime.now(timezone.utc),
        locations=location_exports,
        books=book_exports,
    )
    return JSONResponse(content=export.model_dump(mode="json"))


@router.post("/import", status_code=201)
def import_library(file: UploadFile, db: Session = Depends(get_db)):
    """Import a full library from JSON export."""
    raw = file.file.read()
    data = LibraryExport.model_validate_json(raw)

    # Create locations (deduplicating by room+shelf+level)
    location_map: dict[tuple, int] = {}
    existing_locations = db.query(Location).all()
    for loc in existing_locations:
        location_map[(loc.room, loc.shelf, loc.level)] = loc.id

    for loc_data in data.locations:
        key = (loc_data.room, loc_data.shelf, loc_data.level)
        if key not in location_map:
            loc = Location(**loc_data.model_dump())
            db.add(loc)
            db.flush()
            location_map[key] = loc.id

    # Create books
    imported_count = 0
    for book_data in data.books:
        # Skip duplicates by ISBN
        if book_data.isbn13:
            existing = db.query(Book).filter(Book.isbn13 == book_data.isbn13).first()
            if existing:
                continue

        location_id = None
        if book_data.location_room:
            key = (book_data.location_room, book_data.location_shelf, book_data.location_level)
            location_id = location_map.get(key)

        book = Book(
            title=book_data.title,
            authors=book_data.authors,
            isbn13=book_data.isbn13,
            isbn10=book_data.isbn10,
            publisher=book_data.publisher,
            published_year=book_data.published_year,
            language=book_data.language,
            format=book_data.format,
            reading_status=book_data.reading_status,
            tags=book_data.tags,
            notes=book_data.notes,
            provider_raw_json=book_data.provider_raw_json,
            location_id=location_id,
        )
        db.add(book)
        db.flush()

        if book_data.cover:
            cover_bytes = base64.b64decode(book_data.cover.data_base64)
            cover = Cover(
                book_id=book.id,
                data=cover_bytes,
                mime_type=book_data.cover.mime_type,
                checksum=book_data.cover.checksum,
                width=book_data.cover.width,
                height=book_data.cover.height,
            )
            db.add(cover)

        imported_count += 1

    db.commit()
    logger.info("library_imported", extra={"books": imported_count, "locations": len(data.locations)})
    return {"imported_books": imported_count, "imported_locations": len(data.locations)}
