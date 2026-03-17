'use client';


import Avatar from "@/components/Avatar";


interface Incident {

  id: number;
  driver_id: number;
  driver_name: string;
  type: "accident" | "breakdown" | "other";
  description: string;
  location: string;
  reported_at: string;
  status: "active" | "rescue_assigned" | "resolved";

}

// TODO: Replace with useQuery → GET /api/v1/incidents?status=active (poll every 30s)
const MOCK_INCIDENTS: Incident[] = [
  { id: 1, driver_id: 1, driver_name: 'Saman Kumara', type: 'accident', description: 'Vehicle collision on highway', location: 'Colombo - Kandy Road, Km 42', reported_at: '2026-03-17 09:23', status: 'active' },
  { id: 2, driver_id: 2, driver_name: 'Nimal Perera', type: 'breakdown', description: 'Engine failure, cannot move', location: 'Galle Road, Dehiwala', reported_at: '2026-03-17 10:05', status: 'active' },
  { id: 3, driver_id: 3, driver_name: 'Kasun Jayasuriya', type: 'other', description: 'Package damaged by customer', location: 'Nugegoda Junction', reported_at: '2026-03-17 11:30', status: 'rescue_assigned' },
  { id: 4, driver_id: 4, driver_name: 'Amal Silva', type: 'accident', description: 'Minor collision at junction', location: 'Pettah, Colombo 11', reported_at: '2026-03-17 12:15', status: 'active' },
  { id: 5, driver_id: 5, driver_name: 'Ruwan Hettiarachchi', type: 'breakdown', description: 'Flat tyre, stuck on expressway', location: 'Southern Expressway, Km 18', reported_at: '2026-03-17 13:00', status: 'active' },
];


export default function IncidentsPage() {

  const typeConfig = {
    accident: { label: 'Accident', border: 'border-t-red-500', badge: 'bg-red-500/20 text-red-400' },
    breakdown: { label: 'Breakdown', border: 'border-t-orange-500', badge: 'bg-orange-500/20 text-orange-400' },
    other: { label: 'Other', border: 'border-t-gray-500', badge: 'bg-gray-500/20 text-gray-400' },
  };
  return (
    <div className="p-8">

      {/* Page title */}
      <h1 className="text-3xl font-bold text-white mb-6">Incident Reports</h1>

      {/* Incident cards grid will go here */}
      <div className="grid grid-cols-3 gap-4">
        {MOCK_INCIDENTS.map((incident) => {
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
                  <p className="text-xs text-[#6B7280]">#DRV-00{incident.driver_id}</p>
                </div>
              </div>

              {/* Location */}
              <p className="text-xs text-[#A1A1A1]">📍 {incident.location}</p>

              {/* Description */}
              <p className="text-sm text-[#A1A1A1] line-clamp-2">{incident.description}</p>

              {/* View Details button */}
              <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition-colors mt-auto">
                View Details
              </button>
            </div>
          );
        })};
      </div>

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