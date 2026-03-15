"use client";

import { MapPin, Phone, Package, Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function PackagesPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-white p-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Packages</h1>
        </div>
        <button 
          onClick={() => router.push('/packages/add')}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus size={20} />
          Add New Package
        </button>
      </div>

      {/* Packages Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Package ID</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Status</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Location Pin</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Phone Number</th>
              <th className="text-left px-6 py-4 text-sm font-medium text-gray-900">Address</th>
            </tr>
            
          </thead>
          <tbody className="divide-y divide-gray-200">
            {/* Package Row 1 */}
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Package size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">#PKG-992</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  To be Delivered
                </span>
              </td>
              
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <MapPin size={14} className="text-orange-500" />
                  <span className="text-sm">-</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <Phone size={14} />
                  <span className="text-sm">077-123-4567</span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                No 45, Temple Rd, Colombo
              </td>
            </tr>

            {/* Package Row 2 */}
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Package size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">#PKG-993</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Assigned
                  
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <MapPin size={14} className="text-green-500" />
                  <span className="text-sm">-</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <Phone size={14} />
                  <span className="text-sm">077-234-5678</span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                No 12, Galle Rd, Mount Lavinia
              </td>
            </tr>

            {/* Package Row 3 */}
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Package size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">#PKG-994</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  Ongoing
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <MapPin size={14} className="text-green-500" />
                  <span className="text-sm">-</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <Phone size={14} />
                  <span className="text-sm">077-345-6789</span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                No 78, Kandy Rd, Kaduwela
              </td>
            </tr>

            {/* Package Row 4 */}
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Package size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">#PKG-995</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Completed
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <MapPin size={14} className="text-green-500" />
                  <span className="text-sm">-</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <Phone size={14} />
                  <span className="text-sm">077-456-7890</span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                No 23, Main St, Nugegoda
              </td>
            </tr>

            {/* Package Row 5 */}
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  <Package size={16} className="text-blue-600" />
                  <span className="text-sm font-medium text-gray-900">#PKG-996</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  Failed
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <MapPin size={14} className="text-orange-500" />
                  <span className="text-sm">-</span>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-1 text-gray-600">
                  <Phone size={14} />
                  <span className="text-sm">077-567-8901</span>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                No 56, Station Rd, Maharagama
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

