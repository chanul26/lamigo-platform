'use client';

import { useEffect, useState } from 'react';
import { Package, Wallet, Truck, MapPin, Plus, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

const quickActions = [
  { label: 'Create New Trip', icon: <Plus size={20} />, href: '/trips', primary: true },
  { label: 'Add New Package', icon: <Plus size={20} />, href: '/packages', primary: false },
  { label: 'Process Settlements', icon: <ArrowRight size={20} />, href: '/settlements', primary: false },
];

export default function DashboardPage() {
  const [stats, setStats] = useState({
    pendingPackages: 0,
    activeTrips: 0,
    totalOwed: 0,
    activeIncidents: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setIsLoading(true);
        setError(null);

        // BULLETPROOF FIX: Catch individual 404s so one missing backend route doesn't crash the whole page
        const [packages, trips, settlements, incidents] = await Promise.all([
          apiClient.getPackages().catch((e) => { console.warn("Packages missing/failed:", e); return []; }),
          apiClient.getTrips().catch((e) => { console.warn("Trips missing/failed:", e); return []; }),
          apiClient.getSettlements().catch((e) => { console.warn("Settlements missing/failed:", e); return []; }),
          apiClient.getIncidents().catch((e) => { console.warn("Incidents missing/failed:", e); return []; })
        ]);

        const pendingPkgs = packages.filter((p: any) => p.status === 'TO_BE_DELIVERED').length;
        const activeTrps = trips.filter((t: any) => t.status === 'IN_PROGRESS').length;
        const totalDue = settlements.reduce((sum: number, s: any) => sum + (Number(s.amount_paid) || 0), 0); 
        const openIncidents = incidents.filter((i: any) => i.status === 'REPORTED').length;

        setStats({
          pendingPackages: pendingPkgs,
          activeTrips: activeTrps,
          totalOwed: totalDue,
          activeIncidents: openIncidents
        });

      } catch (err: any) {
        setError(err.message || 'Failed to connect to backend API.');
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  const statCards = [
    {
      title: 'Pending Deliveries',
      value: stats.pendingPackages,
      icon: <Package size={24} />,
      color: 'var(--status-pending)',
      description: 'Packages awaiting dispatch',
    },
    {
      title: 'Active Trips',
      value: stats.activeTrips,
      icon: <Truck size={24} />,
      color: 'var(--status-in-transit)',
      description: 'Routes currently on the road',
    },
    {
      title: 'Total Settlements Paid',
      value: `LKR ${stats.totalOwed.toLocaleString()}`,
      icon: <Wallet size={24} />,
      color: 'var(--status-delivered)',
      description: 'Total cleared to drivers',
    },
    {
      title: 'Active Incidents',
      value: stats.activeIncidents,
      icon: <AlertCircle size={24} />,
      color: 'var(--status-failed)',
      description: 'Emergencies requiring rescue',
    },
  ];

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
          Welcome to LamiGo Logistics
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Manage your deliveries, drivers, and settlements from one place.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-400">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="p-6 rounded-[var(--border-radius)] transition-all duration-200 hover:scale-[1.02]"
            style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className="p-3 rounded-[var(--border-radius-sm)]"
                style={{ backgroundColor: `${stat.color}20`, color: stat.color }}
              >
                {stat.icon}
              </div>
            </div>
            <p className="text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>{stat.title}</p>
            <div className="flex items-center gap-2 mb-1">
              {isLoading ? (
                <Loader2 size={24} className="animate-spin text-gray-500" />
              ) : (
                <span className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {stat.value}
                </span>
              )}
            </div>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{stat.description}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          {quickActions.map((action, index) => (
            <Link
              key={index}
              href={action.href}
              className="flex items-center gap-2 px-6 py-3 rounded-[var(--border-radius)] font-medium text-sm transition-all duration-200"
              style={{
                backgroundColor: action.primary ? 'var(--primary-blue)' : 'var(--card-bg)',
                color: action.primary ? 'white' : 'var(--text-primary)',
                border: action.primary ? 'none' : '1px solid var(--border-color)',
              }}
            >
              {action.icon}
              {action.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}