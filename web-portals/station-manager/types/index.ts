/**
 * LamiGo Station Manager - TypeScript Type Definitions
 * These interfaces mirror the backend Pydantic schemas exactly
 * 
 * Backend source: backend/app/schemas/
 */

// ============================================
// Package Types (mirrors schemas/package.py)
// ============================================

export type PackageStatus = 'TO_BE_DELIVERED' | 'DRAFT' | 'SCHEDULED' | 'ON_TRIP' | 'DELIVERING_NOW' | 'COMPLETED' | 'FAILED';
export type LocationType = 'HOME' | 'APARTMENT' | 'OFFICE' | 'WAREHOUSE' | 'RETAIL_STORE' | 'OTHER';

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

export interface Package {
  package_id: string;
  tracking_id: string;
  branch_id: string;
  status: PackageStatus;
  weight: number;
  is_cod: boolean;
  cod_amount: number;
  delivery_charge: number;
  sender_name: string;
  recipient_name: string;
  recipient_phone?: string;
  address: string;
  created_at: string;
}

// ============================================
// Driver Types (mirrors schemas/driver.py)
// ============================================

export type VehicleType = 'Bike' | 'Van' | 'Truck';

export interface DriverBase {
  name: string;
  phone_number: string;
  vehicle_type: string;
  is_active: boolean;
}

export interface DriverCreate extends DriverBase {}

export interface Driver extends DriverBase {
  id: number;
  current_location_lat?: number;
  current_location_long?: number;
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
