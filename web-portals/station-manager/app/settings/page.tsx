'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, AlertCircle, MapPin, Building, Save, CheckCircle2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import dynamic from 'next/dynamic';
import { apiClient } from '@/lib/api';
import type { BranchUpdate } from '@/types';

// Dynamically import the map to prevent Next.js SSR crashes
const InteractiveMap = dynamic(() => import('@/components/LocationPickerMap'), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-[#1A1A1A] text-gray-500"><Loader2 className="animate-spin" /></div>
});

export default function BranchSettingsPage() {
  const queryClient = useQueryClient();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const { data: branch, isLoading, isError } = useQuery({
    queryKey: ['my-branch'],
    queryFn: apiClient.getMyBranch
  });

  // Setup form with setValue and watch for map integration
  const { register, handleSubmit, setValue, watch, formState: { isSubmitting, isDirty } } = useForm<BranchUpdate>({
    values: {
      name: branch?.name || '',
      address: branch?.address || '',
      gps_lat: branch ? Number(branch.gps_lat) : 0,
      gps_lng: branch ? Number(branch.gps_lng) : 0,
      default_commission_rate: branch ? Number(branch.default_commission_rate) : 0,
    }
  });

  // Watch the coordinates so the map pin knows where to be
  const currentLat = watch('gps_lat') || 0;
  const currentLng = watch('gps_lng') || 0;

  const updateMutation = useMutation({
    mutationFn: apiClient.updateMyBranch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-branch'] });
      setSuccessMsg("Branch settings updated successfully!");
      setTimeout(() => setSuccessMsg(null), 4000);
    }
  });

  function onSubmit(data: BranchUpdate) {
    updateMutation.mutate(data);
  }

  if (isLoading) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin text-blue-500 w-10 h-10" /></div>;
  if (isError || !branch) return <div className="p-8 text-red-500 flex items-center gap-2"><AlertCircle /> Failed to load branch settings.</div>;

  return (
    <div className="p-8 animate-fade-in max-w-6xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-white mb-2">Branch Settings</h1>
        <p className="text-gray-400">Manage your operational hub details and default financial parameters.</p>
      </div>

      {successMsg && (
        <div className="mb-6 p-4 bg-green-900/20 border border-green-500/50 rounded-lg flex items-center gap-3 text-green-400">
          <CheckCircle2 size={20} />
          <p className="text-sm font-medium">{successMsg}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* LEFT COLUMN: Interactive Map */}
        <div className="space-y-6">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-[#2E2E2E] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <MapPin className="text-blue-400" size={20} />
                <h2 className="font-semibold text-white">Live Branch Location</h2>
              </div>
              <span className="text-xs text-blue-400 bg-blue-900/20 px-3 py-1 rounded font-medium">Click map to move pin</span>
            </div>
            
            <div className="w-full h-[400px] bg-[#121212] relative z-0">
              {branch && (
                <InteractiveMap 
                  lat={currentLat} 
                  lng={currentLng} 
                  onLocationSelect={(lat, lng) => {
                    // Two-Way Binding: Update the form boxes when the map is clicked
                    setValue('gps_lat', parseFloat(lat.toFixed(6)), { shouldDirty: true });
                    setValue('gps_lng', parseFloat(lng.toFixed(6)), { shouldDirty: true });
                  }} 
                />
              )}
            </div>
            
            <div className="p-5 bg-[#1A1A1A]">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-900/20 rounded-lg text-blue-400">
                  <Building size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{watch('name') || branch.name}</h3>
                  <p className="text-gray-400 text-sm mt-1 leading-relaxed">{watch('address') || branch.address}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Configuration Form */}
        <div>
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
            <h2 className="font-semibold text-white mb-6">Configuration</h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm mb-1 text-gray-400">Branch Name</label>
                  <input 
                    type="text" 
                    {...register("name")} 
                    className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-medium" 
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1 text-gray-400">Physical Address</label>
                  <textarea 
                    {...register("address")} 
                    rows={2}
                    className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none resize-none font-medium" 
                  />
                </div>
              </div>

              <hr className="border-[#2E2E2E]" />

              <div>
                <label className="block text-sm mb-3 text-gray-400">Map Coordinates (GPS)</label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-gray-500 block mb-1">Latitude</span>
                    <input 
                      type="number" step="any"
                      {...register("gps_lat", { valueAsNumber: true })} 
                      className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-mono text-sm" 
                    />
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block mb-1">Longitude</span>
                    <input 
                      type="number" step="any"
                      {...register("gps_lng", { valueAsNumber: true })} 
                      className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none font-mono text-sm" 
                    />
                  </div>
                </div>
              </div>

              <hr className="border-[#2E2E2E]" />

              <div>
                <label className="block text-sm mb-2 text-gray-400">Driver Commission Rate (%)</label>
                <div className="relative">
                  <input 
                    type="number" step="0.01"
                    {...register("default_commission_rate", { valueAsNumber: true })} 
                    className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none text-lg font-medium pl-4 pr-12" 
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 font-semibold">%</span>
                </div>
              </div>

              <button 
                type="submit" 
                disabled={!isDirty || isSubmitting}
                className="w-full py-3 mt-4 rounded-lg font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 transition-colors"
              >
                {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                Save All Changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}