"use client";

import { Plus, Bike, Bus, Truck, CheckCircle, Clock, Ban, Users } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DriversPage() {
  const router = useRouter();

  const drivers = [
    {
      id: '#DRV-05',
      name: 'Saman Perera',
      initials: 'SP',
      phone: '071-234-5678',
      vehicleType: 'Motorcycle',
      status: 'Available',
      walletBalance: 'LKR 1,200',
    },
    {
      id: '#DRV-12',
      name: 'Nimal Silva',
      initials: 'NS',
      phone: '077-456-7890',
      vehicleType: 'Tuk Tuk',
      status: 'In a Trip',
      walletBalance: 'LKR 8,500',
    },
    {
      id: '#DRV-08',
      name: 'Kasun Fernando',
      initials: 'KF',
      phone: '075-567-8901',
      vehicleType: 'Lorry',
      status: 'Scheduled',
      walletBalance: 'LKR 0',
    },
    {
      id: '#DRV-03',
      name: 'Amal Wijesinghe',
      initials: 'AW',
      phone: '071-678-9012',
      vehicleType: 'Motorcycle',
      status: 'Unavailable',
      walletBalance: 'LKR 0',
    },
  ];

  const getStatusClasses = (status: string) => {
    switch (status) {
      case 'Available':
        return 'bg-green-100 text-green-800';
      case 'In a Trip':
        return 'bg-blue-100 text-blue-800';
      case 'Scheduled':
        return 'bg-yellow-100 text-yellow-800';
      case 'Unavailable':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getVehicleIcon = (vehicleType: string) => {
    switch (vehicleType) {
      case 'Motorcycle':
        return <Bike size={16} className="text-gray-500" />;
      case 'Tuk Tuk':
        return <Bus size={16} className="text-gray-500" />;
      case 'Lorry':
        return <Truck size={16} className="text-gray-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Drivers</h1>
        <button 
          onClick={() => router.push('/drivers/register')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus size={20} />
          Register New Driver
        </button>
      </div>

      {/* Drivers Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Driver ID</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Name</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Phone</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Vehicle</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Status</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Wallet Balance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {drivers.map((driver, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {driver.id}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                      {driver.initials}
                    </div>
                    <span className="text-sm font-medium text-gray-900">{driver.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {driver.phone}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    {getVehicleIcon(driver.vehicleType)}
                    <span className="text-sm text-gray-600">{driver.vehicleType}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClasses(driver.status)}`}>
                    {driver.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {driver.walletBalance}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
