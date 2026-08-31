import type { Book, BookCreate, ISBNLookupResponse, Location, LocationCreate } from '../types';

const BASE = '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(body.detail || resp.statusText);
  }
  if (resp.status === 204) return undefined as unknown as T;
  return resp.json();
}

// Books
export const searchBooks = (query: string, locationId?: number) => {
  const params = new URLSearchParams();
  if (query) params.append('query', query);
  if (locationId !== undefined && locationId !== null) params.append('location_id', String(locationId));
  const url = `${BASE}/books${params.toString() ? `?${params.toString()}` : ''}`;
  return request<Book[]>(url);
}
export const getBookByIsbn = (isbn: string) =>
  request<Book>(`${BASE}/books/by-isbn/${encodeURIComponent(isbn)}`);

export const getBook = (id: number) =>
  request<Book>(`${BASE}/books/${id}`);

export const createBook = (data: BookCreate) =>
  request<Book>(`${BASE}/books`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

export const updateBook = (id: number, data: Partial<BookCreate>) =>
  request<Book>(`${BASE}/books/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

export const deleteBook = (id: number) =>
  request<void>(`${BASE}/books/${id}`, { method: 'DELETE' });

export const getBookCoverUrl = (id: number) =>
  `${BASE}/books/${id}/cover`;

export const uploadCover = (bookId: number, file: File) => {
  const form = new FormData();
  form.append('file', file);
  return request<void>(`${BASE}/books/${bookId}/cover`, {
    method: 'PUT',
    body: form,
  });
};

export const uploadCoverFromUrl = (bookId: number, url: string) =>
  request<void>(`${BASE}/books/${bookId}/cover-from-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

// ISBN lookup
export const lookupIsbn = (isbn: string) =>
  request<ISBNLookupResponse>(`${BASE}/isbn/lookup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ isbn }),
  });

// Locations
export const getLocations = () =>
  request<Location[]>(`${BASE}/locations`);

export const createLocation = (data: LocationCreate) =>
  request<Location>(`${BASE}/locations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

export const updateLocation = (id: number, data: Partial<LocationCreate>) =>
  request<Location>(`${BASE}/locations/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

export const deleteLocation = (id: number) =>
  request<void>(`${BASE}/locations/${id}`, { method: 'DELETE' });

// Tags
export const getTags = () =>
  request<string[]>(`${BASE}/tags`);

// Export/Import
export const exportLibrary = () =>
  request<unknown>(`${BASE}/library/export`);

export const importLibrary = (file: File) => {
  const form = new FormData();
  form.append('file', file);
  return request<{ imported_books: number; imported_locations: number }>(`${BASE}/library/import`, {
    method: 'POST',
    body: form,
  });
};
