"""Tests for ISBN normalization, validation, and conversion."""

from app.utils.isbn import (
    is_valid_isbn10,
    is_valid_isbn13,
    isbn10_to_isbn13,
    looks_like_isbn,
    normalize_isbn,
)


class TestNormalizeIsbn:
    def test_removes_hyphens(self):
        assert normalize_isbn("978-0-13-235088-4") == "9780132350884"

    def test_removes_spaces(self):
        assert normalize_isbn("978 0 13 235088 4") == "9780132350884"

    def test_removes_mixed(self):
        assert normalize_isbn(" 978-0 13-235088 4 ") == "9780132350884"

    def test_no_change(self):
        assert normalize_isbn("9780132350884") == "9780132350884"


class TestIsValidIsbn10:
    def test_valid(self):
        assert is_valid_isbn10("0132350882") is True

    def test_valid_with_x(self):
        assert is_valid_isbn10("080442957X") is True

    def test_valid_lowercase_x(self):
        assert is_valid_isbn10("080442957x") is True

    def test_invalid_check(self):
        assert is_valid_isbn10("0132350883") is False

    def test_wrong_length(self):
        assert is_valid_isbn10("123") is False

    def test_non_digit(self):
        assert is_valid_isbn10("01323508a2") is False


class TestIsValidIsbn13:
    def test_valid(self):
        assert is_valid_isbn13("9780132350884") is True

    def test_invalid_check(self):
        assert is_valid_isbn13("9780132350885") is False

    def test_wrong_length(self):
        assert is_valid_isbn13("978013235088") is False

    def test_non_digit(self):
        assert is_valid_isbn13("978013235088a") is False


class TestIsbn10ToIsbn13:
    def test_conversion(self):
        assert isbn10_to_isbn13("0132350882") == "9780132350884"

    def test_another(self):
        assert isbn10_to_isbn13("0451524934") == "9780451524935"


class TestLooksLikeIsbn:
    def test_isbn13(self):
        assert looks_like_isbn("9780132350884") is True

    def test_isbn10(self):
        assert looks_like_isbn("0132350882") is True

    def test_isbn_with_hyphens(self):
        assert looks_like_isbn("978-0-13-235088-4") is True

    def test_isbn10_with_x(self):
        assert looks_like_isbn("080442957X") is True

    def test_not_isbn(self):
        assert looks_like_isbn("Clean Code") is False

    def test_short_number(self):
        assert looks_like_isbn("12345") is False
