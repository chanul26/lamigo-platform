'use client';

import { useQuery } from '@tanstack/react-query';
import { Package, Route, Banknote, Plus, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import type { PackageResponse, TripResponse, FinancialProfileResponse } from '@/types';

export default function DashboardPage() {
  // Fetch all required data in parallel
  const { data: packages = [], isLoading: loadingPkgs, isError: errorPkgs } = useQuery<PackageResponse[]>({
    queryKey: ['packages'],
    queryFn: apiClient.getPackages
  });

  const { data: trips = [], isLoading: loadingTrips, isError: errorTrips } = useQuery<TripResponse[]>({
    queryKey: ['trips'],
    queryFn: apiClient.getTrips
  });

  const { data: financials = [], isLoading: loadingFins, isError: errorFins } = useQuery<FinancialProfileResponse[]>({
    queryKey: ['financial-profiles'],
    queryFn: apiClient.getFinancialProfiles
  });

  const isLoading = loadingPkgs || loadingTrips || loadingFins;
  const isError = errorPkgs || errorTrips || errorFins;

  // Calculate Dashboard Metrics
  const pendingDeliveriesCount = packages.filter(p => p.status === 'TO_BE_DELIVERED').length;
  const activeTripsCount = trips.filter(t => t.status === 'IN_PROGRESS').length;
  const pendingSettlementsTotal = financials.reduce((sum, profile) => sum + Number(profile.current_payable_balance), 0);

  if (isLoading) return <div className="flex justify-center items-center h-screen"><Loader2 className="animate-spin text-blue-500 w-10 h-10" /></div>;
  if (isError) return <div className="p-8 text-red-500 flex items-center gap-2"><AlertCircle /> Failed to load dashboard metrics.</div>;

  return (
    <div className="p-8 animate-fade-in max-w-7xl">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome to LamiGo Logistics</h1>
        <p className="text-gray-400">Here is the real-time operational overview for your branch.</p>
      </div>

      {/* METRICS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* Metric 1 */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm flex flex-col justify-between relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-5">
            <Package size={100} />
          </div>
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-900/30 rounded-lg"><Package size={20} className="text-blue-400" /></div>
              <h2 className="text-gray-400 font-medium">Pending Deliveries</h2>
            </div>
            <p className="text-4xl font-bold text-white">{pendingDeliveriesCount}</p>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm flex flex-col justify-between relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-5">
            <Route size={100} />
          </div>
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-green-900/30 rounded-lg"><Route size={20} className="text-green-400" /></div>
              <h2 className="text-gray-400 font-medium">Active Trips</h2>
            </div>
            <p className="text-4xl font-bold text-white">{activeTripsCount}</p>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-[#1E1E1E] border border-[#2E2E2E] rounded-xl p-6 shadow-sm flex flex-col justify-between relative overflow-hidden">
          <div className="absolute -right-4 -top-4 opacity-5">
            <Banknote size={100} />
          </div>
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-yellow-900/30 rounded-lg"><Banknote size={20} className="text-yellow-400" /></div>
              <h2 className="text-gray-400 font-medium">Pending Settlements</h2>
            </div>
            <p className="text-4xl font-bold text-white">LKR {pendingSettlementsTotal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          </div>
        </div>
      </div>

      {/* QUICK ACTIONS */}
      <h2 className="text-xl font-bold text-white mb-6">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/trips/new" className="group bg-[#1A1A1A] border border-[#2E2E2E] hover:border-blue-500/50 rounded-xl p-6 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-600 rounded-full text-white"><Plus size={20} /></div>
            <ArrowRight size={20} className="text-gray-600 group-hover:text-blue-400 transition-colors" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Create New Trip</h3>
          <p className="text-sm text-gray-500">Batch pending packages and assign a driver.</p>
        </Link>

        <Link href="/packages/new" className="group bg-[#1A1A1A] border border-[#2E2E2E] hover:border-green-500/50 rounded-xl p-6 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-600 rounded-full text-white"><Package size={20} /></div>
            <ArrowRight size={20} className="text-gray-600 group-hover:text-green-400 transition-colors" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Add New Package</h3>
          <p className="text-sm text-gray-500">Manually insert a new package into inventory.</p>
        </Link>

        <Link href="/settlements" className="group bg-[#1A1A1A] border border-[#2E2E2E] hover:border-yellow-500/50 rounded-xl p-6 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-yellow-600 rounded-full text-white"><Banknote size={20} /></div>
            <ArrowRight size={20} className="text-gray-600 group-hover:text-yellow-400 transition-colors" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-1">Process Settlements</h3>
          <p className="text-sm text-gray-500">Clear outstanding balances with your drivers.</p>
        </Link>
      </div>
    </div>
  );
}