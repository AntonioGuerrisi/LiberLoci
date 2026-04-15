import { Link } from 'react-router-dom';
import type { Book } from '../types';
import { getBookCoverUrl } from '../api/client';

interface BookCardProps {
  book: Book;
}

export default function BookCard({ book }: BookCardProps) {
  return (
    <Link to={`/book/${book.id}`} className="book-card">
      {book.has_cover ? (
        <img
          className="book-card-cover"
          src={getBookCoverUrl(book.id)}
          alt={`Cover of ${book.title}`}
          loading="lazy"
        />
      ) : (
        <div className="book-card-cover-placeholder">📚</div>
      )}
      <div className="book-card-info">
        <div className="book-card-title" title={book.title}>
          {book.title}
        </div>
        <div className="book-card-authors" title={book.authors}>
          {book.authors}
        </div>
        <div className="book-card-meta">
          <span className={`tag-status ${book.reading_status}`}>
            {book.reading_status.replace('_', ' ')}
          </span>
          {book.location && (
            <span className="tag">{book.location.room}</span>
          )}
        </div>
      </div>
    </Link>
  );
}
