'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Clock, MapPin, Phone, Loader2 } from 'lucide-react';

export default function TripDetailPage() {
  const { tripId } = useParams();
  const [trip, setTrip] = useState<any>(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [tripRes, taskRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/trips/${tripId}`),
        fetch(`http://localhost:8000/api/v1/tasks?trip_id=${tripId}`)
      ]);
      setTrip(await tripRes.json());
      setTasks(await taskRes.json());
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000); // Every 15s per requirement
    return () => clearInterval(interval);
  }, [tripId]);

  if (loading) return <div className="p-20 text-center"><Loader2 className="animate-spin mx-auto" /></div>;

  return (
    <div className="p-8">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">Trip Details: #{typeof tripId === 'string' ? tripId.slice(0,8) : 'Loading...'}</h1>
        </div>
        <a href="tel:0112345678" className="flex items-center gap-2 px-4 py-2 border rounded hover:bg-gray-50">
          <Phone size={18} /> Call Driver
        </a>
      </div>

      <div className="grid gap-6">
        <h2 className="font-semibold text-lg flex items-center gap-2"><Clock size={20}/> Delivery Timeline</h2>
        {tasks.map((task: any, index: number) => (
          <div key={task.id} className="flex gap-4 items-start">
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${task.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'}`}>
                {index + 1}
              </div>
              {index !== tasks.length - 1 && <div className="w-0.5 h-16 bg-gray-200" />}
            </div>
            <div className="flex-1 p-4 border rounded bg-white shadow-sm">
              <div className="flex justify-between">
                <p className="font-bold">{task.customer_name}</p>
                <span className="text-xs font-bold uppercase">{task.status}</span>
              </div>
              <p className="text-sm text-gray-600 flex items-center gap-1 mt-1"><MapPin size={14}/> {task.address}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}