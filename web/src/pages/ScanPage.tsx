import { useCallback, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Scanner from '../components/Scanner';
import { getBookByIsbn } from '../api/client';
import type { Book } from '../types';

export default function ScanPage() {
  const navigate = useNavigate();
  const [scanning, setScanning] = useState(true);
  const [error, setError] = useState('');
  const [result, setResult] = useState<{ found: boolean; book?: Book; isbn?: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleScan = useCallback(
    async (isbn: string) => {
      if (loading) return; // Prevent concurrent lookups
      setScanning(false);
      setLoading(true);
      setError('');

      try {
        const book = await getBookByIsbn(isbn);
        setResult({ found: true, book, isbn });
      } catch {
        setResult({ found: false, isbn });
      } finally {
        setLoading(false);
      }
    },
    [loading],
  );

  const handleScanError = useCallback((msg: string) => {
    setError(msg);
  }, []);

  const resetScan = () => {
    setResult(null);
    setError('');
    setScanning(true);
  };

  return (
    <div className="main-content" style={{ maxWidth: 600, margin: '0 auto' }}>
      <div className="flex-between mb-16">
        <h1 style={{ fontSize: '1.25rem' }}>Scan ISBN</h1>
        <Link to="/" className="btn btn-secondary">← Back</Link>
      </div>

      {error && <div className="message message-error">{error}</div>}

      {scanning && !result && <Scanner onScan={handleScan} onError={handleScanError} />}

      {loading && <div className="loading">Looking up ISBN…</div>}

      {result && !loading && (
        <div className="card" style={{ textAlign: 'center' }}>
          {result.found && result.book ? (
            <>
              <div className="message message-success" style={{ marginBottom: 16 }}>
                <strong>Owned!</strong> This book is in your library.
              </div>
              <h2 style={{ marginBottom: 4 }}>{result.book.title}</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: 8 }}>{result.book.authors}</p>
              {result.book.location && (
                <p style={{ marginBottom: 16 }}>
                  📍 {[result.book.location.room, result.book.location.shelf, result.book.location.level].filter(Boolean).join(' › ')}
                </p>
              )}
              {result.book.notes && (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 16, whiteSpace: 'pre-wrap' }}>
                  {result.book.notes}
                </p>
              )}
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
                <Link to={`/book/${result.book.id}`} className="btn btn-primary">View Details</Link>
                <button className="btn btn-secondary" onClick={resetScan}>Scan Again</button>
              </div>
            </>
          ) : (
            <>
              <div className="message message-info" style={{ marginBottom: 16 }}>
                <strong>Not owned.</strong> ISBN {result.isbn} is not in your library.
              </div>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
                <Link to={`/add?isbn=${result.isbn}`} className="btn btn-primary">
                  + Add This Book
                </Link>
                <button className="btn btn-secondary" onClick={resetScan}>Scan Again</button>
              </div>
            </>
          )}
        </div>
      )}

      {!scanning && !result && !loading && (
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <button className="btn btn-primary" onClick={resetScan}>Start Scanner</button>
        </div>
      )}
    </div>
  );
}
