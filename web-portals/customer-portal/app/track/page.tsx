'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { MapPin, CheckCircle, XCircle, RefreshCw, Navigation, LocateFixed } from 'lucide-react';

function TrackingContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  // Poll every 30s for ETA and Driver Position
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    const fetchTrackingData = async () => {
      try {
        const res = await fetch(`/api/v1/customer/track?token=${token}`);
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrackingData();
    const interval = setInterval(fetchTrackingData, 30000);
    return () => clearInterval(interval);
  }, [token]);

  // Geo-Pinning - Saves coordinates to backend
  const handleGeoPin = async () => {
    if (!navigator.geolocation) return alert("Geolocation not supported");
    
    setUpdating(true);
    navigator.geolocation.getCurrentPosition(async (pos) => {
      const { latitude, longitude } = pos.coords;
      try {
        await fetch(`/api/v1/customer/update?token=${token}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            pinned_lat: latitude, 
            pinned_lng: longitude,
            customer_status: 'waiting' 
          }),
        });
        alert("Door location pinned successfully!");
        window.location.reload();
      } catch (err) {
        alert("Failed to pin location.");
      } finally {
        setUpdating(false);
      }
    });
  };

  const handleStatusUpdate = async (status: string) => {
    setUpdating(true);
    try {
      await fetch(`/api/v1/customer/update?token=${token}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_status: status }),
      });
      alert(`Status: ${status} updated!`);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <div className="p-10 text-center">Loading live tracker...</div>;
  if (!data) return <div className="p-10 text-center text-red-500">Invalid link.</div>;

  return (
    <div className="max-w-md mx-auto min-h-screen bg-slate-50">
      {/* Google Maps Embed (Driver + Customer) */}
      <div className="w-full h-80 bg-slate-200 relative">
        <iframe
          width="100%"
          height="100%"
          style={{ border: 0 }}
          loading="lazy"
          allowFullScreen
          referrerPolicy="no-referrer-when-downgrade"
          src={`https://www.google.com/maps/embed/v1/directions?key=YOUR_GOOGLE_MAPS_KEY&origin=${data.driver_lat},${data.driver_lng}&destination=${data.pinned_lat || 6.9271},${data.pinned_lng || 79.8612}&mode=driving`}
        ></iframe>
      </div>

      <div className="p-6 -mt-8 relative z-10">
        {/* ETA & Stops Away Display */}
        <div className="bg-white rounded-3xl shadow-xl p-6 mb-4 border border-slate-100">
          <div className="flex justify-between items-center mb-4">
            <div>
              <p className="text-xs font-bold text-blue-600 uppercase">Estimated Arrival</p>
              <h1 className="text-3xl font-black text-slate-900">{data.eta_minutes ?? '--'} mins</h1>
            </div>
            <div className="text-right">
              <p className="text-xs font-bold text-orange-600 uppercase">Live Progress</p>
              <h2 className="text-xl font-bold text-slate-800">{data.stops_remaining ?? '0'} stops away</h2>
            </div>
          </div>
          
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
             <div className="bg-blue-600 h-full transition-all duration-1000" style={{ width: `${Math.max(10, 100 - (data.stops_remaining * 20))}%` }}></div>
          </div>
        </div>

        {/* Geo-Pinning Button */}
        <button 
          onClick={handleGeoPin}
          disabled={updating}
          className="w-full mb-4 flex items-center justify-center gap-2 p-4 bg-white border-2 border-dashed border-blue-400 text-blue-600 rounded-2xl font-bold hover:bg-blue-50 transition"
        >
          <LocateFixed size={20} />
          Pin My Exact Front Door
        </button>

        {/* 🚦 Action Buttons */}
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => handleStatusUpdate('ready')} className="flex flex-col items-center p-4 bg-white border rounded-2xl shadow-sm">
              <CheckCircle className="text-green-500 mb-1" />
              <span className="text-xs font-bold">I'm Ready</span>
            </button>
            <button onClick={() => handleStatusUpdate('not_available')} className="flex flex-col items-center p-4 bg-white border rounded-2xl shadow-sm">
              <XCircle className="text-red-500 mb-1" />
              <span className="text-xs font-bold">Not Available</span>
            </button>
          </div>
          <button onClick={() => handleStatusUpdate('waiting')} className="w-full flex items-center justify-center gap-2 p-4 bg-slate-900 text-white rounded-2xl font-bold">
            <RefreshCw size={18} className={updating ? "animate-spin" : ""} />
            Request Reschedule
          </button>
        </div>
      </div>
    </div>
  );
}

export default function TrackingPage() {
  return (
    <Suspense fallback={<div>Loading Page...</div>}>
      <TrackingContent />
    </Suspense>
  );
}