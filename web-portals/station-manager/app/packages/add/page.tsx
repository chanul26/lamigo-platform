'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

// 1. THE FIX: Removed .default() here. 
// We want strict numbers, and we will inject the default values via useForm below.
const packageSchema = z.object({
  sender_name: z.string().min(2, "Sender name is required"),
  sender_phone: z.string().optional(),
  recipient_name: z.string().min(2, "Receiver name is required"),
  recipient_phone: z.string().min(9, "Valid phone number required"),
  address: z.string().min(5, "Full address required"),
  weight: z.number().min(0.1, "Weight must be greater than 0"),
  delivery_charge: z.number().min(0, "Invalid charge"),
  is_cod: z.boolean(),
  cod_amount: z.number().min(0),
  gps_lat: z.number(), 
  gps_lng: z.number(), 
});

type PackageFormValues = z.infer<typeof packageSchema>;

export default function AddPackagePage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<PackageFormValues>({
    resolver: zodResolver(packageSchema),
    defaultValues: {
      sender_name: '',
      sender_phone: '',
      recipient_name: '',
      recipient_phone: '',
      address: '',
      is_cod: false,
      cod_amount: 0,
      delivery_charge: 350,
      weight: 1.0,
      gps_lat: 6.9271,  // <-- Default provided here!
      gps_lng: 79.8612  // <-- Default provided here!
    }
  });

  const isCod = watch('is_cod');

  async function onSubmit(data: PackageFormValues) {
    setServerError(null);
    try {
      await apiClient.createPackage(data);
      router.push('/packages'); // Redirect back to table on success
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create package';
      setServerError(message);
    }
  }

  return (
    <div className="p-8 animate-fade-in max-w-3xl">
      <div className="mb-6">
        <Link href="/packages" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline" style={{ color: 'var(--text-secondary)' }}>
          <ArrowLeft size={16} /> Back to Packages
        </Link>
        <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Add New Package</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manual Entry</p>
      </div>

      <div className="p-8 rounded-[var(--border-radius)]" style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          
          <div className="grid grid-cols-2 gap-6">
            {/* Sender Info */}
            <div className="space-y-4">
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Sender Details</h3>
              <div>
                <label className="block text-sm mb-1 text-gray-400">Sender Name *</label>
                <input {...register("sender_name")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
                {errors.sender_name && <p className="text-red-500 text-xs mt-1">{errors.sender_name.message}</p>}
              </div>
              <div>
                <label className="block text-sm mb-1 text-gray-400">Sender Phone</label>
                <input {...register("sender_phone")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
              </div>
            </div>

            {/* Recipient Info */}
            <div className="space-y-4">
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>Receiver Details</h3>
              <div>
                <label className="block text-sm mb-1 text-gray-400">Receiver Name *</label>
                <input {...register("recipient_name")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
                {errors.recipient_name && <p className="text-red-500 text-xs mt-1">{errors.recipient_name.message}</p>}
              </div>
              <div>
                <label className="block text-sm mb-1 text-gray-400">Phone Number *</label>
                <input {...register("recipient_phone")} placeholder="07x-xxx-xxxx" className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
                {errors.recipient_phone && <p className="text-red-500 text-xs mt-1">{errors.recipient_phone.message}</p>}
              </div>
              <div>
                <label className="block text-sm mb-1 text-gray-400">Delivery Address *</label>
                <input {...register("address")} placeholder="House No, Street Name" className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
                {errors.address && <p className="text-red-500 text-xs mt-1">{errors.address.message}</p>}
              </div>
            </div>
          </div>

          <div className="border-t border-[#2E2E2E] my-6"></div>

          {/* Logistics & Financials */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm mb-1 text-gray-400">Weight (kg) *</label>
              <input type="number" step="0.1" {...register("weight", { valueAsNumber: true })} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
              {errors.weight && <p className="text-red-500 text-xs mt-1">{errors.weight.message}</p>}
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">Delivery Charge (LKR) *</label>
              <input type="number" {...register("delivery_charge", { valueAsNumber: true })} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
              {errors.delivery_charge && <p className="text-red-500 text-xs mt-1">{errors.delivery_charge.message}</p>}
            </div>
            
            <div className="col-span-2 flex items-center gap-3 mt-2">
              <input type="checkbox" id="is_cod" {...register("is_cod")} className="w-4 h-4 accent-blue-600" />
              <label htmlFor="is_cod" className="text-sm font-medium text-white">Cash on Delivery (COD)</label>
            </div>

            {isCod && (
              <div className="col-span-2">
                <label className="block text-sm mb-1 text-gray-400">COD Amount to Collect (LKR) *</label>
                <input type="number" {...register("cod_amount", { valueAsNumber: true })} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white outline-none focus:border-blue-500" />
                {errors.cod_amount && <p className="text-red-500 text-xs mt-1">{errors.cod_amount.message}</p>}
              </div>
            )}
          </div>

          {serverError && <p className="text-red-500 font-medium bg-red-900/20 p-3 rounded">{serverError}</p>}

          <div className="flex justify-end gap-4 pt-4">
            <button type="button" onClick={() => router.push('/packages')} className="px-6 py-2.5 rounded font-medium border border-[#2E2E2E] hover:bg-[#252525] transition-colors text-white">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="px-6 py-2.5 rounded font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 flex items-center gap-2">
              {isSubmitting && <Loader2 size={16} className="animate-spin" />}
              Add to Inventory
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}