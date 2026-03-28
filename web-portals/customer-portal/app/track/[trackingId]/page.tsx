'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { MapPin, Box, CheckCircle2, AlertCircle, Loader2, X, UserCircle2, ThumbsUp } from 'lucide-react';
import { trackingClient } from '@/lib/api';
import type { PublicTrackingDetailResponse } from '@/types';

export default function CustomerTrackingPage() {
  const params = useParams();
  const trackingId = params.trackingId as string;

  const [data, setData] = useState<PublicTrackingDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Interaction States
  const [isPinning, setIsPinning] = useState(false);
  const [pinSuccess, setPinSuccess] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [instructionError, setInstructionError] = useState<string | null>(null);
  
  // Modals
  const [showInstructionModal, setShowInstructionModal] = useState(false);
  const [instructionText, setInstructionText] = useState('');
  const [showDateModal, setShowDateModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState('');

  // Calculate Date Limits (Tomorrow to +5 Days)
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDateStr = tomorrow.toISOString().split('T')[0];
  
  const maxDate = new Date();
  maxDate.setDate(maxDate.getDate() + 5);
  const maxDateStr = maxDate.toISOString().split('T')[0];

  useEffect(() => {
    fetchTrackingData();
  }, [trackingId]);

  const fetchTrackingData = async () => {
    try {
      setLoading(true);
      const result = await trackingClient.getTracking(trackingId);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Could not find your package.");
    } finally {
      setLoading(false);
    }
  };

  const handleDropPin = () => {
    setIsPinning(true);
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      setIsPinning(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          await trackingClient.updateLocation(trackingId, {
            gps_lat: position.coords.latitude,
            gps_lng: position.coords.longitude
          });
          setPinSuccess(true);
          fetchTrackingData();
        } catch (err) {
          alert("Failed to save location. Please try again.");
        } finally {
          setIsPinning(false);
        }
      },
      (error) => {
        alert("Please allow location access to drop your delivery pin.");
        setIsPinning(false);
      }
    );
  };

  const submitInstruction = async () => {
    if (!instructionText.trim()) return;
    setInstructionError(null);
    try {
      await trackingClient.addInstruction(trackingId, { content_text: instructionText });
      alert("Instruction saved successfully!");
      setShowInstructionModal(false);
      setInstructionText('');
    } catch (err: any) {
      // Gracefully handle the 400 error from the backend if it's not on a trip yet
      setInstructionError(err.message || "Cannot add instructions right now.");
    }
  };

  const submitUnavailableDate = async () => {
    if (!selectedDate) return;
    try {
      await trackingClient.setPreference(trackingId, { target_date: selectedDate, status: 'UNAVAILABLE' });
      alert(`Delivery rescheduled for after ${selectedDate}!`);
      setShowDateModal(false);
      setIsConfirmed(true); // Treat a reschedule as a resolution
    } catch (err: any) {
      alert("Failed to update delivery preference.");
    }
  };

  if (loading) return <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center text-blue-600"><Loader2 className="animate-spin w-10 h-10 mb-4" /></div>;
  if (error || !data) return <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 text-center"><AlertCircle className="w-12 h-12 text-red-500 mb-4" /><h1 className="text-xl font-bold text-gray-800 mb-2">Tracking Not Found</h1></div>;

  const isVerified = data.recipient?.is_location_verified || pinSuccess;

  return (
    <div className="min-h-screen bg-gray-100 font-sans pb-10">
      <div className="max-w-md mx-auto bg-white min-h-screen shadow-lg relative">
        
        {/* Header - Flow 1 */}
        <div className="pt-12 pb-6 px-6 text-center flex flex-col items-center">
           <UserCircle2 size={64} strokeWidth={1} className="text-gray-800 mb-3" />
           <h1 className="text-xl font-bold text-gray-800">Hi, {data.recipient_name.split(' ')[0]}.</h1>
           <p className="text-gray-600 font-medium mt-1">You have 1 shipment arriving soon</p>
        </div>

        <div className="px-5 space-y-4">
          
          {/* Top Card (Peach Color from Figma) */}
          <div className="bg-[#FFEFE5] rounded-2xl p-5 border border-[#FFD5B8]">
             <div className="flex items-start gap-3 mb-4">
               <div className="p-2.5 bg-blue-100/50 rounded-xl text-blue-600">
                 <Box size={24} />
               </div>
               <div>
                 <p className="text-gray-800 font-bold text-lg leading-tight">Order ID : {data.tracking_id.split('-')[1]}</p>
                 <p className="text-sm text-gray-600 font-medium">
                   Cash on Delivery Rs.{Number(data.cod_amount).toFixed(2)}
                 </p>
               </div>
             </div>

             {isConfirmed ? (
               <div className="bg-green-100 text-green-800 p-4 rounded-xl flex items-center gap-3 mb-2 font-bold border border-green-200">
                 <ThumbsUp size={24} /> Thank you! We will deliver it soon.
               </div>
             ) : (
               <>
                 <p className="text-gray-800 font-bold leading-snug mb-5">
                   Your order will be delivered to your location. Please confirm your availability.
                 </p>

                 <div className="flex gap-3 mb-3">
                   <button 
                     onClick={() => setIsConfirmed(true)}
                     className="flex-1 bg-[#38A169] text-white font-bold py-3 rounded-xl shadow-sm active:scale-95 transition-transform text-sm"
                   >
                     Confirm to Receive
                   </button>
                   <button 
                     onClick={() => setShowDateModal(true)}
                     className="flex-1 bg-[#E53E3E] text-white font-bold py-3 rounded-xl shadow-sm active:scale-95 transition-transform text-sm"
                   >
                     Not Available
                   </button>
                 </div>
               </>
             )}

             <button 
               onClick={() => {
                 setInstructionError(null);
                 setShowInstructionModal(true);
               }}
               className="w-full bg-[#1A202C] text-white font-bold py-3.5 rounded-xl shadow-sm active:scale-95 transition-transform text-sm mt-2"
             >
               Add Instructions
             </button>
          </div>

          {/* Bottom Card (Location Pin) */}
          <div className="bg-[#FFEFE5] rounded-2xl p-6 border border-[#FFD5B8] text-center flex flex-col items-center">
             <div className="w-12 h-12 border-2 border-gray-800 rounded-full flex items-center justify-center mb-3 text-gray-800">
               <MapPin size={24} />
             </div>
             <p className="text-gray-800 font-bold mb-1">{data.address}</p>
             <p className="text-gray-800 font-bold text-lg leading-tight mb-4">Help driver to find your location</p>
             
             {isVerified ? (
               <div className="w-full bg-green-100 text-green-700 font-bold py-3 rounded-xl flex justify-center items-center gap-2">
                 <CheckCircle2 size={18} /> Location Verified
               </div>
             ) : (
               <button 
                 onClick={handleDropPin}
                 disabled={isPinning}
                 className="w-2/3 bg-[#38A169] text-white font-bold py-3 rounded-xl shadow-sm active:scale-95 transition-transform text-sm flex justify-center items-center gap-2"
               >
                 {isPinning ? <Loader2 size={16} className="animate-spin"/> : null}
                 {isPinning ? 'Locating...' : 'Pin Your Location'}
               </button>
             )}
          </div>

          {/* Bottom Footer Button */}
          <div className="pt-4 pb-8">
            <button 
              onClick={() => setIsConfirmed(true)}
              className={`w-full font-bold py-4 rounded-xl shadow-md text-lg active:scale-95 transition-all ${isConfirmed ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-[#38A169] text-white'}`}
            >
              {isConfirmed ? 'Order Confirmed' : 'Ready to Receive Order'}
            </button>
          </div>

        </div>

        {/* MODAL: Add Instruction */}
        {showInstructionModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fade-in">
              <div className="flex justify-between items-center p-4 border-b border-gray-100">
                <h3 className="font-bold text-gray-800 text-lg">Add Instruction</h3>
                <button onClick={() => setShowInstructionModal(false)} className="text-gray-400 hover:text-gray-800"><X size={24}/></button>
              </div>
              <div className="p-4">
                {instructionError && (
                  <div className="mb-3 p-3 bg-red-50 text-red-600 text-sm rounded-lg flex items-start gap-2">
                    <AlertCircle size={16} className="mt-0.5 shrink-0" />
                    <p>{instructionError}</p>
                  </div>
                )}
                <textarea 
                  value={instructionText}
                  onChange={(e) => setInstructionText(e.target.value)}
                  placeholder="Leave with the security guard at the main lobby desk..."
                  className="w-full h-32 border border-gray-300 rounded-xl p-3 outline-none focus:border-blue-500 text-gray-700 resize-none"
                />
                <button onClick={submitInstruction} className="w-full mt-4 bg-[#1A202C] text-white font-bold py-3.5 rounded-xl text-sm">
                  Save Instruction
                </button>
              </div>
            </div>
          </div>
        )}

        {/* MODAL: Not Available (Date Picker) */}
        {showDateModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fade-in">
              <div className="flex justify-between items-center p-4 border-b border-gray-100">
                <h3 className="font-bold text-gray-800 text-lg">Available Dates</h3>
                <button onClick={() => setShowDateModal(false)} className="text-gray-400 hover:text-gray-800"><X size={24}/></button>
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-600 mb-4">Please select a date when you will be available to receive the package (Max 5 days ahead).</p>
                <input 
                  type="date" 
                  min={minDateStr}
                  max={maxDateStr}
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full border border-gray-300 rounded-xl p-3 outline-none focus:border-blue-500 text-gray-700"
                />
                <button 
                  onClick={submitUnavailableDate} 
                  disabled={!selectedDate}
                  className="w-full mt-4 bg-[#E53E3E] disabled:bg-[#fc9b9b] text-white font-bold py-3.5 rounded-xl text-sm transition-colors"
                >
                  Confirm Reschedule
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}