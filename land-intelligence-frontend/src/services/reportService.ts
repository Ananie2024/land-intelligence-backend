import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { APIResponse } from '@/types/api';

export interface TaxReportSummary {
  parcel_id: string;
  parcel_number: string;
  total_outstanding: number;
  overdue_amount: number;
  upcoming_amount: number;
  records: TaxRecordSummary[];
}

export interface TaxRecordSummary {
  id: string;
  assessment_year: string;
  assessed_value: number;
  base_tax_amount: number;
  penalties_amount: number;
  total_amount: number;
  status: string;
  due_date: string;
}

export interface GisComplianceReport {
  intersects: boolean;
  intersection_area: number;
  percentage_overlap: number;
  zoning_code: string;
}

export const reportService = {
  getTaxReport: async (parcelId: string): Promise<APIResponse<TaxReportSummary>> => {
    return apiClient.get<TaxReportSummary>(ENDPOINTS.TAX.OUTSTANDING(parcelId));
  },

  getTaxHistoryReport: async (
    parcelId: string, 
    params?: { skip?: number; limit?: number }
  ): Promise<APIResponse<TaxRecordSummary[]>> => {
    return apiClient.get<TaxRecordSummary[]>(ENDPOINTS.TAX.HISTORY(parcelId), params);
  },

  getGisOverlayReport: async (
    parcelId: string,
    zoningWkt: string,
    zoningCode: string
  ): Promise<APIResponse<GisComplianceReport>> => {
    return apiClient.post<GisComplianceReport>(ENDPOINTS.GIS.CHECK_OVERLAY, {
      parcel_id: parcelId,
      zoning_wkt: zoningWkt,
      zoning_code: zoningCode,
    });
  },

  calculateDistance: async (payload: {
    geom1_wkt?: string;
    parcel_id_1?: string;
    geom2_wkt?: string;
    parcel_id_2?: string;
  }): Promise<APIResponse<{ distance_meters: number; message: string }>> => {
    return apiClient.post<{ distance_meters: number; message: string }>(ENDPOINTS.GIS.DISTANCE, payload);
  },

  // Additional GIS methods
  checkIntersection: async (payload: {
    geom1_wkt?: string;
    parcel_id_1?: string;
    geom2_wkt?: string;
    parcel_id_2?: string;
  }): Promise<APIResponse<{
    intersects: boolean;
    overlaps: boolean;
    intersection_area_sqm: number;
    percentage_overlap_geom1: number;
    percentage_overlap_geom2: number;
  }>> => {
    return apiClient.post(ENDPOINTS.GIS.INTERSECTS, payload);
  },

  containsPoint: async (payload: {
    geom_wkt?: string;
    parcel_id?: string;
    x: number;
    y: number;
  }): Promise<APIResponse<{ contains: boolean; intersects: boolean }>> => {
    return apiClient.post(ENDPOINTS.GIS.CONTAINS_POINT, payload);
  },
};

export default reportService;