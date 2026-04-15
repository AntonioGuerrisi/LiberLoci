import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import BookCard from '../components/BookCard';
import LocationTree from '../components/LocationTree';
import { getLocations, searchBooks } from '../api/client';
import { useDebounce } from '../hooks/useDebounce';
import type { Book, Location } from '../types';

export default function HomePage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const debouncedQuery = useDebounce(query, 300);

  const [books, setBooks] = useState<Book[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLocations().then(setLocations).catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    searchBooks(debouncedQuery)
      .then(setBooks)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  const bookCounts = useMemo(() => {
    const map = new Map<number, number>();
    for (const b of books) {
      if (b.location_id) {
        map.set(b.location_id, (map.get(b.location_id) ?? 0) + 1);
      }
    }
    return map;
  }, [books]);

  const filteredBooks = useMemo(() => {
    if (selectedLocationId === null) return books;
    return books.filter((b) => b.location_id === selectedLocationId);
  }, [books, selectedLocationId]);

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <LocationTree
          locations={locations}
          selectedId={selectedLocationId}
          onSelect={setSelectedLocationId}
          bookCounts={bookCounts}
        />
      </aside>
      <main className="main-content">
        <div className="flex-between mb-16">
          <h1 style={{ fontSize: '1.25rem' }}>
            {query ? `Results for "${query}"` : 'Library'}
            <span style={{ color: 'var(--text-secondary)', fontWeight: 400, fontSize: '0.9rem', marginLeft: 8 }}>
              ({filteredBooks.length} {filteredBooks.length === 1 ? 'book' : 'books'})
            </span>
          </h1>
        </div>

        {loading ? (
          <div className="loading">Loading…</div>
        ) : filteredBooks.length === 0 ? (
          <div className="empty-state">
            <h2>No books found</h2>
            <p>Try a different search or add a book.</p>
          </div>
        ) : (
          <div className="book-grid">
            {filteredBooks.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
