'use client';

import { Users, Plus, Loader2, AlertCircle, ShieldBan, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import type { DriverResponse } from '@/types';

export default function DriversPage() {
  const { data: drivers = [], isLoading, isError } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Drivers</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage driver profiles and assignments.</p>
        </div>
        <Link
          href="/drivers/register"
          className="flex items-center gap-2 px-6 py-3 rounded-[var(--border-radius)] font-medium text-sm transition-all duration-200 hover:bg-blue-700"
          style={{ backgroundColor: 'var(--primary-blue)', color: 'white' }}
        >
          <Plus size={20} />
          Register New Driver
        </Link>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Driver ID</th>
              <th className="p-4 font-medium">Name & Identity</th>
              <th className="p-4 font-medium">Vehicle</th>
              <th className="p-4 font-medium">Operational Status</th>
              <th className="p-4 font-medium">Account Status</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={5} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={5} className="p-8 text-center text-red-500 flex items-center justify-center gap-2"><AlertCircle size={16}/> Failed to load drivers</td></tr>}
            {!isLoading && !isError && drivers.length === 0 && <tr><td colSpan={5} className="p-8 text-center text-gray-500">No drivers registered yet.</td></tr>}
            
            {drivers.map((drv) => (
              <tr key={drv.uid} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors">
                <td className="p-4 font-mono text-xs text-gray-400">{drv.uid.substring(0, 12)}...</td>
                <td className="p-4">
                  <p className="font-semibold text-white">{drv.full_name}</p>
                  <p className="text-xs text-gray-400">{drv.phone_number}</p>
                </td>
                <td className="p-4">
                  <p className="text-white">{drv.vehicle_type.replace(/_/g, ' ')}</p>
                  <p className="text-xs font-mono text-gray-400">{drv.vehicle_number}</p>
                </td>
                <td className="p-4">
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-900/30 text-blue-400">
                    {drv.status ? drv.status.replace(/_/g, ' ') : 'OFF DUTY'}
                  </span>
                </td>
                <td className="p-4">
                  {drv.is_active ? (
                    <span className="flex items-center gap-1 text-green-400 text-xs font-medium"><CheckCircle2 size={14}/> Active</span>
                  ) : (
                    <span className="flex items-center gap-1 text-red-400 text-xs font-medium"><ShieldBan size={14}/> Suspended</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}