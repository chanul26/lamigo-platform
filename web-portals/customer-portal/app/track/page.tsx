'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { MapPin, CheckCircle, XCircle, RefreshCw, Loader2 } from 'lucide-react';

function TrackingContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

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

  const handleUpdate = async (status: string) => {
    setUpdating(true);
    try {
      await fetch(`/api/v1/customer/update?token=${token}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_status: status }),
      });
      alert("Status updated!");
    } catch (err) {
      alert("Update failed.");
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <div className="p-10 text-center text-slate-500">Connecting to LamiGo...</div>;
  if (!data) return <div className="p-10 text-center text-red-500">Link expired or invalid.</div>;

  return (
    <div className="max-w-md mx-auto min-h-screen bg-slate-50 p-6">
      <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg mb-6">
        <h1 className="text-xl font-bold">Arriving in {data.eta_minutes ?? '--'} mins</h1>
        <p className="text-sm opacity-80">Package: {data.package_id}</p>
      </div>

      <div className="space-y-4">
        <button 
          onClick={() => handleUpdate('ready')}
          className="w-full flex items-center justify-between p-4 bg-white border rounded-xl shadow-sm hover:bg-green-50"
        >
          <span className="font-bold text-slate-700">Ready to Receive</span>
          <CheckCircle className="text-green-500" />
        </button>

        <button 
          onClick={() => handleUpdate('not_available')}
          className="w-full flex items-center justify-between p-4 bg-white border rounded-xl shadow-sm hover:bg-red-50"
        >
          <span className="font-bold text-slate-700">Not Available Today</span>
          <XCircle className="text-red-500" />
        </button>

        <button 
          onClick={() => handleUpdate('waiting')}
          className="w-full flex items-center justify-center gap-2 p-4 bg-orange-500 text-white rounded-xl shadow-md font-bold"
        >
          <RefreshCw size={18} />
          Request Return-Trip
        </button>
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