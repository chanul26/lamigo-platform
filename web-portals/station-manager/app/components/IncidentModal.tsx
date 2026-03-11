// app/components/IncidentModal.tsx - Full version
'use client'

import { useState } from 'react'
import { X, AlertTriangle, Truck, Wrench, MessageSquare, MapPin, Package, Phone } from 'lucide-react'

interface IncidentModalProps {
  isOpen: boolean
  onClose: () => void
  tripId: string
}

type IncidentType = 'accident' | 'breakdown' | 'other'

export default function IncidentModal({ isOpen, onClose, tripId }: IncidentModalProps) {
  const [incidentType, setIncidentType] = useState<IncidentType>('accident')
  const [selectedDrivers, setSelectedDrivers] = useState<string[]>([])
  const [incidentNotes, setIncidentNotes] = useState('')

  if (!isOpen) return null

  const incidentTypeConfig = {
    accident: { 
      bgColor: 'bg-[#fee2e2]', 
      textColor: 'text-[#ef4444]',
      borderColor: 'border-[#ef4444]',
      hoverColor: 'hover:bg-[#ef4444]/10',
      icon: AlertTriangle,
      label: 'Accident'
    },
    breakdown: { 
      bgColor: 'bg-[#fed7aa]', 
      textColor: 'text-[#f59e0b]',
      borderColor: 'border-[#f59e0b]',
      hoverColor: 'hover:bg-[#f59e0b]/10',
      icon: Wrench,
      label: 'Breakdown'
    },
    other: { 
      bgColor: 'bg-[#f3f4f6]', 
      textColor: 'text-[#64748b]',
      borderColor: 'border-[#64748b]',
      hoverColor: 'hover:bg-[#f3f4f6]',
      icon: AlertTriangle,
      label: 'Other'
    }
  }

  const mockDrivers = [
    { id: 'D001', name: 'Nimal Silva', location: 'Colombo', available: true },
    { id: 'D002', name: 'Priyantha Perera', location: 'Kadawatha', available: true },
    { id: 'D003', name: 'Sunil Weerasinghe', location: 'Gampaha', available: false },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-[#e9ecef]">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-[#fee2e2] rounded-lg">
              <AlertTriangle className="w-6 h-6 text-[#ef4444]" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-[#1e293b]">Incident Management</h2>
              <p className="text-sm text-[#64748b]">Report and handle trip exceptions</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="p-2 text-[#94a3b8] hover:text-[#64748b] hover:bg-[#f3f4f6] rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Trip Context */}
          <div className="bg-[#f8f9fa] rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <span className="text-sm font-semibold text-[#1e293b]">Trip ID:</span>
              <span className="text-sm text-[#2563eb] font-medium">{tripId}</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2 text-sm">
                <MapPin className="w-4 h-4 text-[#94a3b8]" />
                <span className="text-[#64748b]">Near Pettah Market, Colombo</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <Package className="w-4 h-4 text-[#94a3b8]" />
                <span className="text-[#64748b]">15 items (LKR 45,000)</span>
              </div>
            </div>
          </div>

          {/* Incident Type Selector */}
          <div>
            <label className="block text-sm font-medium text-[#1e293b] mb-3">
              Incident Category
            </label>
            <div className="grid grid-cols-3 gap-3">
              {(Object.keys(incidentTypeConfig) as IncidentType[]).map((type) => {
                const config = incidentTypeConfig[type]
                const Icon = config.icon
                const isSelected = incidentType === type
                
                return (
                  <button
                    key={type}
                    onClick={() => setIncidentType(key)}
                    className={`flex flex-col items-center space-y-2 px-4 py-3 rounded-lg border-2 transition-all ${
                      isSelected 
                        ? `${config.bgColor} ${config.textColor} ${config.borderColor}`
                        : 'border-[#e9ecef] text-[#64748b] hover:bg-[#f8f9fa]'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-xs font-medium">{config.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Rescue & Recovery */}
          <div className="bg-white rounded-lg border border-[#e9ecef] p-5">
            <h3 className="font-semibold text-[#1e293b] mb-4 flex items-center">
              <Truck className="w-5 h-5 mr-2 text-[#64748b]" />
              Rescue & Recovery
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-[#64748b] mb-2">
                  Assign Rescue Driver(s)
                </label>
                <select 
                  multiple 
                  className="w-full border border-[#e9ecef] rounded-lg p-2.5 h-28 focus:outline-none focus:ring-2 focus:ring-[#2563eb]"
                  value={selectedDrivers}
                  onChange={(e) => {
                    const values = Array.from(e.target.selectedOptions, option => option.value)
                    setSelectedDrivers(values)
                  }}
                >
                  {mockDrivers.map(driver => (
                    <option 
                      key={driver.id} 
                      value={driver.id}
                      disabled={!driver.available}
                      className="py-2"
                    >
                      {driver.name} - {driver.location} {!driver.available ? '(Unavailable)' : ''}
                    </option>
                  ))}
                </select>
              </div>
              
              <button className="w-full bg-[#1e293b] text-white px-4 py-2.5 rounded-lg hover:bg-[#334155] transition-colors flex items-center justify-center space-x-2 font-medium">
                <Truck className="w-5 h-5" />
                <span>Dispatch Rescue Team</span>
              </button>
            </div>
          </div>

          {/* Communication */}
          <div className="bg-white rounded-lg border border-[#e9ecef] p-5">
            <h3 className="font-semibold text-[#1e293b] mb-4">Communication</h3>
            <div className="space-y-3">
              <button className="w-full bg-[#f59e0b] text-white px-4 py-2.5 rounded-lg hover:bg-[#d97706] transition-colors flex items-center justify-center space-x-2 font-medium">
                <MessageSquare className="w-5 h-5" />
                <span>Broadcast Delay SMS to Customers</span>
              </button>
              <button className="w-full bg-[#ef4444] text-white px-4 py-2.5 rounded-lg hover:bg-[#dc2626] transition-colors flex items-center justify-center space-x-2 font-medium">
                <X className="w-5 h-5" />
                <span>Abort Trip & Cancel SMS</span>
              </button>
            </div>
          </div>

          {/* Resolution Notes */}
          <div>
            <label className="block text-sm font-medium text-[#1e293b] mb-2">
              Incident Log
            </label>
            <textarea
              className="w-full border border-[#e9ecef] rounded-lg p-3 h-24 focus:outline-none focus:ring-2 focus:ring-[#2563eb] resize-none"
              placeholder="Enter detailed notes about the incident and resolution..."
              value={incidentNotes}
              onChange={(e) => setIncidentNotes(e.target.value)}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-[#e9ecef] bg-[#f8f9fa]">
          <button
            onClick={onClose}
            className="px-4 py-2.5 border border-[#e9ecef] rounded-lg text-[#64748b] hover:bg-white transition-colors font-medium"
          >
            Cancel
          </button>
          <button
            className="px-4 py-2.5 bg-[#10b981] text-white rounded-lg hover:bg-[#0f9e6e] transition-colors font-medium"
          >
            Mark Incident as Resolved
          </button>
        </div>
      </div>
    </div>
  )
}
