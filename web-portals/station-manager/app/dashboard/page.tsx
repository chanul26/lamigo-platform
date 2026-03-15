'use client';

import { useState, useEffect } from "react";
import {
  Package,
  Wallet,
  Truck,
  MapPin,
  Plus,
  ArrowRight,
  Loader2,
} from 'lucide-react';
import Link from 'next/link';

interface StatCard {
  title: string;
  icon: React.ReactNode;
  color: string;
  description: string;
}

const statCards: StatCard[] = [
  {
    title: 'Pending Deliveries',
    icon: <Package size={24} />,
    color: 'var(--status-pending)',
    description: 'Packages awaiting dispatch',
  },
  {
    title: 'In Transit',
    icon: <Truck size={24} />,
    color: 'var(--status-in-transit)',
    description: 'Active deliveries',
  },
  {
    title: 'Pending Settlements',
    icon: <Wallet size={24} />,
    color: 'var(--status-failed)',
    description: 'Driver payments due',
  },
  {
    title: 'Active Trips',
    icon: <MapPin size={24} />,
    color: 'var(--status-delivered)',
    description: 'Ongoing routes',
  },
];

const quickActions = [
  {
    label: 'Create New Trip',
    icon: <Plus size={20} />,
    href: '/trips',
    primary: true,
  },
  {
    label: 'Add New Package',
    icon: <Plus size={20} />,
    href: '/packages',
    primary: false,
  },
  {
    label: 'Process Settlements',
    icon: <ArrowRight size={20} />,
    href: '/settlements',
    primary: false,
  },
];

export default function DashboardPage() {

  const [stats, setStats] = useState({
    pendingPackages: 0,
    inTransit: 0,
    settlements: 0,
    activeTrips: 0
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [pkgRes, tripRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/packages'),
          fetch('http://localhost:8000/api/v1/trips')
        ]);

        const pkgs = await pkgRes.json();
        const trips = await tripRes.json();

        setStats({
          pendingPackages: pkgs.filter((p: any) => p.status === 'pending').length,
          inTransit: pkgs.filter((p: any) => p.status === 'in_transit').length,
          settlements: 0, 
          activeTrips: trips.filter((t: any) => t.status === 'ongoing').length,
        });
        setLoading(false);
      } catch (error) {
        console.error("Connection to Backend failed:", error);
        setLoading(false);
      }
    }
    fetchDashboardData();
  }, []);

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1
          className="text-2xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Welcome to LamiGo Logistics
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Manage your deliveries, drivers, and settlements from one place.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="p-6 rounded-[var(--border-radius)] transition-all duration-200 hover:scale-[1.02]"
            style={{
              backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-color)',
            }}
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className="p-3 rounded-[var(--border-radius-sm)]"
                style={{
                  backgroundColor: `${stat.color}20`,
                  color: stat.color,
                }}
              >
                {stat.icon}
              </div>
            </div>
            <p
              className="text-sm mb-1"
              style={{ color: 'var(--text-secondary)' }}
            >
              {stat.title}
            </p>
            <div className="flex items-center gap-2 mb-1">
              <span
                className="text-2xl font-semibold"
                style={{ color: 'var(--text-primary)' }}
              >
                {loading
                  ? '—'
                  : index === 0
                  ? stats.pendingPackages
                  : index === 1
                  ? stats.inTransit
                  : index === 2
                  ? stats.settlements
                  : stats.activeTrips}
              </span>

              {loading && (
                <Loader2
                  size={16}
                  className="animate-spin"
                  style={{ color: 'var(--text-muted)' }}
                />
              )}
            </div>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              {stat.description}
            </p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2
          className="text-lg font-semibold mb-4"
          style={{ color: 'var(--text-primary)' }}
        >
          Quick Actions
        </h2>
        <div className="flex flex-wrap gap-4">
          {quickActions.map((action, index) => (
            <Link
              key={index}
              href={action.href}
              className="flex items-center gap-2 px-6 py-3 rounded-[var(--border-radius)] font-medium text-sm transition-all duration-200"
              style={{
                backgroundColor: action.primary
                  ? 'var(--primary-blue)'
                  : 'var(--card-bg)',
                color: action.primary ? 'white' : 'var(--text-primary)',
                border: action.primary
                  ? 'none'
                  : '1px solid var(--border-color)',
              }}
              onMouseEnter={(e) => {
                if (action.primary) {
                  e.currentTarget.style.backgroundColor =
                    'var(--primary-blue-hover)';
                } else {
                  e.currentTarget.style.backgroundColor =
                    'var(--card-bg-hover)';
                }
              }}
              onMouseLeave={(e) => {
                if (action.primary) {
                  e.currentTarget.style.backgroundColor = 'var(--primary-blue)';
                } else {
                  e.currentTarget.style.backgroundColor = 'var(--card-bg)';
                }
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
