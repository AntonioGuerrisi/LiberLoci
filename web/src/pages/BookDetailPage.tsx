import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { deleteBook, getBook, getBookCoverUrl } from '../api/client';
import type { Book } from '../types';

export default function BookDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    getBook(Number(id))
      .then(setBook)
      .catch((err) => setError(err.message));
  }, [id]);

  const handleDelete = async () => {
    if (!book || !confirm('Delete this book?')) return;
    await deleteBook(book.id);
    navigate('/');
  };

  if (error) return <div className="main-content"><div className="message message-error">{error}</div></div>;
  if (!book) return <div className="main-content"><div className="loading">Loading…</div></div>;

  const locationLabel = book.location
    ? [book.location.room, book.location.shelf, book.location.level].filter(Boolean).join(' › ')
    : 'Not assigned';

  return (
    <div className="main-content" style={{ maxWidth: 800, margin: '0 auto' }}>
      <div className="flex-between mb-16">
        <Link to="/" className="btn btn-secondary">← Back</Link>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to={`/book/${book.id}/edit`} className="btn btn-primary">Edit</Link>
          <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
        </div>
      </div>

      <div className="book-detail">
        <div className="book-detail-cover">
          {book.has_cover ? (
            <img src={getBookCoverUrl(book.id)} alt={`Cover of ${book.title}`} />
          ) : (
            <div className="book-detail-cover-placeholder">📚</div>
          )}
        </div>

        <div className="book-detail-info">
          <h1 className="book-detail-title">{book.title}</h1>
          <p className="book-detail-authors">{book.authors}</p>

          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <span className={`tag-status ${book.reading_status}`}>
              {book.reading_status.replace('_', ' ')}
            </span>
            <span className="tag">{book.format}</span>
          </div>

          <dl className="book-detail-meta">
            {book.isbn13 && <><dt>ISBN-13</dt><dd style={{ fontFamily: 'var(--font-mono)' }}>{book.isbn13}</dd></>}
            {book.isbn10 && <><dt>ISBN-10</dt><dd style={{ fontFamily: 'var(--font-mono)' }}>{book.isbn10}</dd></>}
            {book.publisher && <><dt>Publisher</dt><dd>{book.publisher}</dd></>}
            {book.published_year && <><dt>Year</dt><dd>{book.published_year}</dd></>}
            {book.language && <><dt>Language</dt><dd>{book.language}</dd></>}
            <dt>Location</dt><dd>{locationLabel}</dd>
          </dl>

          {book.tags.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Tags</strong>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
                {book.tags.map((tag) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          )}

          {book.notes && (
            <div>
              <strong style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Notes</strong>
              <p style={{ marginTop: 4, whiteSpace: 'pre-wrap' }}>{book.notes}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
