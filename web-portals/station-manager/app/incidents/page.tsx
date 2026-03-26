'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, AlertCircle, AlertTriangle, CheckCircle2, MapPin } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { IncidentResponse, DriverResponse, IncidentStatus } from '@/types';

export default function IncidentsPage() {
  const queryClient = useQueryClient();

  const { data: incidents = [], isLoading: loadingIncidents } = useQuery<IncidentResponse[]>({
    queryKey: ['incidents'],
    queryFn: apiClient.getIncidents
  });

  const { data: drivers = [] } = useQuery<DriverResponse[]>({
    queryKey: ['drivers'],
    queryFn: apiClient.getDrivers
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string, status: IncidentStatus }) => apiClient.updateIncident(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
    }
  });

  const getDriverName = (driverId: string) => {
    const driver = drivers.find(d => d.uid === driverId);
    return driver ? driver.full_name : 'Unknown Driver';
  };

  // Filter for ONLY active incidents (Reported or Investigating)
  const activeIncidents = incidents.filter(i => i.status !== 'RESOLVED');

  if (loadingIncidents) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin text-red-500 w-10 h-10" /></div>;

  return (
    <div className="p-8 animate-fade-in max-w-7xl">
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-red-900/30 rounded-lg">
              <AlertTriangle size={24} className="text-red-500" />
            </div>
            <h1 className="text-2xl font-semibold text-white">Incident Reports</h1>
          </div>
          <p className="text-gray-400">Live command center for active driver emergencies and disruptions.</p>
        </div>
        <Link 
          href="/incidents/history" 
          className="px-4 py-2 bg-[#2E2E2E] hover:bg-[#3E3E3E] text-white rounded-md text-sm font-medium transition-colors"
        >
          View Past Resolved Incidents &rarr;
        </Link>
      </div>

      {activeIncidents.length === 0 ? (
        <div className="bg-green-900/10 border border-green-500/20 rounded-xl p-12 text-center">
          <CheckCircle2 size={48} className="text-green-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-green-400 mb-1">All Clear</h3>
          <p className="text-gray-500">There are no active incidents in your branch right now.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {activeIncidents.map(incident => (
            <div key={incident.incident_id} className="bg-[#1E1E1E] border border-red-900/50 rounded-xl overflow-hidden shadow-lg flex flex-col">
              <div className="bg-red-900/20 p-4 border-b border-red-900/30 flex justify-between items-start">
                <div>
                  <span className="px-2.5 py-1 bg-red-500 text-white text-[10px] font-bold tracking-wider rounded uppercase">
                    {incident.type.replace('_', ' ')}
                  </span>
                  <h3 className="text-white font-semibold mt-3 text-lg">{getDriverName(incident.driver_id)}</h3>
                  <p className="text-xs text-gray-500 mt-1 font-mono">Trip: {incident.trip_id.substring(0, 8).toUpperCase()}</p>
                </div>
                <span className="text-xs text-red-400 font-medium px-2 py-1 bg-red-900/40 rounded">
                  {incident.status}
                </span>
              </div>
              
              <div className="p-5 flex-1 space-y-4">
                <div className="flex items-start gap-3 text-sm text-gray-300">
                  <MapPin size={16} className="text-gray-500 mt-0.5 shrink-0" />
                  <p>GPS: {incident.reported_at_lat}, {incident.reported_at_lng}<br/><span className="text-xs text-gray-500">Location approximation pending</span></p>
                </div>
                <div className="text-sm bg-[#121212] p-3 rounded text-gray-400 italic">
                  "{incident.description || 'No description provided by driver.'}"
                </div>
              </div>

              <div className="p-4 border-t border-[#2E2E2E] bg-[#1A1A1A]">
                <button
                  onClick={() => updateMutation.mutate({ id: incident.incident_id, status: 'RESOLVED' })}
                  disabled={updateMutation.isPending}
                  className="w-full py-2.5 bg-[#2E2E2E] hover:bg-green-600 hover:text-white text-gray-300 rounded-lg text-sm font-medium transition-all flex justify-center items-center gap-2"
                >
                  {updateMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
                  Mark Incident as Resolved
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}