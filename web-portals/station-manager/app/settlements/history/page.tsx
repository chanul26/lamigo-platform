'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, AlertCircle, ArrowLeft, History } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { SettlementResponse, DriverResponse } from '@/types';

export default function PaymentHistoryPage() {
  // 1. Fetch the Immutable Settlement Ledger
  const { data: settlements = [], isLoading: loadingSettlements, isError: errorSettlements } = useQuery<SettlementResponse[]>({
    queryKey: ['settlements'],
    queryFn: apiClient.getSettlements
  });

  // 2. Fetch the Drivers (to translate Driver IDs into real names)
  const { data: drivers = [] } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  // Helper function to map IDs to Names
  const getDriverName = (driverId: string) => {
    const driver = drivers.find(d => d.uid === driverId);
    return driver ? driver.full_name : driverId.substring(0, 10) + '...';
  };

  const isLoading = loadingSettlements;
  const isError = errorSettlements;

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-8">
        <Link href="/settlements" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400 transition-colors hover:text-white">
          <ArrowLeft size={16} /> Back to Active Ledger
        </Link>
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#2E2E2E] rounded-lg">
            <History size={24} className="text-gray-300" />
          </div>
          <h1 className="text-2xl font-semibold text-white">Payment History</h1>
        </div>
        <p className="text-gray-400">Immutable ledger of all past driver settlements and payouts.</p>
      </div>

      <div className="rounded-[var(--border-radius)] overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Date & Time</th>
              <th className="p-4 font-medium">Driver</th>
              <th className="p-4 font-medium">Amount Paid</th>
              <th className="p-4 font-medium">Method</th>
              <th className="p-4 font-medium">Reference Note</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={5} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={5} className="p-8 text-center text-red-500 flex items-center justify-center gap-2"><AlertCircle size={16}/> Failed to load history</td></tr>}
            {!isLoading && !isError && settlements.length === 0 && <tr><td colSpan={5} className="p-8 text-center text-gray-500">No payment history found in the database.</td></tr>}

            {settlements.map((record) => (
              <tr key={record.settlement_id} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors">
                <td className="p-4 text-gray-300">
                  {new Date(record.created_at).toLocaleDateString()} 
                  <span className="text-gray-500 text-xs ml-2">{new Date(record.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                </td>
                <td className="p-4 font-medium text-white">{getDriverName(record.driver_id)}</td>
                <td className="p-4 font-semibold text-green-400">LKR {Number(record.amount_paid).toLocaleString()}</td>
                <td className="p-4">
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-[#2E2E2E] text-gray-300">
                    {record.payment_method.replace('_', ' ')}
                  </span>
                </td>
                <td className="p-4 text-gray-400 text-xs">{record.reference_note || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}