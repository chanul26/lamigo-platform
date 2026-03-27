'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, ArrowLeft, PackagePlus, CheckCircle2, AlertCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { PackageCreate } from '@/types';

export default function AddPackagePage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { register, handleSubmit, watch, formState: { isSubmitting } } = useForm<PackageCreate>({
    defaultValues: {
      weight: 1.0,
      delivery_charge: 350.00,
      cod_amount: 0.00,
      is_cod: false,
      location_type: 'HOME',
      // Defaulting to general Colombo coordinates to prevent 422 errors if left blank
      gps_lat: 6.9271, 
      gps_lng: 79.8612,
    }
  });

  const createMutation = useMutation({
    mutationFn: (data: PackageCreate) => apiClient.createPackage(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] });
      setSuccessMsg("Package successfully added to inventory!");
      setTimeout(() => {
        router.push('/packages');
      }, 1500);
    }
  });

  const onSubmit = (data: PackageCreate) => {
    // Auto-calculate the COD flag based on the amount entered
    const payload = {
      ...data,
      is_cod: Number(data.cod_amount) > 0,
      weight: Number(data.weight),
      delivery_charge: Number(data.delivery_charge),
      cod_amount: Number(data.cod_amount),
      gps_lat: Number(data.gps_lat),
      gps_lng: Number(data.gps_lng),
    };
    createMutation.mutate(payload);
  };

  return (
    <div className="p-8 animate-fade-in max-w-4xl">
      <div className="mb-8">
        <Link href="/packages" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400 transition-colors hover:text-white">
          <ArrowLeft size={16} /> Back to Inventory
        </Link>
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-900/30 rounded-lg">
            <PackagePlus size={24} className="text-blue-400" />
          </div>
          <h1 className="text-2xl font-semibold text-white">Add New Package</h1>
        </div>
        <p className="text-gray-400">Manually insert a single package into the system for delivery.</p>
      </div>

      {successMsg && (
        <div className="mb-6 p-4 bg-green-900/20 border border-green-500/50 rounded-lg flex items-center gap-3 text-green-400">
          <CheckCircle2 size={20} />
          <p className="text-sm font-medium">{successMsg}</p>
        </div>
      )}

      {createMutation.isError && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-400">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">Failed to create package. Please check your inputs.</p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* RECIPIENT DETAILS */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-white mb-4">Recipient Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm mb-1 text-gray-400">Receiver Name *</label>
              <input required {...register("recipient_name")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" placeholder="e.g. Saman Perera" />
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">Phone Number *</label>
              <input required {...register("recipient_phone")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" placeholder="07x-xxx-xxxx" />
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-sm mb-1 text-gray-400">Delivery Address *</label>
            <input required {...register("address")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" placeholder="House No, Street Name, City" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm mb-1 text-gray-400">Location Type</label>
              <select {...register("location_type")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium">
                <option value="HOME">Home</option>
                <option value="APARTMENT">Apartment</option>
                <option value="OFFICE">Office</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">GPS Latitude *</label>
              <input required type="number" step="any" {...register("gps_lat")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-mono text-sm" />
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">GPS Longitude *</label>
              <input required type="number" step="any" {...register("gps_lng")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-mono text-sm" />
            </div>
          </div>
        </div>

        {/* PACKAGE & FINANCIAL DETAILS */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-white mb-4">Logistics & Finances</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm mb-1 text-gray-400">Weight (KG) *</label>
              <input required type="number" step="0.01" {...register("weight")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" />
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">Delivery Charge (LKR) *</label>
              <input required type="number" step="0.01" {...register("delivery_charge")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" />
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">COD Amount (LKR)</label>
              <input type="number" step="0.01" {...register("cod_amount")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" placeholder="0.00" />
            </div>
          </div>
        </div>

        {/* SENDER DETAILS */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-white mb-4">Sender Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-1 text-gray-400">Sender Name *</label>
              <input required {...register("sender_name")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" placeholder="Merchant or Individual Name" />
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">Sender Phone</label>
              <input {...register("sender_phone")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" placeholder="Optional" />
            </div>
          </div>
        </div>

        <button 
          type="submit" 
          disabled={isSubmitting}
          className="w-full py-4 rounded-lg font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 transition-colors"
        >
          {isSubmitting ? <Loader2 size={20} className="animate-spin" /> : <PackagePlus size={20} />}
          Add to Inventory
        </button>
      </form>
    </div>
  );
}