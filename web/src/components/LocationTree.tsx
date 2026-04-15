import { useMemo, useState } from 'react';
import type { Location, LocationGroup } from '../types';

interface LocationTreeProps {
  locations: Location[];
  selectedId: number | null;
  onSelect: (id: number | null) => void;
  bookCounts?: Map<number, number>;
}

function groupLocations(locations: Location[]): LocationGroup[] {
  const roomMap = new Map<string, Map<string | null, Location[]>>();

  for (const loc of locations) {
    if (!roomMap.has(loc.room)) {
      roomMap.set(loc.room, new Map());
    }
    const shelfMap = roomMap.get(loc.room)!;
    const key = loc.shelf;
    if (!shelfMap.has(key)) {
      shelfMap.set(key, []);
    }
    shelfMap.get(key)!.push(loc);
  }

  const groups: LocationGroup[] = [];
  for (const [room, shelfMap] of roomMap) {
    const shelves: LocationGroup['shelves'] = [];
    for (const [shelf, levels] of shelfMap) {
      shelves.push({ shelf, levels: levels.sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0)) });
    }
    groups.push({ room, shelves });
  }
  return groups;
}

export default function LocationTree({ locations, selectedId, onSelect, bookCounts }: LocationTreeProps) {
  const groups = useMemo(() => groupLocations(locations), [locations]);
  const [expandedRooms, setExpandedRooms] = useState<Set<string>>(new Set(groups.map((g) => g.room)));

  const toggleRoom = (room: string) => {
    setExpandedRooms((prev) => {
      const next = new Set(prev);
      if (next.has(room)) next.delete(room);
      else next.add(room);
      return next;
    });
  };

  return (
    <div className="location-tree">
      <h3>Locations</h3>
      <div
        className={`location-item ${selectedId === null ? 'active' : ''}`}
        style={{ paddingLeft: 8 }}
        onClick={() => onSelect(null)}
      >
        All locations
      </div>
      {groups.map((group) => (
        <div key={group.room}>
          <div className="location-room" onClick={() => toggleRoom(group.room)}>
            {expandedRooms.has(group.room) ? '▾' : '▸'} {group.room}
          </div>
          {expandedRooms.has(group.room) &&
            group.shelves.map((shelf) => (
              <div key={shelf.shelf ?? '_none'} className="location-shelf">
                {shelf.levels.map((loc) => {
                  const label = [shelf.shelf, loc.level].filter(Boolean).join(' › ') || 'Default';
                  const count = bookCounts?.get(loc.id) ?? 0;
                  return (
                    <div
                      key={loc.id}
                      className={`location-item ${selectedId === loc.id ? 'active' : ''}`}
                      onClick={() => onSelect(loc.id)}
                    >
                      {label}
                      {count > 0 && <span className="count"> ({count})</span>}
                    </div>
                  );
                })}
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}
