'use client';

import { AlertTriangle, X } from "lucide-react";

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

            <div className="relative z-10 w-full max-w-2xl 
                mx-4 bg-[#1E1E1E] border border-[#2E2E2E] 
                rounded-2xl shadow-2xl flex flex-col"
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
            </div>

        </div>
    );
}