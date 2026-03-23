'use client';

import { Truck, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';

interface Trip {
  id: string;
  driver_name: string;
  start_time: string;
  eta: string;
  cod_total: number;
  completed_stops: number;
  total_stops: number;
}

export default function OngoingTripsPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchTrips() {
    try {
      const token = localStorage.getItem("token");
      // Full localhost path to FastAPI backend
      const res = await fetch("http://localhost:8000/api/v1/trips?status=active", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const data = await res.json();
      setTrips(data);
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchTrips();
    const interval = setInterval(fetchTrips, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
          Ongoing Trips
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Monitor active delivery routes in real-time.
        </p>
      </div>

      <div
        className="rounded-[var(--border-radius)] overflow-hidden"
        style={{
          backgroundColor: "var(--card-bg)",
          border: "1px solid var(--border-color)",
        }}
      >
        <table className="w-full text-sm">
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-color)", color: "var(--text-secondary)" }}>
              <th className="p-4 text-left">Trip ID</th>
              <th className="p-4 text-left">Driver</th>
              <th className="p-4 text-left">Started At</th>
              <th className="p-4 text-left">ETA to Station</th>
              <th className="p-4 text-left">COD Amount</th>
              <th className="p-4 text-left">Progress</th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="p-8 text-center">
                  <Loader2 className="animate-spin mx-auto" />
                </td>
              </tr>
            ) : (
              trips.map((trip) => {
                // Progress calculation
                const progress = (trip.completed_stops / trip.total_stops) * 100;

                return (
                  <tr key={trip.id} style={{ borderBottom: "1px solid var(--border-color)" }}>
                    <td className="p-4 font-medium">{trip.id}</td>
                    <td className="p-4">{trip.driver_name}</td>
                    <td className="p-4">{trip.start_time}</td>
                    <td className="p-4">{trip.eta}</td>
                    <td className="p-4">LKR {trip.cod_total}</td>
                    <td className="p-4">
                      <div className="w-32">
                        <div
                          className="h-2 rounded"
                          style={{ backgroundColor: "var(--border-color)" }}
                        >
                          <div
                            className="h-2 rounded"
                            style={{
                              width: `${progress}%`,
                              backgroundColor: "var(--primary-blue)"
                            }}
                          />
                        </div>
                        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                          {trip.completed_stops}/{trip.total_stops}
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
