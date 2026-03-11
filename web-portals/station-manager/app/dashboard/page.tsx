

'use client'

import { Truck, Package, Users, AlertTriangle, TrendingUp, Clock } from 'lucide-react'

const stats = [
  { name: 'Active Trips', value: '12', icon: Truck, change: '+2', changeType: 'increase' },
  { name: 'Packages in Transit', value: '145', icon: Package, change: '+18', changeType: 'increase' },
  { name: 'Active Drivers', value: '24', icon: Users, change: '-1', changeType: 'decrease' },
  { name: 'Incidents Today', value: '3', icon: AlertTriangle, change: '-2', changeType: 'decrease' },
]

export default function DashboardPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-[#1e293b] mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-[#2563eb]/10 rounded-xl">
                  <Icon className="w-6 h-6 text-[#2563eb]" />
                </div>
                <span className={`text-sm font-semibold px-2 py-1 rounded-full ${
                  stat.changeType === 'increase' ? 'bg-[#10b981]/10 text-[#10b981]' : 'bg-[#ef4444]/10 text-[#ef4444]'
                }`}>
                  {stat.change}
                </span>
              </div>
              <p className="text-3xl font-bold text-[#1e293b]">{stat.value}</p>
              <p className="text-[#64748b] text-sm mt-1">{stat.name}</p>
            </div>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-[#1e293b] mb-4">Recent Trips</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between py-3 border-b border-[#e9ecef] last:border-0">
                <div>
                  <p className="font-medium text-[#1e293b]">#TR-2025-00{i}</p>
                  <p className="text-sm text-[#64748b]">Colombo → Kandy</p>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-[#64748b] flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {i * 15} min ago
                  </span>
				 
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-[#1e293b] mb-4">Performance Overview</h2>
          <div className="space-y-5">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-[#64748b]">On-Time Delivery</span>
                <span className="font-semibold text-[#1e293b]">92%</span>
              </div>

            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-[#64748b]">Fleet Utilization</span>
                <span className="font-semibold text-[#1e293b]">78%</span>
              </div>
              <div className="w-full bg-[#f3f4f6] rounded-full h-2.5">
                <div className="bg-[#2563eb] h-2.5 rounded-full" style={{ width: '78%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-[#64748b]">Customer Satisfaction</span>
                <span className="font-semibold text-[#1e293b]">4.8/5</span>
              </div>
              <div className="w-full bg-[#f3f4f6] rounded-full h-2.5">
                <div className="bg-[#8b5cf6] h-2.5 rounded-full" style={{ width: '96%' }}></div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#e9ecef]">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[#64748b]">Today's Revenue</span>
              <span className="text-xl font-bold text-[#1e293b]">LKR 124,500</span>
            </div>
            <div className="flex items-center text-[#10b981] text-sm mt-1">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>+12.5% from yesterday</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
