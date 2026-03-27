'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, ArrowLeft, Route, CheckCircle2, AlertCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { DriverResponse, PackageResponse } from '@/types';

interface TripFormInputs {
  driver_id: string;
  scheduled_start_time: string;
}

export default function CreateTripPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [selectedPackages, setSelectedPackages] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { register, handleSubmit } = useForm<TripFormInputs>();

  // 1. Fetch dependencies
  const { data: branch } = useQuery({ queryKey: ['my-branch'], queryFn: apiClient.getMyBranch });
  const { data: drivers = [] } = useQuery<DriverResponse[]>({ queryKey: ['drivers'], queryFn: apiClient.getDrivers });
  const { data: packages = [], isLoading: loadingPackages } = useQuery<PackageResponse[]>({ queryKey: ['packages'], queryFn: apiClient.getPackages });

  // Only show drivers who are available or off-duty
  const availableDrivers = drivers.filter(d => d.status === 'AVAILABLE' || d.status === 'OFF_DUTY');
  
  // Only show packages that are waiting in the hub
  const availablePackages = packages.filter(p => p.status === 'TO_BE_DELIVERED');

  const togglePackage = (packageId: string) => {
    setSelectedPackages(prev => 
      prev.includes(packageId) 
        ? prev.filter(id => id !== packageId) 
        : [...prev, packageId]
    );
  };

  const onSubmit = async (data: TripFormInputs) => {
    if (!branch) {
      setErrorMsg("Branch data missing. Cannot create trip.");
      return;
    }
    if (selectedPackages.length === 0) {
      setErrorMsg("You must select at least one package to create a trip.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      // Step 1: Create the empty Trip Manifest
      const newTrip = await apiClient.createTrip({
        branch_id: branch.branch_id,
        driver_id: data.driver_id || null, // Null if unassigned
        scheduled_start_time: data.scheduled_start_time ? new Date(data.scheduled_start_time).toISOString() : null
      });

      // Step 2: Loop through selected packages and assign them to the Trip as Tasks
      const taskPromises = selectedPackages.map((pkgId, index) => {
        return apiClient.createTask({
          trip_id: newTrip.trip_id,
          package_id: pkgId,
          sequence_number: index + 1 // Route ordering 1, 2, 3...
        });
      });

      await Promise.all(taskPromises); // Wait for all tasks to securely attach

      // Step 3: Success and redirect
      queryClient.invalidateQueries({ queryKey: ['trips'] });
      queryClient.invalidateQueries({ queryKey: ['packages'] });
      
      setSuccessMsg("Trip successfully created and packages assigned!");
      setTimeout(() => {
        router.push('/trips');
      }, 1500);

    } catch (err: any) {
      setErrorMsg(err.message || "Failed to construct the trip manifest.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8 animate-fade-in max-w-5xl">
      <div className="mb-8">
        <Link href="/trips" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400 transition-colors hover:text-white">
          <ArrowLeft size={16} /> Back to Trips
        </Link>
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-900/30 rounded-lg">
            <Route size={24} className="text-blue-400" />
          </div>
          <h1 className="text-2xl font-semibold text-white">Create New Trip</h1>
        </div>
      </div>

      {successMsg && (
        <div className="mb-6 p-4 bg-green-900/20 border border-green-500/50 rounded-lg flex items-center gap-3 text-green-400">
          <CheckCircle2 size={20} />
          <p className="text-sm font-medium">{successMsg}</p>
        </div>
      )}

      {errorMsg && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-400">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">{errorMsg}</p>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Logistics Configuration */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-white mb-4">Logistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm mb-1 text-gray-400">Assign Driver</label>
              <select {...register("driver_id")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium">
                <option value="">-- Unassigned (Draft) --</option>
                {availableDrivers.map(d => (
                  <option key={d.uid} value={d.uid}>{d.full_name} ({d.vehicle_type})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm mb-1 text-gray-400">Scheduled Start Time</label>
              <input type="datetime-local" {...register("scheduled_start_time")} className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" />
            </div>
          </div>
        </div>

        {/* Package Selection Table */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-[#2E2E2E] bg-[#1A1A1A]">
            <h2 className="font-semibold text-white">Select Packages</h2>
            <p className="text-xs text-gray-400 mt-1">Only packages in "To Be Delivered" state are shown.</p>
          </div>
          
          <table className="w-full text-sm text-left">
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                <th className="p-4 font-medium w-12"></th>
                <th className="p-4 font-medium">Package ID</th>
                <th className="p-4 font-medium">Delivery Address</th>
                <th className="p-4 font-medium text-right">COD Amount</th>
              </tr>
            </thead>
            <tbody>
              {loadingPackages && <tr><td colSpan={4} className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-gray-500" /></td></tr>}
              {!loadingPackages && availablePackages.length === 0 && <tr><td colSpan={4} className="p-8 text-center text-gray-500">No available packages in your hub. Go add some first!</td></tr>}
              
              {availablePackages.map(pkg => (
                <tr key={pkg.package_id} className={`border-b border-[#2E2E2E] transition-colors cursor-pointer ${selectedPackages.includes(pkg.package_id) ? 'bg-blue-900/10' : 'hover:bg-[#252525]'}`} onClick={() => togglePackage(pkg.package_id)}>
                  <td className="p-4">
                    <input 
                      type="checkbox" 
                      checked={selectedPackages.includes(pkg.package_id)}
                      onChange={() => togglePackage(pkg.package_id)}
                      className="w-4 h-4 rounded bg-[#121212] border-[#2E2E2E]"
                      onClick={e => e.stopPropagation()} 
                    />
                  </td>
                  <td className="p-4 font-mono text-gray-300">{pkg.tracking_id}</td>
                  <td className="p-4 text-gray-400 truncate max-w-[300px]">{pkg.address}</td>
                  <td className={`p-4 text-right font-medium ${pkg.is_cod ? 'text-green-400' : 'text-gray-500'}`}>
                    {pkg.is_cod ? `LKR ${pkg.cod_amount}` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer Action Bar */}
        <div className="flex items-center justify-between pt-2">
          <span className="text-gray-400 font-medium">
            <strong className="text-white">{selectedPackages.length}</strong> packages selected
          </span>
          <button 
            type="submit" 
            disabled={isSubmitting || selectedPackages.length === 0}
            className="px-8 py-3 rounded-lg font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle2 size={18} />}
            Create Trip Manifest
          </button>
        </div>
      </form>
    </div>
  );
}