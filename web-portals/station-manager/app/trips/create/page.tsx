'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { ArrowLeft, Truck, Package, Send } from 'lucide-react';

const MOCK_DRIVERS = [
  { id: 'd1', name: 'Saman (Available)' },
  { id: 'd2', name: 'Nimal (Busy)', busy: true },
];

const MOCK_PACKAGES: { id: string; address: string; area: string }[] = [
  { id: 'p1', address: '45 Galle Road, Colombo 03', area: 'Colombo' },
  { id: 'p2', address: '123 Kandy Road, Kadawatha', area: 'Kadawatha' },
  { id: 'p3', address: '78 Beach Road, Mount Lavinia', area: 'Mount Lavinia' },
  { id: 'p4', address: '56 Temple Road, Nugegoda', area: 'Nugegoda' },
  { id: 'p5', address: '92 Station Road, Dehiwala', area: 'Dehiwala' },
  { id: 'p6', address: '12 Main Street, Colombo 05', area: 'Colombo' },
  { id: 'p7', address: '34 Lake Road, Kandy', area: 'Kandy' },
  { id: 'p8', address: '67 Park Avenue, Nugegoda', area: 'Nugegoda' },
  { id: 'p9', address: '89 Ocean Drive, Galle', area: 'Galle' },
  { id: 'p10', address: '21 Hill Street, Kotte', area: 'Kotte' },
];

const COD_PER_PACKAGE = 500;

