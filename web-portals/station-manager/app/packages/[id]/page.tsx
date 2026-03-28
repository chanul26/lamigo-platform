'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, ArrowLeft, MapPin, Phone, MessageSquare, AlertTriangle, Edit, CheckCircle2, Printer, X, Image as ImageIcon, RotateCcw } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import dynamic from 'next/dynamic';
import { apiClient } from '@/lib/api';
import type { PackageUpdate } from '@/types';

// Dynamically import the map to prevent Next.js SSR crashes
const LocationPickerMap = dynamic(() => import('@/components/LocationPickerMap'), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-[#121212] text-gray-500"><Loader2 className="animate-spin" /></div>
});

export default function PackageDetailsPage() {
  const params = useParams();
  const packageId = params.id as string;
  const queryClient = useQueryClient();
  const [smsSent, setSmsSent] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const { data: pkg, isLoading, isError } = useQuery({
    queryKey: ['package', packageId],
    queryFn: () => apiClient.getPackage(packageId),
  });

  const { register, handleSubmit, reset } = useForm<PackageUpdate>();

  const updateMutation = useMutation({
    mutationFn: (data: PackageUpdate) => apiClient.updatePackage(packageId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['package', packageId] });
      queryClient.invalidateQueries({ queryKey: ['packages'] });
      setIsEditModalOpen(false);
    }
  });

  const smsMutation = useMutation({
    mutationFn: apiClient.sendSmsLog,
    onSuccess: () => {
      setSmsSent(true);
      setTimeout(() => setSmsSent(false), 5000);
    }
  });

  const handleSendSMS = () => {
    if (!pkg) return;
    
    // THE FIX: Construct the URL and inject it into the SMS body
    const trackingUrl = `http://localhost:3001/track/${pkg.tracking_id}`;
    
    smsMutation.mutate({
      package_id: pkg.package_id,
      recipient_phone: pkg.recipient?.phone_number || '',
      message_body: `LamiGo Delivery: Please click this link to verify your exact GPS location for package ${pkg.tracking_id}. Link: ${trackingUrl}`,
      category: 'PIN_VERIFICATION',
      status: 'SENT'
    });
  };

  const openEditModal = () => {
    if (pkg) {
      reset({ status: pkg.status });
      setIsEditModalOpen(true);
    }
  };

  const onSubmitUpdate = (data: PackageUpdate) => {
    const payload: PackageUpdate = { status: data.status };
    if (data.num_of_attempts) payload.num_of_attempts = Number(data.num_of_attempts);
    if (data.package_photo_url) payload.package_photo_url = data.package_photo_url;
    
    updateMutation.mutate(payload);
  };

  if (isLoading) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin text-blue-500 w-10 h-10" /></div>;
  if (isError || !pkg) return <div className="p-8 text-red-500 flex items-center gap-2"><AlertTriangle /> Package not found.</div>;

  return (
    <div className="p-8 animate-fade-in max-w-6xl relative">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link href="/packages" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400 hover:text-white">
            <ArrowLeft size={16} /> Back to Inventory
          </Link>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            Package {pkg.tracking_id}
            <span className="px-3 py-1 bg-[#2E2E2E] text-white text-xs font-bold uppercase tracking-wider rounded">
              {pkg.status.replace(/_/g, ' ')}
            </span>
          </h1>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT COLUMN: Map & SMS Action */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl overflow-hidden shadow-sm">
            <div className="w-full h-[350px] bg-[#121212] relative z-0">
              
              {/* THE FIX: Smartly select which GPS coordinates to display */}
              <LocationPickerMap 
                lat={pkg.recipient?.is_location_verified ? Number(pkg.recipient.gps_lat) : Number(pkg.gps_lat)} 
                lng={pkg.recipient?.is_location_verified ? Number(pkg.recipient.gps_lng) : Number(pkg.gps_lng)} 
                onLocationSelect={() => {}} // View-only mode
              />

              {!pkg.recipient?.is_location_verified && (
                <div className="absolute inset-0 bg-black/70 flex flex-col items-center justify-center pointer-events-none z-10">
                   <div className="bg-[#1A1A1A] p-4 rounded-full mb-3 border border-gray-700 shadow-lg">
                      <MapPin size={32} className="text-gray-400" />
                   </div>
                   <h3 className="text-lg font-bold text-white tracking-widest drop-shadow-md">LOCATION UNVERIFIED</h3>
                </div>
              )}
            </div>
            
            <div className="p-6 bg-[#1A1A1A] border-t border-[#2E2E2E] flex items-center justify-between">
               <div>
                 <p className="text-sm text-gray-400 mb-1">Customer GPS Pin Required</p>
                 <p className="text-xs text-gray-500">Send an automated SMS to {pkg.recipient?.phone_number || 'the customer'} to verify coordinates.</p>
               </div>
               <button 
                 onClick={handleSendSMS}
                 disabled={smsMutation.isPending || smsSent}
                 className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-green-700 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-all"
               >
                 {smsMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : smsSent ? <CheckCircle2 size={16} /> : <MessageSquare size={16} />}
                 {smsSent ? 'SMS Sent Successfully!' : 'Request GPS Pin via SMS'}
               </button>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Details & Actions */}
        <div className="space-y-6">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
            <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 border-b border-[#2E2E2E] pb-2">Recipient</h2>
            <div className="space-y-4">
              <div>
                <p className="text-white font-medium text-lg">{pkg.recipient_name}</p>
                <p className="text-gray-400 text-sm flex items-center gap-2 mt-1">
                  <Phone size={14}/> {pkg.recipient?.phone_number || 'N/A'}
                </p>
              </div>
              <div className="bg-[#121212] p-3 rounded border border-[#2E2E2E]">
                <p className="text-gray-300 text-sm">{pkg.address}</p>
              </div>
            </div>
          </div>

          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
            <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 border-b border-[#2E2E2E] pb-2">Financials & Logistics</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Weight</span>
                <span className="text-white font-medium">{pkg.weight} KG</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Delivery Charge</span>
                <span className="text-white font-medium">LKR {pkg.delivery_charge}</span>
              </div>
              <div className="flex justify-between pt-3 border-t border-[#2E2E2E]">
                <span className="text-gray-400 font-medium">COD to Collect</span>
                <span className={`font-bold ${pkg.is_cod ? 'text-green-400' : 'text-gray-500'}`}>
                  LKR {pkg.cod_amount}
                </span>
              </div>
            </div>
          </div>

          {/* ACTION BUTTONS */}
          <div className="flex gap-4 pt-2">
            <button 
              onClick={openEditModal}
              className="flex-1 py-3 bg-[#2E2E2E] hover:bg-[#3E3E3E] text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2 transition-all border border-[#3E3E3E]"
            >
              <Edit size={16} /> Edit Package
            </button>
            <button 
              onClick={() => window.print()}
              className="flex-1 py-3 bg-[#2E2E2E] hover:bg-[#3E3E3E] text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2 transition-all border border-[#3E3E3E]"
            >
              <Printer size={16} /> Print Label
            </button>
          </div>
        </div>

      </div>

      {/* EDIT PACKAGE MODAL */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 w-full max-w-md shadow-2xl animate-fade-in">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white flex items-center gap-2"><Edit size={20} className="text-blue-400"/> Edit Details</h2>
              <button onClick={() => setIsEditModalOpen(false)} className="text-gray-500 hover:text-white transition-colors"><X size={20}/></button>
            </div>
            
            <form onSubmit={handleSubmit(onSubmitUpdate)} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Status</label>
                <select {...register("status")} className="w-full bg-[#121212] border border-[#2E2E2E] text-white rounded-lg p-3 outline-none focus:border-blue-500">
                  <option value="TO_BE_DELIVERED">To Be Delivered</option>
                  <option value="SCHEDULED">Scheduled</option>
                  <option value="ON_TRIP">On Trip</option>
                  <option value="DELIVERING_NOW">Delivering Now</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="FAILED">Failed</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1 flex items-center gap-2">
                  <RotateCcw size={14}/> Manual Delivery Attempts
                </label>
                <input 
                  type="number" 
                  min="0" 
                  placeholder="Override failed attempts counter"
                  {...register("num_of_attempts")} 
                  className="w-full bg-[#121212] border border-[#2E2E2E] text-white rounded-lg p-3 outline-none focus:border-blue-500" 
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1 flex items-center gap-2">
                  <ImageIcon size={14}/> Proof of Delivery URL
                </label>
                <input 
                  type="text" 
                  placeholder="https://..." 
                  {...register("package_photo_url")} 
                  className="w-full bg-[#121212] border border-[#2E2E2E] text-white rounded-lg p-3 outline-none focus:border-blue-500" 
                />
              </div>

              <div className="pt-4 border-t border-[#2E2E2E]">
                <button 
                  type="submit" 
                  disabled={updateMutation.isPending} 
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex justify-center items-center gap-2 transition-colors"
                >
                  {updateMutation.isPending ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle2 size={18} />}
                  Save Package Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}