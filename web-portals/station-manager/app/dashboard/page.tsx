'use client';

import { 
  Package, 
  Wallet, 
  Truck, 
  Plus, 
  ArrowRight, 
  Loader2 
} from 'lucide-react';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  // Setup state to hold real data from the API
  const [stats, setStats] = useState({
    pendingPackages: 0,
    activeTrips: 0,
    totalSettlements: 0,
  });
  const [loading, setLoading] = useState(true);

  // Fetch data from local FastAPI backend
  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        const [pkgRes, tripRes, setRes] = await Promise.all([
          fetch("http://localhost:8000/api/v1/packages", { headers }),
          fetch("http://localhost:8000/api/v1/trips?status=active", { headers }),
          fetch("http://localhost:8000/api/v1/settlements", { headers })
        ]);

        const packages = await pkgRes.json();
        const trips = await tripRes.json();
        const settlements = await setRes.json();

        setStats({
          //Filter for 'pending' status specifically
          pendingPackages: Array.isArray(packages) 
            ? packages.filter((p: any) => p.status === 'pending').length 
            : 0,
          activeTrips: Array.isArray(trips) ? trips.length : 0,
          // Sum amount_due for settlements
          totalSettlements: Array.isArray(settlements)
            ? settlements.reduce((acc: number, curr: any) => acc + (curr.amount_due || 0), 0)
            : 0
        });
      } catch (error) {
        console.error("Dashboard fetch error:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  // The UI mapping for the cards
  const statCards = [
    {
      title: 'Pending Deliveries',
      value: stats.pendingPackages,
      icon: <Package size={24} />,
      color: 'var(--primary-blue)',
      description: 'Packages awaiting dispatch',
    },
    {
      title: 'Pending Settlements',
      value: `LKR ${stats.totalSettlements.toLocaleString()}`,
      icon: <Wallet size={24} />,
      color: '#f59e0b', 
      description: 'Driver payments due',
    },
    {
      title: 'Active Trips',
      value: stats.activeTrips,
      icon: <Truck size={24} />,
      color: '#10b981', 
      description: 'Ongoing routes',
    },
  ];

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
          Dashboard
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome to LamiGo Logistics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="p-6 rounded-[var(--border-radius)]"
            style={{ 
              backgroundColor: 'var(--card-bg)', 
              border: '1px solid var(--border-color)' 
            }}
          >
            <div className="flex items-center justify-between mb-4">
               <div 
                 className="p-3 rounded-lg" 
                 style={{ backgroundColor: `${stat.color}15`, color: stat.color }}
               >
                {stat.icon}
              </div>
            </div>
            <p className="text-sm text-[var(--text-secondary)] font-medium">{stat.title}</p>
            <div className="text-3xl font-bold my-1 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
              {loading ? (
                <Loader2 className="animate-spin text-[var(--text-muted)]" size={24} />
              ) : (
                stat.value
              )}
            </div>
            <p className="text-xs text-[var(--text-muted)]">{stat.description}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Quick Actions
      </h2>
      <div className="flex flex-wrap gap-4">
        <Link 
          href="/trips/create" 
          className="flex items-center gap-2 px-6 py-3 bg-[var(--primary-blue)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          <Plus size={20} />
          Create New Trip
        </Link>
        
        <Link 
          href="/packages" 
          className="flex items-center gap-2 px-6 py-3 border border-[var(--border-color)] bg-[var(--card-bg)] text-[var(--text-primary)] rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          <Plus size={20} />
          Add New Package
        </Link>

        <Link 
          href="/settlements" 
          className="flex items-center gap-2 px-6 py-3 border border-[var(--border-color)] bg-[var(--card-bg)] text-[var(--text-primary)] rounded-lg font-medium hover:bg-gray-50 transition-colors"
        >
          <ArrowRight size={20} />
          Process Settlements
        </Link>
      </div>
    </div>
  );
}