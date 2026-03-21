'use client';

import { ArrowLeft, Hash, Calendar, User, Tag, FileText } from "lucide-react";
import Avatar from "@/components/Avatar";


interface ResolvedIncident {
    id: string;
    driver_id: string;
    driver_name: string;
    type: 'ACCIDENT' | 'VEHICLE_BREAKDOWN' | 'TRAFFIC_POLICE' | 'MEDICAL_EMERGENCY' | 'OTHER';
    description: string;
    resolved_at: string;
    trip_id: string;
}

// TODO: Replace with useQuery → GET /api/v1/incidents?status=resolved when Heshadha delivers incidents.py
const MOCK_RESOLVED: ResolvedIncident[] = [
  { id: 'f1225531-a94d-48ac-958f-d94622015b64', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl2', driver_name: 'Saman Kumara',        type: 'ACCIDENT',          description: 'Vehicle collision on highway',   resolved_at: '2026-03-10 14:30', trip_id: 'TRP-001' },
  { id: 'f1225531-a94d-48ac-958f-d94622015b65', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl3', driver_name: 'Nimal Perera',        type: 'VEHICLE_BREAKDOWN', description: 'Engine failure, cannot move',     resolved_at: '2026-03-11 10:15', trip_id: 'TRP-002' },
  { id: 'f1225531-a94d-48ac-958f-d94622015b66', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl4', driver_name: 'Kasun Jayasuriya',    type: 'OTHER',             description: 'Package damaged by customer',    resolved_at: '2026-03-12 09:45', trip_id: 'TRP-003' },
  { id: 'f1225531-a94d-48ac-958f-d94622015b67', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl5', driver_name: 'Amal Silva',          type: 'ACCIDENT',          description: 'Minor collision at junction',    resolved_at: '2026-03-13 16:00', trip_id: 'TRP-004' },
  { id: 'f1225531-a94d-48ac-958f-d94622015b68', driver_id: 'uC2V93X7znQOfrHxtAOt8WkIVFl6', driver_name: 'Ruwan Hettiarachchi', type: 'VEHICLE_BREAKDOWN', description: 'Flat tyre, stuck on expressway', resolved_at: '2026-03-14 11:30', trip_id: 'TRP-005' },
];


export default function ResolvedIncidentsPage() {
    return (
        <div className="p-8">

            {/* Back link */}

            <a href="/incidents"
                className="flex items-center gap-2 text-sm text-[#A1A1A1] hover:text-white transition-colors mb-6"
            >
                <ArrowLeft size={16} />
                Back to Incidents
            </a>

            {/* Page title */}
            <h1 className="text-3xl font-bold text-white mb-6">Resolved Incidents</h1>

            {/* Table card will go here */}
            <div className="bg-[#1E1E1E] rounded-xl border border-[#2E2E2E] overflow-hidden">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-[#2E2E2E]">
                            <th className="text-left px-6 py-4 text-xs 
                                font-semibold text-[#6B7280] 
                                uppercase tracking-widest"
                            >
                                <div className="flex item-center gap-2">
                                    <Hash size={14} />
                                    Incident ID
                                </div>
                                
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <Calendar size={14} />
                                    Resolved At
                                </div>
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <User size={14} />
                                    Driver
                                </div>
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <Tag size={14} />
                                    Category
                                </div>
                            </th>

                            <th className="text-left px-6 py-4 text-xs font-semibold text-[#6B7280] uppercase tracking-widest">
                                <div className="flex items-center gap-2">
                                    <FileText size={14} />
                                    Description
                                </div>
                            </th>

                        </tr>

                    </thead>

                    <tbody>
                        {MOCK_RESOLVED.map((incident, i) => {
                            const isLast = i === MOCK_RESOLVED.length - 1;

                            const typeConfig = {
                                ACCIDENT: { label: 'Accident', badge: 'bg-red-500/20 text-red-400' },
                                VEHICLE_BREAKDOWN: { label: 'Breakdown', badge: 'bg-orange-500/20 text-orange-400' },
                                TRAFFIC_POLICE: { label: 'Traffic Police', badge: 'bg-blue-500/20 text-blue-400' },
                                MEDICAL_EMERGENCY: { label: 'Medical Emergency', badge: 'bg-pink-500/20 text-pink-400' },
                                OTHER: { label: 'Other', badge: 'bg-gray-500/20 text-gray-400' },
                            };

                            const config = typeConfig[incident.type];

                            return (
                                <tr
                                    key={incident.id}
                                    className={`hover:bg-[#252525] transition-colors ${!isLast ? 'border-b border-[#2E2E2E]' : ''}`}
                                >
                                    {/* Incident ID */}
                                    <td className="px-6 py-4 text-[#A1A1A1] font-mono">
                                        #INC-{String(incident.id).padStart(4, '0')}
                                    </td>

                                    {/* Resolved At */}
                                    <td className="px-6 py-4 text-[#A1A1A1]">
                                        {incident.resolved_at}
                                    </td>

                                    {/* Driver */}
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <Avatar name={incident.driver_name} size="sm" />
                                            <div>
                                                <p className="font-medium text-white">{incident.driver_name}</p>
                                                <p className="text-xs text-[#6B7280]">{incident.driver_id.substring(0, 8)}</p>
                                            </div>
                                        </div>
                                    </td>

                                    {/* Category badge */}
                                    <td className="px-6 py-4">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.badge}`}>
                                            {config.label}
                                        </span>
                                    </td>

                                    {/* Description */}
                                    <td className="px-6 py-4 text-[#A1A1A1] max-w-[200px] truncate">
                                        {incident.description}
                                    </td>

                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

        </div>
    );

}