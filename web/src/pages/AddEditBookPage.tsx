import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { createBook, getBook, getLocations, lookupIsbn, updateBook, uploadCover, uploadCoverFromUrl } from '../api/client';
import type { Book, BookCreate, BookDraft, Location } from '../types';

const LOOKUP_FIELDS = ['title', 'authors', 'isbn13', 'isbn10', 'publisher', 'published_year', 'language'] as const;

type LookupField = (typeof LOOKUP_FIELDS)[number];

const LOOKUP_FIELD_LABELS: Record<LookupField, string> = {
  title: 'Title',
  authors: 'Authors',
  isbn13: 'ISBN-13',
  isbn10: 'ISBN-10',
  publisher: 'Publisher',
  published_year: 'Published Year',
  language: 'Language',
};

const PROVIDER_LABELS: Record<string, string> = {
  google_books: 'Google Books',
  open_library: 'Open Library',
};

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
  const [lookupDrafts, setLookupDrafts] = useState<BookDraft[]>([]);
  const [fieldSource, setFieldSource] = useState<Partial<Record<LookupField, number | 'manual'>>>({});
  const [coverSelection, setCoverSelection] = useState('');

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
      const response = await lookupIsbn(target);
      const drafts = response.drafts || [];
      if (drafts.length === 0) {
        throw new Error('No metadata found for this ISBN. You can add the book manually.');
      }

      const nextForm = { ...form } as Record<string, unknown>;
      const nextFieldSource: Partial<Record<LookupField, number | 'manual'>> = {};
      LOOKUP_FIELDS.forEach((field) => {
        const sourceIndex = drafts.findIndex((draft) => draft[field] != null && draft[field] !== '');
        if (sourceIndex >= 0) {
          nextFieldSource[field] = sourceIndex;
          nextForm[field] = drafts[sourceIndex][field] as string | number;
        }
      });

      setForm((prev) => ({
        ...prev,
        title: nextForm.title as string,
        authors: nextForm.authors as string,
        isbn13: nextForm.isbn13 as string,
        isbn10: nextForm.isbn10 as string,
        publisher: nextForm.publisher as string,
        published_year: nextForm.published_year as number | undefined,
        language: nextForm.language as string,
      }));
      setFieldSource(nextFieldSource);
      setLookupDrafts(drafts);

      const selectedCover = drafts.find((draft) => draft.cover_url) ?? drafts[0];
      if (selectedCover?.cover_url) {
        setCoverUrlFromLookup(selectedCover.cover_url);
        setCoverSelection(selectedCover.cover_url);
      }

      setProviderRawJson({ providers: drafts.map((draft) => ({ provider: draft.provider, raw: draft.provider_raw_json })) });
      setSuccess('Metadata loaded from multiple providers');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ISBN lookup failed');
    } finally {
      setLookupLoading(false);
    }
  };

  const selectFieldSource = (field: LookupField, value: string) => {
    if (value === 'manual') {
      setFieldSource((prev) => ({ ...prev, [field]: 'manual' }));
      return;
    }
    const index = Number(value);
    const draft = lookupDrafts[index];
    if (!draft) return;
    const fieldValue = draft[field];
    setFieldSource((prev) => ({ ...prev, [field]: index }));
    setForm((prev) => ({ ...prev, [field]: fieldValue ?? prev[field] }));
  };

  const handleCoverSelection = (url: string) => {
    setCoverSelection(url);
    setCoverUrlFromLookup(url);
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
        // Download cover server-side to bypass CORS restrictions
        try {
          await uploadCoverFromUrl(savedBook.id, coverUrlFromLookup);
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
                onKeyDown={(e) => { if (e.key === 'Enter') handleLookup(); }}
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

      {lookupDrafts.length > 0 && !isEdit && (
        <div className="card mb-16">
          <div className="flex-between mb-12">
            <div>
              <h2 style={{ marginBottom: 4 }}>Choose metadata per field</h2>
              <p className="text-secondary">Select the best value from each provider before saving.</p>
            </div>
          </div>

          {LOOKUP_FIELDS.map((field) => (
            <div className="form-group" key={field}>
              <label>{LOOKUP_FIELD_LABELS[field]}</label>
              <select
                value={fieldSource[field] ?? 'manual'}
                onChange={(e) => selectFieldSource(field, e.target.value)}
              >
                <option value="manual">Keep current / manual value</option>
                {lookupDrafts.map((draft, index) => {
                  const sourceValue = draft[field];
                  if (sourceValue == null || sourceValue === '') {
                    return null;
                  }
                  return (
                    <option key={`${field}-${index}`} value={index}>
                      From {PROVIDER_LABELS[draft.provider ?? ''] || draft.provider || `Source ${index + 1}`} — {String(sourceValue)}
                    </option>
                  );
                })}
              </select>
            </div>
          ))}

          <div className="form-group">
            <label>Cover from provider</label>
            <div className="lookup-cover-list">
              {lookupDrafts.map((draft, index) =>
                draft.cover_url ? (
                  <label key={`cover-${index}`} className="lookup-cover-item">
                    <input
                      type="radio"
                      name="cover-selection"
                      value={draft.cover_url}
                      checked={coverSelection === draft.cover_url}
                      onChange={() => handleCoverSelection(draft.cover_url ?? '')}
                    />
                    <span>{PROVIDER_LABELS[draft.provider ?? ''] || draft.provider || `Source ${index + 1}`}</span>
                    <img src={draft.cover_url} alt={`Cover ${index + 1}`} className="lookup-cover-preview" />
                  </label>
                ) : null,
              )}
              <label className="lookup-cover-item">
                <input
                  type="radio"
                  name="cover-selection"
                  value=""
                  checked={!coverSelection}
                  onChange={() => handleCoverSelection('')}
                />
                <span>No cover</span>
              </label>
            </div>
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
