import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { createBook, getBook, getLocations, lookupIsbn, updateBook, uploadCover } from '../api/client';
import type { Book, BookCreate, Location } from '../types';

export default function AddEditBookPage() {
  const { id } = useParams<{ id: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // ISBN lookup
  const [isbnInput, setIsbnInput] = useState(searchParams.get('isbn') || '');
  const [lookupLoading, setLookupLoading] = useState(false);

  // Form state
  const [form, setForm] = useState<BookCreate>({
    title: '',
    authors: '',
    isbn13: '',
    isbn10: '',
    publisher: '',
    published_year: undefined,
    language: '',
    format: 'paper',
    reading_status: 'to_read',
    tags: [],
    location_id: null,
    notes: '',
  });
  const [tagsInput, setTagsInput] = useState('');
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [coverUrlFromLookup, setCoverUrlFromLookup] = useState('');
  const [providerRawJson, setProviderRawJson] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    getLocations().then(setLocations).catch(console.error);
  }, []);

  // Load existing book for editing
  useEffect(() => {
    if (isEdit && id) {
      getBook(Number(id)).then((book) => {
        setForm({
          title: book.title,
          authors: book.authors,
          isbn13: book.isbn13 || '',
          isbn10: book.isbn10 || '',
          publisher: book.publisher || '',
          published_year: book.published_year || undefined,
          language: book.language || '',
          format: book.format,
          reading_status: book.reading_status,
          tags: book.tags,
          location_id: book.location_id,
          notes: book.notes || '',
        });
        setTagsInput(book.tags.join(', '));
      }).catch((err) => setError(err.message));
    }
  }, [id, isEdit]);

  // Auto-lookup if isbn param is provided
  useEffect(() => {
    const isbn = searchParams.get('isbn');
    if (isbn && !isEdit) {
      handleLookup(isbn);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLookup = async (isbn?: string) => {
    const target = isbn || isbnInput.trim();
    if (!target) return;
    setLookupLoading(true);
    setError('');
    try {
      const draft = await lookupIsbn(target);
      setForm((prev) => ({
        ...prev,
        title: draft.title || prev.title,
        authors: draft.authors || prev.authors,
        isbn13: draft.isbn13 || prev.isbn13 || '',
        isbn10: draft.isbn10 || prev.isbn10 || '',
        publisher: draft.publisher || prev.publisher || '',
        published_year: draft.published_year || prev.published_year,
        language: draft.language || prev.language || '',
      }));
      if (draft.cover_url) setCoverUrlFromLookup(draft.cover_url);
      if (draft.provider_raw_json) setProviderRawJson(draft.provider_raw_json);
      setSuccess('Metadata loaded from ' + (draft.provider || 'provider'));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ISBN lookup failed');
    } finally {
      setLookupLoading(false);
    }
  };

  const handleChange = (field: keyof BookCreate, value: string | number | null) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title || !form.authors) {
      setError('Title and authors are required.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const payload: BookCreate = {
        ...form,
        tags: tagsInput.split(',').map((t) => t.trim()).filter(Boolean),
        isbn13: form.isbn13 || null,
        isbn10: form.isbn10 || null,
        publisher: form.publisher || null,
        language: form.language || null,
        location_id: form.location_id || null,
        notes: form.notes || null,
        provider_raw_json: providerRawJson,
      };

      let savedBook: Book;
      if (isEdit && id) {
        savedBook = await updateBook(Number(id), payload);
      } else {
        savedBook = await createBook(payload);
      }

      // Upload cover if file selected
      if (coverFile) {
        await uploadCover(savedBook.id, coverFile);
      } else if (coverUrlFromLookup && !isEdit) {
        // Download cover from lookup URL via API proxy or direct
        try {
          const resp = await fetch(coverUrlFromLookup);
          if (resp.ok) {
            const blob = await resp.blob();
            const file = new File([blob], 'cover.jpg', { type: blob.type });
            await uploadCover(savedBook.id, file);
          }
        } catch {
          // Cover download failed, proceed without cover
        }
      }

      navigate(`/book/${savedBook.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content" style={{ maxWidth: 700, margin: '0 auto' }}>
      <div className="flex-between mb-16">
        <h1 style={{ fontSize: '1.25rem' }}>{isEdit ? 'Edit Book' : 'Add Book'}</h1>
        <Link to={isEdit ? `/book/${id}` : '/'} className="btn btn-secondary">Cancel</Link>
      </div>

      {!isEdit && (
        <div className="card mb-16">
          <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
            <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
              <label>ISBN Lookup</label>
              <input
                type="text"
                placeholder="Enter ISBN to auto-fill metadata…"
                value={isbnInput}
                onChange={(e) => setIsbnInput(e.target.value)}
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={() => handleLookup()}
              disabled={lookupLoading}
              style={{ marginBottom: 0 }}
            >
              {lookupLoading ? 'Looking up…' : 'Lookup'}
            </button>
          </div>
        </div>
      )}

      {error && <div className="message message-error">{error}</div>}
      {success && <div className="message message-success">{success}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Title *</label>
            <input type="text" value={form.title} onChange={(e) => handleChange('title', e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Authors *</label>
            <input type="text" value={form.authors} onChange={(e) => handleChange('authors', e.target.value)} required />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>ISBN-13</label>
            <input type="text" value={form.isbn13 || ''} onChange={(e) => handleChange('isbn13', e.target.value)} />
          </div>
          <div className="form-group">
            <label>ISBN-10</label>
            <input type="text" value={form.isbn10 || ''} onChange={(e) => handleChange('isbn10', e.target.value)} />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Publisher</label>
            <input type="text" value={form.publisher || ''} onChange={(e) => handleChange('publisher', e.target.value)} />
          </div>
          <div className="form-group">
            <label>Published Year</label>
            <input
              type="number"
              value={form.published_year ?? ''}
              onChange={(e) => handleChange('published_year', e.target.value ? Number(e.target.value) : null)}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Language</label>
            <input type="text" value={form.language || ''} onChange={(e) => handleChange('language', e.target.value)} />
          </div>
          <div className="form-group">
            <label>Format</label>
            <select value={form.format} onChange={(e) => handleChange('format', e.target.value)}>
              <option value="paper">Paper</option>
              <option value="ebook">E-book</option>
              <option value="audiobook">Audiobook</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Reading Status</label>
            <select value={form.reading_status} onChange={(e) => handleChange('reading_status', e.target.value)}>
              <option value="to_read">To Read</option>
              <option value="reading">Reading</option>
              <option value="read">Read</option>
            </select>
          </div>
          <div className="form-group">
            <label>Location</label>
            <select
              value={form.location_id ?? ''}
              onChange={(e) => handleChange('location_id', e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">None</option>
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {[loc.room, loc.shelf, loc.level].filter(Boolean).join(' › ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Tags (comma separated)</label>
          <input
            type="text"
            placeholder="e.g. fiction, fantasy, classic"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Notes</label>
          <textarea value={form.notes || ''} onChange={(e) => handleChange('notes', e.target.value)} />
        </div>

        <div className="form-group">
          <label>Cover Image</label>
          <input type="file" accept="image/*" onChange={(e) => setCoverFile(e.target.files?.[0] ?? null)} />
          {coverUrlFromLookup && !coverFile && (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Cover will be downloaded from provider.
            </p>
          )}
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving…' : isEdit ? 'Save Changes' : 'Add Book'}
          </button>
          <Link to={isEdit ? `/book/${id}` : '/'} className="btn btn-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
