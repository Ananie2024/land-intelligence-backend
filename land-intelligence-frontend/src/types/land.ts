import { BaseEntity, QueryFilters } from './common';

export interface Parish extends BaseEntity {
  name: string;
}

export interface ParishCreate {
  name: string;
}

export interface ParcelGeo {
  id: string;
  upi: string;
  owner_name: string;
  area_sqm: number;
  geometry: [number, number][][]; // Array of polygon rings
  valuation?: number;
}

export interface Parcel extends BaseEntity {
  upi: string;
  parish_id: string;
  land_use_category_id?: string | null;
  area_sqm: number;
  geometry_wkb?: string | null;
  owner_name: string;
  owner_contact?: string | null;
  location_description?: string | null;
  valuation?: number | null;
  valuation_date?: string | null;
  metadata?: Record<string, any> | null;
  parish_name?: string | null;
  land_use_category_name?: string | null;
  // Parsed geometry for map display
  geometry?: [number, number][][];
}

export interface ParcelCreate {
  upi: string;
  parish_id: string;
  land_use_category_id?: string | null;
  area_sqm: number;
  geometry_wkb?: string | null;
  owner_name: string;
  owner_contact?: string | null;
  location_description?: string | null;
  valuation?: number | null;
  valuation_date?: string | null;
  metadata?: Record<string, any> | null;
}

export interface ParcelFilters extends QueryFilters {
  parish_id?: string;
  land_use_category_id?: string;
  owner_name?: string;
  upi?: string;
  min_area_sqm?: number;
  max_area_sqm?: number;
}

export interface ParcelOwnershipHistory extends BaseEntity {
  parcel_upi: string;
  owner_name: string;
  owner_contact?: string | null;
  transfer_date: string;
  document_reference?: string | null;
  notes?: string | null;
}