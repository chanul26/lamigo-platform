'use client';


import Avatar from "@/components/Avatar";
import { useState } from 'react';
import IncidentManagementModal from '@/components/IncidentsManagementModel';

interface Incident {

  id: string;
  driver_id: string;
  driver_name: string;
  phone: string;
  type: "ACCIDENT" | "VEHICLE_BREAKDOWN" | "OTHER";
  description: string;
  location: string;
  reported_at: string;
  status: "REPORTED" | "INVESTIGATING" | "RESOLVED";

}

// TODO: Replace with useQuery → GET /api/v1/incidents?status=active (poll every 30s)
const MOCK_INCIDENTS: Incident[] = [
  { id: 'f1225531-a94d-48ac-958f-d94622015b64', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl2', driver_name: 'Saman Kumara',        phone: '+94771234561', type: 'ACCIDENT',           description: 'Vehicle collision on highway',   location: 'Colombo - Kandy Road, Km 42', reported_at: '2026-03-17 09:23', status: 'REPORTED'     },
  { id: 'f1225531-a94d-48ac-958f-d94622015b65', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl3', driver_name: 'Nimal Perera',        phone: '+94771234562', type: 'VEHICLE_BREAKDOWN',  description: 'Engine failure, cannot move',    location: 'Galle Road, Dehiwala',        reported_at: '2026-03-17 10:05', status: 'REPORTED'     },
  { id: 'f1225531-a94d-48ac-958f-d94622015b66', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl4', driver_name: 'Kasun Jayasuriya',    phone: '+94771234563', type: 'OTHER',              description: 'Package damaged by customer',   location: 'Nugegoda Junction',           reported_at: '2026-03-17 11:30', status: 'INVESTIGATING'},
  { id: 'f1225531-a94d-48ac-958f-d94622015b67', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl5', driver_name: 'Amal Silva',          phone: '+94771234564', type: 'ACCIDENT',           description: 'Minor collision at junction',   location: 'Pettah, Colombo 11',          reported_at: '2026-03-17 12:15', status: 'REPORTED'     },
  { id: 'f1225531-a94d-48ac-958f-d94622015b68', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl6', driver_name: 'Ruwan Hettiarachchi', phone: '+94771234565', type: 'VEHICLE_BREAKDOWN',  description: 'Flat tyre, stuck on expressway', location: 'Southern Expressway, Km 18', reported_at: '2026-03-17 13:00', status: 'REPORTED'     },
];


export default function IncidentsPage() {

  const [incidents, setIncidents] = useState<Incident[]>(MOCK_INCIDENTS);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);


  const typeConfig = {
  ACCIDENT:           { label: 'Accident',           border: 'border-t-red-500',    badge: 'bg-red-500/20 text-red-400'       },
  VEHICLE_BREAKDOWN:  { label: 'Breakdown',          border: 'border-t-orange-500', badge: 'bg-orange-500/20 text-orange-400' },
  TRAFFIC_POLICE:     { label: 'Traffic Police',     border: 'border-t-blue-500',   badge: 'bg-blue-500/20 text-blue-400'     },
  MEDICAL_EMERGENCY:  { label: 'Medical Emergency',  border: 'border-t-pink-500',   badge: 'bg-pink-500/20 text-pink-400'     },
  OTHER:              { label: 'Other',              border: 'border-t-gray-500',   badge: 'bg-gray-500/20 text-gray-400'     },
  };

  function handleResolve(incidentId: string) {
    setIncidents((prev) => prev.filter((i) => i.id !== incidentId));
    setSelectedIncident(null);
  }


  return (
    <div className="p-8">

      {/* Page title */}
      <h1 className="text-3xl font-bold text-white mb-6">Incident Reports</h1>

      {/* Incident cards grid will go here */}
      <div className="grid grid-cols-3 gap-4">
        {incidents.map((incident) => {
          const config = typeConfig[incident.type];
          return (
            <div
              key={incident.id}
              className={`bg-[#1E1E1E] border border-[#2E2E2E] border-t-4 ${config.border} rounded-xl p-5 flex flex-col gap-4`}
            >

              <span className={`self-start px-3 py-1 rounded-full text-xs font-semibold ${config.badge}`}>
                {config.label}
              </span>

              {/* Driver info */}
              <div className="flex items-center gap-3">
                <Avatar name={incident.driver_name} size="md" />
                <div>
                  <p className="font-medium text-white">{incident.driver_name}</p>
                  <p className="text-xs text-[#6B7280]">{incident.driver_id.substring(0, 8)}</p>
                </div>
              </div>

              {/* Location */}
              <p className="text-xs text-[#A1A1A1]">📍 {incident.location}</p>

              {/* Description */}
              <p className="text-sm text-[#A1A1A1] line-clamp-2">{incident.description}</p>

              {/* View Details button */}
              <button 
                onClick={() => setSelectedIncident(incident)}
                className="w-full py-2 bg-blue-600 
                hover:bg-blue-700 text-white text-sm font-semibold 
                rounded-lg transition-colors mt-auto"
              >
                View Details
              </button>
            </div>
          );
        })}
        
      </div>

      {selectedIncident && (
          <IncidentManagementModal
            incidents={selectedIncident}
            onResolve={handleResolve}
            onClose={() => setSelectedIncident(null)}
          />
      )}

      {/* View Past Resolved Incidents button will go here */}
      <div className="mt-6">
        <a 
        href="/incidents/resolved"
        className="w-full flex items-center justify-center py-3 
          text-sm font-medium rounded-lg border border-blue-600
          text-blue-500 hover:bg-blue-600/10 transition-colors"
        >
          View Past Resolved Incidents
        </a>
      </div>

    </div>
  );
}