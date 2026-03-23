'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';
import {
  LayoutDashboard,
  Truck,
  Route,
  Package,
  Users,
  Wallet,
  AlertTriangle,
  Settings,
  LogOut,
} from 'lucide-react';
import { signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { logoutUser } from '@/lib/api';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: <LayoutDashboard size={20} />,
  },
  {
    label: 'Ongoing Trips',
    href: '/ongoing-trips',
    icon: <Truck size={20} />,
  },
  {
    label: 'Trips',
    href: '/trips',
    icon: <Route size={20} />,
  },
  {
    label: 'Packages',
    href: '/packages',
    icon: <Package size={20} />,
  },
  {
    label: 'Drivers',
    href: '/drivers',
    icon: <Users size={20} />,
  },
  {
    label: 'Settlements',
    href: '/settlements',
    icon: <Wallet size={20} />,
  },
  {
    label: 'Incident Reports',
    href: '/incidents',
    icon: <AlertTriangle size={20} />,
  },
  {
    label: 'Branch Settings',
    href: '/settings',
    icon: <Settings size={20} />,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);

  async function handleSignOut() {
    setIsSigningOut(true);
    try {
      // 1. Tell backend to clear FCM token + revoke Firebase session
      await logoutUser();
      // 2. Sign out from Firebase client
      await signOut(auth);
    } catch {
      // Best-effort — still redirect even if network fails
    } finally {
      setIsSigningOut(false);
      router.push('/');
    }
  }

  return (
    <aside
      className="fixed left-0 top-0 h-screen flex flex-col justify-between py-6 px-4"
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--card-bg)',
        borderRight: '1px solid var(--border-color)',
      }}
    >
      {/* Logo */}
      <div>
        <div className="px-4 mb-8">
          <Link href="/" className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-[var(--border-radius-sm)] flex items-center justify-center font-bold text-white text-lg"
              style={{ backgroundColor: 'var(--primary-blue)' }}
            >
              L
            </div>
            <div>
              <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                LamiGo
              </h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                Station Manager
              </p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-4 py-3 rounded-[var(--border-radius-sm)] transition-all duration-200"
                style={{
                  backgroundColor: isActive ? 'var(--primary-blue)' : 'transparent',
                  color: isActive ? 'white' : 'var(--text-secondary)',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'var(--card-bg-hover)';
                    e.currentTarget.style.color = 'var(--text-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.color = 'var(--text-secondary)';
                  }
                }}
              >
                {item.icon}
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Sign Out Button */}
      <div className="px-2">
        <button
          onClick={handleSignOut}
          disabled={isSigningOut}
          className="flex items-center gap-3 w-full px-4 py-3 rounded-[var(--border-radius-sm)] transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
          style={{
            color: 'var(--status-failed)',
            backgroundColor: 'transparent',
          }}
          onMouseEnter={(e) => {
            if (!isSigningOut)
              e.currentTarget.style.backgroundColor = 'var(--status-failed-bg)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <LogOut size={20} />
          <span className="font-medium text-sm">
            {isSigningOut ? 'Signing out…' : 'Sign Out'}
          </span>
        </button>
      </div>
    </aside>
  );
}
