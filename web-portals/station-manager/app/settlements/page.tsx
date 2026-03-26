'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Wallet, Loader2, AlertCircle, X, CheckCircle2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { apiClient } from '@/lib/api';
import type { DriverResponse } from '@/types';

// Zod schema for the Payment Modal
const paymentSchema = z.object({
  amount_paid: z.number().min(1, "Amount must be greater than 0"),
  payment_method: z.enum(['CASH', 'BANK_TRANSFER', 'CHEQUE']),
  reference_note: z.string().optional(),
});

type PaymentFormValues = z.infer<typeof paymentSchema>;

export default function SettlementsPage() {
  const queryClient = useQueryClient();
  const [selectedDriver, setSelectedDriver] = useState<DriverResponse | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // 1. Fetch all drivers to check their wallet balances
  const { data: drivers = [], isLoading, isError } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentSchema),
    defaultValues: { payment_method: 'CASH', amount_paid: 0 }
  });

  // 2. Mutation to process the payout
  const payoutMutation = useMutation({
    mutationFn: apiClient.createSettlement,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drivers'] }); // Refresh balances instantly
      queryClient.invalidateQueries({ queryKey: ['settlements'] }); // Refresh dashboard stats
      setSuccessMsg(`Successfully processed payment for ${selectedDriver?.full_name}`);
      closeModal();
      setTimeout(() => setSuccessMsg(null), 4000);
    },
    onError: (err: any) => {
      setServerError(err.message || 'Failed to process payment');
    }
  });

  function openModal(driver: DriverResponse) {
    setSelectedDriver(driver);
    setServerError(null);
    reset({ payment_method: 'CASH', amount_paid: Number(driver.wallet_balance) });
  }

  function closeModal() {
    setSelectedDriver(null);
    reset();
  }

  function onSubmit(data: PaymentFormValues) {
    if (!selectedDriver) return;
    if (data.amount_paid > Number(selectedDriver.wallet_balance)) {
      setServerError("Cannot pay more than the total due amount.");
      return;
    }

    payoutMutation.mutate({
      driver_id: selectedDriver.uid,
      amount_paid: data.amount_paid,
      payment_method: data.payment_method,
      reference_note: data.reference_note,
    });
  }

  // Filter out drivers who are completely paid off for a cleaner ledger
  const driversOwed = drivers.filter(d => Number(d.wallet_balance) > 0);
  const totalOwedStation = driversOwed.reduce((sum, d) => sum + Number(d.wallet_balance), 0);

  return (
    <div className="p-8 animate-fade-in relative">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Driver Settlements</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Manage and clear outstanding balances owed to delivery personnel.</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400 mb-1">Total Station Liability</p>
          <p className="text-2xl font-semibold text-red-400">LKR {totalOwedStation.toLocaleString()}</p>
        </div>
      </div>

      {successMsg && (
        <div className="mb-6 p-4 bg-green-900/20 border border-green-500/50 rounded-lg flex items-center gap-3 text-green-400">
          <CheckCircle2 size={20} />
          <p className="text-sm font-medium">{successMsg}</p>
        </div>
      )}

      <div className="rounded-[var(--border-radius)] overflow-hidden" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <table className="w-full text-sm text-left">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
              <th className="p-4 font-medium">Driver</th>
              <th className="p-4 font-medium">Identity Tag</th>
              <th className="p-4 font-medium">Total to be Paid</th>
              <th className="p-4 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && <tr><td colSpan={4} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
            {isError && <tr><td colSpan={4} className="p-8 text-center text-red-500 flex items-center justify-center gap-2"><AlertCircle size={16}/> Failed to load financial data</td></tr>}
            {!isLoading && !isError && driversOwed.length === 0 && <tr><td colSpan={4} className="p-8 text-center text-green-500">All drivers are currently fully settled.</td></tr>}
            
            {driversOwed.map((drv) => (
              <tr key={drv.uid} style={{ borderBottom: '1px solid var(--border-color)' }} className="hover:bg-[#252525] transition-colors">
                <td className="p-4 font-semibold text-white">{drv.full_name}</td>
                <td className="p-4 font-mono text-xs text-gray-400">{drv.uid.substring(0, 10).toUpperCase()}</td>
                <td className="p-4 font-semibold text-red-400">LKR {Number(drv.wallet_balance).toLocaleString()}</td>
                <td className="p-4 text-right">
                  <button
                    onClick={() => openModal(drv)}
                    className="px-6 py-2 rounded-md font-medium text-xs bg-blue-600 hover:bg-blue-700 text-white transition-colors"
                  >
                    Pay
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Settle Payment Modal (Matches Page 15) */}
      {selectedDriver && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-8 w-full max-w-md shadow-2xl relative animate-fade-in">
            <button onClick={closeModal} className="absolute top-4 right-4 text-gray-400 hover:text-white">
              <X size={20} />
            </button>
            
            <h2 className="text-xl font-semibold text-white mb-1">Settle Payment</h2>
            <p className="text-sm text-gray-400 mb-6">Recording payment for driver <span className="text-white font-medium">{selectedDriver.full_name}</span></p>

            <div className="bg-red-900/10 border border-red-500/20 p-4 rounded-lg mb-6 text-center">
              <p className="text-xs text-gray-400 mb-1 tracking-wider font-semibold">TOTAL DUE AMOUNT</p>
              <p className="text-2xl font-bold text-red-400">LKR {Number(selectedDriver.wallet_balance).toLocaleString()}</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm mb-1 text-gray-400">Amount Paying Now (LKR) *</label>
                <input 
                  type="number" 
                  {...register("amount_paid", { valueAsNumber: true })} 
                  className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none text-lg font-medium" 
                />
                <p className="text-xs text-gray-500 mt-1">Adjust this value for partial payments.</p>
                {errors.amount_paid && <p className="text-red-500 text-xs mt-1">{errors.amount_paid.message}</p>}
              </div>

              <div>
                <label className="block text-sm mb-1 text-gray-400">Payment Method</label>
                <select {...register("payment_method")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none">
                  <option value="CASH">Cash Handover</option>
                  <option value="BANK_TRANSFER">Bank Transfer</option>
                  <option value="CHEQUE">Cheque</option>
                </select>
              </div>

              {serverError && <p className="text-red-500 text-sm bg-red-900/20 p-3 rounded font-medium">{serverError}</p>}

              <div className="flex justify-end gap-3 pt-4">
                <button type="button" onClick={closeModal} className="px-5 py-2.5 rounded font-medium border border-[#2E2E2E] hover:bg-[#252525] text-white">
                  Cancel
                </button>
                <button type="submit" disabled={isSubmitting} className="px-6 py-2.5 rounded font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 flex items-center gap-2">
                  {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : <Wallet size={16} />}
                  Confirm Payment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}