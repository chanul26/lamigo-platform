/**
 * LamiGo Station Manager - TypeScript Type Definitions
 * These interfaces mirror the backend Pydantic schemas exactly
 * 
 * Backend source: backend/app/schemas/
 */

// ============================================
// Package Types (mirrors schemas/package_schemas.py)
// ============================================

export type PackageStatus = 'TO_BE_DELIVERED' | 'DRAFT' | 'SCHEDULED' | 'ON_TRIP' | 'DELIVERING_NOW' | 'COMPLETED' | 'FAILED';
export type LocationType = 'HOME' | 'APARTMENT' | 'OFFICE' | 'WAREHOUSE' | 'RETAIL_STORE' | 'OTHER';

export interface RecipientSummary {
  recipient_id: string;
  phone_number: string;
  location_type?: LocationType;
}

export interface PackageCreate {
  weight: number;
  is_cod: boolean;
  cod_amount: number;
  delivery_charge: number;
  sender_name: string;
  sender_phone?: string;
  sender_address?: string;
  recipient_name: string;
  recipient_phone: string;
  address: string;
  location_type?: LocationType;
  floor_number?: string;
  gps_lat: number;
  gps_lng: number;
}

export interface PackageResponse {
  package_id: string;
  tracking_id: string;
  branch_id: string;
  status: PackageStatus;
  weight: number;
  is_cod: boolean;
  cod_amount: number;
  delivery_charge: number;
  sender_name: string;
  sender_phone?: string;
  recipient_name: string;
  address: string;
  gps_lat: number;
  gps_lng: number;
  recipient?: RecipientSummary;
  created_at: string;
  updated_at: string;
}

// ============================================
// Driver Types (mirrors schemas/user_schemas.py)
// ============================================

export type VehicleType = 'MOTORCYCLE' | 'THREE_WHEEL' | 'LORRY';
export type DriverStatus = 'OFF_DUTY' | 'AVAILABLE' | 'TRIP_SCHEDULED' | 'ON_TRIP' | 'ON_INCIDENT' | 'INCIDENT_RESPONSE';

export interface DriverCreate {
  role: 'DRIVER';
  full_name: string;
  phone_number: string;
  nic_number: string;
  vehicle_type: VehicleType;
  vehicle_number: string;
  license_number: string;
  commission_rate?: number;
}

export interface DriverResponse {
  uid: string;
  full_name: string;
  nic_number: string;
  phone_number: string;
  vehicle_type: VehicleType;
  vehicle_number: string;
  status: DriverStatus;
  is_active: boolean;
  wallet_balance: number;
}

// ============================================
// Station Types (mirrors schemas/station.py)
// ============================================

export interface StationBase {
  name: string;
  location_code: string;
  address: string;
  latitude?: number;
  longitude?: number;
}

export interface StationCreate extends StationBase {}

export interface Station extends StationBase {
  id: number;
  is_active: boolean;
  package_count: number;
}

// ============================================
// API Response Types
// ============================================

export interface ApiResponse<T> {
  data: T;
  status: 'success' | 'error';
  message?: string;
}

export interface OptimizationResult {
  status: string;
  message: string;
  package_ids: number[];
  optimized_order: number[];
  estimated_time_minutes: number;
  total_distance_km: number;
}

// ============================================
// Dashboard Statistics
// ============================================

export interface DashboardStats {
  total_packages: number;
  pending_packages: number;
  in_transit_packages: number;
  delivered_packages: number;
  active_drivers: number;
  total_drivers: number;
}

// ============================================
// Settlement Types (mirrors schemas/settlement_schemas.py)
// ============================================

export type PaymentMethod = 'CASH' | 'BANK_TRANSFER' | 'CHEQUE';

export interface SettlementCreate {
  driver_id: string;
  amount_paid: number;
  payment_method: PaymentMethod;
  reference_note?: string;
}

export interface SettlementResponse {
  settlement_id: string;
  driver_id: string;
  processed_by: string;
  amount_paid: number;
  balance_at_settlement: number;
  payment_method: PaymentMethod;
  reference_note?: string;
  created_at: string;
}

// ============================================
// Branch Types (mirrors schemas/branch_schemas.py)
// ============================================

export interface BranchUpdate {
  name?: string;
  address?: string;
  gps_lat?: number;
  gps_lng?: number;
  default_commission_rate?: number;
}

export interface BranchResponse {
  branch_id: string;
  org_id: string;
  name: string;
  address: string;
  gps_lat: number;
  gps_lng: number;
  default_commission_rate: number;
  created_at: string;
  updated_at: string;
}

// ============================================
// Incident Types (mirrors schemas/incident_schemas.py)
// ============================================

export type IncidentType = 'VEHICLE_BREAKDOWN' | 'ACCIDENT' | 'TRAFFIC_POLICE' | 'MEDICAL_EMERGENCY' | 'OTHER';
export type IncidentStatus = 'REPORTED' | 'INVESTIGATING' | 'RESOLVED';
export type ResponseType = 'HELP' | 'PACKAGE_RESCUE' | 'MECHANICAL_AID' | 'OTHER';
export type ResponseStatus = 'DISPATCHED' | 'ON_SITE' | 'COMPLETED' | 'CANCELLED';

export interface IncidentResponse {
  incident_id: string;
  trip_id: string;
  driver_id: string;
  type: IncidentType;
  reported_at_lat: number;
  reported_at_lng: number;
  description?: string;
  status: IncidentStatus;
  handled_by?: string;
  handled_at?: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentUpdate {
  status: IncidentStatus;
  description?: string;
}

// ============================================
// Package Update & Communication Types
// ============================================

export interface PackageUpdate {
  status?: PackageStatus;
  package_photo_url?: string;
  num_of_attempts?: number;
}

export interface SMSCreate {
  package_id: string;
  recipient_phone: string;
  message_body: string;
  category: string;
  status: string;
}

// ============================================
// Trips & Tasks Types (mirrors schemas)
// ============================================

export type TripStatus = 'DRAFT' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
export type TaskStatus = 'DRAFT' | 'SCHEDULED' | 'ON_TRIP' | 'DELIVERING_NOW' | 'COMPLETED' | 'FAILED';

export interface TripCreate {
  branch_id: string;
  driver_id?: string | null;
  scheduled_start_time?: string | null;
}

export interface TripResponse {
  trip_id: string;
  branch_id: string;
  driver_id?: string | null;
  status: TripStatus;
  total_tasks_count: number;
  delivered_count: number;
  total_weight: number;
  total_cod_to_collect: number;
  scheduled_start_time?: string | null;
  actual_start_time?: string | null;
  estimated_return_time_scheduled?: string | null;
  estimated_return_time_actual?: string | null;
  actual_return_time?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  sequence_number: number;
  trip_id: string;
  package_id: string;
  estimated_start_time?: string | null;
  estimated_arrival_time?: string | null;
}

export interface TaskResponse {
  task_id: string;
  trip_id: string;
  package_id: string;
  status: TaskStatus;
  sequence_number: number;
  created_at: string;
  updated_at: string;
}

// ============================================
// Financial Profile Types
// ============================================
export interface FinancialProfileResponse {
  driver_id: string;
  current_payable_balance: number;
  total_lifetime_earnings: number;
  total_lifetime_settled: number;
  last_settlement_date?: string | null;
  updated_at: string;
}

