'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, AlertCircle, MapPin, Building, Save, CheckCircle2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { apiClient } from '@/lib/api';
import type { BranchUpdate } from '@/types';

export default function BranchSettingsPage() {
  const queryClient = useQueryClient();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // 1. Fetch the Manager's Branch
  const { data: branch, isLoading, isError } = useQuery({
    queryKey: ['my-branch'],
    queryFn: apiClient.getMyBranch
  });

  // 2. Form Setup
  const { register, handleSubmit, formState: { isSubmitting, isDirty } } = useForm<BranchUpdate>({
    values: {
      default_commission_rate: branch ? Number(branch.default_commission_rate) : 0,
    }
  });

  // 3. Mutation to Update Settings
  const updateMutation = useMutation({
    mutationFn: apiClient.updateMyBranch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-branch'] });
      setSuccessMsg("Branch settings updated successfully!");
      setTimeout(() => setSuccessMsg(null), 4000);
    }
  });

  function onSubmit(data: BranchUpdate) {
    updateMutation.mutate({ default_commission_rate: data.default_commission_rate });
  }

  if (isLoading) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin text-blue-500 w-10 h-10" /></div>;
  if (isError || !branch) return <div className="p-8 text-red-500 flex items-center gap-2"><AlertCircle /> Failed to load branch settings.</div>;

  return (
    <div className="p-8 animate-fade-in max-w-5xl">
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COLUMN: Map & Location */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl overflow-hidden shadow-sm">
            <div className="p-4 border-b border-[#2E2E2E] flex items-center gap-3">
              <MapPin className="text-blue-400" size={20} />
              <h2 className="font-semibold text-white">Branch Location</h2>
            </div>
            {/* THE FREE GOOGLE MAPS IFRAME TRICK */}
            <div className="w-full h-[400px] bg-[#121212]">
              <iframe 
                width="100%" 
                height="100%" 
                frameBorder="0" 
                style={{ border: 0 }}
                src={`https://maps.google.com/maps?q=${branch.gps_lat},${branch.gps_lng}&z=16&output=embed`}
                allowFullScreen
              />
            </div>
            <div className="p-5 bg-[#1A1A1A]">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-900/20 rounded-lg text-blue-400">
                  <Building size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{branch.name}</h3>
                  <p className="text-gray-400 text-sm mt-1 leading-relaxed">{branch.address}</p>
                  <p className="text-xs text-gray-500 mt-2 font-mono">GPS: {branch.gps_lat}, {branch.gps_lng}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Settings Form */}
        <div className="space-y-6">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
            <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
              Financial Parameters
            </h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <div>
                <label className="block text-sm mb-2 text-gray-400">Driver Commission Rate (%)</label>
                <div className="relative">
                  <input 
                    type="number" 
                    step="0.01"
                    {...register("default_commission_rate", { valueAsNumber: true })} 
                    className="w-full p-3 rounded bg-[#121212] border border-[#2E2E2E] text-white focus:border-blue-500 outline-none text-lg font-medium pl-4 pr-12" 
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 font-semibold">%</span>
                </div>
                <p className="text-xs text-gray-500 mt-2 leading-relaxed">
                  This base rate applies to all drivers in your branch unless overridden on their individual profile.
                </p>
              </div>

              <button 
                type="submit" 
                disabled={!isDirty || isSubmitting}
                className="w-full py-3 rounded-lg font-medium bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 transition-colors"
              >
                {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                Save Configuration
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}