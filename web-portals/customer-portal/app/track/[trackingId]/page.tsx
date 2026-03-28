'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import dynamic from 'next/dynamic';
import { MapPin, Box, CheckCircle2, AlertCircle, Loader2, X, UserCircle2, HandCoins, Navigation, Clock } from 'lucide-react';
import { trackingClient } from '@/lib/api';
import type { PublicTrackingDetailResponse } from '@/types';

// Dynamically import the map to prevent Next.js SSR crashes
const CustomerMap = dynamic(() => import('@/components/CustomerMap'), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-gray-50"><Loader2 className="animate-spin text-[#38A169]" /></div>
});

export default function CustomerTrackingPage() {
  const params = useParams();
  const trackingId = params.trackingId as string;

  const [data, setData] = useState<PublicTrackingDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Interaction States
  const [isPinning, setIsPinning] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [instructionError, setInstructionError] = useState<string | null>(null);
  
  // Modals
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [instructionText, setInstructionText] = useState('');
  const [showDateModal, setShowDateModal] = useState(false);
  const [selectedDates, setSelectedDates] = useState<string[]>([]);
  
  // Map State
  const [showMapModal, setShowMapModal] = useState(false);
  const [mapCoords, setMapCoords] = useState({ lat: 0, lng: 0 });

  const getNextDays = () => {
    const days = [];
    const date = new Date();
    for (let i = 1; i <= 4; i++) {
      date.setDate(date.getDate() + 1);
      days.push({
        fullDate: date.toISOString().split('T')[0],
        dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
        dayNum: date.getDate()
      });
    }
    return days;
  };
  const availableDates = getNextDays();

  useEffect(() => {
    fetchTrackingData();
  }, [trackingId]);

  const fetchTrackingData = async () => {
    try {
      setLoading(true);
      const result = await trackingClient.getTracking(trackingId);
      setData(result);
      
      // If they already have a verified location, use that. Otherwise use the default branch/snapshot location.
      if (result.recipient?.is_location_verified && result.recipient?.gps_lat) {
        setMapCoords({ lat: Number(result.recipient.gps_lat), lng: Number(result.recipient.gps_lng) });
      } else {
        setMapCoords({ lat: Number(result.gps_lat), lng: Number(result.gps_lng) });
      }
    } catch (err: any) {
      setError(err.message || "Could not find your package.");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenMap = () => {
    setIsPinning(true);
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          // Only auto-center on their device GPS if they HAVEN'T verified a location yet.
          // If they are editing, we want to show them where the pin currently is.
          if (!data?.recipient?.is_location_verified) {
             setMapCoords({ lat: position.coords.latitude, lng: position.coords.longitude });
          }
          setIsPinning(false);
          setShowMapModal(true);
        },
        () => {
          setIsPinning(false);
          setShowMapModal(true);
        },
        { timeout: 5000 }
      );
    } else {
      setIsPinning(false);
      setShowMapModal(true);
    }
  };

  const submitLocation = async () => {
    try {
      setIsPinning(true);
      await trackingClient.updateLocation(trackingId, {
        gps_lat: mapCoords.lat,
        gps_lng: mapCoords.lng
      });
      setShowMapModal(false);
      fetchTrackingData(); // Refresh to show Verified Checkmark
    } catch (err) {
      alert("Failed to save location. Please try again.");
    } finally {
      setIsPinning(false);
    }
  };

  const submitInstruction = async () => {
    if (!instructionText.trim()) return;
    setInstructionError(null);
    try {
      await trackingClient.addInstruction(trackingId, { content_text: instructionText });
      setShowInstructionModal(false);
      setInstructionText('');
      fetchTrackingData();
    } catch (err: any) {
      setInstructionError(err.message || "Cannot add instructions right now.");
    }
  };

  const submitPreferredDates = async () => {
    if (selectedDates.length === 0) return;
    try {
      await trackingClient.setPreference(trackingId, { target_dates: selectedDates, status: 'AVAILABLE' });
      setShowDateModal(false);
      setIsConfirmed(true);
    } catch (err: any) {
      alert("Failed to update delivery preference.");
    }
  };

  const formatTime = (isoString?: string | null) => {
    if (!isoString) return "--:--";
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><Loader2 className="animate-spin text-[#38A169] w-10 h-10" /></div>;
  if (error || !data) return <div className="min-h-screen flex items-center justify-center bg-gray-50"><p className="text-red-500 font-bold">{error}</p></div>;

  const isVerified = data.recipient?.is_location_verified;
  const shortOrderId = data.tracking_id.split('-')[1];

  // ==========================================
  // FLOW 3: COMPLETED STATE
  // ==========================================
  if (data.status === 'COMPLETED') {
    return (
      <div className="min-h-screen bg-gray-100 font-sans pb-10 flex justify-center">
        <div className="w-full max-w-md bg-white min-h-screen shadow-lg flex flex-col items-center pt-12 px-6">
          <h2 className="font-bold text-[#1A202C] text-lg mb-8">Order No: #{shortOrderId}</h2>
          <div className="w-24 h-24 bg-green-50 border-4 border-[#38A169] rounded-full flex items-center justify-center mb-4">
            <CheckCircle2 className="text-[#38A169] w-12 h-12" />
          </div>
          <h1 className="text-xl font-bold text-[#1A202C] mb-1">Delivery Completed</h1>
          <p className="text-gray-500 font-medium mb-10">Your package was delivered safely.</p>
          <div className="w-full text-left mb-2"><h3 className="font-bold text-[#1A202C]">Summary</h3></div>
          <div className="w-full bg-[#FFEFE5] rounded-2xl p-5 mb-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 bg-[#1A202C] rounded-full flex items-center justify-center text-white"><UserCircle2 size={24} /></div>
              <div><p className="font-bold text-[#1A202C]">LamiGo Driver</p><p className="text-xs text-gray-600">Assigned Logistics</p></div>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-[#FFD5B8] pb-2"><span className="text-gray-600">Delivery Time</span><span className="font-bold text-[#1A202C]">{formatTime(data.completed_at)}</span></div>
              <div className="flex justify-between border-b border-[#FFD5B8] pb-2"><span className="text-gray-600">Customer Name</span><span className="font-bold text-[#1A202C]">{data.recipient_name}</span></div>
              <div className="flex justify-between pt-1"><span className="text-gray-600">Total</span><span className="font-black text-[#1A202C]">Rs. {Number(data.cod_amount).toFixed(2)}</span></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // FLOW 2: LIVE PROCESS STATE
  // ==========================================
  if (data.status === 'ON_TRIP' || data.status === 'DELIVERING_NOW') {
    return (
      <div className="min-h-screen bg-gray-100 font-sans pb-10 flex justify-center">
        <div className="w-full max-w-md bg-white min-h-screen shadow-lg p-6 pt-12">
          <div className="bg-[#FFEFE5] rounded-3xl p-6 text-center shadow-sm relative overflow-hidden mb-6">
            <p className="font-bold text-[#1A202C] mb-1">Order ID : {shortOrderId}</p>
            <div className="flex items-center justify-center gap-2 mb-6">
              <span className="w-2.5 h-2.5 bg-[#38A169] rounded-full animate-pulse"></span><span className="text-sm font-semibold text-gray-600">Live Tracking</span>
            </div>
            <h1 className="text-5xl font-black text-[#1A202C] tracking-tight mb-1">{formatTime(data.current_task?.estimated_arrival_time)}</h1>
            <p className="text-sm text-gray-600 font-bold mb-6">Estimated Time of Arrival</p>
            <p className="text-[#1A202C] font-bold mb-4">Your driver is <span className="text-xl text-[#38A169]">Stop #{data.current_task?.sequence_number || 1}</span> on the route!</p>
            <div className="flex gap-2 w-full h-2 px-4">
              <div className="flex-1 bg-[#38A169] rounded-full"></div><div className="flex-1 bg-[#38A169] rounded-full"></div><div className="flex-1 bg-[#38A169] rounded-full"></div><div className="flex-1 bg-gray-300 rounded-full"></div><div className="flex-1 bg-gray-300 rounded-full"></div>
            </div>
          </div>
          <div className="bg-[#1A202C] rounded-2xl p-5 flex items-center justify-center gap-3 text-white shadow-md mb-6">
            <div className="bg-white/10 p-2 rounded-full"><HandCoins size={24} /></div><p className="text-xl font-bold">Amount Rs. {Number(data.cod_amount).toFixed(2)}</p>
          </div>
          <div>
            <h3 className="font-bold text-[#1A202C] mb-3">Instructions</h3>
            <textarea value={instructionText} onChange={(e) => setInstructionText(e.target.value)} placeholder="Leave with the security guard..." className="w-full h-28 border border-gray-300 rounded-xl p-4 outline-none focus:border-[#38A169] text-gray-700 resize-none shadow-sm mb-4" />
            <button onClick={submitInstruction} className="w-full bg-[#1A202C] text-white font-bold py-4 rounded-xl shadow-md active:scale-95 transition-transform text-lg">Update Instructions</button>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // FLOW 1: PRE-DELIVERY STATE
  // ==========================================
  return (
    <div className="min-h-screen bg-gray-100 font-sans pb-10 flex justify-center">
      <div className="w-full max-w-md bg-white min-h-screen shadow-lg relative">
        <div className="pt-12 pb-6 px-6 text-center flex flex-col items-center">
           <UserCircle2 size={56} strokeWidth={1.5} className="text-[#1A202C] mb-3" />
           <h1 className="text-xl font-bold text-[#1A202C]">Hi, {data.recipient_name.split(' ')[0]}.</h1>
           <p className="text-gray-600 font-medium mt-1">You have 1 shipment arriving soon</p>
        </div>

        <div className="px-5 space-y-4">
          {/* Peach Top Card */}
          <div className="bg-[#FFEFE5] rounded-2xl p-5 border border-[#FFD5B8]">
             <div className="flex items-start gap-3 mb-4">
               <div className="p-3 bg-white rounded-xl text-[#1A202C] border border-[#FFD5B8]"><Box size={24} /></div>
               <div className="pt-1">
                 <p className="text-[#1A202C] font-bold text-lg leading-tight">Order ID : {shortOrderId}</p>
                 <p className="text-xs text-gray-600 font-bold mt-1 uppercase tracking-wide">Cash on Delivery Rs.{Number(data.cod_amount).toFixed(2)}</p>
               </div>
             </div>
             <p className="text-[#1A202C] font-bold leading-snug mb-5 text-[15px]">Your order will be delivered to your location. Please confirm your availability.</p>
             <div className="flex gap-3 mb-3">
               <button onClick={() => setIsConfirmed(true)} className="flex-1 bg-[#38A169] text-white font-bold py-3.5 rounded-xl shadow-sm active:scale-95 transition-transform text-sm">Confirm to Receive</button>
               <button onClick={() => setShowDateModal(true)} className="flex-1 bg-[#E53E3E] text-white font-bold py-3.5 rounded-xl shadow-sm active:scale-95 transition-transform text-sm">Set Preferred Dates</button>
             </div>
             <button onClick={() => setShowInstructionModal(true)} className="w-full bg-[#1A202C] text-white font-bold py-3.5 rounded-xl shadow-sm active:scale-95 transition-transform text-sm">Add Instructions</button>
          </div>

          {/* Peach Location Pin Card */}
          <div className="bg-[#FFEFE5] rounded-2xl p-6 border border-[#FFD5B8] text-center flex flex-col items-center">
             <div className="w-12 h-12 border border-[#1A202C] rounded-full flex items-center justify-center mb-3 text-[#1A202C] bg-white"><MapPin size={20} strokeWidth={2.5} /></div>
             <p className="text-[#1A202C] font-bold mb-1">{data.address}</p>
             <p className="text-[#1A202C] font-bold text-lg leading-tight mb-5">Help driver to find your location</p>
             
             {isVerified ? (
               <div className="w-full flex flex-col items-center gap-3">
                 <div className="w-[80%] bg-green-100 text-[#38A169] font-bold py-3.5 rounded-xl flex justify-center items-center gap-2 border border-green-200">
                   <CheckCircle2 size={18} strokeWidth={3} /> Location Verified
                 </div>
                 {/* NEW: Editable Location Button */}
                 <button onClick={handleOpenMap} className="text-sm font-bold text-gray-500 underline underline-offset-4 hover:text-[#1A202C] transition-colors">
                   Edit Pinned Location
                 </button>
               </div>
             ) : (
               <button onClick={handleOpenMap} disabled={isPinning} className="w-[80%] bg-[#38A169] text-white font-bold py-3.5 rounded-xl shadow-sm active:scale-95 transition-transform text-sm flex justify-center items-center gap-2">
                 {isPinning ? <Loader2 size={16} className="animate-spin"/> : null}
                 {isPinning ? 'Locating...' : 'Pin Your Location'}
               </button>
             )}
          </div>

          <div className="pt-2 pb-8">
            <button className="w-full bg-[#38A169] text-white font-bold py-4 rounded-xl shadow-md text-[17px] active:scale-95 transition-transform flex items-center justify-center gap-3">
              Ready to Receive Order
            </button>
          </div>
        </div>

        {/* MODAL: INTERACTIVE MAP */}
        {showMapModal && (
          <div className="fixed inset-0 bg-black/80 z-50 flex flex-col justify-end animate-fade-in">
            <div className="bg-white w-full h-[85vh] rounded-t-3xl overflow-hidden flex flex-col shadow-2xl">
              <div className="p-5 flex justify-between items-center border-b z-10 bg-white">
                <div>
                  <h3 className="font-black text-[#1A202C] text-lg">Pin Exact Location</h3>
                  <p className="text-xs text-gray-500 font-medium">Drag the marker to your doorstep</p>
                </div>
                <button onClick={() => setShowMapModal(false)} className="bg-gray-100 p-2 rounded-full text-gray-600 hover:bg-gray-200"><X size={20}/></button>
              </div>
              <div className="flex-1 relative z-0">
                <CustomerMap 
                  initialLat={mapCoords.lat} 
                  initialLng={mapCoords.lng} 
                  onLocationChange={(lat, lng) => setMapCoords({ lat, lng })}
                />
              </div>
              <div className="p-6 bg-white z-10 shadow-[0_-10px_20px_rgba(0,0,0,0.05)]">
                <button onClick={submitLocation} disabled={isPinning} className="w-full bg-[#38A169] text-white font-bold py-4 rounded-xl text-lg flex justify-center items-center gap-2 shadow-lg active:scale-95 transition-transform">
                  {isPinning ? <Loader2 size={20} className="animate-spin"/> : <MapPin size={20}/>}
                  {isPinning ? 'Saving...' : 'Confirm Exact Location'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* MODAL: Preferred Dates (Multi-Select) */}
        {showDateModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fade-in">
              <div className="flex justify-between items-center p-5 border-b border-gray-100">
                <h3 className="font-bold text-gray-500 uppercase tracking-widest text-sm">Select Preferred Dates</h3>
                <button onClick={() => setShowDateModal(false)} className="text-gray-400 hover:text-[#1A202C]"><X size={24}/></button>
              </div>
              <div className="p-6">
                <div className="flex justify-between gap-2 mb-6">
                  {availableDates.map((day) => {
                    const isSelected = selectedDates.includes(day.fullDate);
                    return (
                      <button key={day.fullDate} onClick={() => isSelected ? setSelectedDates(selectedDates.filter(d => d !== day.fullDate)) : setSelectedDates([...selectedDates, day.fullDate])} className={`flex-1 py-3 flex flex-col items-center justify-center rounded-xl font-bold transition-all border-2 ${isSelected ? 'bg-[#38A169] text-white border-[#38A169] scale-105 shadow-md' : 'bg-white text-gray-600 border-gray-200 hover:border-[#38A169]'}`}>
                        <span className="text-xs uppercase">{day.dayName}</span><span className="text-lg">{day.dayNum}</span>
                      </button>
                    );
                  })}
                </div>
                <button onClick={submitPreferredDates} disabled={selectedDates.length === 0} className="w-full bg-[#1A202C] disabled:bg-gray-300 text-white font-bold py-4 rounded-xl text-sm transition-colors">Confirm Preferred Dates</button>
              </div>
            </div>
          </div>
        )}

        {/* MODAL: Add Instruction */}
        {showInstructionModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fade-in">
              <div className="flex justify-between items-center p-5 border-b border-gray-100">
                <h3 className="font-bold text-gray-500 uppercase tracking-widest text-sm">Add Instruction</h3>
                <button onClick={() => setShowInstructionModal(false)} className="text-gray-400 hover:text-[#1A202C]"><X size={24}/></button>
              </div>
              <div className="p-6">
                {instructionError && <div className="mb-4 p-3 bg-red-50 text-[#E53E3E] text-sm rounded-lg border border-red-100 flex items-start gap-2"><AlertCircle size={16} className="mt-0.5 shrink-0" /><p className="font-medium">{instructionError}</p></div>}
                <textarea value={instructionText} onChange={(e) => setInstructionText(e.target.value)} placeholder="Leave with the security guard..." className="w-full h-32 border-2 border-gray-200 rounded-xl p-4 outline-none focus:border-[#38A169] text-gray-700 resize-none font-medium text-sm mb-2" />
                <button onClick={submitInstruction} className="w-full bg-[#1A202C] text-white font-bold py-4 rounded-xl text-sm shadow-md">Add instructions</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}