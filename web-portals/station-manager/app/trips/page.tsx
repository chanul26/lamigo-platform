import { Route } from 'lucide-react';

export default function TripsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
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

      {/* Coming Soon Card */}
      <div
        className="p-12 rounded-[var(--border-radius)] text-center"
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <div
          className="w-16 h-16 mx-auto mb-4 rounded-[var(--border-radius)] flex items-center justify-center"
          style={{
            backgroundColor: 'var(--primary-blue)20',
            color: 'var(--primary-blue)',
          }}
        >
          <Route size={32} />
        </div>
        <h2
          className="text-xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Coming Soon
        </h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Trip management and route planning will be available here.
        </p>
      </div>
    </div>
  );
}
