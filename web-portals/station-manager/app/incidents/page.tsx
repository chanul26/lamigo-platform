// app/incidents/page.tsx
'use client'

import { useState } from 'react'
import { Search, AlertTriangle, Wrench, MoreVertical } from 'lucide-react'

interface Incident {
  id: string
  category: 'accident' | 'breakdown' | 'other'
  description: string
  tripId: string
  date: string
  status: 'resolved' | 'pending'
  location: string
}

const mockIncidents: Incident[] = [
  {
    id: '#INC-005',
    category: 'accident',
    description: 'Minor collision at intersection, no injuries',
    tripId: '#TR-2025-001',
    date: '2025-03-10',
    status: 'resolved',
    location: 'Colombo 03'
  },
  {
    id: '#INC-004',
    category: 'breakdown',
    description: 'Engine overheating on highway',
    tripId: '#TR-2025-002',
    date: '2025-03-09',
    status: 'resolved',
    location: 'Kadawatha'
  }
]

const categoryConfig = {
  accident: { color: 'bg-[#fee2e2] text-[#ef4444]', icon: AlertTriangle },
  breakdown: { color: 'bg-[#fed7aa] text-[#f59e0b]', icon: Wrench },
  other: { color: 'bg-[#f3f4f6] text-[#64748b]', icon: AlertTriangle }
}

export default function Incidents_Page() {
  const [searchTerm, setSearchTerm] = useState('')
  const [incidents] = useState(mockIncidents)

  const filteredIncidents = incidents.filter(incident => 
    incident.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    incident.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-[#1e293b]">Incident Reports</h1>
        <div className="text-sm text-[#64748b]">
          Showing resolved incidents
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#94a3b8] w-5 h-5" />
          <input
            type="text"
            placeholder="Search incidents..."
            className="w-full pl-10 pr-4 py-2 border border-[#e9ecef] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb]"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-[#e9ecef]">
          <thead className="bg-[#f3f4f6]">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Incident ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Trip
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-[#e9ecef]">
            {filteredIncidents.map((incident) => {
              const CategoryIcon = categoryConfig[incident.id].icon
              
              return (
                <tr key={incident.id} className="hover:bg-[#f3f4f6]/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-[#1e293b]">
                    {incident.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex items-center text-xs leading-5 font-semibold rounded-full ${categoryConfig[incident.category].color}`}>
                      <CategoryIcon className="w-4 h-4 mr-1" />
                      {incident.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-[#64748b] max-w-xs truncate">
                    {incident.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                    {incident.trip}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                    {incident.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                    {incident.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-[#64748b]">
                    <button className="text-[#2563eb] hover:text-[#1d4ed8] mr-3">
                      View
                    </button>
                    <button className="text-[#94a3b8] hover:text-[#64748b]">
                      <MoreVertical className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
