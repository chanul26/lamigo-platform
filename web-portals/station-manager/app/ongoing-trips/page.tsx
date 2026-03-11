// app/ongoing-trips/page.tsx - Full version
'use client'

import { useState } from 'react'
import { Search, Clock, MapPin, Phone } from 'lucide-react'
import Link from 'next/link'

interface OngoingTrip {
  id: string
  driver: string
  driverAvatar: string
  route: string
  eta: string
  etaVariance: number
  codCollected: number
  totalCOD: number
  stopsCompleted: number
  totalStops: number
}

const mockOngoingTrips: OngoingTrip[] = [
  {
    id: '#TR-2025-001',
    driver: 'Kamal Perera',
    driverAvatar: 'KP',
    route: 'Colombo - Kandy',
    eta: '14:30',
    etaVariance: -15,
    codCollected: 4300,
    totalCOD: 11800,
    stopsCompleted: 2,
    totalStops: 5
  },
  {
    id: '#TR-2025-004',
    driver: 'Sunil Weerasinghe',
    driverAvatar: 'SW',
    route: 'Kurunegala - Anuradhapura',
    eta: '16:45',
    etaVariance: 5,
    codCollected: 8900,
    totalCOD: 8900,
    stopsCompleted: 4,
    totalStops: 4
  },
  {
    id: '#TR-2025-005',
    driver: 'Mahinda Silva',
    driverAvatar: 'MS',
    route: 'Galle - Matara',
    eta: '15:20',
    etaVariance: -5,
    codCollected: 2500,
    totalCOD: 6700,
    stopsCompleted: 1,
    totalStops: 3
  }
]

export default function OngoingTripsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [trips] = useState(mockOngoingTrips)

  const filteredTrips = trips.filter(trip => 
    trip.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trip.driver.toLowerCase().includes(driver.toLowerCase())
  )

  return 
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-[#1e293b]">Ongoing Trips</h1>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-[#10b981] rounded-full"></div>
            <span className="text-[#64748b]">On Time</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-[#ef4444] rounded-full"></div>
            <span className="text-[#64748b]">Delayed</span>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#94a3b8] w-5 h-5" />
          <input
            type="text"
            placeholder="Monitor trips by ID or driver..."
            className="w-full pl-10 pr-4 py-2.5 border border-[#e9ecef] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563eb]"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Ongoing Trips Cards */}
      <div className="grid grid-cols-1 gap-6">
        {filteredTrips.map((trip) => (
          <Link
            key={trip.id}
            href={`/ongoing-trips/${trip.id}`}
            className="bg-white rounded-xl shadow-sm hover:shadow-md transition-all p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-[#2563eb] rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold">{trip.driverAvatar}</span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-[#1e293b]">{trip.id}</h3>
                  <p className="text-[#64748b]">{trip.driver}</p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <p className="text-sm text-[#64748b]">ETA to Station</p>
                  <p className={`font-semibold flex items-center ${
                    trip.etaVariance < 0 ? 'text-[#ef4444]' : 'text-[#10b981]'
                  }`}>
                    <Clock className="w-4 h-4 mr-1" />
                    {trip.eta} ({trip.etaVariance > 0 ? '+' : ''}{trip.etaVariance} min)
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-[#64748b]">COD Collected</p>
                  <p className="font-semibold text-[#1e293b]">LKR {trip.codCollected.toLocaleString()}</p>
                </div>
                <button className="p-2.5 bg-[#10b981] text-white rounded-lg hover:bg-[#0f9e6e] transition-colors">
                  <Phone className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-[#64748b]">
                  <MapPin className="w-4 h-4 mr-1" />
                  <span className="text-sm">{trip.route}</span>
                </div>
                <div className="flex items-center text-[#64748b]">
                  <span className="text-sm">Progress: {trip.stopsCompleted}/{trip.totalStops} stops</span>
                </div>
              </div>
              
              <div className="w-48">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-[#64748b]">Completion</span>
                  <span className="font-medium text-[#1e293b]">
                    {Math.round((trip.stopsCompleted / trip.totalStops) * 100)}%
                  </span>
                </div>
                <div className="w-full bg-[#f3f4f6] rounded-full h-2">
                  <div 
                    className="bg-[#2563eb] h-2 rounded-full"
                    style={{ width: `${(trip.stopsCompleted / trip.totalStops) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
