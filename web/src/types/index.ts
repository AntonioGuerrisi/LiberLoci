export interface Location {
  id: number;
  room: string;
  shelf: string | null;
  level: string | null;
  sort_order: number | null;
}

export interface Book {
  id: number;
  title: string;
  authors: string;
  isbn13: string | null;
  isbn10: string | null;
  publisher: string | null;
  published_year: number | null;
  language: string | null;
  format: 'paper' | 'ebook' | 'audiobook';
  reading_status: 'to_read' | 'reading' | 'read';
  tags: string[];
  location_id: number | null;
  location: Location | null;
  notes: string | null;
  has_cover: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookDraft {
  title: string | null;
  authors: string | null;
  isbn13: string | null;
  isbn10: string | null;
  publisher: string | null;
  published_year: number | null;
  language: string | null;
  cover_url: string | null;
  provider_raw_json: Record<string, unknown> | null;
  provider: string | null;
}

export interface ISBNLookupResponse {
  drafts: BookDraft[];
}

export interface BookCreate {
  title: string;
  authors: string;
  isbn13?: string | null;
  isbn10?: string | null;
  publisher?: string | null;
  published_year?: number | null;
  language?: string | null;
  format?: string;
  reading_status?: string;
  tags?: string[];
  location_id?: number | null;
  notes?: string | null;
  provider_raw_json?: Record<string, unknown> | null;
}

export interface LocationCreate {
  room: string;
  shelf?: string | null;
  level?: string | null;
  sort_order?: number | null;
}

export type Theme = 'light' | 'dark';

/** Location tree grouped by room → shelf → level */
export interface LocationGroup {
  room: string;
  shelves: {
    shelf: string | null;
    levels: Location[];
  }[];
}
