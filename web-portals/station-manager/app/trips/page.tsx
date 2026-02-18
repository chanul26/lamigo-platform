import Link from 'next/link';
import { Route, Plus } from 'lucide-react';

const TRIPS = [
  { id: 'TRP-001', driver: 'Saman', status: 'In Progress', progress: '3/8' },
  { id: 'TRP-002', driver: 'Nimal', status: 'Scheduled', progress: '0/5' },
  { id: 'TRP-003', driver: 'Sunil', status: 'Completed', progress: '6/6' },
  { id: 'TRP-004', driver: 'Chaminda', status: 'In Progress', progress: '2/4' },
  { id: 'TRP-005', driver: 'Priyantha', status: 'Scheduled', progress: '0/7' },
];

export default function TripsPage() {
  return (
    <div className="p-8 animate-fade-in">
      {/* Header: title left, action right */}
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1
            className="text-2xl font-semibold mb-2"
            style={{ color: 'var(--text-primary)' }}
          >
            Trips
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Manage and schedule delivery trips.
          </p>
        </div>
        <Link
          href="/trips/create"
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-[var(--border-radius)] font-semibold text-sm transition-colors hover:opacity-90 shrink-0"
          style={{
            backgroundColor: 'var(--primary-blue)',
            color: 'white',
          }}
        >
          <Plus size={20} />
          Create New Trip
        </Link>
      </div>

      {/* Trips table */}
      <div
        className="rounded-[var(--border-radius)] overflow-hidden border"
        style={{
          backgroundColor: 'var(--card-bg)',
          borderColor: 'var(--border-color)',
        }}
      >
        <table className="w-full text-left">
          <thead>
            <tr
              style={{
                backgroundColor: 'var(--card-bg-hover)',
                borderBottom: '1px solid var(--border-color)',
              }}
            >
              <th
                className="px-6 py-4 text-xs font-semibold uppercase tracking-wider"
                style={{ color: 'var(--text-muted)' }}
              >
                Trip ID
              </th>
              <th
                className="px-6 py-4 text-xs font-semibold uppercase tracking-wider"
                style={{ color: 'var(--text-muted)' }}
              >
                Driver
              </th>
              <th
                className="px-6 py-4 text-xs font-semibold uppercase tracking-wider"
                style={{ color: 'var(--text-muted)' }}
              >
                Status
              </th>
              <th
                className="px-6 py-4 text-xs font-semibold uppercase tracking-wider"
                style={{ color: 'var(--text-muted)' }}
              >
                Progress
              </th>
            </tr>
          </thead>
          <tbody>
            {TRIPS.map((trip) => (
              <tr
                key={trip.id}
                style={{
                  borderBottom: '1px solid var(--border-color)',
                }}
              >
                <td
                  className="px-6 py-4 font-medium font-mono text-sm"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {trip.id}
                </td>
                <td
                  className="px-6 py-4 text-sm"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {trip.driver}
                </td>
                <td className="px-6 py-4">
                  <span
                    className="inline-block px-3 py-1 rounded-full text-xs font-medium"
                    style={{
                      backgroundColor:
                        trip.status === 'Completed'
                          ? 'var(--status-delivered-bg)'
                          : trip.status === 'In Progress'
                            ? 'var(--status-in-transit-bg)'
                            : 'var(--status-pending-bg)',
                      color:
                        trip.status === 'Completed'
                          ? 'var(--status-delivered)'
                          : trip.status === 'In Progress'
                            ? 'var(--status-in-transit)'
                            : 'var(--status-pending)',
                    }}
                  >
                    {trip.status}
                  </span>
                </td>
                <td
                  className="px-6 py-4 text-sm"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {trip.progress}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
