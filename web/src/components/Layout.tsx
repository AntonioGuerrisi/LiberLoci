import { Outlet, Link, useNavigate, useSearchParams } from 'react-router-dom';
import SearchBar from './SearchBar';
import ThemeToggle from './ThemeToggle';

export default function Layout() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  return (
    <>
      <header className="header">
        <Link to="/" className="header-logo">
          📚 <span>LiberLoci</span>
        </Link>
        <div className="header-search">
          <SearchBar
            initialQuery={query}
            onSearch={(q) => navigate(`/?q=${encodeURIComponent(q)}`)}
          />
        </div>
        <div className="header-actions">
          <Link to="/scan" className="btn btn-primary" title="Scan ISBN">
            📷 Scan
          </Link>
          <Link to="/add" className="btn btn-secondary" title="Add book manually">
            + Add
          </Link>
          <Link to="/settings" className="btn btn-secondary" title="Settings">
            ⚙️
          </Link>
          <ThemeToggle />
        </div>
      </header>
      <Outlet />
    </>
  );
}
