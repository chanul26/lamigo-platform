// ============================================
// LamiGo Customer Portal - Types
// ============================================

export type PackageStatus = 'TO_BE_DELIVERED' | 'DRAFT' | 'SCHEDULED' | 'ON_TRIP' | 'DELIVERING_NOW' | 'COMPLETED' | 'FAILED';

export interface PublicRecipientOut {
  recipient_id: string;
  name: string;
  phone_number: string;
  address: string;
  location_type?: string | null;
  floor_number?: string | null;
  is_location_verified: boolean;
  gps_lat: number;
  gps_lng: number;
}

export interface PublicCurrentTaskOut {
  estimated_arrival_time?: string | null;
  sequence_number: number;
}

export interface PublicTrackingDetailResponse {
  package_id: string;
  tracking_id: string;
  branch_id: string;
  status: PackageStatus;
  weight: number;
  is_cod: boolean;
  cod_amount: number;
  delivery_charge: number;
  sender_name: string;
  sender_phone?: string | null;
  recipient_name: string;
  address: string;
  gps_lat: number;
  gps_lng: number;
  num_of_attempts: number;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
  recipient?: PublicRecipientOut | null;
  current_task?: PublicCurrentTaskOut | null;
}

export interface PublicRecipientLocationUpdate {
  gps_lat: number;
  gps_lng: number;
}

export interface PublicRecipientLocationResponse {
  message: string;
  recipient: PublicRecipientOut;
}

export interface PublicInstructionCreate {
  content_text: string;
}

export interface PublicPreferenceCreate {
  target_date: string; // Format: YYYY-MM-DD
  status?: 'UNAVAILABLE';
}