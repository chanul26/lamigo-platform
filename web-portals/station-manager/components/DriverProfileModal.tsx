'use client';

import { X, User, Phone, MapPin, Car, Wallet, Lock, Edit } from 'lucide-react';
import type { DriverResponse } from '@/types';

interface DriverProfileModalProps {
  driver: DriverResponse;
  onClose: () => void;
}

export default function DriverProfileModal({ driver, onClose }: DriverProfileModalProps) {
  
  // We will wire up the actual edit/password logic in Phase 4 if needed, 
  // for now, we build the exact UI from Page 19.
  const handleEdit = () => alert("Edit driver functionality coming soon.");
  const handleChangePassword = () => alert("Password reset functionality coming soon.");
  const handleLogout = () => alert("Force logout functionality coming soon.");

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col">
        
        {/* HEADER */}
        <div className="bg-[#1A1A1A] p-6 border-b border-[#2E2E2E] flex justify-between items-start relative">
          <div className="flex gap-4 items-center">
            {/* Initials Avatar */}
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold shadow-md">
              {driver.full_name.split(' ').map(n => n[0]).join('').substring(0,2).toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{driver.full_name}</h2>
              <p className="text-sm font-mono text-gray-400">#DRV-{driver.uid.substring(0,6).toUpperCase()}</p>
              <div className="mt-1 flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${driver.status === 'AVAILABLE' ? 'bg-green-500' : driver.status === 'OFF_DUTY' ? 'bg-gray-500' : 'bg-blue-500'}`}></span>
                <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">{driver.status.replace(/_/g, ' ')}</span>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors absolute top-4 right-4">
            <X size={24} />
          </button>
        </div>

        {/* BODY - DATA GRID */}
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-6">
            
            <div>
              <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 flex items-center gap-1"><Car size={12}/> Vehicle</p>
              <p className="text-sm text-white font-medium">{driver.vehicle_type.replace(/_/g, ' ')}</p>
              <p className="text-xs text-gray-400 mt-0.5">{driver.vehicle_number}</p>
            </div>

            <div>
              <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 flex items-center gap-1"><User size={12}/> NIC NO</p>
              <p className="text-sm font-mono text-white">{driver.nic_number}</p>
            </div>

            <div>
              <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 flex items-center gap-1"><Phone size={12}/> Contact</p>
              <button className="text-sm text-blue-400 hover:underline flex items-center gap-1">Call {driver.phone_number}</button>
            </div>

            <div>
               <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 flex items-center gap-1"><Wallet size={12}/> Wallet Balance</p>
               <p className="text-lg font-bold text-green-400">LKR {Number(driver.wallet_balance).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
            </div>

          </div>

          <div className="border-t border-[#2E2E2E] pt-4">
            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 flex items-center gap-1"><MapPin size={12}/> Address</p>
            <p className="text-sm text-gray-300">No 15, Temple Rd, Colombo (Placeholder)</p> 
            {/* Note: In a real app, address would be added to the Driver model if strictly needed */}
          </div>
        </div>

        {/* FOOTER ACTIONS */}
        <div className="bg-[#1A1A1A] p-4 border-t border-[#2E2E2E] flex flex-col gap-2">
          <button onClick={handleEdit} className="w-full py-2.5 bg-[#2E2E2E] hover:bg-[#3E3E3E] text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2 transition-colors border border-[#3E3E3E]">
            <Edit size={16} /> Edit Details
          </button>
          <div className="flex gap-2">
            <button onClick={handleChangePassword} className="flex-1 py-2.5 bg-[#2E2E2E] hover:bg-[#3E3E3E] text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2 transition-colors border border-[#3E3E3E]">
              <Lock size={16} /> Change Password
            </button>
            <button onClick={handleLogout} className="flex-1 py-2.5 bg-red-900/20 hover:bg-red-900/40 text-red-400 text-sm font-medium rounded-lg transition-colors border border-red-900/50">
              Logout Driver
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}