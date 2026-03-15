'use client'

import { useState, useEffect } from 'react';
import { Route , Plus, Loader2 } from 'lucide-react';
import Link from 'next/link';

interface Trip {
  id: string;
  status: 'Draft' | 'In Progress' | 'Completed';
  driver_name: string;
  package_count: number;
}

export default function TripsPage() {

  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTrips() {
      try {
        const res = await fetch('http://localhost:8000/api/v1/trips');
        const data = await res.json();
        setTrips(data);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    }
    fetchTrips();
  }, []);

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'In Progress': return { bg: 'var(--status-in-transit-bg)', text: 'var(--status-in-transit)' };
      case 'Completed': return { bg: 'rgba(34, 197, 94, 0.1)', text: '#16a34a' };
      default: return { bg: 'rgba(107, 114, 128, 0.1)', text: '#6b7280' };
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Trips</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage and schedule delivery trips.</p>
        </div>
        <Link href="/trips/create" className="flex items-center gap-2 px-4 py-2 bg-[var(--primary-blue)] text-white rounded-[var(--border-radius)] hover:opacity-90 transition-all">
          <Plus size={18} />
          Create New Trip
        </Link>
      </div>

      <div className="bg-[var(--card-bg)] rounded-[var(--border-radius)] border border-[var(--border-color)] overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50/50 border-b border-[var(--border-color)]">
            <tr className="text-[var(--text-secondary)]">
              <th className="p-4 text-left font-medium">Trip ID</th>
              <th className="p-4 text-left font-medium">Status</th>
              <th className="p-4 text-left font-medium">Driver</th>
              <th className="p-4 text-left font-medium">Package Count</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={4} className="p-10 text-center"><Loader2 className="animate-spin mx-auto" /></td></tr>
            ) : trips.map((trip) => (
              <tr key={trip.id} className="border-b border-[var(--border-color)] hover:bg-gray-50/30">
                <td className="p-4 font-medium">
                  <Link href={`/trips/${trip.id}`} className="text-[var(--primary-blue)] hover:underline">#{trip.id.slice(0,8)}</Link>
                </td>
                <td className="p-4">
                   <span className="px-2 py-1 rounded-full text-xs font-medium" style={{ backgroundColor: getStatusStyle(trip.status).bg, color: getStatusStyle(trip.status).text }}>
                    {trip.status}
                  </span>
                </td>
                <td className="p-4 text-[var(--text-primary)]">{trip.driver_name || 'Unassigned'}</td>
                <td className="p-4">{trip.package_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
