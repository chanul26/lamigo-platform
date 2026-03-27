'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, Route, Map } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { TripResponse, DriverResponse } from '@/types';

export default function TripsPage() {
  // 1. Fetch all trips for this branch
  const { data: trips = [], isLoading: loadingTrips, isError: errorTrips } = useQuery<TripResponse[]>({
    queryKey: ['trips'],
    queryFn: apiClient.getTrips
  });

  // 2. Fetch drivers to map the names
  const { data: drivers = [] } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  const getDriverName = (driverId?: string | null) => {
    if (!driverId) return 'Unassigned';
    const driver = drivers.find(d => d.uid === driverId);
    return driver ? driver.full_name : 'Unknown Driver';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DRAFT': return 'bg-gray-800 text-gray-300';
      case 'SCHEDULED': return 'bg-purple-900/40 text-purple-400';
      case 'IN_PROGRESS': return 'bg-blue-900/40 text-blue-400';
      case 'COMPLETED': return 'bg-green-900/40 text-green-400';
      case 'CANCELLED': return 'bg-red-900/40 text-red-400';
      default: return 'bg-[#2E2E2E] text-gray-300';
    }
  };

  const isLoading = loadingTrips;
  const isError = errorTrips;

  return (
    <div className="p-8 animate-fade-in max-w-6xl">
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-[#2E2E2E] rounded-lg">
              <Route size={24} className="text-gray-300" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Trips Ledger</h1>
          </div>
          <p className="text-gray-400">Master log of all route manifests, assignments, and historical deliveries.</p>
        </div>
        <Link 
          href="/trips/new" 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors shadow-lg"
        >
          + Create New Trip
        </Link>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden shadow-sm" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Trip ID</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Assigned Driver</th>
              <th className="p-4 font-medium">Package Count</th>
              <th className="p-4 font-medium">Financials</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={5} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={5} className="p-8 text-center text-red-500"><AlertCircle className="inline mr-2" size={16}/> Failed to load trips</td></tr>}
            {!isLoading && !isError && trips.length === 0 && <tr><td colSpan={5} className="p-12 text-center text-gray-500"><Map size={32} className="mx-auto mb-3 opacity-20"/> No trips have been created yet.</td></tr>}

            {trips.map((trip) => (
              <tr key={trip.trip_id} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors cursor-pointer" onClick={() => window.location.href = `/trips/${trip.trip_id}`}>
                <td className="p-4 font-mono font-medium text-white">
                  #TR-{trip.trip_id.substring(0, 8).toUpperCase()}
                </td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${getStatusColor(trip.status)}`}>
                    {trip.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="p-4 text-gray-300 font-medium">
                  {getDriverName(trip.driver_id)}
                </td>
                <td className="p-4 text-gray-400">
                  {trip.total_tasks_count} Stops
                </td>
                <td className="p-4 text-gray-400">
                  <span className="text-xs">COD:</span> LKR {trip.total_cod_to_collect}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}