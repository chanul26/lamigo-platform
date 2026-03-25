'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

const driverSchema = z.object({
  role: z.literal('DRIVER'), // Hardcoded to satisfy Pydantic UserRole
  full_name: z.string().min(2, "Full name required"),
  phone_number: z.string().min(9, "Valid phone required. Ex: +94771234567"),
  nic_number: z.string().min(10, "Valid NIC required"),
  vehicle_type: z.enum(['MOTORCYCLE', 'THREE_WHEEL', 'LORRY']),
  vehicle_number: z.string().min(4, "Vehicle plate required"),
  license_number: z.string().min(4, "License number required"),
});

type DriverFormValues = z.infer<typeof driverSchema>;

export default function RegisterDriverPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<DriverFormValues>({
    resolver: zodResolver(driverSchema),
    defaultValues: {
      role: 'DRIVER', full_name: '', phone_number: '+94', nic_number: '', vehicle_type: 'MOTORCYCLE', vehicle_number: '', license_number: ''
    }
  });

  async function onSubmit(data: DriverFormValues) {
    setServerError(null);
    try {
      await apiClient.createDriver(data);
      router.push('/drivers');
    } catch (err: unknown) {
      setServerError(err instanceof Error ? err.message : 'Failed to register driver');
    }
  }

  return (
    <div className="p-8 animate-fade-in max-w-2xl">
      <Link href="/drivers" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400">
        <ArrowLeft size={16} /> Back to Drivers
      </Link>
      <h1 className="text-2xl font-semibold mb-2 text-white">Register New Driver</h1>
      <p className="text-gray-400 mb-6">Enter personal and vehicle details.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 p-8 rounded-xl bg-[#1E1E1E] border border-[#2E2E2E]">
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm mb-1 text-gray-400">Full Name (As per NIC) *</label>
            <input {...register("full_name")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none" />
            {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name.message}</p>}
          </div>
          <div>
            <label className="block text-sm mb-1 text-gray-400">Mobile Number *</label>
            <input {...register("phone_number")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none" />
            {errors.phone_number && <p className="text-red-500 text-xs mt-1">{errors.phone_number.message}</p>}
          </div>
          <div>
            <label className="block text-sm mb-1 text-gray-400">NIC Number *</label>
            <input {...register("nic_number")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none" />
            {errors.nic_number && <p className="text-red-500 text-xs mt-1">{errors.nic_number.message}</p>}
          </div>
          <div>
            <label className="block text-sm mb-1 text-gray-400">Driver License *</label>
            <input {...register("license_number")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none" />
            {errors.license_number && <p className="text-red-500 text-xs mt-1">{errors.license_number.message}</p>}
          </div>
        </div>

        <div className="border-t border-[#2E2E2E] my-4"></div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm mb-1 text-gray-400">Vehicle Type *</label>
            <select {...register("vehicle_type")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none">
              <option value="MOTORCYCLE">Motorcycle</option>
              <option value="THREE_WHEEL">Three Wheeler (Tuk Tuk)</option>
              <option value="LORRY">Lorry / Van</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1 text-gray-400">Vehicle Plate Number *</label>
            <input {...register("vehicle_number")} className="w-full p-2.5 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none" />
            {errors.vehicle_number && <p className="text-red-500 text-xs mt-1">{errors.vehicle_number.message}</p>}
          </div>
        </div>

        {serverError && <p className="text-red-500 text-sm bg-red-900/20 p-3 rounded">{serverError}</p>}

        <div className="flex justify-end pt-4">
          <button type="submit" disabled={isSubmitting} className="px-6 py-2.5 rounded font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 flex items-center gap-2">
            {isSubmitting && <Loader2 size={16} className="animate-spin" />}
            Register Driver
          </button>
        </div>
      </form>
    </div>
  );
}