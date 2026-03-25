/**
 * LamiGo Station Manager - API Client
 * Handles all communication with the FastAPI backend
 */

import type { Package, Driver, Station, OptimizationResult } from '@/types';

// Base URL for the LamiGo API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Generic fetch wrapper with Firebase Token Injection
 */
export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Securely inject the Firebase JWT token into the request
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('lamigo_station_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...options,
    headers: { ...headers, ...options.headers }
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

/**
 * LamiGo API Client
 */
export const apiClient = {
  getPackages: (): Promise<Package[]> => fetchApi<Package[]>('/packages/'),
  createPackage: (data: any): Promise<Package> => fetchApi<Package>('/packages/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getDrivers: (): Promise<any[]> => fetchApi<any[]>('/drivers/'),
  getTrips: (): Promise<any[]> => fetchApi<any[]>('/trips/'),
  getSettlements: (): Promise<any[]> => fetchApi<any[]>('/settlements/'),
  getIncidents: (): Promise<any[]> => fetchApi<any[]>('/incidents/'),
};



/**
 * Calls the backend logout endpoint and clears the locally stored token.
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