'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, Activity, MapPin } from 'lucide-react';
import { apiClient } from '@/lib/api';
import type { TripResponse, DriverResponse } from '@/types';

export default function OngoingTripsPage() {
  // Fetch Trips
  const { data: trips = [], isLoading: loadingTrips, isError: errorTrips } = useQuery<TripResponse[]>({
    queryKey: ['trips'],
    queryFn: apiClient.getTrips
  });

  // Fetch Drivers for name mapping
  const { data: drivers = [] } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  // STRICT FILTER: Only show trips currently on the road
  const ongoingTrips = trips.filter(trip => trip.status === 'IN_PROGRESS');

  const getDriverName = (driverId?: string | null) => {
    if (!driverId) return 'Unassigned';
    const driver = drivers.find(d => d.uid === driverId);
    return driver ? driver.full_name : 'Unknown Driver';
  };

  const formatTime = (dateString?: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="p-8 animate-fade-in max-w-7xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-900/30 rounded-lg">
              <Activity size={24} className="text-blue-400" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Ongoing Trips</h1>
          </div>
          <p className="text-gray-400">Live monitoring of all drivers currently on active delivery routes.</p>
        </div>
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] px-4 py-2 rounded-lg flex items-center gap-3 shadow-sm">
           <span className="relative flex h-3 w-3">
             <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
             <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
           </span>
           <span className="text-sm font-medium text-gray-300">{ongoingTrips.length} Active Routes</span>
        </div>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden shadow-sm" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Trip ID</th>
              <th className="p-4 font-medium">Driver</th>
              <th className="p-4 font-medium">Started At</th>
              <th className="p-4 font-medium">ETA to Station</th>
              <th className="p-4 font-medium">COD Amount</th>
              <th className="p-4 font-medium min-w-[200px]">Progress</th>
            </tr>
          </thead>
          <tbody>
            {loadingTrips && <tr><td colSpan={6} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-blue-500 w-8 h-8" /></td></tr>}
            {errorTrips && <tr><td colSpan={6} className="p-8 text-center text-red-500"><AlertCircle className="inline mr-2" size={16}/> Failed to load live trips</td></tr>}
            {!loadingTrips && !errorTrips && ongoingTrips.length === 0 && (
              <tr>
                <td colSpan={6} className="p-16 text-center text-gray-500">
                  <MapPin size={32} className="mx-auto mb-3 opacity-20"/> 
                  <p>No drivers are currently on the road.</p>
                </td>
              </tr>
            )}

            {ongoingTrips.map((trip) => {
              // Calculate mathematical progress for the visual bar
              const progressPercentage = trip.total_tasks_count > 0 
                ? Math.round((trip.delivered_count / trip.total_tasks_count) * 100) 
                : 0;

              return (
                <tr key={trip.trip_id} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors cursor-pointer" onClick={() => window.location.href = `/trips/${trip.trip_id}`}>
                  <td className="p-4 font-mono font-medium text-white">
                    #TR-{trip.trip_id.substring(0, 8).toUpperCase()}
                  </td>
                  <td className="p-4 text-gray-300 font-medium">
                    {getDriverName(trip.driver_id)}
                  </td>
                  <td className="p-4 text-gray-400">
                    {formatTime(trip.actual_start_time)}
                  </td>
                  <td className="p-4 text-blue-400 font-medium">
                    {formatTime(trip.estimated_return_time_actual) || 'Calculating...'}
                  </td>
                  <td className="p-4 text-gray-300">
                    LKR {trip.total_cod_to_collect}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-full bg-[#121212] rounded-full h-2 border border-[#2E2E2E] overflow-hidden">
                        <div 
                          className="bg-blue-500 h-2 rounded-full transition-all duration-500" 
                          style={{ width: `${progressPercentage}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-medium text-gray-400 whitespace-nowrap">
                        {trip.delivered_count} / {trip.total_tasks_count}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}