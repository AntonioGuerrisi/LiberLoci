import { useEffect, useState } from 'react';
import { createLocation, deleteLocation, getLocations, updateLocation } from '../api/client';
import type { Location, LocationCreate } from '../types';

const emptyForm: LocationCreate = { room: '', shelf: '', level: '', sort_order: null };

export default function SettingsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<LocationCreate>({ ...emptyForm });
  const [showAdd, setShowAdd] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    getLocations()
      .then(setLocations)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setForm({ ...emptyForm });
    setEditId(null);
    setShowAdd(false);
    setError('');
  };

  const startEdit = (loc: Location) => {
    setEditId(loc.id);
    setShowAdd(false);
    setForm({ room: loc.room, shelf: loc.shelf || '', level: loc.level || '', sort_order: loc.sort_order });
  };

  const startAdd = () => {
    setShowAdd(true);
    setEditId(null);
    setForm({ ...emptyForm });
  };

  const handleSave = async () => {
    if (!form.room.trim()) {
      setError('Room is required.');
      return;
    }
    setError('');
    const payload: LocationCreate = {
      room: form.room.trim(),
      shelf: form.shelf?.trim() || null,
      level: form.level?.trim() || null,
      sort_order: form.sort_order,
    };
    try {
      if (editId != null) {
        await updateLocation(editId, payload);
      } else {
        await createLocation(payload);
      }
      resetForm();
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteLocation(id);
      setDeleteConfirm(null);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  const formatLocation = (loc: Location) =>
    [loc.room, loc.shelf, loc.level].filter(Boolean).join(' › ');

  return (
    <div className="main-content" style={{ maxWidth: 700, margin: '0 auto' }}>
      <div className="flex-between mb-16">
        <h1 style={{ fontSize: '1.25rem' }}>Settings</h1>
      </div>

      <div className="card mb-16">
        <div className="flex-between mb-12">
          <h2 style={{ fontSize: '1.1rem', margin: 0 }}>Locations</h2>
          {!showAdd && editId == null && (
            <button className="btn btn-primary" onClick={startAdd}>+ Add Location</button>
          )}
        </div>

        {error && <div className="message message-error mb-12">{error}</div>}

        {(showAdd || editId != null) && (
          <div className="settings-form mb-12">
            <div className="form-row">
              <div className="form-group">
                <label>Room *</label>
                <input
                  type="text"
                  value={form.room}
                  onChange={(e) => setForm((f) => ({ ...f, room: e.target.value }))}
                  placeholder="e.g. Living Room"
                />
              </div>
              <div className="form-group">
                <label>Shelf</label>
                <input
                  type="text"
                  value={form.shelf || ''}
                  onChange={(e) => setForm((f) => ({ ...f, shelf: e.target.value }))}
                  placeholder="e.g. Bookcase A"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Level</label>
                <input
                  type="text"
                  value={form.level || ''}
                  onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))}
                  placeholder="e.g. Top shelf"
                />
              </div>
              <div className="form-group">
                <label>Sort Order</label>
                <input
                  type="number"
                  value={form.sort_order ?? ''}
                  onChange={(e) => setForm((f) => ({ ...f, sort_order: e.target.value ? Number(e.target.value) : null }))}
                />
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" onClick={handleSave}>
                {editId != null ? 'Save' : 'Add'}
              </button>
              <button className="btn btn-secondary" onClick={resetForm}>Cancel</button>
            </div>
          </div>
        )}

        {loading && <p className="text-secondary">Loading…</p>}

        {!loading && locations.length === 0 && (
          <p className="text-secondary">No locations defined yet.</p>
        )}

        {!loading && locations.length > 0 && (
          <table className="settings-table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Order</th>
                <th style={{ width: 120 }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {locations.map((loc) => (
                <tr key={loc.id}>
                  <td>{formatLocation(loc)}</td>
                  <td>{loc.sort_order ?? '—'}</td>
                  <td>
                    {deleteConfirm === loc.id ? (
                      <span style={{ display: 'flex', gap: 4 }}>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(loc.id)}>Confirm</button>
                        <button className="btn btn-secondary btn-sm" onClick={() => setDeleteConfirm(null)}>No</button>
                      </span>
                    ) : (
                      <span style={{ display: 'flex', gap: 4 }}>
                        <button className="btn btn-secondary btn-sm" onClick={() => startEdit(loc)}>Edit</button>
                        <button className="btn btn-secondary btn-sm" onClick={() => setDeleteConfirm(loc.id)}>Delete</button>
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
