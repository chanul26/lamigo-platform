"use client";

import { ArrowLeft, Package, Upload, FileText } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function AddPackagePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('manual');

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <button 
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
        >
          <ArrowLeft size={20} />
          <span className="text-sm">Back to Packages</span>
        </button>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Add New Package</h1>
      </div>

      {/* Form Container */}
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-8">
          <button
            onClick={() => setActiveTab('manual')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'manual'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <Package size={16} />
              Manual Entry
            </div>
          </button>
          <button
            onClick={() => setActiveTab('bulk')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'bulk'
                ? 'text-blue-600 border-blue-600'
                : 'text-gray-500 border-transparent hover:text-gray-700'
            }`}
          >
            <div className="flex items-center gap-2">
              <Upload size={16} />
              Bulk Upload
            </div>
          </button>
        </div>

        {/* Manual Entry Form */}
        {activeTab === 'manual' && (
          <form className="space-y-6">
            {/* Package Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Package Number
              </label>
              <input
                type="text"
                placeholder="e.g. PKG-2024-00123"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              />
            </div>

            {/* Receiver Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Receiver Name
              </label>
              <input
                type="text"
                placeholder="Saman Perera"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              />
            </div>

            {/* Phone Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                placeholder="07x-xxx-xxxx"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              />
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Address
              </label>
              <input
                type="text"
                placeholder="House No, Street Name"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              />
            </div>

            {/* City/Area */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                City/Area
              </label>
              <input
                type="text"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              />
            </div>

            {/* COD Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                COD Amount (LKR)
              </label>
              <input
                type="text"
                defaultValue="0.00"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
              />
            </div>

            {/* Note/Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Note / Description
              </label>
              <textarea
                placeholder="e.g. Fragile"
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors resize-none"
              />
            </div>

            {/* Description Text */}
            <div className="text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-4">
              Package will be added to Inventory and assigned to a driver.
            </div>

            {/* Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Add to Inventory
              </button>
            </div>
          </form>
        )}

        {/* Bulk Upload Form */}
        {activeTab === 'bulk' && (
          <div className="text-center py-12">
            <FileText size={48} className="text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Bulk Upload</h3>
            <p className="text-gray-600 mb-6">Upload multiple packages at once using CSV file</p>
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
              Choose CSV File
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
