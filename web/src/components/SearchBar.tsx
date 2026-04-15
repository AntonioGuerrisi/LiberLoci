import { useState, useCallback, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';

interface SearchBarProps {
  initialQuery?: string;
  onSearch?: (query: string) => void;
}

export default function SearchBar({ initialQuery = '', onSearch }: SearchBarProps) {
  const [value, setValue] = useState(initialQuery);
  const navigate = useNavigate();

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      if (onSearch) {
        onSearch(value);
      } else {
        navigate(`/?q=${encodeURIComponent(value)}`);
      }
    },
    [value, onSearch, navigate],
  );

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <span className="search-icon">🔍</span>
      <input
        type="text"
        placeholder="Search by title, author, or ISBN..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        aria-label="Search books"
      />
    </form>
  );
}
