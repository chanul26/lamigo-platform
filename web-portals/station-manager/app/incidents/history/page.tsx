'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, ArrowLeft, Archive } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { IncidentResponse, DriverResponse } from '@/types';

export default function ResolvedIncidentsPage() {
  const { data: incidents = [], isLoading, isError } = useQuery<IncidentResponse[]>({
    queryKey: ['incidents'],
    queryFn: apiClient.getIncidents
  });

  const { data: drivers = [] } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  const getDriverName = (driverId: string) => {
    const driver = drivers.find(d => d.uid === driverId);
    return driver ? driver.full_name : 'Unknown';
  };

  // Filter for ONLY resolved incidents
  const resolvedIncidents = incidents.filter(i => i.status === 'RESOLVED');

  return (
    <div className="p-8 animate-fade-in max-w-7xl">
      <div className="mb-8">
        <Link href="/incidents" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400 transition-colors hover:text-white">
          <ArrowLeft size={16} /> Back to Active Incidents
        </Link>
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#2E2E2E] rounded-lg">
            <Archive size={24} className="text-gray-300" />
          </div>
          <h1 className="text-2xl font-semibold text-white">Resolved Incidents</h1>
        </div>
        <p className="text-gray-400">Historical log of all successfully handled emergencies and disruptions.</p>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Incident ID</th>
              <th className="p-4 font-medium">Date Resolved</th>
              <th className="p-4 font-medium">Driver</th>
              <th className="p-4 font-medium">Category</th>
              <th className="p-4 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={5} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={5} className="p-8 text-center text-red-500"><AlertCircle className="inline mr-2" size={16}/> Failed to load records</td></tr>}
            {!isLoading && !isError && resolvedIncidents.length === 0 && <tr><td colSpan={5} className="p-8 text-center text-gray-500">No resolved incidents found.</td></tr>}

            {resolvedIncidents.map((record) => (
              <tr key={record.incident_id} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors">
                <td className="p-4 font-mono text-xs text-gray-400">#{record.incident_id.substring(0,8).toUpperCase()}</td>
                <td className="p-4 text-gray-300">
                  {new Date(record.updated_at).toLocaleDateString()}
                </td>
                <td className="p-4 font-medium text-white">{getDriverName(record.driver_id)}</td>
                <td className="p-4">
                  <span className="px-2 py-1 rounded text-[10px] font-bold uppercase bg-[#2E2E2E] text-gray-300">
                    {record.type.replace('_', ' ')}
                  </span>
                </td>
                <td className="p-4 text-gray-400 text-xs truncate max-w-[250px]">
                  {record.description || 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}