import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Cover
from app.schemas import BookCreate, BookResponse, BookUpdate
from app.services.cover import process_cover
from app.services.search import find_by_isbn, find_soft_duplicates, search_books
from app.utils.isbn import is_valid_isbn10, is_valid_isbn13, normalize_isbn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
def list_books(query: Optional[str] = Query(None, alias="query"), db: Session = Depends(get_db)):
    books = search_books(db, query or "")
    return [BookResponse.from_book(b) for b in books]


@router.get("/by-isbn/{isbn}", response_model=BookResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    normalized = normalize_isbn(isbn)
    book = find_by_isbn(db, normalized)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookResponse.from_book(book)


@router.post("", response_model=BookResponse, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    # Dedupe by ISBN-13
    if payload.isbn13:
        normalized = normalize_isbn(payload.isbn13)
        if not is_valid_isbn13(normalized):
            raise HTTPException(status_code=400, detail="Invalid ISBN-13 check digit")
        existing = find_by_isbn(db, normalized)
        if existing:
            logger.info("dedupe_hit", extra={"isbn13": normalized, "existing_id": existing.id})
            return BookResponse.from_book(existing)

    if payload.isbn10:
        normalized10 = normalize_isbn(payload.isbn10)
        if not is_valid_isbn10(normalized10):
            raise HTTPException(status_code=400, detail="Invalid ISBN-10 check digit")

    # Soft dedupe for books without ISBN
    if not payload.isbn13:
        dupes = find_soft_duplicates(db, payload.title, payload.authors)
        if dupes:
            logger.info("soft_dedupe_hit", extra={"title": payload.title, "existing_id": dupes[0].id})
            return BookResponse.from_book(dupes[0])

    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    logger.info("book_created", extra={"id": book.id, "isbn13": book.isbn13})
    return BookResponse.from_book(book)


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookResponse.from_book(book)


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "isbn13" in update_data and update_data["isbn13"]:
        if not is_valid_isbn13(update_data["isbn13"]):
            raise HTTPException(status_code=400, detail="Invalid ISBN-13 check digit")
    if "isbn10" in update_data and update_data["isbn10"]:
        if not is_valid_isbn10(update_data["isbn10"]):
            raise HTTPException(status_code=400, detail="Invalid ISBN-10 check digit")

    for key, value in update_data.items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return BookResponse.from_book(book)


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()


@router.get("/{book_id}/cover")
def get_cover(book_id: int, db: Session = Depends(get_db)):
    cover = db.query(Cover).filter(Cover.book_id == book_id).first()
    if not cover:
        raise HTTPException(status_code=404, detail="Cover not found")
    return Response(content=cover.data, media_type=cover.mime_type)


@router.put("/{book_id}/cover", status_code=204)
def upload_cover(book_id: int, file: UploadFile, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    raw = file.file.read()
    data, width, height, checksum = process_cover(raw)

    existing = db.query(Cover).filter(Cover.book_id == book_id).first()
    if existing:
        existing.data = data
        existing.mime_type = "image/jpeg"
        existing.checksum = checksum
        existing.width = width
        existing.height = height
    else:
        cover = Cover(
            book_id=book_id,
            data=data,
            mime_type="image/jpeg",
            checksum=checksum,
            width=width,
            height=height,
        )
        db.add(cover)

    db.commit()
    logger.info("cover_stored", extra={"book_id": book_id, "checksum": checksum, "width": width, "height": height})
