/**
 * LamiGo Station Manager - API Client
 * Handles all communication with the FastAPI backend
 */

import type { PackageResponse, PackageCreate, PackageUpdate, SMSCreate, Station, OptimizationResult, DriverResponse, DriverCreate, SettlementResponse, SettlementCreate, BranchResponse, BranchUpdate, IncidentResponse, IncidentUpdate, TripResponse, TripCreate, TaskCreate, TaskResponse } from '@/types';

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
  // Packages
  getPackages: (): Promise<PackageResponse[]> => fetchApi<PackageResponse[]>('/packages/'),
  getPackage: (id: string): Promise<PackageResponse> => fetchApi<PackageResponse>(`/packages/${id}`),
  createPackage: (data: PackageCreate): Promise<PackageResponse> => fetchApi<PackageResponse>('/packages/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  updatePackage: (id: string, data: PackageUpdate): Promise<PackageResponse> => fetchApi<PackageResponse>(`/packages/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  // Communication
  sendSmsLog: (data: SMSCreate): Promise<{message: string}> => fetchApi<{message: string}>('/communication/sms', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  
  // Drivers
  getDrivers: (): Promise<DriverResponse[]> => fetchApi<DriverResponse[]>('/users/?role=DRIVER'),
  createDriver: (data: DriverCreate): Promise<DriverResponse> => fetchApi<DriverResponse>('/users/drivers', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Settlements
  getSettlements: (): Promise<SettlementResponse[]> => fetchApi<SettlementResponse[]>('/settlements/'),
  createSettlement: (data: SettlementCreate): Promise<SettlementResponse> => fetchApi<SettlementResponse>('/settlements/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Branch Settings
  getMyBranch: (): Promise<BranchResponse> => fetchApi<BranchResponse>('/branches/my-branch/info'),
  updateMyBranch: (data: BranchUpdate): Promise<BranchResponse> => fetchApi<BranchResponse>('/branches/my-branch/info', {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  // Incidents
  getIncidents: (): Promise<IncidentResponse[]> => fetchApi<IncidentResponse[]>('/incidents/'),
  updateIncident: (id: string, data: IncidentUpdate): Promise<IncidentResponse> => fetchApi<IncidentResponse>(`/incidents/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),

  // Trips & Routing
  getTrips: (): Promise<TripResponse[]> => fetchApi<TripResponse[]>('/trips/'),
  createTrip: (data: TripCreate): Promise<TripResponse> => fetchApi<TripResponse>('/trips/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Delivery Tasks
  createTask: (data: TaskCreate): Promise<TaskResponse> => fetchApi<TaskResponse>('/tasks/', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
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