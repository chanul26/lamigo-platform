'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, Users } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { DriverResponse } from '@/types';
import DriverProfileModal from '@/components/DriverProfileModal';

export default function DriversPage() {
  const [selectedDriver, setSelectedDriver] = useState<DriverResponse | null>(null);

  const { data: drivers = [], isLoading, isError } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE': return 'bg-green-900/40 text-green-400';
      case 'OFF_DUTY': return 'bg-gray-800 text-gray-300';
      case 'IN_A_TRIP':
      case 'ON_TRIP': return 'bg-blue-900/40 text-blue-400';
      case 'SCHEDULED': return 'bg-purple-900/40 text-purple-400';
      case 'UNAVAILABLE': return 'bg-red-900/40 text-red-400';
      default: return 'bg-[#2E2E2E] text-gray-300';
    }
  };

  return (
    <div className="p-8 animate-fade-in max-w-6xl">
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-[#2E2E2E] rounded-lg">
              <Users size={24} className="text-gray-300" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Drivers Fleet</h1>
          </div>
          <p className="text-gray-400">Manage all delivery personnel assigned to your branch.</p>
        </div>
        <Link 
          href="/drivers/register" 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors shadow-lg"
        >
          + Register New Driver
        </Link>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden shadow-sm" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Driver ID</th>
              <th className="p-4 font-medium">Name</th>
              <th className="p-4 font-medium">Phone</th>
              <th className="p-4 font-medium">Vehicle</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium text-right">Wallet Balance</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={6} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={6} className="p-8 text-center text-red-500"><AlertCircle className="inline mr-2" size={16}/> Failed to load fleet data</td></tr>}

            {!isLoading && !isError && drivers.map((driver) => (
              <tr 
                key={driver.uid} 
                style={{ borderBottom: '1px solid var(--border-color)' }} 
                className="hover:bg-[#252525] transition-colors cursor-pointer"
                onClick={() => setSelectedDriver(driver)}
              >
                <td className="p-4 font-mono font-medium text-gray-400">
                  #DRV-{driver.uid.substring(0, 6).toUpperCase()}
                </td>
                <td className="p-4 text-white font-medium flex items-center gap-3">
                   <div className="w-8 h-8 rounded bg-[#1A1A1A] border border-[#2E2E2E] flex items-center justify-center text-xs font-bold text-gray-400">
                     {driver.full_name.split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase()}
                   </div>
                   {driver.full_name}
                </td>
                <td className="p-4 text-gray-400">{driver.phone_number}</td>
                <td className="p-4 text-gray-300 capitalize">{driver.vehicle_type.toLowerCase().replace('_', ' ')}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${getStatusColor(driver.status)}`}>
                    {driver.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="p-4 text-right font-medium text-green-400">
                  LKR {Number(driver.wallet_balance).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Render Modal if a driver is selected */}
      {selectedDriver && (
        <DriverProfileModal 
          driver={selectedDriver} 
          onClose={() => setSelectedDriver(null)} 
        />
      )}
    </div>
  );
}