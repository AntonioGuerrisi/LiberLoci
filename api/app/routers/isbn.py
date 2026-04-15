import logging

from fastapi import APIRouter, HTTPException

from app.schemas import BookDraft, ISBNLookupRequest
from app.services.isbn_lookup import lookup_isbn
from app.utils.isbn import is_valid_isbn10, is_valid_isbn13, isbn10_to_isbn13, normalize_isbn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/isbn", tags=["isbn"])


@router.post("/lookup", response_model=BookDraft)
def isbn_lookup(payload: ISBNLookupRequest):
    isbn = normalize_isbn(payload.isbn)

    # Validate
    if len(isbn) == 10:
        if not is_valid_isbn10(isbn):
            raise HTTPException(status_code=400, detail="Invalid ISBN-10 check digit")
        isbn13 = isbn10_to_isbn13(isbn)
    elif len(isbn) == 13:
        if not is_valid_isbn13(isbn):
            raise HTTPException(status_code=400, detail="Invalid ISBN-13 check digit")
        isbn13 = isbn
    else:
        raise HTTPException(status_code=400, detail="ISBN must be 10 or 13 digits")

    draft = lookup_isbn(isbn13)
    if not draft:
        # Try with original if it was ISBN-10
        if len(isbn) == 10:
            draft = lookup_isbn(isbn)
        if not draft:
            raise HTTPException(status_code=404, detail="No metadata found for this ISBN. You can add the book manually.")

    return draft
