'use client';

import { AlertTriangle, Phone, X } from "lucide-react";
import Avatar from "@/components/Avatar";

interface Incidents {

    id: number;
    driver_id: number;
    driver_name: string;
    type: 'accident' | 'breakdown' | 'other';
    description: string;
    location: string;
    reported_at: string;
    status: 'active' | 'rescue_assigned' | 'resolved';
}

interface Props {

    incidents: Incidents;
    onClose: () => void;

}

export default function IncidentsManagementModel({ incidents, onClose }: Props) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="absolute inset-0 bg-black/60" onClick={onClose} />

            <div className="relative z-10 w-full 
                max-w-md mx-4 bg-[#1E1E1E] border border-[#2E2E2E] 
                rounded-2xl shadow-2xl flex flex-col  "
            >
                {/* Header */}
                <div className="flex items-start justify-between px-6 pt-6 pb-5 border-b border-[#2E2E2E]">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-orange-500/20 flex items-center justify-center">
                            <AlertTriangle size={20} className="text-orange-400" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white">
                                Incident Management #{String(incidents.id).padStart(4, '0')}
                            </h2>
                            <p className="text-sm text-[#A1A1A1] mt-0.5">
                                Reported at {incidents.reported_at}
                            </p>
                        </div>
                    </div>

                    {/* Close button */}
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center rounded-full text-[#6B7280] hover:bg-[#252525] transition-colors"
                    >
                        <X size={16} />
                    </button>
                </div>


                {/* Body */}

                <div className="px-6 py-5 space-y-4 overflow-y-auto">

                    <div className="flex items-center justify-between">
                        <Avatar name={incidents.driver_name} size="md" />
                        <div>
                            <p className="font-medium text-white">{incidents.driver_name}</p>
                            <p className="text-xs text-[#6B7280]">#DRV-00{incidents.driver_id}</p>
                        </div>
                    </div>

                    <a href='tel:${incident.phone}'
                        className="flex items-center gap-2 px-4 py-2 bg-[#252525] hover:bg-[#2E2E2E] 
                        text-white text-sm font-medium rounded-lg transition-colors"
                    >
                        <Phone size={14} />
                        Call Driver
                    </a>
                </div>


                {/* Location and Description side by side */}
                <div className="grid grid-cols-2 gap-4 mt-2 mb-2 ml-2 mr-2">

                    {/* Location */}
                    <div className="bg-gradient-to-br from-[#1a1a1a] to-[#141414] rounded-lg p-3 border border-[#2E2E2E]">
                        <p className="text-xs font-semibold uppercase tracking-widest text-[#6B7280] mb-1">Location</p>
                        <p className="text-sm text-white">📍 {incidents.location}</p>
                    </div>

                    {/* Description */}
                    <div className="bg-gradient-to-br from-[#1a1a1a] to-[#141414] rounded-lg p-3 border border-[#2E2E2E]">
                        <p className="text-xs font-semibold uppercase tracking-widest text-[#6B7280] mb-1">Description</p>
                        <p className="text-sm text-white">{incidents.description}</p>
                    </div>

                    

                 

                </div>

                <div className="border border-[#2E2E2E] rounded-lg p-4 space-y-3">

                    {/* Rescue & Recovery */}
                    <div className="border border-[#2E2E2E] rounded-lg p-4 space-y-3">
                        <p className="text-sm font-semibold text-white">🚨 Rescue & Recovery</p>

                        {/* Dropdown full width */}
                        <select className="w-full px-4 py-2.5 bg-[#121212] text-white text-sm rounded-lg border border-[#2E2E2E] outline-none focus:border-blue-600 transition-colors">
                            <option value="">Select rescue driver...</option>
                            <option value="1">Kasun Jayasuriya — Available</option>
                            <option value="2">Amal Silva — Available</option>
                        </select>

                        {/* Dispatch button full width */}
                        {/* TODO: wire to PATCH /api/v1/incidents/{id}/assign-rescue */}
                        <button className="w-full py-2.5 bg-[#121212] hover:bg-[#252525] border border-[#2E2E2E] text-white text-sm font-semibold rounded-lg transition-colors">
                            Dispatch Rescue Team
                        </button>
                    </div>

                </div>

                
                {/* Footer */}
                <div className="flex items-center justify-between px-6 py-4 border-t border-[#2E2E2E]">
                    <button
                        onClick={onClose}
                        className="px-5 py-2.5 text-sm font-medium text-[#A1A1A1] hover:bg-[#252525] rounded-lg transition-colors"
                    >
                        Close
                    </button>

                    {/* TODO: wire to PATCH /api/v1/incidents/{id}/resolve Body: { resolution_notes: str } */}
                    <button className="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold rounded-lg transition-colors">
                        ✓ Mark as Resolved
                    </button>
                </div>
                
            </div>

        </div>
    );
}