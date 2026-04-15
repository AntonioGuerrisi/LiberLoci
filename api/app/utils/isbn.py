import re


def normalize_isbn(raw: str) -> str:
    """Remove spaces and hyphens from an ISBN string."""
    return re.sub(r"[\s\-]", "", raw.strip())


def is_valid_isbn10(isbn: str) -> bool:
    """Validate ISBN-10 check digit."""
    if len(isbn) != 10:
        return False
    total = 0
    for i, ch in enumerate(isbn[:9]):
        if not ch.isdigit():
            return False
        total += int(ch) * (10 - i)
    last = isbn[9].upper()
    if last == "X":
        total += 10
    elif last.isdigit():
        total += int(last)
    else:
        return False
    return total % 11 == 0


def is_valid_isbn13(isbn: str) -> bool:
    """Validate ISBN-13 check digit."""
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(isbn))
    return total % 10 == 0


def isbn10_to_isbn13(isbn10: str) -> str:
    """Convert a valid ISBN-10 to ISBN-13."""
    base = "978" + isbn10[:9]
    total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(base))
    check = (10 - (total % 10)) % 10
    return base + str(check)


def looks_like_isbn(query: str) -> bool:
    """Check if a search query looks like an ISBN (after normalization)."""
    normalized = normalize_isbn(query)
    if len(normalized) == 13 and normalized.isdigit():
        return True
    if len(normalized) == 10 and normalized[:9].isdigit() and (normalized[9].isdigit() or normalized[9].upper() == "X"):
        return True
    return False
