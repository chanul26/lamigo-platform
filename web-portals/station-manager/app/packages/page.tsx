'use client';

import { Package, Plus, MapPin, Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export default function PackagesPage() {
  const { data: packages = [], isLoading, isError } = useQuery({
    queryKey: ['packages'],
    queryFn: apiClient.getPackages
  });

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Packages</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Track and manage all delivery packages.</p>
        </div>
        <Link
          href="/packages/add"
          className="flex items-center gap-2 px-6 py-3 rounded-[var(--border-radius)] font-medium text-sm transition-all duration-200"
          style={{ backgroundColor: 'var(--primary-blue)', color: 'white' }}
        >
          <Plus size={20} />
          Add New Package
        </Link>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Tracking ID</th>
              <th className="p-4 font-medium">Status</th>
              <th className="p-4 font-medium">Location Pin</th>
              <th className="p-4 font-medium">Recipient</th>
              <th className="p-4 font-medium">Address</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={5} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>
            )}
            {isError && (
              <tr><td colSpan={5} className="p-8 text-center text-red-500 flex items-center justify-center gap-2"><AlertCircle size={16}/> Failed to load packages</td></tr>
            )}
            {!isLoading && !isError && packages.length === 0 && (
              <tr><td colSpan={5} className="p-8 text-center text-gray-500">No packages found for this branch.</td></tr>
            )}
            {packages.map((pkg) => (
              <tr key={pkg.package_id} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors">
                <td className="p-4 font-semibold text-blue-400">{pkg.tracking_id}</td>
                <td className="p-4">
                  <span className="px-3 py-1 rounded-full text-xs font-medium" style={{ backgroundColor: 'var(--status-pending-bg)', color: 'var(--status-pending)' }}>
                    {pkg.status.replace(/_/g, ' ')}
                  </span>
                </td>
                <td className="p-4">
                  <MapPin size={18} className="text-gray-400" />
                </td>
                <td className="p-4">
                  <div>
                    <p className="font-medium" style={{ color: 'var(--text-primary)' }}>{pkg.recipient_name}</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{pkg.recipient_phone || 'No phone'}</p>
                  </div>
                </td>
                <td className="p-4" style={{ color: 'var(--text-secondary)' }}>{pkg.address}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}