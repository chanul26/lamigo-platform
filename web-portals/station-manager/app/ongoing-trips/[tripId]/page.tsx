'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { MapPin, CheckCircle2, Circle, Loader2, ChevronLeft, Navigation } from 'lucide-react';
import Link from 'next/link';

interface Task {
  id: string;
  sequence_number: number;
  status: 'pending' | 'in_progress' | 'completed';
  address: string;
  package_id: string;
}

export default function TripDetailPage() {
  const { tripId } = useParams();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDetails = async () => {
    try {
      const token = localStorage.getItem("token");
      // GET /api/v1/tasks?trip_id={tripId}
      const res = await fetch(`http://localhost:8000/api/v1/tasks?trip_id=${tripId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      // Ordered stop list by sequence_number
      const sorted = data.sort((a: Task, b: Task) => a.sequence_number - b.sequence_number);
      setTasks(sorted);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
    // Poll every 15s for live updates
    const interval = setInterval(fetchDetails, 15000);
    return () => clearInterval(interval);
  }, [tripId]);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <Link href="/ongoing-trips" className="flex items-center gap-2 text-sm text-[var(--text-muted)] mb-6 hover:text-[var(--primary-blue)] transition-colors font-medium">
        <ChevronLeft size={16} /> Back to Live Monitor
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Timeline Column */}
        <div className="lg:col-span-4 bg-[var(--card-bg)] p-6 rounded-xl border border-[var(--border-color)] shadow-sm">
          <h2 className="text-lg font-bold mb-8 flex items-center gap-2">
            <Navigation size={20} className="text-[var(--primary-blue)]" /> Route Stop Timeline
          </h2>
          
          <div className="space-y-0 relative">
            {tasks.map((task, idx) => (
              <div key={task.id} className="relative pl-8 pb-10 last:pb-0">
                {/* Vertical Line */}
                {idx !== tasks.length - 1 && (
                  <div className="absolute left-[11px] top-6 w-[2px] h-[calc(100%-12px)] bg-gray-100" />
                )}
                
                {/* Status Icon */}
                <div className="absolute left-0 top-1 z-10 bg-[var(--card-bg)]">
                  {task.status === 'completed' ? (
                    <CheckCircle2 size={24} className="text-emerald-500" />
                  ) : task.status === 'in_progress' ? (
                    <div className="w-6 h-6 rounded-full border-4 border-[var(--primary-blue)] animate-pulse bg-white" />
                  ) : (
                    <Circle size={24} className="text-gray-300" />
                  )}
                </div>

                <div>
                  <p className="font-bold text-sm text-[var(--text-primary)]">Stop {task.sequence_number + 1}</p>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">{task.address}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-[10px] bg-gray-100 px-2 py-1 rounded font-bold text-gray-500 uppercase tracking-tight">
                      PKG: {task.package_id}
                    </span>
                    {task.status === 'in_progress' && (
                      <span className="text-[10px] bg-blue-50 text-[var(--primary-blue)] px-2 py-1 rounded font-bold uppercase animate-pulse">
                        Driver Arriving
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Map Column */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-[var(--card-bg)] rounded-xl border border-[var(--border-color)] h-[600px] shadow-sm relative overflow-hidden flex flex-col items-center justify-center text-[var(--text-muted)] bg-gray-50">
             <div className="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-full border border-[var(--border-color)] text-[10px] font-bold flex items-center gap-2 z-20 shadow-sm">
               <div className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" /> LIVE GPS FEED (15S POLL)
             </div>
             <MapPin size={48} className="opacity-10 mb-4" />
             <p className="font-medium">Map Visualization Integration Pending</p>
             <p className="text-xs">Driver location updates every 15 seconds</p>
          </div>
        </div>
      </div>
    </div>
  );
}