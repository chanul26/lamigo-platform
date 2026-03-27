'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, Package as PackageIcon, MapPin, Phone } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { PackageResponse } from '@/types';

export default function PackagesPage() {
  const { data: packages = [], isLoading, isError } = useQuery<PackageResponse[]>({
    queryKey: ['packages'],
    queryFn: apiClient.getPackages
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'TO_BE_DELIVERED': return 'bg-blue-900/40 text-blue-400';
      case 'SCHEDULED': return 'bg-purple-900/40 text-purple-400';
      case 'ON_TRIP':
      case 'DELIVERING_NOW': return 'bg-yellow-900/40 text-yellow-400';
      case 'COMPLETED': return 'bg-green-900/40 text-green-400';
      case 'FAILED': return 'bg-red-900/40 text-red-400';
      default: return 'bg-[#2E2E2E] text-gray-300';
    }
  };

  return (
    <div className="p-8 animate-fade-in max-w-7xl">
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-[#2E2E2E] rounded-lg">
              <PackageIcon size={24} className="text-gray-300" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Packages Inventory</h1>
          </div>
          <p className="text-gray-400">Manage all incoming and outgoing parcels for your branch.</p>
        </div>
        <Link 
          href="/packages/new" 
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors"
        >
          + Add New Package
        </Link>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Package ID</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Recipient</th>
              <th className="p-4 font-medium">Phone Number</th>
              <th className="p-4 font-medium">Delivery Address</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={5} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={5} className="p-8 text-center text-red-500"><AlertCircle className="inline mr-2" size={16}/> Failed to load packages</td></tr>}
            {!isLoading && !isError && packages.length === 0 && <tr><td colSpan={5} className="p-8 text-center text-gray-500">No packages found in inventory.</td></tr>}

            {packages.map((pkg) => (
              <tr key={pkg.package_id} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors cursor-pointer">
                <td className="p-4 font-mono font-medium text-white">{pkg.tracking_id}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${getStatusColor(pkg.status)}`}>
                    {pkg.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="p-4 text-gray-300 font-medium">
                  {pkg.recipient_name}
                </td>
                <td className="p-4 text-gray-400">
                  <div className="flex items-center gap-2">
                    <Phone size={14} />
                    {pkg.recipient?.phone_number || 'N/A'}
                  </div>
                </td>
                <td className="p-4 text-gray-400 truncate max-w-[250px]">
                  <div className="flex items-center gap-2">
                    <MapPin size={14} className={pkg.recipient ? 'text-green-500' : 'text-red-500'} />
                    {pkg.address}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}