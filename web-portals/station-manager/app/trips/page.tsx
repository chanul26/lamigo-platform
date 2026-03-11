// app/trips/page.tsx - Full version with proper design
'use client'

import { useState } from 'react'
import { Search, Plus, MoreVertical, Filter } from 'lucide-react'
import Link from 'next/link'

interface Trip {
  id: string
  status: 'Progress' | 'Draft' | 'Completed'
  driver: string 
  driverInitials: string
  packageCount: number
  route: string
  date: string
}

const mockTrips: Trip[] = [
  {
    id: '#TR-2025-001',
    status: 'In Progress',
    driver: 'Kamal Perera',
    driverInitials: 'KP',
    packageCount: 12,
    route: 'Colombo - Kandy',
    date: '2025-03-10'
  },
  {
    id: '#TR-2025-002',
    status: 'Completed',
    driver: 'Nimal Silva',
    driverInitials: 'NS',
    packageCount: 8,
    route: 'Galle - Matara',
    date: '2025-03-09'
  },
  {
    id: '#TR-2025-003',
    status: 'Draft',
    driver: null,
    driverInitials: '',
    packageCount: 5,
    route: 'Negombo - Jaffna',
    date: '2025-03-11'
  },
    {
    id: '#TR-2025-004',
    status: 'In Progress',
    driver: 'Sunil Weerasinghe',
    driverInitials: 'SW',
    packageCount: 15,
    route: 'Kurunegala - Anuradhapura',
    date: '2025-03-10'
  }
  

]

export default function TripsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [trips] = useState(mockTrips)

  const filteredTrips = trips.filter(trip => 
    trip.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (trip.driver && trip.driver.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-[#1e293b]">Trips</h1>
        <button className="bg-[#2563eb] text-white px-4 py-2.5 rounded-lg flex items-center space-x-2 hover:bg-[#1d4ed8] transition-colors shadow-sm">
          <Plus className="w-5 h-5" />
          <span className="font-medium">Create New Trip</span>
        </button>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex space-x-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#94a3b8] w-5 h-5" />
          <input
            type="text"
            placeholder="Search trips by ID or driver..."
            className="w-full pl-10 pr-4 py-2.5 border border-[#e9ecef] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb] focus:border-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="px-4 py-2.5 border border-[#e9ecef] rounded-lg text-[#64748b] hover:bg-[#f3f4f6] flex items-center space-x-2 transition-colors">
          <Filter className="w-5 h-5" />
          <span className="font-medium">Filter</span>
        </button>
      </div>

      {/* Trips Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-[#e9ecef]">
          <thead className="bg-[#f8f9fa]">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Trip ID
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Driver
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Package Count
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Route
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-[#e9ecef]">
            {filteredTrips.map((trip) => (
              <tr key={trip.id} className="hover:bg-[#f8f9fa] transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <Link href={`/trips/${trip.id}`} className="text-[#2563eb] hover:text-[#1d4ed8] font-medium">
                    {trip.id}
                  </Link>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                    trip.status === 'In Progress' ? 'bg-[#2563eb]/10 text-[#2563eb]' :
                    trip.status === 'Completed' ? 'bg-[#10b981]/10 text-[#10b981]' :
                    'bg-[#f3f4f6] text-[#64748b]'
                  }`}>
                    {trip.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {trip.driver ? (
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-[#2563eb] rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-medium">{trip.driverInitials}</span>
                      </div>
                      <span className="text-sm text-[#1e293b]">{trip.driver}</span>
                    </div>
                  ) : (
                    <span className="text-sm text-[#94a3b8]">Unassigned</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                  {trip.packageCount} items
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                  {trip.route}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                  {trip.date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button className="p-2 text-[#94a3b8] hover:text-[#64748b] hover:bg-[#f3f4f6] rounded-lg transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {/* Empty State */}
        {filteredTrips.length === 0 && (
          <div className="px-6 py-12 text-center">
            <p className="text-[#94a3b8]">No trips found matching your search criteria</p>
          </div>
        )}
      </div>
    </div>
  )
}
