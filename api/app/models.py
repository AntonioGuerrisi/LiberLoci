from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    isbn13 = Column(String(13), nullable=True)
    isbn10 = Column(String(10), nullable=True)
    publisher = Column(String, nullable=True)
    published_year = Column(Integer, nullable=True)
    language = Column(String, nullable=True)
    format = Column(String, nullable=False, default="paper")
    reading_status = Column(String, nullable=False, default="to_read")
    tags = Column(ARRAY(String), nullable=False, server_default="{}")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    notes = Column(Text, nullable=True)
    provider_raw_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=datetime.utcnow)

    location = relationship("Location", back_populates="books")
    cover = relationship("Cover", back_populates="book", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_books_isbn13_unique", "isbn13", unique=True, postgresql_where=text("isbn13 IS NOT NULL")),
        Index("ix_books_title", "title"),
        Index("ix_books_authors", "authors"),
    )


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String, nullable=False)
    shelf = Column(String, nullable=True)
    level = Column(String, nullable=True)
    sort_order = Column(Integer, nullable=True)

    books = relationship("Book", back_populates="location")


class Cover(Base):
    __tablename__ = "covers"

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    data = Column(LargeBinary, nullable=False)
    mime_type = Column(String, nullable=False, default="image/jpeg")
    checksum = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    book = relationship("Book", back_populates="cover")
