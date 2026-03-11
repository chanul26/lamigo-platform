

'use client'

import { useState } from 'react'
import { Phone, MapPin, Package, CreditCard, AlertTriangle, Clock, CheckCircle } from 'lucide-react'
import IncidentModal from '../../components/IncidentModal'

interface Stop {
  id: number
  address: string
  status: 'delivered' | 'en-route' 
}

const mockStops: Stop[] = [
  { id: 1, address: '12 Temple Road, Colombo 03', status: 'delivered', cod: 2500 },
  { id: 2, address: '45 Galle Road, Mount Lavinia', status: 'delivered', cod: 1800 },
  { id: 3, address: '78 Kandy Road, Kadawatha', status: 'en-route', cod: 3200 },
  { id: 4, address: '23 Negombo Road, Ja-Ela', status: 'pending', cod: 1500 },
  { id: 5, address: '156 High Level Road, Nugegoda', status: 'pending', cod: 2800 },
]

export default function OngoingTripDetails({ params }: { params: { id: string } }) {
  const [showIncidentModal, setShowIncidentModal] = useState(false)
  const completedStops = mockStops.filter(stop => stop.status === 'delivered').length
  const totalCOD = mockStops.reduce((sum, stop) => sum + (stop.cod || 0), 0)
  const collectedCOD = mockStops
    .filter(stop => stop.status === 'delivered')
    .reduce((sum, stop) => sum + (stop.cod || 0), 0)

  return (
    <>
      <div className="h-full flex">
        {/* Main Content */}
        <div className="flex-1 p-8 overflow-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-2xl font-bold text-[#1e293b]">Trip {params.id}</h1>
              <div className="flex items-center space-x-3 mt-2">
                <span className="px-3 py-1 text-xs font-semibold rounded-full bg-[#2563eb]/10 text-[#2563eb]">
                  In Progress
                </span>
                <span className="text-sm text-[#94a3b8]">• Updated 2 min ago</span>
              </div>
            </div>
            <button
              onClick={() => setShowIncidentModal(true)}
              className="px-4 py-2.5 bg-[#ef4444] text-white rounded-lg flex items-center space-x-2 hover:bg-[#dc2626] transition-colors shadow-sm"
            >
              <AlertTriangle className="w-5 h-5" />
              <span className="font-medium">Report Incident</span>
            </button>
          </div>

          {/* Map Card */}
          <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-[#1e293b]">Live Route</h2>
              <span className="text-xs px-2 py-1 bg-[#f3f4f6] text-[#64748b] rounded-full">GPS Active</span>
            </div>
            <div className="bg-[#f3f4f6] rounded-lg h-64 relative overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center text-[#94a3b8]">
                <MapPin className="w-8 h-8 mr-2" />
                <span>Live Map View - Vehicle near Kadawatha</span>
              </div>
            </div>
          </div>

          {/* Delivery Timeline Card */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="font-semibold text-[#1e293b] mb-6">Delivery Sequence</h2>
            <div className="space-y-4">
              {mockStops.map((stop, index) => (
                <div key={stop.id} className="relative pl-8 pb-6 last:pb-0">
                  {/* Timeline line */}
                  {index < mockStops.length - 1 && (
                    <div className="absolute left-[0.6rem] top-5 bottom-0 w-0.5 bg-[#e9ecef]"></div>
                  )}
                  
                  {/* Timeline dot */}
                  <div className={`absolute left-0 top-1 w-5 h-5 rounded-full border-2 ${
                    stop.status === 'delivered' ? 'bg-[#10b981] border-[#10b981]/20' :
                    stop.status === 'en-route' ? 'bg-[#2563eb] border-[#2563eb]/20' :
                    'bg-[#e9ecef] border-[#e9ecef]'
                  }`}></div>
                  
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-[#1e293b]">Stop #{index + 1}</span>
                        {stop.status === 'delivered' && (
                          <CheckCircle className="w-4 h-4 text-[#10b981]" />
                        )}
                      </div>
                      <p className="text-[#64748b] text-sm mt-1">{stop.address}</p>
                      {stop.cod && (
                        <p className="text-xs text-[#94a3b8] mt-1 flex items-center">
                          <CreditCard className="w-3 h-3 mr-1" />
                          COD: LKR {stop.cod.toLocaleString()}
                        </p>
                      )}
                    </div>
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
                      stop.status === 'delivered' ? 'bg-[#10b981]/10 text-[#10b981]' :
                      stop.status === 'en-route' ? 'bg-[#2563eb]/10 text-[#2563eb]' :
                      'bg-[#f3f4f6] text-[#64748b]'
                    }`}>
                      {stop.status === 'delivered' ? 'Delivered' :
                       stop.status === 'en-route' ? 'En Route' : 'Pending'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Sidebar - Trip Stats */}
        <div className="w-80 bg-white border-l border-[#e9ecef] p-6 overflow-auto">
          {/* Driver Profile Card */}
          <div className="bg-white rounded-xl shadow-sm p-5 mb-6">
            <h3 className="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider mb-4">
              Driver
            </h3>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-14 h-14 bg-[#2563eb] rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-lg">KP</span>
                </div>
                <div>
                  <p className="font-semibold text-[#1e293b]">Kamal Perera</p>
                  <p className="text-xs text-[#94a3b8] mt-0.5">License: B123456</p>
                </div>
              </div>
              <button className="p-3 bg-[#10b981] text-white rounded-lg hover:bg-[#0f9e6e] transition-colors">
                <Phone className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Trip Progress */}
          <div className="bg-white rounded-xl shadow-sm p-5 mb-6">
            <h3 className="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider mb-4">
              Progress
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-[#64748b]">Stops Completed</span>
                <span className="font-semibold text-[#1e293b]">{completedStops}/{mockStops.length}</span>
              </div>
              <div className="w-full bg-[#f3f4f6] rounded-full h-2.5">
                <div 
                  className="bg-[#2563eb] h-2.5 rounded-full" 
                  style={{ width: `${(completedStops / mockStops.length) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Finances Card */}
          <div className="bg-white rounded-xl shadow-sm p-5 mb-6">
            <h3 className="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider mb-4">
              Finances
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-[#64748b]">Total COD</span>
                <span className="font-semibold text-[#1e293b]">LKR {totalCOD.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#64748b]">Collected</span>
                <span className="font-semibold text-[#10b981]">LKR {collectedCOD.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center pt-3 border-t border-[#e9ecef]">
                <span className="text-[#64748b]">Pending</span>
                <span className="font-semibold text-[#f59e0b]">LKR {(totalCOD - collectedCOD).toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* ETA Card */}
          <div className="bg-white rounded-xl shadow-sm p-5 border-l-4 border-[#ef4444]">
            <div className="flex items-start space-x-3">
              <Clock className="w-5 h-5 text-[#ef4444] flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-[#ef4444]">Delayed by 15 mins</p>
                <p className="text-sm text-[#64748b] mt-1">
                  Due to traffic near Pettah Market
                </p>
                <p className="text-xs text-[#94a3b8] mt-2">
                  Expected arrival: 14:45 (was 14:30)
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Incident Modal */}
      <IncidentModal 
        isOpen={showIncidentModal}
        onClose={() => setShowIncidentModal(false)}
        tripId={params.id}
      />
    </>
  )
}
