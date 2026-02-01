/**
 * LamiGo Station Manager - TypeScript Type Definitions
 * These interfaces mirror the backend Pydantic schemas exactly
 * Backend source: backend/app/schemas/
 */

// ============================================
// Package Types (mirrors schemas/package.py)
// ============================================

export type PackageStatus = 'Pending' | 'In Transit' | 'Delivered' | 'Returned';

export interface PackageBase {
  tracking_number: string;
  recipient_name: string;
  delivery_address: string;
  status: PackageStatus;
}

export interface PackageCreate extends PackageBase {
  station_id?: number;
}

export interface Package extends PackageBase {
  id: number;
  assigned_driver_id?: number;
  created_at: string; // ISO datetime string from JSON
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
