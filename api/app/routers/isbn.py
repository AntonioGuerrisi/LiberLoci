import logging

from fastapi import APIRouter, HTTPException

from app.schemas import BookDraft, ISBNLookupRequest, ISBNLookupResponse
from app.services.isbn_lookup import lookup_all_providers, lookup_isbn
from app.utils.isbn import is_valid_isbn10, is_valid_isbn13, isbn10_to_isbn13, normalize_isbn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/isbn", tags=["isbn"])


@router.post("/lookup", response_model=ISBNLookupResponse)
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

    drafts = lookup_all_providers(isbn13)
    if not drafts and len(isbn) == 10:
        drafts = lookup_all_providers(isbn)
    if not drafts:
        raise HTTPException(status_code=404, detail="No metadata found for this ISBN. You can add the book manually.")

    return ISBNLookupResponse(drafts=drafts)
