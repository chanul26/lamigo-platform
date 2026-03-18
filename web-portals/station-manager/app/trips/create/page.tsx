'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Check, ChevronRight, Loader2, Save } from 'lucide-react';

export default function CreateTripPage() {
  const router = useRouter();
  const [packages, setPackages] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [selectedPackages, setSelectedPackages] = useState<string[]>([]);
  const [selectedDriver, setSelectedDriver] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [pkgRes, drvRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/packages?status=pending'),
          fetch('http://localhost:8000/api/v1/drivers?status=available')
        ]);
        setPackages(await pkgRes.json());
        setDrivers(await drvRes.json());
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    }
    fetchData();
  }, []);

  const handleCreateTrip = async () => {
    if (!selectedDriver || selectedPackages.length === 0) return alert("Select driver and packages!");
    
    const res = await fetch('http://localhost:8000/api/v1/trips', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        driver_id: selectedDriver,
        package_ids: selectedPackages
      })
    });

    if (res.ok) router.push('/trips');
  };

  if (loading) return <div className="p-20 text-center"><Loader2 className="animate-spin mx-auto" /></div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create New Trip</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left: Package Selection */}
        <div className="md:col-span-2 space-y-4">
          <h2 className="font-semibold text-lg">1. Select Packages</h2>
          <div className="border rounded-[var(--border-radius)] bg-[var(--card-bg)]">
            {packages.map((pkg: any) => (
              <div key={pkg.id} className="p-4 flex items-center gap-4 border-b last:border-0">
                <input 
                  type="checkbox" 
                  checked={selectedPackages.includes(pkg.id)}
                  onChange={(e) => e.target.checked 
                    ? setSelectedPackages([...selectedPackages, pkg.id])
                    : setSelectedPackages(selectedPackages.filter(id => id !== pkg.id))
                  }
                />
                <div>
                  <p className="font-medium">{pkg.customer_name}</p>
                  <p className="text-xs text-gray-500">{pkg.address}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Driver & Action */}
        <div className="space-y-6">
          <div className="space-y-4">
            <h2 className="font-semibold text-lg">2. Assign Driver</h2>
            <select 
              className="w-full p-2 border rounded"
              value={selectedDriver}
              onChange={(e) => setSelectedDriver(e.target.value)}
            >
              <option value="">Select a Driver</option>
              {drivers.map((d: any) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>

          <button 
            onClick={handleCreateTrip}
            className="w-full py-3 bg-[var(--primary-blue)] text-white rounded font-bold flex items-center justify-center gap-2 hover:opacity-90"
          >
            <Save size={18} /> Finalize Trip
          </button>
        </div>
      </div>
    </div>
  );
}