export default function CreateTripPage() {
  const [selectedDriverId, setSelectedDriverId] = useState<string>('');
  const [availablePackages, setAvailablePackages] = useState(MOCK_PACKAGES);
  const [selectedPackageIds, setSelectedPackageIds] = useState<string[]>([]);
  const [areaFilter, setAreaFilter] = useState('');

  const selectedPackages = useMemo(
    () => MOCK_PACKAGES.filter((p) => selectedPackageIds.includes(p.id)),
    [selectedPackageIds]
  );

  const filteredAvailable = useMemo(() => {
    if (!areaFilter.trim()) return availablePackages;
    const q = areaFilter.trim().toLowerCase();
    return availablePackages.filter(
      (p) =>
        p.area.toLowerCase().includes(q) ||
        p.address.toLowerCase().includes(q)
    );
  }, [availablePackages, areaFilter]);

  const totalCod = selectedPackageIds.length * COD_PER_PACKAGE;

  const moveToSelected = (id: string) => {
    setAvailablePackages((prev) => prev.filter((p) => p.id !== id));
    setSelectedPackageIds((prev) => [...prev, id]);
  };

  const moveToAvailable = (id: string) => {
    setSelectedPackageIds((prev) => prev.filter((pid) => pid !== id));
    setAvailablePackages((prev) => {
      const pkg = MOCK_PACKAGES.find((p) => p.id === id);
      return pkg ? [...prev, pkg].sort((a, b) => a.id.localeCompare(b.id)) : prev;
    });
  };

  const handleDispatch = () => {
    console.log('Dispatch — Driver ID:', selectedDriverId);
    console.log('Dispatch — Package IDs:', selectedPackageIds);
  };

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="mb-6 flex items-center gap-4">
        <Link
          href="/trips"
          className="flex items-center gap-2 text-sm font-medium transition-colors hover:opacity-80"
          style={{ color: 'var(--text-secondary)' }}
        >
          <ArrowLeft size={18} />
          Back to Trips
        </Link>
      </div>
      <div className="mb-8">
        <h1
          className="text-2xl font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Create Trip (Dispatch)
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Select a driver and packages to dispatch a new trip.
        </p>
      </div>

      {/* Driver selector card */}
      <div
        className="rounded-[var(--border-radius)] p-6 mb-6"
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <div className="flex items-center gap-2 mb-4">
          <Truck size={20} style={{ color: 'var(--primary-blue)' }} />
          <h2
            className="text-lg font-semibold"
            style={{ color: 'var(--text-primary)' }}
          >
            Driver
          </h2>
        </div>
        <label
          htmlFor="driver-select"
          className="block text-sm font-medium mb-2"
          style={{ color: 'var(--text-secondary)' }}
        >
          Assign driver
        </label>
        <select
          id="driver-select"
          value={selectedDriverId}
          onChange={(e) => setSelectedDriverId(e.target.value)}
          className="w-full max-w-xs px-4 py-3 rounded-[var(--border-radius-sm)] text-sm outline-none focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30"
          style={{
            backgroundColor: 'var(--bg-dark)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
          }}
        >
          <option value="">Select a driver</option>
          {MOCK_DRIVERS.map((d) => (
            <option
              key={d.id}
              value={d.id}
              disabled={'busy' in d && d.busy}
            >
              {d.name}
            </option>
          ))}
        </select>
      </div>

      {/* Dual-list package selector */}
      <div
        className="rounded-[var(--border-radius)] p-6 mb-6"
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <div className="flex items-center gap-2 mb-4">
          <Package size={20} style={{ color: 'var(--primary-blue)' }} />
          <h2
            className="text-lg font-semibold"
            style={{ color: 'var(--text-primary)' }}
          >
            Packages
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Available packages */}
          <div className="flex flex-col">
            <div
              className="text-sm font-medium mb-2"
              style={{ color: 'var(--text-secondary)' }}
            >
              Available packages
            </div>
            <input
              type="text"
              placeholder="Search by area or address..."
              value={areaFilter}
              onChange={(e) => setAreaFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-[var(--border-radius-sm)] text-sm mb-3 outline-none focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30"
              style={{
                backgroundColor: 'var(--bg-dark)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
            />
            <div
              className="flex-1 min-h-[280px] overflow-y-auto rounded-[var(--border-radius-sm)] border space-y-1 p-2"
              style={{
                backgroundColor: 'var(--bg-dark)',
                borderColor: 'var(--border-color)',
              }}
            >
              {filteredAvailable.map((pkg) => (
                <button
                  key={pkg.id}
                  type="button"
                  onClick={() => moveToSelected(pkg.id)}
                  className="w-full text-left px-3 py-2.5 rounded-[var(--border-radius-sm)] text-sm transition-colors hover:bg-[var(--card-bg-hover)]"
                  style={{
                    backgroundColor: 'var(--card-bg)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-color)',
                  }}
                >
                  <span className="font-mono text-xs opacity-70">{pkg.id}</span>
                  <div className="font-medium truncate">{pkg.address}</div>
                  <div
                    className="text-xs"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    {pkg.area}
                  </div>
                </button>
              ))}
              {filteredAvailable.length === 0 && (
                <div
                  className="py-8 text-center text-sm"
                  style={{ color: 'var(--text-muted)' }}
                >
                  No packages match the filter.
                </div>
              )}
            </div>
          </div>

          {/* Right: Selected for trip */}
          <div className="flex flex-col">
            <div
              className="text-sm font-medium mb-2"
              style={{ color: 'var(--text-secondary)' }}
            >
              Selected for trip
            </div>
            <div className="mb-3 h-9" aria-hidden />
            <div
              className="flex-1 min-h-[280px] overflow-y-auto rounded-[var(--border-radius-sm)] border space-y-1 p-2"
              style={{
                backgroundColor: 'var(--bg-dark)',
                borderColor: 'var(--border-color)',
              }}
            >
              {selectedPackages.map((pkg) => (
                <button
                  key={pkg.id}
                  type="button"
                  onClick={() => moveToAvailable(pkg.id)}
                  className="w-full text-left px-3 py-2.5 rounded-[var(--border-radius-sm)] text-sm transition-colors hover:bg-[var(--card-bg-hover)]"
                  style={{
                    backgroundColor: 'var(--status-in-transit-bg)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--status-in-transit)',
                  }}
                >
                  <span className="font-mono text-xs opacity-70">{pkg.id}</span>
                  <div className="font-medium truncate">{pkg.address}</div>
                  <div
                    className="text-xs"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    {pkg.area}
                  </div>
                </button>
              ))}
              {selectedPackages.length === 0 && (
                <div
                  className="py-8 text-center text-sm"
                  style={{ color: 'var(--text-muted)' }}
                >
                  Select packages from the left.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Summary footer */}
      <div
        className="rounded-[var(--border-radius)] p-6 mb-6 flex flex-wrap items-center justify-between gap-4"
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <div className="flex flex-wrap gap-8">
          <div>
            <div
              className="text-xs font-medium uppercase tracking-wider mb-1"
              style={{ color: 'var(--text-muted)' }}
            >
              Total packages selected
            </div>
            <div
              className="text-xl font-semibold"
              style={{ color: 'var(--text-primary)' }}
            >
              {selectedPackageIds.length}
            </div>
          </div>
          <div>
            <div
              className="text-xs font-medium uppercase tracking-wider mb-1"
              style={{ color: 'var(--text-muted)' }}
            >
              Estimated COD (LKR)
            </div>
            <div
              className="text-xl font-semibold"
              style={{ color: 'var(--status-delivered)' }}
            >
              {totalCod.toLocaleString()}
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={handleDispatch}
          disabled={!selectedDriverId || selectedPackageIds.length === 0}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-[var(--border-radius)] font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            backgroundColor: 'var(--status-delivered)',
            color: 'white',
          }}
        >
          <Send size={18} />
          Dispatch Trip
        </button>
      </div>
    </div>
  );
}
