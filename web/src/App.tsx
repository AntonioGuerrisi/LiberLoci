import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import BookDetailPage from './pages/BookDetailPage';
import AddEditBookPage from './pages/AddEditBookPage';
import ScanPage from './pages/ScanPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/book/:id" element={<BookDetailPage />} />
        <Route path="/add" element={<AddEditBookPage />} />
        <Route path="/book/:id/edit" element={<AddEditBookPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
