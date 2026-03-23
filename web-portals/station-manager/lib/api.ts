/**
 * LamiGo Station Manager - API Client
 * Handles all communication with the FastAPI backend
 */

import type { Package, Driver, Station, OptimizationResult } from '@/types';

// Base URL for the LamiGo API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = await fetch(url, { ...defaultOptions, ...options });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * LamiGo API Client
 * Provides typed methods for all API endpoints
 */
export const apiClient = {
  // ============================================
  // Package Endpoints
  // ============================================

  /**
   * Get all packages
   */
  getPackages: (): Promise<Package[]> => {
    return fetchApi<Package[]>('/packages/');
  },

  /**
   * Get a specific package by ID
   */
  getPackage: (id: number): Promise<Package> => {
    return fetchApi<Package>(`/packages/${id}`);
  },

  /**
   * Get a package by tracking number
   */
  getPackageByTracking: (trackingNumber: string): Promise<Package> => {
    return fetchApi<Package>(`/packages/tracking/${trackingNumber}`);
  },

  // ============================================
  // Driver Endpoints
  // ============================================

  /**
   * Get all drivers
   */
  getDrivers: (): Promise<Driver[]> => {
    return fetchApi<Driver[]>('/drivers/');
  },

  /**
   * Get only active drivers
   */
  getActiveDrivers: (): Promise<Driver[]> => {
    return fetchApi<Driver[]>('/drivers/active');
  },

  /**
   * Get a specific driver by ID
   */
  getDriver: (id: number): Promise<Driver> => {
    return fetchApi<Driver>(`/drivers/${id}`);
  },

  // ============================================
  // Station Endpoints (to be implemented)
  // ============================================

  /**
   * Get all stations
   */
  getStations: (): Promise<Station[]> => {
    return fetchApi<Station[]>('/stations/');
  },

  /**
   * Get a specific station by ID
   */
  getStation: (id: number): Promise<Station> => {
    return fetchApi<Station>(`/stations/${id}`);
  },

  // ============================================
  // Optimization Endpoints (to be implemented)
  // ============================================

  /**
   * Request route optimization for packages
   */
  optimizeRoute: (packageIds: number[]): Promise<OptimizationResult> => {
    return fetchApi<OptimizationResult>('/optimization/route', {
      method: 'POST',
      body: JSON.stringify({ package_ids: packageIds }),
    });
  },
};

/**
 * Calls the backend logout endpoint and clears the locally stored token.
 * Pass an explicit token when you have one (e.g. straight after Firebase auth),
 * otherwise it falls back to the value stored in localStorage.
 */
export async function logoutUser(token?: string): Promise<void> {
  const storedToken =
    token ??
    (typeof window !== 'undefined'
      ? localStorage.getItem('lamigo_station_token')
      : null);

  if (storedToken) {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${storedToken}`,
        },
      });
    } catch {
      // Best-effort — don't block the local logout if the network fails
    }
  }

  if (typeof window !== 'undefined') {
    localStorage.removeItem('lamigo_station_token');
  }
}

/**
 * Health check utility
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/`);
    return response.ok;
  } catch {
    return false;
  }
}

export default apiClient;
