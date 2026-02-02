import { Truck } from 'lucide-react';

export default function OngoingTripsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1
          className="text-2xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Ongoing Trips
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Monitor active delivery routes in real-time.
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
            backgroundColor: 'var(--status-in-transit-bg)',
            color: 'var(--status-in-transit)',
          }}
        >
          <Truck size={32} />
        </div>
        <h2
          className="text-xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Coming Soon
        </h2>
        <p style={{ color: 'var(--text-muted)' }}>
          Real-time trip tracking and monitoring will be available here.
        </p>
      </div>
    </div>
  );
}
