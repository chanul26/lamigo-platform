'use client';

import { useQuery } from '@tanstack/react-query';
import { Loader2, ArrowLeft, Map, CheckCircle2, XCircle, Clock, Navigation, Banknote, Phone } from 'lucide-react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { apiClient } from '@/lib/api';
import type { TripResponse, TaskResponse, PackageResponse, DriverResponse } from '@/types';

export default function TripDetailsPage() {
  const params = useParams();
  const tripId = params.id as string;

  // 1. Fetch Trip Data
  const { data: trip, isLoading: loadingTrip, isError: errorTrip } = useQuery<TripResponse>({
    queryKey: ['trip', tripId],
    queryFn: () => apiClient.getTrip(tripId),
  });

  // 2. Fetch Tasks (The Delivery Sequence)
  const { data: tasks = [], isLoading: loadingTasks } = useQuery<TaskResponse[]>({
    queryKey: ['tasks', tripId],
    queryFn: () => apiClient.getTasks(tripId),
  });

  // 3. Fetch Packages (To get addresses and COD amounts)
  const { data: packages = [] } = useQuery<PackageResponse[]>({
    queryKey: ['packages'],
    queryFn: apiClient.getPackages,
  });

  // 4. Fetch Drivers (To get driver name)
  const { data: drivers = [] } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers,
  });

  if (loadingTrip || loadingTasks) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin text-blue-500 w-10 h-10" /></div>;
  if (errorTrip || !trip) return <div className="p-8 text-red-500">Failed to load trip details.</div>;

  const driver = drivers.find(d => d.uid === trip.driver_id);
  const isCompleted = trip.status === 'COMPLETED' || trip.status === 'CANCELLED';

  const getTaskStatusUI = (status: string) => {
    switch(status) {
      case 'COMPLETED': return <span className="flex items-center gap-1 text-green-400 text-xs font-bold uppercase"><CheckCircle2 size={14}/> Delivered</span>;
      case 'FAILED': return <span className="flex items-center gap-1 text-red-400 text-xs font-bold uppercase"><XCircle size={14}/> Failed</span>;
      case 'DELIVERING_NOW': return <span className="flex items-center gap-1 text-yellow-400 text-xs font-bold uppercase"><Navigation size={14}/> Next Stop</span>;
      default: return <span className="flex items-center gap-1 text-gray-500 text-xs font-bold uppercase"><Clock size={14}/> Pending</span>;
    }
  };

  return (
    <div className="p-8 animate-fade-in max-w-6xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link href="/trips" className="inline-flex items-center gap-2 text-sm mb-4 hover:underline text-gray-400 hover:text-white">
            <ArrowLeft size={16} /> Back to Trips
          </Link>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            Trip #TR-{trip.trip_id.substring(0, 8).toUpperCase()}
            <span className={`px-3 py-1 text-xs font-bold uppercase tracking-wider rounded ${isCompleted ? 'bg-green-900/40 text-green-400' : 'bg-blue-900/40 text-blue-400'}`}>
              {trip.status.replace(/_/g, ' ')}
            </span>
          </h1>
          <p className="text-gray-400 mt-2">
            {trip.actual_start_time ? `Started ${new Date(trip.actual_start_time).toLocaleString()}` : 'Not started yet'}
            {trip.actual_return_time && ` • Ended ${new Date(trip.actual_return_time).toLocaleString()}`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT COLUMN: Delivery Sequence Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
            <h2 className="font-semibold text-white mb-6 border-b border-[#2E2E2E] pb-4 flex items-center gap-2">
              <Map className="text-blue-400" size={20}/> Delivery Sequence
            </h2>
            
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[#2E2E2E] before:to-transparent">
              {tasks.map((task, index) => {
                const pkg = packages.find(p => p.package_id === task.package_id);
                return (
                  <div key={task.task_id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-[#1E1E1E] bg-[#2E2E2E] text-gray-400 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow">
                      {index + 1}
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-[#121212] p-4 rounded-lg border border-[#2E2E2E] shadow-sm">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-mono text-xs text-gray-500">PKG-{task.package_id.substring(0,6).toUpperCase()}</span>
                        {getTaskStatusUI(task.status)}
                      </div>
                      <p className="text-gray-300 text-sm font-medium mb-1">{pkg?.address || 'Loading address...'}</p>
                      {pkg?.is_cod && (
                        <p className="text-xs text-green-400 font-medium">COD: LKR {pkg.cod_amount}</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {tasks.length === 0 && (
              <p className="text-center text-gray-500 py-8">No tasks assigned to this trip.</p>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Driver & Finances */}
        <div className="space-y-6">
          
          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
             <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 border-b border-[#2E2E2E] pb-2">Assigned Driver</h2>
             {driver ? (
               <div>
                 <p className="text-white font-medium text-lg flex items-center gap-2">{driver.full_name} <span className="text-xs bg-[#2E2E2E] px-2 py-0.5 rounded text-gray-400">{driver.vehicle_type}</span></p>
                 <p className="text-gray-400 text-sm flex items-center gap-2 mt-2">
                   <Phone size={14}/> {driver.phone_number}
                 </p>
               </div>
             ) : (
               <p className="text-gray-500 italic">No driver assigned (Draft)</p>
             )}
          </div>

          <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm">
            <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 border-b border-[#2E2E2E] pb-2 flex items-center gap-2">
              <Banknote size={16}/> Trip Finances
            </h2>
            <div className="space-y-4 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Packages</span>
                <span className="text-white font-medium">{trip.total_tasks_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Successful Deliveries</span>
                <span className="text-green-400 font-medium">{trip.delivered_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Total Weight</span>
                <span className="text-white font-medium">{trip.total_weight} KG</span>
              </div>
              <div className="flex justify-between pt-4 border-t border-[#2E2E2E]">
                <span className="text-gray-300 font-medium">Total COD Expected</span>
                <span className="font-bold text-blue-400">
                  LKR {trip.total_cod_to_collect}
                </span>
              </div>
            </div>
          </div>
          
        </div>

      </div>
    </div>
  );
}