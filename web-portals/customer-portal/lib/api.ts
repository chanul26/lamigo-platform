import type { 
  PublicTrackingDetailResponse, 
  PublicRecipientLocationUpdate, 
  PublicRecipientLocationResponse,
  PublicInstructionCreate,
  PublicPreferenceCreate
} from '@/types';

// Base URL for the LamiGo API (Make sure it matches your FastAPI port)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Generic fetch wrapper for public endpoints (NO AUTH HEADERS)
 */
export async function fetchPublicApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, { 
    ...options, 
    headers: { 
      'Content-Type': 'application/json',
      ...options.headers 
    } 
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * LamiGo Public Tracking API Client
 */
export const trackingClient = {
  
  // 1. Fetch package details by the public Tracking ID (e.g., LMG-12345-ABCDE)
  getTracking: (trackingId: string): Promise<PublicTrackingDetailResponse> => 
    fetchPublicApi<PublicTrackingDetailResponse>(`/public/tracking/${trackingId}`),

  // 2. Customer updates their own GPS coordinates
  updateLocation: (trackingId: string, data: PublicRecipientLocationUpdate): Promise<PublicRecipientLocationResponse> => 
    fetchPublicApi<PublicRecipientLocationResponse>(`/public/tracking/${trackingId}/location`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    }),

  // 3. Add a text instruction for the driver
  addInstruction: (trackingId: string, data: PublicInstructionCreate): Promise<{message: string}> => 
    fetchPublicApi<{message: string}>(`/public/tracking/${trackingId}/instruction`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // 4. Set delivery preference (Unavailable date)
  setPreference: (trackingId: string, data: PublicPreferenceCreate): Promise<{message: string}> => 
    fetchPublicApi<{message: string}>(`/public/tracking/${trackingId}/preference`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // 5. Reject scheduled delivery
  rejectDelivery: (trackingId: string): Promise<{message: string}> => 
    fetchPublicApi<{message: string}>(`/public/tracking/${trackingId}/reject`, { 
      method: 'POST' 
    }),
};